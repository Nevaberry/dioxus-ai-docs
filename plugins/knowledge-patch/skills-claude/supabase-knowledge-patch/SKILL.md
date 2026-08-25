---
name: supabase-knowledge-patch
description: Supabase
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Supabase Knowledge Patch

Use this skill for current Supabase implementation, migration, administration, and troubleshooting work. It covers hosted, local CLI, and Docker self-hosted behavior across Auth, Database, Data API, Edge Functions, Realtime, Storage, branching, queues, integrations, and platform controls.

Choose the reference that matches the task before proposing code or operational steps. Keep hosted, local, and self-hosted contracts distinct, and preserve alpha, beta, feature-preview, and plan restrictions stated in the references.

## Working method

1. Identify whether the target is hosted Supabase, the local CLI stack, or Docker self-hosting.
2. Read the relevant topic reference; read more than one when a workflow crosses service boundaries.
3. Check the breaking changes and deprecations below before using a familiar API or migration path.
4. Preserve exact option names, defaults, limits, security boundaries, and lifecycle conditions from the references.
5. Do not infer a replacement, guarantee, or hosted/self-hosted equivalence that the references do not state.

## Reference index

| Reference | Topics |
| --- | --- |
| [Authentication, OAuth, Hooks, and Keys](references/auth-and-keys.md) | Auth flows, identity providers, hooks, signing keys, passkeys, MFA, and API-key lifecycle |
| [Clients, Developer Tools, and MCP](references/clients-tools-and-mcp.md) | JavaScript client compatibility, project starters, hosted and local MCP, and server SDKs |
| [Cron, Queues, and Platform Integrations](references/cron-queues-and-integrations.md) | Scheduled jobs, queue delivery, Management API workflows, ETL, and marketplaces |
| [Database and Data API](references/database-and-data-api.md) | Connections, Postgres settings, extensions, migrations, replication, PostgREST, GraphQL, and types |
| [Edge Functions](references/edge-functions.md) | Dependencies, invocation, filesystems, deployment, quotas, regions, WebSockets, and metrics |
| [Local Development, CLI, Branching, and Deployment](references/local-cli-and-branching.md) | Local configuration, migrations, seeds, CLI compatibility, previews, and GitHub deployment |
| [Platform Administration and Security](references/platform-administration-and-security.md) | Roles, billing, backups, networking, project lifecycle, observability, and compliance |
| [Realtime](references/realtime.md) | Channels, authorization, Broadcast, Presence, Postgres Changes, protocol behavior, and limits |
| [Self-hosting](references/self-hosting.md) | Docker configuration, key rotation, Auth, Functions, proxying, Storage, MCP, and restores |
| [Storage, AI, and Vectors](references/storage-ai-and-vectors.md) | Uploads, S3, Analytics and Vector buckets, embeddings, CDN behavior, and encryption |

## Breaking changes and migration traps

- Supabase JavaScript libraries from 2.79.0 require Node.js 20 and native `fetch`; 2.78.0 is the last Node.js 18-compatible release.
- The npm-distributed CLI also requires Node.js 20 and does not support global npm installation.
- A joined Realtime channel rejects new `postgres_changes` listeners; register every binding before `subscribe()`.
- Passing an async callback directly to `onAuthStateChange` is deprecated.
- New projects disable Postgres Changes until the relevant tables are enabled in Realtime replication.
- New projects require explicit grants before PostgREST or GraphQL can expose new `public` tables, and `pg_graphql` is opt-in.
- Explicit extension versions in `CREATE EXTENSION` or `ALTER EXTENSION` are ignored from August 5; the default version is installed with a warning.
- The `realtime` schema is protected from object creation, alteration, and deletion; existing `realtime.messages` RLS policies still work.
- Do not begin new `pgsodium` or Transparent Column Encryption deployments; Vault remains available.
- Before a Postgres 17 upgrade, migrate TimescaleDB hypertables and drop deprecated `pgjwt`.
- New Storage ownership uses `owner_id`; the older `owner` field is deprecated, and ownership itself does not grant access.
- Self-hosted Docker upgrades require matching Compose and mounted-configuration migrations, not image-tag changes alone.
- `supabase migration squash` is schema-only and omits all DML, including cron jobs, Storage buckets, and Vault secrets.
- Preview branches remember applied migrations and run their seed only at creation; recreating a preview reruns both and discards branch-local data.
- Custom-domain activation immediately changes OAuth callback URLs and the SAML entity ID.
- Opaque API keys are not bearer JWTs; Edge Functions using them need disabled built-in JWT verification plus explicit `apikey` validation.

## Auth and keys quick reference

- A publishable key selects `anon` unless a user JWT selects `authenticated`; a secret key selects `service_role`, bypasses RLS, stays server-side, and is rejected in browsers.
- Hosted opaque keys can rotate independently while legacy JWT keys remain active. Self-hosted deployments support only one opaque key per role.
- The OAuth scopes `openid`, `email`, `profile`, and `phone` control identity fields, not database authorization; use RLS for database access.
- OAuth access tokens carry `client_id`, while direct user sessions do not.
- Asymmetric signing-key migration uses a standby, rotation, and later explicit revocation; move direct legacy-secret verification to `getClaims()` or JWKS before switching.
- External JWKS verifiers should allow roughly twenty minutes for edge and client cache propagation; Supabase services honor revocation immediately.
- Clerk, Firebase Auth, Auth0, Amazon Cognito, and WorkOS tokens need an asymmetric signature, a `kid`, and `role: "authenticated"` to avoid falling back to `anon`.
- HTTP Auth Hooks use Standard Webhooks signatures, not JWT verification, and retry only `429` or `503` responses with a nonempty `retry-after`, within the stated budget.
- With Secure Email Change and a Send Email Hook, send both messages and preserve the documented reversed token/hash pairing.
- SAML identities do not automatically link by email; reference application data by user UUID.
- Auth supports passkey authentication and administration, AWS KMS-backed RS256 signing keys, zero-downtime SAML SP key rotation, and per-provider custom OAuth claim allowlists.
- For server-side Next.js authorization with `@supabase/ssr`, call `getClaims()` in root `proxy.ts` and copy refreshed cookies into the request and response; do not authorize from `getSession()`.

## Database and Data API quick reference

- Data API requests use nearest-read-replica routing by default on load-balancer endpoints.
- Paid projects can choose direct connections, shared Supavisor, or a database-co-located dedicated PgBouncer pooler.
- Supavisor and dedicated PgBouncer each receive the configured pool-size budget independently.
- Dashboard and client statement timeouts top out at 60 seconds; role changes used by PostgREST need a config reload.
- `.explain()` is opt-in because query plans expose database structure; protect plan media types from untrusted production callers.
- HypoPG index creation and `EXPLAIN` must execute in one connection.
- `pg_net` starts requests only after commit; its POST body is JSON and PATCH/PUT are unsupported.
- Foreign tables from Wrappers do not enforce RLS; keep them in an unexposed schema and expose only deliberately secured functions.
- A Data API pre-request function can inspect request settings and raise SQLSTATE `PGRST` to control response status, headers, and body.
- Data API error logs split database failures into `postgres_logs` and API failures into `edge_logs`; PostgREST codes appear in logs only on version 14 or later.
- Python database types generated by CLI 2.66.0 or later use Pydantic row models and `TypedDict` insert/update payloads.
- Managed replication targets BigQuery and requires source primary keys. Restart after publication changes; downstream consumers must deduplicate when exactly-once behavior matters.

## Edge Functions quick reference

- Keep a separate `deno.json` and, when needed, `.npmrc` beside each deployed function; colocated `deno.json` wins over a legacy import map.
- Publishable keys are not injected automatically; store one under an `SB_` secret name because `SUPABASE_` is reserved.
- Mounted S3-compatible buckets appear under `/s3/<bucket>`; `/tmp` is invocation-scoped and limited by plan.
- In request handlers and callbacks, use asynchronous filesystem calls; synchronous Deno and Node calls are blocklisted there.
- Static bundled files require CLI 2.7.0 or later and Docker-based bundling, not `--use-api`.
- A pinned region does not fail over during an outage; inspect `x-sb-edge-region` or `SB_REGION` to confirm placement.
- Hosted workers have explicit memory, CPU, response-idle, wall-clock, bundle, log, and secret ceilings detailed in the reference.
- Resource termination returns status `546` with `WORKER_LIMIT`.
- Browser WebSockets require handler-level token validation when gateway JWT verification is disabled, and connections end at the worker wall-clock limit.

## Realtime quick reference

- Private Broadcast and Presence require `private: true`, disabled public access, and `realtime.messages` RLS; `SELECT` receives and `INSERT` sends or tracks.
- Those channel policies are cached at join and refreshed by a new access-token message; they do not govern Postgres Changes.
- `realtime.broadcast_changes()` can publish trigger-formatted row changes to record-specific private topics.
- `REPLICA IDENTITY FULL` exposes old values, but RLS delete payloads still retain only primary keys; delete events cannot be filtered.
- Oversized Postgres Changes payloads retain only fields whose individual values are at most 64 bytes.
- Realtime settings changes disconnect all clients.
- Custom-JWT channels retain their token across resubscription and no longer require `setAuth()`.
- Self-hosted authorization deployments should use Realtime 2.112.10 or later for the `apply_rls` role-leak fix.

## Storage, AI, and vectors quick reference

- Analytics buckets are private-alpha Iceberg warehouses with separate catalog and S3 data credentials.
- Vector index dimension, metric, and data type are immutable; current indexes use `float32`, up to 4,096 dimensions, and the documented distance choices.
- Use 500 vectors as the conservative write batch while the alpha examples and limit table disagree.
- Generated S3 keys bypass RLS; an RLS-scoped client instead uses project reference, anon key, and user JWT as session credentials.
- Supabase S3 does not support versioning, lifecycle configuration, bucket CORS configuration, ACLs, object locking, or server-side-encryption controls.
- Large TUS uploads use `/storage/v1/upload/resumable` and should use the direct Storage hostname with chunks of exactly `6 * 1024 * 1024` bytes.
- Cross-bucket copy and move are limited to 5 GB and require the documented source/destination privileges.
- `NoSuchBucket` or `NoSuchKey` may mean RLS hid an existing resource; lock, timeout, and throttle failures use `423`, `504`, and `503`.
- Smart CDN invalidation can take up to 60 seconds and does not clear browser caches.
- Queue-backed embedding workers delete only successful jobs and let failed or interrupted jobs become visible for retry.
- `Supabase.ai.Session` currently supports only `gte-small`; keep it at module scope and use mean pooling plus normalization for dot-product sentence embeddings.

## Local development, branching, and self-hosting quick reference

- `supabase config push` applies local `config.toml` to a linked hosted project.
- Declarative schema diffs omit DML and several object classes; keep those changes in explicit versioned migrations.
- Local Auth templates use relative `content_path` files and a restart; hosted templates require hosted project configuration.
- Seed path globs are lexically sorted and deduplicated, making multi-file seed order deterministic.
- `supabase test db` rolls each pgTAP file back; `supabase db lint` needs `--fail-on` to fail CI on findings.
- Persistent branch configuration lives below `[remotes.<name>]` and applies only when the branch exists and its project ID matches.
- Git-backed preview secrets use dotenvx encryption; literal `encrypted:` values work only in designated secret fields.
- GitHub production deployment applies migrations, Edge Functions, and declared Storage buckets, but ignores API settings, Auth settings, and seeds by default.
- Self-hosted opaque and ES256 keys must be enabled together across Auth, Realtime, and Storage; changing `JWT_SECRET` also requires regenerating JWKS.
- Rotating only opaque self-hosted API keys preserves sessions; replacing the EC P-256 pair invalidates ES256 sessions.
- Self-hosted Auth template settings must be reachable HTTP URLs, not mounted file paths.
- The self-hosted MCP route is default-deny and has no OAuth 2.1; restrict it by IP and tunnel access rather than exposing it publicly.
- Self-hosted Functions share `volumes/functions`, require a service restart for code changes, and use internal `SUPABASE_URL` for service calls.
- Storage object migration must use S3-to-S3 transfer; copying into `volumes/storage` does not rebuild metadata.

## Cron, queues, integrations, and platform controls

- Scheduling the same case-sensitive cron name replaces the job; unscheduling leaves run history, while disabling `pg_cron` deletes all jobs.
- Client queue access is opt-in through `pgmq_public`; keep raw `pgmq` private and add RLS plus operation-specific grants to every exposed queue table.
- `read_with_poll()` waits for work and leases messages; `pop()` deletes on read and is at-most-once if processing fails.
- `detach_archive()` preserves an archive across extension removal without stopping later archive writes while the extension remains installed.
- Management API OAuth apps configure scopes on the app, not in the authorization request; users must reauthorize after scope changes.
- Poll project health until the required service is `ACTIVE_HEALTHY` before post-provision configuration.
- Management API database migrations are transactional; restore-point undo does not restore configuration, secrets, stored objects, or deployed Functions.
- Branch merge through the Management API promotes only database changes and deployed Edge Functions.
- Supabase Pipelines is a public alpha on paid plans.
- Developer and Read-Only role names do not imply secret isolation; consult the platform reference before delegating organization access.
- Physical backups omit custom-role passwords and Storage objects; non-Realtime subscriptions and replication slots must be dropped and recreated for restore.
- Network restrictions cover direct and pooled database routes, not HTTPS APIs, and direct database access from Edge Functions remains blocked.
- Platform Audit Logs cover dashboard and Platform API member actions, not project Auth events.
- High Compliance projects require the HIPAA prerequisites, continuous Security Advisor checks, PITR, at least Small compute, SSL enforcement, and network restrictions.
