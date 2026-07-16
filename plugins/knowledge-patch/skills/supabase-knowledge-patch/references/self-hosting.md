# Self-hosting

## Upgrade and key architecture

### Configuration-aware Docker upgrades

Releases change Compose wiring, not only images. Merge every Docker changelog file, then recreate. The 2026-03-16 config changes Compose files, `.env.example`, Kong config/entrypoints, Function main worker, Auth-key utilities, proxy overlays.

```sh
docker compose pull
docker compose down
docker compose up -d
```

### Self-hosted publishable keys and asymmetric sessions

The 2026-03-16 stack adds `sb_publishable_...`/`sb_secret_...` beside `ANON_KEY`/`SERVICE_ROLE_KEY`. Use Node 16+ and OpenSSL to generate opaque keys and EC P-256 pair:

```sh
sh utils/add-new-auth-keys.sh --update-env
```

Set signing/verification on every JWT-aware service: Auth `GOTRUE_JWT_KEYS`, Realtime `API_JWT_JWKS`, Storage `JWT_JWKS`; PostgREST selects `${JWT_JWKS:-${JWT_SECRET}}`. `JWT_KEYS` has private EC plus legacy symmetric key; `JWT_JWKS` accepts ES256 and HS256. Changing `JWT_SECRET` requires regeneration. Public `/auth/v1/.well-known/jwks.json` publishes only EC public key.

### Self-hosted key compatibility and rotation

Gateway accepts old/new concurrently, but only one publishable and one secret key. It exact-matches opaque values without checksum validation, exchanges unauthenticated opaque keys for internal role JWTs, and preserves actual user bearer sessions.

```sh
# Opaque keys only; sessions survive.
sh utils/rotate-new-api-keys.sh --update-env
# Opaque keys and EC pair; ES256 sessions invalidated.
sh utils/add-new-auth-keys.sh --update-env
```

Legacy HS256 sessions survive EC regeneration while `JWT_SECRET` stays in JWKS. Restart, then update clients after opaque rotation.

### Hybrid authentication for self-hosted Functions

Merge `SUPABASE_PUBLISHABLE_KEYS`, `SUPABASE_SECRET_KEYS`, `SUPABASE_PUBLIC_URL` into Functions and update `volumes/functions/main/index.ts` for hybrid JWT verification. March 2026 adds optional rate limiting; February adds persistent named `deno-cache`.

## Functions and Storage

### Self-hosted Function lifecycle and URLs

Functions live `volumes/functions/<name>/index.ts`. Restart after code edits; force-recreate after environment changes. Internally use `SUPABASE_URL=http://kong:8000`; use `SUPABASE_PUBLIC_URL` only for external links.

```sh
docker compose restart functions --no-deps
docker compose up -d --force-recreate --no-deps functions
```

Defaults are 150 MB/60s per invocation, configurable as `memoryLimitMb`/`workerTimeoutMs` in main worker. Current Studio mounts same function directory; management UI needs February 2026 Compose changes.

### S3 protocol and S3 backend are independent

`/storage/v1/s3` is a protocol even with filesystem persistence. `STORAGE_BACKEND=s3` separately changes persistence. Protocol credentials: `REGION`, `S3_PROTOCOL_ACCESS_KEY_ID`, `S3_PROTOCOL_ACCESS_KEY_SECRET`. Non-AWS backend: `GLOBAL_S3_BUCKET`, `GLOBAL_S3_ENDPOINT`, path-style.

For AWS omit endpoint/path style. User-RLS S3 uses `STORAGE_TENANT_ID` access key, `ANON_KEY` secret, user JWT session token. On Cloudflare R2 set `TUS_ALLOW_S3_TAGS: "false"` if resumable upload fails because R2 lacks `x-amz-tagging`.

### Copying hosted Storage objects correctly

Never write downloaded files into `volumes/storage`; that bypasses internal layout/metadata. Pre-create buckets and copy through hosted/self-hosted S3 remotes; a restored DB already has bucket definitions. S3 never auto-creates a destination bucket.

```sh
rclone copy platform:media self-hosted:media --progress
rclone size platform:media
rclone size self-hosted:media
```

Use hosted `/storage/v1/s3`, preferring direct Storage hostname for large transfers.

## Auth and email

### URL-served Auth email templates

Auth fetches Go HTML templates over HTTP, not mounted volumes, and falls back to defaults for invalid/unreachable URLs. Serve private static files on Compose network. Flow templates: confirmation, recovery, magic link, invite, email change, reauth. Enabled notification variants: password/email/phone changes, MFA enrollment, identity linking. Recreate Auth after adding service/variables.

```yaml
auth:
  environment:
    GOTRUE_MAILER_TEMPLATES_INVITE: http://templates-server/invite.html
    GOTRUE_MAILER_SUBJECTS_INVITE: You have been invited
    GOTRUE_MAILER_NOTIFICATIONS_PASSWORD_CHANGED_ENABLED: 'true'
    GOTRUE_MAILER_TEMPLATES_PASSWORD_CHANGED_NOTIFICATION: http://templates-server/password_changed.html
```

### Self-hosted phone and MFA defaults

Phone signup defaults enabled but needs SMS provider. SMS OTP default: 60s, six digits (6–10 configurable). TOTP enroll/verify enabled; phone MFA disabled; 10 factors/user. Every setting needs matching `GOTRUE_SMS_*`/`GOTRUE_MFA_*` Compose pass-through and Auth force-recreate.

```dotenv
SMS_OTP_EXP=300
SMS_OTP_LENGTH=6
SMS_MAX_FREQUENCY=60s
MFA_PHONE_ENROLL_ENABLED=true
MFA_PHONE_VERIFY_ENABLED=true
MFA_MAX_ENROLLED_FACTORS=5
SMS_TEST_OTP=16505551234:123456
SMS_TEST_OTP_VALID_UNTIL=2026-12-31T23:59:59Z
```

Remove test OTPs in production. `GOTRUE_RATE_LIMIT_SMS_SENT` separately defaults to 30/hour.

## MCP and reverse proxy

### Self-hosted MCP is local-only and denied by default

Self-hosted MCP lacks OAuth 2.1 and Kong denies it by default. Expose only through VPN/SSH. For SSH, allow Docker bridge gateway in route `ip-restriction`, retain `deny: []`, restart Kong, and tunnel gateway port.

```sh
docker inspect supabase-kong \
  --format '{{range .NetworkSettings.Networks}}{{println .Gateway}}{{end}}'
docker compose restart kong
ssh -L localhost:8080:localhost:8000 you@your-supabase-host
```

Client URL is `http://localhost:8080/mcp`. Older automation must replace removed `get_anon_key` with `get_publishable_keys`.

### Reverse-proxy and HTTPS contract

Production TLS terminates before Kong. Proxy headers, Realtime WebSocket upgrade, and route Storage directly to Storage rather than Kong. Set public/Auth/Site URLs to HTTPS; remove Kong host binding if proxy shares network.

```dotenv
SUPABASE_PUBLIC_URL=https://supabase.example.com
API_EXTERNAL_URL=https://supabase.example.com
SITE_URL=https://app.example.com
```

Supplied Caddy or Nginx/Certbot overlays are available. Self-signed certs may mount into Kong 8443 for development, but browsers warn and most OAuth callbacks reject them.

## Restore and bootstrap

### Platform-to-self-host restore mismatches

Use `supabase db dump` because it filters internals/roles. Test for service/Postgres skew: Postgres 17 dump into current Postgres 15 can contain `SET transaction_timeout = 0` and newer Auth/Storage `COPY` columns. Identify in non-atomic trial, remove incompatibilities, then final single transaction.

```sh
sed -i 's/^SET transaction_timeout/-- &/' data.sql
```

Hosted JWTs fail after move due different secrets; preserved users reauthenticate. Storage objects/Functions need separate copies.

### Docker bootstrap and password helpers

`utils/generate-keys.sh` populates initial secrets; `utils/db-passwd.sh` rotates DB password across roles/`.env`. Review values and recreate. Rootless Docker needs `DOCKER_SOCKET_LOCATION`, e.g. `/run/user/1000/docker.sock`, or Vector may exit.

### Recent self-hosted security and configuration boundaries

February 2026 stops Logflare on `0.0.0.0:4000`, removes `/analytics/v1` from Kong, rewires Storage, enables S3 endpoint. Preserve when merging custom routes. March makes `METRICS_JWT_SECRET` mandatory for Realtime in `docker-compose.s3.yml`, adds `STORAGE_PUBLIC_URL`, named S3 volumes, optional RustFS, and passes `PGRST_DB_SCHEMAS`, `PGRST_DB_EXTRA_SEARCH_PATH`, `PGRST_DB_MAX_ROWS` into Studio.
