# Self-Hosting & Docker

## Asymmetric Auth Keys for Self-Hosting

Self-hosted Supabase now supports the new `sb_publishable_`/`sb_secret_` API keys alongside legacy HS256 JWTs. Setup uses two utility scripts:

```bash
# Generate ES256 key pair + new API keys, write to .env
sh utils/add-new-auth-keys.sh --update-env

# Rotate only the sb_ API keys (keeps EC key pair)
sh utils/rotate-new-api-keys.sh --update-env
```

New environment variables after running the script:

| Variable | Purpose |
|----------|---------|
| `SUPABASE_PUBLISHABLE_KEY` | Opaque client-side key (replaces `ANON_KEY`) |
| `SUPABASE_SECRET_KEY` | Opaque server-side key (replaces `SERVICE_ROLE_KEY`) |
| `JWT_KEYS` | JSON array of signing JWKs (EC private + legacy symmetric) — used by Auth |
| `JWT_JWKS` | JWKS with EC public + legacy symmetric key — used by PostgREST, Realtime, Storage |

After updating `.env`, uncomment `GOTRUE_JWT_KEYS`, `API_JWT_JWKS`, and `JWT_JWKS` in the respective service sections of `docker-compose.yml`, then restart. PostgREST auto-detects via `${JWT_JWKS:-${JWT_SECRET}}`.

Kong routes both key types simultaneously — the `kong-entrypoint.sh` script strips empty credential entries. For `sb_` keys, Kong substitutes internal pre-signed ES256 JWTs in the `Authorization` header. For legacy JWT keys, the key is passed through as-is. User session JWTs (from Auth) always pass through unchanged.

Backward compatible: all new variables are optional, empty = legacy-only mode.

## Supavisor Connection Pooler

Supavisor is now the default connection pooler (replaces direct Postgres access). Two connection modes:

```bash
# Session mode (port 5432) — behaves like direct Postgres
psql 'postgres://postgres.[POOLER_TENANT_ID]:[POSTGRES_PASSWORD]@[domain]:5432/postgres'

# Transaction mode (port 6543) — pooled connections
psql 'postgres://postgres.[POOLER_TENANT_ID]:[POSTGRES_PASSWORD]@[domain]:6543/postgres'
```

The username format is `postgres.[POOLER_TENANT_ID]` (default tenant ID: `your-tenant-id`, configurable in `.env`). To bypass Supavisor and expose Postgres directly, remove the `supavisor` service and add port mapping to the `db` service.

## Self-Hosted MCP Server Access

The MCP server runs behind Kong with all connections denied by default. Enable local-only access via SSH tunnel:

1. Get Docker bridge gateway IP: `docker inspect supabase-kong --format '{{range .NetworkSettings.Networks}}{{println .Gateway}}{{end}}'`
2. In `volumes/api/kong.yml`, comment out `request-termination`, uncomment the `ip-restriction` plugin, add the gateway IP to `allow`
3. `docker compose restart kong`
4. SSH tunnel: `ssh -L localhost:8080:localhost:8000 you@your-supabase-host`
5. MCP client config: `{ "url": "http://localhost:8080/mcp" }`

No OAuth 2.1 authentication — never expose to the internet.

## Platform-to-Self-Hosted Migration

Export platform database as three SQL files using the CLI (not raw `pg_dump`):

```bash
supabase db dump --db-url "[CONN_STRING]" -f roles.sql --role-only
supabase db dump --db-url "[CONN_STRING]" -f schema.sql
supabase db dump --db-url "[CONN_STRING]" -f data.sql --use-copy --data-only
```

Restore with triggers disabled:

```bash
psql --single-transaction --variable ON_ERROR_STOP=1 \
  --file roles.sql --file schema.sql \
  --command 'SET session_replication_role = replica' \
  --file data.sql \
  --dbname "postgres://postgres.your-tenant-id:[PASS]@[domain]:5432/postgres"
```

PG17→PG15 compatibility: `sed -i 's/^SET transaction_timeout/-- &/' data.sql`. Comment out `COPY` blocks for tables/columns that don't exist on self-hosted (e.g., `auth.oauth_clients`, `storage.buckets_vectors`).

Not included in dump: JWT secrets, OAuth provider config, Edge Functions code, Storage objects, SMTP settings, custom domains.

## Reverse Proxy HTTPS Overlays

Pre-configured Docker Compose overlays for HTTPS termination:

```bash
# Caddy (auto TLS, zero config)
docker compose -f docker-compose.yml -f docker-compose.caddy.yml up -d

# Nginx + Let's Encrypt
docker compose -f docker-compose.yml -f docker-compose.nginx.yml up -d
```

Requires `PROXY_DOMAIN` and `CERTBOT_EMAIL` in `.env`. Update `SUPABASE_PUBLIC_URL`, `API_EXTERNAL_URL`, and `SITE_URL` to `https://`. Caddy config in `volumes/proxy/caddy/Caddyfile`. Existing reverse proxies (HAProxy, Traefik) must proxy to Kong port 8000, enable WebSocket support, and proxy Storage directly to its container.

## Custom Email Templates via URL

Auth fetches email templates via HTTP GET (not Docker volume mounts). Serve templates with a sidecar like Caddy:

```yaml
templates-server:
  image: caddy:2-alpine
  command: ["caddy", "file-server", "-r", "/templates", "--listen", ":80"]
  volumes:
    - ./volumes/templates:/templates

auth:
  depends_on:
    templates-server:
      condition: service_started
  environment:
    GOTRUE_MAILER_TEMPLATES_INVITE: "http://templates-server/invite.html"
    GOTRUE_MAILER_SUBJECTS_INVITE: "You have been invited"
```

Notification templates (password changed, email changed, MFA enrolled, etc.) use `GOTRUE_MAILER_NOTIFICATIONS_<TYPE>_ENABLED` and `GOTRUE_MAILER_TEMPLATES_<TYPE>_NOTIFICATION`.

## Storage S3 Protocol Endpoint

Storage exposes an S3-compatible API at `/storage/v1/s3` — independent of the storage backend. Works with the default file-based backend.

Requires `REGION`, `S3_PROTOCOL_ACCESS_KEY_ID`, `S3_PROTOCOL_ACCESS_KEY_SECRET` in `.env`. Test with AWS CLI or rclone against `http://localhost:8000/storage/v1/s3`.

Use `docker-compose.s3.yml` overlay for MinIO backend, or `docker-compose.rustfs.yml` for RustFS backend.

## Utility Scripts & Key Configuration

```bash
sh utils/generate-keys.sh # Generate all secrets at once (experimental)
sh utils/db-passwd.sh     # Change database password post-setup
```

Studio uses HTTP basic auth (`DASHBOARD_USERNAME`/`DASHBOARD_PASSWORD` in `.env`). New secrets to configure: `SECRET_KEY_BASE` (64+ chars, for Realtime/Supavisor), `VAULT_ENC_KEY` (exactly 32 chars), `PG_META_CRYPTO_KEY` (32+ chars), `LOGFLARE_PUBLIC_ACCESS_TOKEN`, `LOGFLARE_PRIVATE_ACCESS_TOKEN`, `SUPABASE_PUBLIC_URL`.
