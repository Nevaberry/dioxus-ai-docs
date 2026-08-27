---
name: supabase-knowledge-patch
description: Supabase
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Supabase Knowledge Patch

Use this skill for Supabase implementation, migration, operations, and debugging work where current platform behavior matters.

## How to use this skill

1. Identify the affected surface: Auth, database, Data API, Edge Functions, Realtime, Storage, local development, self-hosting, administration, or integrations.
2. Read the matching reference before proposing code, configuration, migration steps, or operational advice.
3. For work spanning several surfaces, load only the references needed for those surfaces.
4. Preserve stated limits, defaults, prerequisites, and hosted-versus-self-hosted boundaries.
5. Treat alpha, beta, preview, and experimental features as labeled in the references.

## Reference index

| Reference | Topics | Read when |
| --- | --- | --- |
| [Authentication, OAuth, hooks, and keys](references/auth-and-keys.md) | Auth flows, OAuth/OIDC, hooks, MFA, signing keys, API keys | Implementing sign-in, identity linking, token verification, key rotation, or Auth administration |
| [Clients, developer tools, and MCP](references/clients-tools-and-mcp.md) | JavaScript and Python clients, generated types, hosted and local MCP, server SDKs | Configuring clients, type generation, MCP tooling, or application starters |
| [Cron, queues, and platform integrations](references/cron-queues-and-integrations.md) | `pg_cron`, `pgmq`, Management API OAuth, ETL, Vercel, Pipelines | Scheduling work, consuming queues, provisioning projects, or integrating external platforms |
| [Database and Data API](references/database-and-data-api.md) | Connections, Postgres configuration, extensions, migrations, PostgREST, GraphQL | Designing schemas, tuning queries, exposing APIs, or moving data |
| [Edge Functions](references/edge-functions.md) | Dependencies, filesystems, regions, quotas, WebSockets, deployment | Building, invoking, deploying, or operating Edge Functions |
| [Local development, CLI, branching, and deployment](references/local-cli-and-branching.md) | CLI runtime, local config, migrations, seeds, previews, branch workflows | Running the local stack, managing migrations, or deploying branches |
| [Platform administration and security](references/platform-administration-and-security.md) | Billing, roles, backups, networking, compliance, audit logs, observability | Administering organizations and projects or assessing security boundaries |
| [Realtime](references/realtime.md) | Channel lifecycle, Broadcast, Presence, Postgres Changes, limits | Implementing or authorizing Realtime features |
| [Self-hosting](references/self-hosting.md) | Docker configuration, key management, Auth, proxies, Storage, restores | Installing, upgrading, or operating self-hosted Supabase |
| [Storage, AI, and vectors](references/storage-ai-and-vectors.md) | Object Storage, S3, resumable uploads, Analytics, Vector, embeddings | Working with files, Iceberg, vector search, or embedding pipelines |

## Cross-surface routing

- For API-key use in Edge Functions, read both Auth and keys and Edge Functions.
- For private Realtime authorization, read Realtime together with the relevant Auth and database guidance.
- For automatic embedding pipelines, read Storage, AI, and vectors together with cron, queues, and integrations.
- For hosted-to-self-hosted moves, read database migration, local CLI, and self-hosting guidance together.

## Breaking changes and deprecations

- Supabase JavaScript libraries from 2.79.0 require Node.js 20 or later and native `fetch`; 2.78.0 is the last Node.js 18-compatible release.
- As of 2.101.0, register every `postgres_changes` binding before `subscribe()` because a joined channel rejects new listeners.
- Passing an async function directly to `onAuthStateChange` is deprecated.
- Table and view names passed to `from()` and columns passed to `eq()` or `neq()` are now type-checked.
- New publishable keys are not automatically injected into Edge Functions; add one under an `SB_` secret name.
- The Storage `owner` field is deprecated in favor of `owner_id`.
- Do not begin new `pgsodium` or Transparent Column Encryption deployments; Vault itself is not deprecated.
- Before moving to Postgres 17, replace TimescaleDB hypertables and drop `pgjwt`.
- New projects require explicit grants before PostgREST or GraphQL can expose tables, and `pg_graphql` is opt-in.
- Explicit versions in `CREATE EXTENSION` and `ALTER EXTENSION` are ignored and produce a warning.
- Creating, altering, or dropping objects in the `realtime` schema now fails; existing policies on `realtime.messages` still work.

## Authentication and key quick reference

- A publishable key selects `anon` unless a user JWT selects `authenticated`.
- A secret key selects `service_role`, bypasses RLS, must remain server-side, and is rejected from browsers.
- Hosted opaque keys rotate independently from legacy JWT keys but cannot be used as bearer JWTs.
- Opaque-key callers to Edge Functions need `--no-verify-jwt` and explicit `apikey` validation in the function.
- Move direct legacy-secret verification and legacy Edge Function JWT verification to `getClaims()` or JWKS before rotating signing keys.
- Allow about twenty minutes for edge and client JWKS caches when operating custom verifiers.
- Third-party Auth JWTs need asymmetric signing, a `kid`, and `role: "authenticated"`; otherwise Postgres uses `anon`.
- OAuth scopes control ID-token and UserInfo fields, not database authorization; enforce database access with RLS.
- OAuth client redirect URIs require exact matches rather than the wildcard rules used by ordinary Auth redirects.
- HTTP Auth Hooks use Standard Webhooks signatures, not JWT verification, and retry only qualifying `429` or `503` responses.
- A custom-access-token hook must preserve required JWT claims.
- Phone MFA uses `enroll`, `challenge`, and `verify`, and shares the phone-login provider configuration.
- Await `auth.initialize()` explicitly when redirect errors must be inspected.

## Database and Data API quick reference

- Data API requests use the nearest read replica by default on load-balancer endpoints.
- Direct connections, shared Supavisor, and dedicated PgBouncer are separate connection options.
- Supavisor and dedicated PgBouncer each receive the configured pool-size budget independently.
- `postgres-config update` merges overrides unless `--replace-existing-overrides` is supplied.
- Dashboard and client statement timeouts cannot be configured above 60 seconds.
- PostgREST role-setting changes require `notify pgrst, 'reload config'`.
- `.explain()` is disabled by default because query plans expose database structure.
- HypoPG index creation and its `EXPLAIN` must run in one connection.
- `pg_net` begins queued HTTP work only after transaction commit.
- A `SELECT` accepted by `pg_plan_filter` can still call a mutating function.
- Foreign tables from Wrappers do not enforce RLS; keep them in an unexposed schema.
- A Data API pre-request function can inspect request settings and raise SQLSTATE `PGRST` for a custom HTTP response.
- Database-writing rate limits cannot cover read-only `GET` or `HEAD` requests.
- Disabling the Data API also disables REST, GraphQL, and database access through client libraries.

## Edge Functions and Realtime quick reference

- Give each deployed function its own `deno.json` and, for private packages, its own `.npmrc`.
- A colocated `deno.json` takes precedence over a legacy import map.
- `/tmp` is invocation-scoped; synchronous filesystem calls are allowed only during initial module evaluation.
- Static-file bundles require CLI 2.7.0 or later, Docker-based bundling, and cannot use `--use-api`.
- Explicitly pinned function invocations do not fail over to another region.
- Resource-limit termination returns status `546` with `WORKER_LIMIT`.
- Browser WebSocket clients need handler-level token validation when gateway JWT verification is disabled.
- Private Broadcast and Presence use RLS policies on `realtime.messages`; these policies do not authorize Postgres Changes.
- A new access-token message refreshes cached private-channel policies.
- Set `REPLICA IDENTITY FULL` for old update and delete values, but RLS still limits delete old records to primary keys.
- Delete events cannot be filtered, and oversized Postgres Changes payloads retain only small individual values.
- Any Realtime Settings change disconnects all connected clients.
- New projects disable Postgres Changes until the relevant tables are enabled for Realtime replication.

## Storage, vectors, and embeddings quick reference

- Analytics clients need separate catalog and S3 data credentials.
- A Vector index's dimension, metric, and data type cannot change after creation.
- Use 500 vectors as the conservative write batch while the alpha documentation's 500 and 1,000 limits differ.
- Generated S3 access keys bypass RLS and must remain server-side.
- For user-scoped S3 access, combine the project reference, anon key, and user JWT as session credentials.
- The TUS endpoint is `/storage/v1/upload/resumable`; use the direct Storage hostname and exactly 6 MiB chunks.
- Resumable upload URLs last up to 24 hours and accept only one concurrent writer each.
- Cross-bucket `copy()` and `move()` are limited to 5 GB objects and require distinct source and destination permissions.
- `NoSuchBucket` or `NoSuchKey` can mean that RLS hid an existing resource.
- Smart CDN invalidation does not clear browser caches; `cacheControl` remains independent.
- Queue-backed embedding workers should delete successful jobs and let failures reappear after the visibility timeout.
- `Supabase.ai.Session` currently supports only `gte-small`; keep the session at module scope for reuse.

## Local development and deployment quick reference

- Run the npm CLI with Node.js 20 or later through `npx`, `bunx`, or a development dependency; global npm installation is unsupported.
- Preserve uncommitted schema and data before clearing local volumes for an upgrade.
- `supabase config push` applies local `config.toml` settings to a linked project.
- Declarative schema diffs omit DML and several database object and privilege categories; keep those changes in migrations.
- `migration squash` emits schema only and drops all DML, including cron jobs, Storage buckets, and Vault secrets.
- `db lint` needs `--fail-on warning` or `--fail-on error` to fail CI on findings.
- Preview branches apply only new migrations after creation and seed only once.
- Recreating a preview reruns migrations and seeding but loses branch-local data.
- The production deployment option ignores API settings, Auth settings, and seeds by default.
- Branch deployment steps are dependent; migration failure prevents seed and deploy.
- Self-hosted upgrades require matching Compose and mounted-configuration migrations, not image-tag changes alone.
- Self-hosted Functions use a shared filesystem and require a service restart after code changes.

## Administration, security, and integration quick reference

- Developer and Read-Only role names do not imply Function-secret isolation; inspect the exact permissions before assigning them.
- Physical backups omit custom-role passwords and Storage API objects.
- Restore-to-new-project does not copy Functions, Storage objects and settings, several service settings, database settings, or replicas.
- Network restrictions replace the complete database allowlist and do not cover HTTPS APIs.
- PrivateLink carries direct Postgres and PgBouncer traffic only.
- Changing SSL enforcement restarts the database.
- High Compliance requires a signed BAA, the HIPAA add-on, PITR, suitable compute, SSL enforcement, and network restrictions.
- New-format secret keys exposed in public GitHub repositories are revoked automatically.
- Platform Audit Logs cover dashboard and Platform API member actions, not project Auth events.
- Cron job names are case-sensitive; rescheduling the same name replaces the job.
- Exposing Queues to clients requires `pgmq_public`, RLS on every queue table, and operation-specific grants.
- `pgmq.pop()` deletes on read and therefore provides at-most-once delivery.
- Management API OAuth scope changes require existing users to authorize again.
- Poll project health until the required service is `ACTIVE_HEALTHY` after programmatic provisioning.
- A platform branch merge promotes database changes and deployed Edge Functions only.
- Removing a table from an ETL publication does not remove its destination data.
