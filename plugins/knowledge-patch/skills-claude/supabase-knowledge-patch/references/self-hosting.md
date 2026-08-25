# Self-hosting

Use this reference for Docker configuration, key rotation, Auth and Functions setup, proxying, Storage, MCP, and restores.

## Docker and self-hosting operations

### Opaque API keys and ES256 are opt-in for Docker
The Docker stack can now add one `sb_publishable` and one `sb_secret` key alongside the legacy JWT keys with `utils/add-new-auth-keys.sh --update-env`. The script creates `JWT_KEYS` for Auth signing and `JWT_JWKS` for verification; enable them together in Auth, Realtime, and Storage, while PostgREST already falls back from `JWT_JWKS` to `JWT_SECRET`.

```yaml
auth:
  environment:
    GOTRUE_JWT_KEYS: ${JWT_KEYS:-[]}
realtime:
  environment:
    API_JWT_JWKS: ${JWT_JWKS:-{"keys":[]}}
storage:
  environment:
    JWT_JWKS: ${JWT_JWKS:-{"keys":[]}}
```

Self-hosted opaque keys are matched literally—the checksum is not validated—and, unlike hosted projects, only one key per role is supported. Changing `JWT_SECRET` also requires regenerating the JWKS because the legacy symmetric key is embedded in both generated values.

### Kong translates self-hosted opaque keys into role JWTs
For an API-key-only request, Kong replaces an `sb_` bearer value with an internal pre-signed `anon` or `service_role` ES256 JWT; a real user session JWT is passed through unchanged. Realtime WebSockets put the API key in `?apikey=`, while Storage and Functions routes do not require an API key at the gateway.

### API-key and signing-key rotations have different blast radii
`rotate-new-api-keys.sh` changes only the opaque keys and leaves user sessions valid. Re-running `add-new-auth-keys.sh` replaces the EC P-256 pair and invalidates ES256 sessions, while legacy HS256 sessions remain valid as long as `JWT_SECRET` is unchanged.

```sh
sh utils/rotate-new-api-keys.sh --update-env
```

### Docker upgrades require configuration migrations
Self-hosted updates cannot be handled safely by changing image tags alone: recent bundles require matching changes to Compose files and mounted configuration. Notable requirements include Realtime's mandatory `METRICS_JWT_SECRET`, Storage's `STORAGE_PUBLIC_URL` and named S3 volumes, Edge Runtime's `SUPABASE_PUBLISHABLE_KEYS`, `SUPABASE_SECRET_KEYS`, `SUPABASE_PUBLIC_URL`, and hybrid verifier, Studio's `PGRST_DB_SCHEMAS`/`PGRST_DB_EXTRA_SEARCH_PATH`/`PGRST_DB_MAX_ROWS`, the Vector 0.53 config rewrite, and removal of public Logflare `:4000` and the default Kong `/analytics/v1` route.

### Bootstrap and database-password helpers
`generate-keys.sh` generates and applies the initial secrets, while `db-passwd.sh` changes the database roles and `.env` together before the services are recreated. Manual configuration has non-obvious constraints: `VAULT_ENC_KEY` is exactly 32 characters, `SECRET_KEY_BASE` is at least 64, and `DASHBOARD_PASSWORD` must contain a letter but no special characters.

```sh
sh ./utils/generate-keys.sh
sh ./utils/db-passwd.sh
docker compose up -d --force-recreate
```

### Auth email templates are fetched over HTTP
Self-hosted Auth does not read templates directly from mounted volumes; every `GOTRUE_MAILER_TEMPLATES_*` value must be a URL reachable from the Auth container and return a valid Go HTML template, with fetch or parsing failures falling back to the built-in template. A private Caddy file-server container can serve the mounted files, and notification templates additionally require their `GOTRUE_MAILER_NOTIFICATIONS_*_ENABLED` switch.

```yaml
GOTRUE_MAILER_TEMPLATES_INVITE: http://templates-server/invite.html
GOTRUE_MAILER_NOTIFICATIONS_PASSWORD_CHANGED_ENABLED: 'true'
GOTRUE_MAILER_TEMPLATES_PASSWORD_CHANGED_NOTIFICATION: http://templates-server/password_changed_notification.html
```

### Self-hosted MCP is default-deny and has no OAuth
The Docker MCP route maps `/mcp` to Studio's internal `/api/mcp`, but Kong denies every connection by default and the server currently has no OAuth 2.1 authentication. Permit only a VPN or the Docker bridge gateway IP in Kong's `ip-restriction` plugin, retain `deny: []`, and reach it through an SSH tunnel rather than exposing it publicly.

```sh
ssh -L localhost:8080:localhost:8000 you@your-supabase-host
```

### Functions deploy from a shared filesystem
Self-hosted Functions live at `volumes/functions/<name>/index.ts`; Studio mounts the same directory, and adding or changing code requires restarting the `functions` service. Configuration changes require container recreation, `env_file` values load before explicit `environment` values, and the default per-invocation limits are 150 MB and 60 seconds in `volumes/functions/main/index.ts`.

```sh
docker compose restart functions --no-deps
docker compose up -d --force-recreate --no-deps functions
```

Inside a function, use the internal `SUPABASE_URL` (`http://kong:8000`) for service calls and `SUPABASE_PUBLIC_URL` only when constructing externally reachable links.

### OAuth settings need explicit Compose passthrough
Values placed in `.env` do not enter the Auth container unless matching `GOTRUE_EXTERNAL_*` entries exist under its Compose `environment`; every provider callback is `${API_EXTERNAL_URL}/auth/v1/callback`, and Auth must be recreated after changes. Keycloak additionally requires its full realm URL, while LinkedIn and Slack use the `LINKEDIN_OIDC` and `SLACK_OIDC` prefixes.

```yaml
GOTRUE_EXTERNAL_KEYCLOAK_REDIRECT_URI: ${API_EXTERNAL_URL}/auth/v1/callback
GOTRUE_EXTERNAL_KEYCLOAK_URL: ${KEYCLOAK_URL}
```

### Phone Auth and MFA defaults
Phone signup is enabled by default but cannot deliver codes until an SMS provider is passed into the Auth container; SMS OTPs default to six digits, a 60-second lifetime, and a 60-second per-number send interval. TOTP enrollment and verification are on by default, phone MFA is off, and users may enroll up to ten factors.

Development numbers can bypass delivery through `SMS_TEST_OTP`, optionally bounded by `SMS_TEST_OTP_VALID_UNTIL`; production should remove these mappings.

```dotenv
SMS_TEST_OTP=16505551234:123456
SMS_TEST_OTP_VALID_UNTIL=2026-12-31T23:59:59Z
```

### Reverse proxies have a Supabase-specific routing contract
A production proxy must forward normal traffic to Kong on port 8000, send Storage traffic directly to the Storage container, preserve `X-Forwarded` headers, and support Realtime WebSocket upgrades. The Docker bundle supplies Caddy and Nginx/Certbot overlays; after choosing one, set `SUPABASE_PUBLIC_URL`, `API_EXTERNAL_URL`, and `SITE_URL` to the same HTTPS origin.

```sh
docker compose -f docker-compose.yml -f docker-compose.caddy.yml up -d
```

### The S3 endpoint and S3 storage backend are independent
`/storage/v1/s3` is an S3-compatible client endpoint that can run over the default file backend, while `STORAGE_BACKEND=s3` can store objects in S3 without exposing that endpoint. The client endpoint uses `REGION`, `S3_PROTOCOL_ACCESS_KEY_ID`, and `S3_PROTOCOL_ACCESS_KEY_SECRET`; an AWS backend omits `GLOBAL_S3_ENDPOINT` and `GLOBAL_S3_FORCE_PATH_STYLE`, while Cloudflare R2 needs `TUS_ALLOW_S3_TAGS: "false"` for resumable uploads.

For an RLS-scoped S3 client on self-hosted Storage, use `STORAGE_TENANT_ID` as the access-key ID, `ANON_KEY` as the secret, and the user's JWT as the session token.

### Storage migrations must pass through the S3 protocol
Copying downloaded objects into `volumes/storage` does not recreate Storage's internal layout or metadata. Pre-create matching destination buckets, then copy S3-to-S3; restoring the database first already supplies the bucket definitions but not the objects.

```sh
rclone copy platform:your-bucket self-hosted:your-bucket --progress
```

### Platform restores need self-hosted version cleanup
Use `supabase db dump` rather than raw `pg_dump`, because the CLI filters internal schemas and reserved roles and makes the SQL idempotent. A hosted Postgres 17 dump can target the current Postgres 15 Docker image, but may require commenting out `transaction_timeout` and `COPY` blocks for newer Auth or Storage tables and columns; diagnose once without `--single-transaction`, then perform the corrected restore atomically.

```sh
sed -i 's/^SET transaction_timeout/-- &/' data.sql
```
