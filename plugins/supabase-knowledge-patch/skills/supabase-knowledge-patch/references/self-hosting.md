# Self-Hosting & Docker

## Supavisor Connection Pooler (Default)

Self-hosted Supabase now uses Supavisor (not PgBouncer) as the default connection pooler. Connection strings use a `postgres.[TENANT_ID]` username format:

```bash
# Session mode (port 5432) — behaves like direct Postgres
psql 'postgres://postgres.your-tenant-id:YOUR_PASSWORD@your-domain:5432/postgres'

# Transaction mode (port 6543) — connection pooling
psql 'postgres://postgres.your-tenant-id:YOUR_PASSWORD@your-domain:6543/postgres'
```

`POOLER_TENANT_ID` defaults to `your-tenant-id` in `.env`. When using `psql -U`, the username must also be `postgres.your-tenant-id`, not just `postgres`.

To bypass Supavisor for direct Postgres access: remove the `supavisor` service from `docker-compose.yml` and add port mapping to the `db` service.

## New API Keys for Self-Hosting (Asymmetric ES256)

Self-hosted Supabase now supports the new `sb_publishable_`/`sb_secret_` API keys alongside legacy JWT keys. Setup:

```bash
# Generate new keys and update .env
sh utils/add-new-auth-keys.sh --update-env

# Rotate API keys without changing the asymmetric key pair
sh utils/rotate-new-api-keys.sh --update-env
```

New environment variables (all optional — empty = legacy-only mode):

| Variable | Purpose |
|----------|---------|
| `SUPABASE_PUBLISHABLE_KEY` | Replaces `ANON_KEY` for client-side use |
| `SUPABASE_SECRET_KEY` | Replaces `SERVICE_ROLE_KEY` for server-side use |
| `JWT_KEYS` | JSON array of signing JWKs (EC private + symmetric). Used by Auth. |
| `JWT_JWKS` | JWKS with EC public + symmetric key. Used by PostgREST, Realtime, Storage. |

After generating keys, uncomment `GOTRUE_JWT_KEYS`, `API_JWT_JWKS`, and `JWT_JWKS` in `docker-compose.yml` for Auth, Realtime, and Storage respectively. PostgREST auto-detects via `PGRST_JWT_SECRET: ${JWT_JWKS:-${JWT_SECRET}}`.

**Backward compatibility**: Kong accepts both legacy and new keys simultaneously. `JWT_JWKS` includes both the EC public key (ES256) and symmetric key (HS256), so services verify both token types. No database changes required.

**Differences from managed platform**: Self-hosted supports one `sb_publishable` and one `sb_secret` key (platform allows multiple). No checksum validation on self-hosted.

## Self-Hosted Edge Functions

Edge Functions are pre-configured at `volumes/functions/`. Add new functions as `volumes/functions/<name>/index.ts`, then restart: `docker compose restart functions --no-deps`.

Key environment variables available inside functions:

| Variable | Value | Use |
|----------|-------|-----|
| `SUPABASE_URL` | `http://kong:8000` | Internal — use for server-side Supabase client calls |
| `SUPABASE_PUBLIC_URL` | `http://<your-domain>:8000` | External — use for URLs clients reach from outside |

Custom env vars via `.env.functions` file:

```yaml
# docker-compose.yml
functions:
  env_file:
    - .env.functions
```

Default limits: 150 MB memory, 60s timeout (configurable in `volumes/functions/main/index.ts`).

## Self-Hosted MCP Server Access

The MCP server runs behind Kong with all external connections denied by default. Access via SSH tunnel:

```bash
# 1. Find Docker bridge gateway IP
docker inspect supabase-kong --format '{{range .NetworkSettings.Networks}}{{println .Gateway}}{{end}}'

# 2. Add that IP to volumes/api/kong.yml under ip-restriction allow list
# 3. Restart Kong: docker compose restart kong
# 4. SSH tunnel from local machine
ssh -L localhost:8080:localhost:8000 you@your-supabase-host
```

MCP client config: `"url": "http://localhost:8080/mcp"`.

## Platform-to-Self-Hosted Database Restore

Export from managed Supabase in three separate dumps (uses `pg_dump` inside a Supabase Postgres container):

```bash
supabase db dump --db-url "CONNECTION_STRING" -f roles.sql --role-only
supabase db dump --db-url "CONNECTION_STRING" -f schema.sql
supabase db dump --db-url "CONNECTION_STRING" -f data.sql --use-copy --data-only
```

Restore to self-hosted (sets `session_replication_role = replica` to disable triggers during import):

```bash
psql --single-transaction --variable ON_ERROR_STOP=1 \
  --file roles.sql --file schema.sql \
  --command 'SET session_replication_role = replica' \
  --file data.sql \
  --dbname "postgres://postgres.your-tenant-id:PASS@host:5432/postgres"
```

**PG version mismatch workaround** (platform PG17 -> self-hosted PG15): edit `data.sql` before restore:

```bash
sed -i 's/^SET transaction_timeout/-- &/' data.sql
```

Comment out `COPY` statements for tables/columns that don't exist on self-hosted (e.g., `auth.oauth_clients`, `storage.buckets_vectors`).

## HTTPS with Docker Compose Overlays

Pre-configured reverse proxy overlays for Caddy (auto TLS) or Nginx + Let's Encrypt:

```bash
# Caddy (easiest — automatic TLS, HTTP/2, HTTP/3)
docker compose -f docker-compose.yml -f docker-compose.caddy.yml up -d

# Nginx + Let's Encrypt
docker compose -f docker-compose.yml -f docker-compose.nginx.yml up -d
```

Set `PROXY_DOMAIN` and `CERTBOT_EMAIL` in `.env`. Update `SUPABASE_PUBLIC_URL`, `API_EXTERNAL_URL`, and `SITE_URL` to HTTPS.

## Custom Email Templates (URL-Based)

Auth fetches email templates from HTTP URLs (not mounted files). Serve templates via a Caddy sidecar:

```yaml
# docker-compose.yml
auth:
  environment:
    GOTRUE_MAILER_TEMPLATES_INVITE: "http://templates-server/invite.html"
    GOTRUE_MAILER_SUBJECTS_INVITE: "You have been invited"

templates-server:
  image: caddy:2-alpine
  command: ["caddy", "file-server", "-r", "/templates", "--listen", ":80"]
  volumes:
    - ./volumes/templates:/templates
```

Notification emails use separate env vars: `GOTRUE_MAILER_NOTIFICATIONS_<TYPE>_ENABLED`, `GOTRUE_MAILER_TEMPLATES_<TYPE>_NOTIFICATION`. Types: `PASSWORD_CHANGED`, `EMAIL_CHANGED`, `PHONE_CHANGED`, `MFA_FACTOR_ENROLLED`, `MFA_FACTOR_UNENROLLED`, `IDENTITY_LINKED`, `IDENTITY_UNLINKED`.
