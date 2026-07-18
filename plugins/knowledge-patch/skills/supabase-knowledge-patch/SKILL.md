---
name: supabase-knowledge-patch
description: Supabase
license: MIT
version: null
metadata:
  author: Nevaberry
---

# Supabase Knowledge Patch

Baseline: Supabase through early 2025 (supabase-js v2, CLI v1, PostgREST v12, legacy JWT API keys, Deno Edge Functions, Realtime, S3-compatible Storage, and pgvector); covered changes span April 4, 2025 through July 12, 2026, including full batch IDs `launch-week-14` and `supabase-js-2.101.0` (patch version 2025.04).

## Reference index

| Reference | Topics |
|---|---|
| [auth-and-keys.md](references/auth-and-keys.md) | Hooks, MFA and passkeys, identity linking, custom providers, OAuth 2.1 server, third-party JWTs, signing keys, API keys |
| [database-and-data-api.md](references/database-and-data-api.md) | Poolers, configuration, extensions, timeouts, Data API exposure and errors, replication, Postgres 17, OrioleDB |
| [platform-administration-and-security.md](references/platform-administration-and-security.md) | Roles, billing, backups, disks, domains, networking, replicas, migrations, upgrades, compliance and advisors |
| [edge-functions.md](references/edge-functions.md) | Dashboard deployment, dependencies, CORS, filesystems, background work, limits, regions, WebSockets, server SDK |
| [realtime.md](references/realtime.md) | Listener ordering, private-channel RLS, Broadcast, replay, protocol 2.0, quotas, database resources, releases |
| [storage-ai-and-vectors.md](references/storage-ai-and-vectors.md) | S3, resumable uploads, Analytics/Iceberg, Vector buckets, automatic embeddings, remote vector stores |
| [local-cli-and-branching.md](references/local-cli-and-branching.md) | CLI installation, config, schemas, migrations, tests, local services, preview and persistent branches, deployment |
| [self-hosting.md](references/self-hosting.md) | Compose upgrades, asymmetric auth, Functions, Storage, email, MCP, TLS, restores, MFA, security boundaries |
| [cron-queues-and-integrations.md](references/cron-queues-and-integrations.md) | pg_cron, PGMQ, Data API queue wrappers, Management API OAuth, provisioning, ETL and marketplace integration |
| [clients-tools-and-mcp.md](references/clients-tools-and-mcp.md) | JavaScript APIs, typed queries, SSR and mobile setup, UI and SQL tools, hosted/local MCP, Terraform and integrations |

## Breaking changes and migration traps

### Secure-by-default Data API

New projects no longer automatically expose new `public` tables. Grant privileges explicitly:

```sql
grant select on table public.catalog to anon, authenticated;
```

New projects also leave `pg_graphql` disabled. Enable it explicitly if the application uses GraphQL:

```sql
create extension pg_graphql;
```

Disabling **Enable Data API** disables REST, GraphQL, and database access through Supabase clients. When exposing a custom schema, remove `public` from both exposed schemas and the extra search path, then grant the custom schema deliberately.

### API keys and JWT verification

Hosted projects support `sb_publishable_...` and `sb_secret_...` keys. Put these opaque values in `apikey`; they are not bearer JWTs. A publishable key starts with `anon`, while a secret selects `service_role` and must remain server-side.

```sh
curl "$SUPABASE_URL/rest/v1/items?select=*" \
  -H "apikey: $SUPABASE_PUBLISHABLE_KEY" \
  -H "Authorization: Bearer $USER_JWT"
```

Migrate with new and legacy keys active together, then deactivate legacy keys. Before revoking the legacy JWT secret, replace direct-secret verification with `supabase.auth.getClaims()` or JWKS verification and replace legacy `anon`/`service_role` JWT keys with publishable/secret keys.

Edge Functions do not automatically authorize new-format keys. Calls using them require disabled built-in JWT verification and explicit `apikey` authorization inside the function.

### Asymmetric signing-key rotation

Signing keys now have standby, current, previously-used, and revoked states. Rotate issuance to the asymmetric key, wait at least the JWT lifetime plus 15 minutes, then revoke the old key. External verifiers may retain a revoked key for ten minutes at the edge plus another library cache interval; purge caches when required.

The bearer JWT and the `apikey` are separate credentials for Data API calls. Imported ES256 keys support external minting, but private material cannot be exported after creation.

### Realtime listener ordering

As of `supabase-js` 2.101.0, register every `postgres_changes` binding before `subscribe()`; adding one after the channel joins is blocked.

```ts
const channel = supabase
  .channel('database-changes')
  .on('postgres_changes', { event: '*', schema: 'public' }, handleChange)
  .subscribe()
```

Realtime settings changes restart the service and disconnect every connected client. Plan them as reconnect events.

### JavaScript response overrides

`.returns()` is deprecated. Use `.overrideTypes<T>()`; it merges by default, or replaces the result type with `{ merge: false }`.

```ts
const rows = supabase.from('users').select()
  .overrideTypes<{ id: number; name: string }, { merge: false }>()
```

### Postgres 17 compatibility

TimescaleDB is unavailable on Postgres 17. Migrate hypertables and dependent objects, drop the extension, and use native partitioning plus optional `pg_partman`; Timescale-specific bucketing and compression have no direct replacement.

Disable `plcoffee`, `plls`, `plv8`, and `pgjwt` before upgrading to Postgres 17. Logical replication must use a direct connection; Postgres 17 permits a dedicated replication login and read-replica subscription.

### CLI and migration hazards

The npm CLI requires Node 20+ and does not support global npm installation. Before a local-stack upgrade, dump schema/data and run `supabase stop --no-backup` so service migrations start with fresh volumes.

`supabase migration squash` omits all DML, including cron jobs, buckets, and Vault secrets. `db reset --linked` preserves cluster-level custom roles. A schema-specific first `db pull` ignores `--schema` when the migrations directory is empty.

## High-value authentication features

### OAuth 2.1 server

A project can act as an OAuth 2.1/OIDC provider. Local support requires CLI 2.54.11+. Configure a consent path, inspect the `authorization_id`, and approve or deny it from the application UI.

```toml
[auth.oauth_server]
enabled = true
authorization_url_path = "/oauth/consent"
allow_dynamic_registration = false
```

Only authorization-code-with-PKCE and refresh-token grants are supported. Redirect URIs are exact, authorization codes are single-use and valid for ten minutes, custom scopes are unavailable, and `openid` requires asymmetric signing. OAuth scopes control identity claims, not database authorization; use the token's `client_id` in RLS.

### Auth hooks

The Before User Created hook runs before `auth.users` insertion. HTTP hooks must verify the raw Standard Webhooks body, stay within 20 KB and five seconds, return JSON, and expect retries only for `429`/`503` with `retry-after`. Custom Access Token, MFA Verification, and Password Verification hooks require bodies and cannot return `204`.

The Send Email hook replaces SMTP only while the Email provider stays enabled. Secure email-change token/hash field names are intentionally crossed; see the Auth reference before implementing a custom sender.

### MFA, passkeys, and identity linking

Phone MFA uses enroll/challenge/verify and refreshes successful sessions to `aal2`; phone codes can remain valid for five minutes and older issued codes remain usable until expiry. Passkeys support discoverable authentication, progressive enrollment, and user/admin list/delete endpoints.

Native identity linking accepts provider ID/access tokens without a redirect when manual linking is enabled. A user may unlink only while at least two identities remain.

### Third-party authentication

Clerk, Auth0, Cognito, Firebase, and WorkOS JWTs can authorize Data API, Storage, Realtime, and Functions directly. Tokens need asymmetric signing, `kid`, and normally `role: authenticated`; key changes can take 30 minutes to propagate. Keep issuer/audience RLS checks especially strict for self-hosted Firebase.

## High-value data and runtime features

### Private Realtime channels and replay

Authorize private Broadcast/Presence channels with RLS on `realtime.messages`: `SELECT` receives, `INSERT` sends, `realtime.topic()` identifies the topic, and `extension` separates Broadcast from Presence. Postgres Changes still uses table RLS and ignores `private`.

Broadcast Replay is alpha, private-channel-only, and replays database-originated messages retained for three days. Supply millisecond `since` and optional `limit <= 25`; client and REST broadcasts are not replayed.

### Database-triggered Broadcast

Database triggers can publish controlled Realtime Broadcast payloads. REST Broadcast can also send a batch without joining a WebSocket channel, and sending on an unsubscribed JavaScript channel uses this path.

### Analytics and Vector buckets

Analytics buckets store Iceberg metadata plus Parquet data and expose a REST Catalog and S3 endpoint. Query with PyIceberg, Spark, DuckDB, or an Iceberg FDW in Postgres; ingestion must come from an external pipeline.

Vector buckets are S3-backed, backend-oriented embedding stores. Index dimension, `float32` type, and distance metric are immutable. Use `putVectors()` and `queryVectors()` or the SQL wrapper's `data <==> query`; keep batches at 500 vectors while alpha documentation remains inconsistent.

### Queues and asynchronous embeddings

Supabase Queues wraps `pgmq`: `read()` hides messages for a visibility interval, `pop()` gives at-most-once behavior, and explicit delete/archive completes work. Exposing `pgmq_public` requires per-table RLS and role grants; local/self-hosted deployments must also add it to PostgREST schemas.

Automatic embedding updates should enqueue row identity in triggers, process batches with Cron plus an Edge Function, and delete only after storage succeeds. Align the queue visibility timeout with the function timeout; clear stale embeddings on update when correctness requires it.

### Edge Function execution

Use function-local `deno.json` and `.npmrc`. The runtime provides per-invocation `/tmp`, persistent `/s3/<bucket>` mounts when configured, `EdgeRuntime.waitUntil()` for background work, region selection, and inbound/outbound WebSockets.

Hosted workers have 256 MB, two seconds of CPU per request, 150/400-second Free/paid wall time, and 20 MB bundles. Resource exhaustion returns `546 WORKER_LIMIT`; startup failures return `503 BOOT_ERROR`.

## Deployment and operations essentials

Branches are isolated instances with separate credentials, data, Storage, Functions, and Auth configuration. Preview branches are ephemeral and empty of production data; persistent branches need explicit `[remotes.<name>]` configuration and branch-local secrets.

Git deployment runs `Clone -> Pull -> Health -> Configure -> Migrate -> Seed -> Deploy`. Production integration deploys migrations, changed Functions, and declared Storage buckets, but ignores API/Auth config and seed data. Editing an already-applied preview migration does nothing; recreate the preview to replay history.

For self-hosting, upgrade configuration files and entrypoint logic together with image tags. The current stack supports opaque keys plus ES256 sessions, but key variables must reach every JWT-aware service and Functions need hybrid verification. Restart after code changes; force-recreate after environment changes.

Use direct or session-mode port 5432 connections for dumps, restores, migrations, and logical replication. Supavisor transaction mode on 6543 does not support prepared statements; Prisma needs its pooler switch and a separate direct/session migration URL.

Read the matching reference before changing Auth, exposed schemas, RLS, signing keys, networking, backups, branches, self-hosted Compose, Realtime limits, or Storage alpha features.
