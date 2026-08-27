# Cron, queues, and platform integrations

## Cron job identity, replacement, and history

Job names are case-sensitive and cannot be renamed; calling `cron.schedule()` again with the same name replaces that job, and intervals from 1 through 59 seconds require Postgres `15.1.1.61` or later. `cron.unschedule()` removes the definition but leaves `cron.job_run_details`, whose rows are never cleaned automatically, while disabling `pg_cron` permanently deletes all jobs.

```sql
select cron.schedule('worker', '30 seconds', 'call process_work()');
select cron.unschedule('worker');
```

## Maintenance cron can disrupt platform work

A blanket maintenance job such as `pg_terminate_backend()` for idle sessions can terminate critical Supabase processes, including nightly backups. Prefer the corresponding Postgres setting, such as `idle_session_timeout`, when it fits the task.

## Queue durability and physical layout

Supabase Queues requires Postgres `15.6.1.143` or later, and each queue creates active `pgmq.q_<name>` and archive `pgmq.a_<name>` tables. An unlogged queue makes only the active table unlogged—the archive remains durable—and partitioned queues are not yet available.

```sql
select pgmq.create_unlogged('transient_jobs');
```

## Client queue access is an opt-in wrapper surface

Queues are not exposed through the Data API by default; enabling exposure creates `pgmq_public` wrappers for message operations but not queue creation or deletion, while the raw `pgmq` schema must remain private because its queue tables have no RLS by default. Enable RLS and policies on every client-accessible `pgmq.q_<name>` table, then grant each API role the required permissions: `send`/`send_batch` need `SELECT, INSERT`; `read`/`pop` need `SELECT, UPDATE`; and `archive`/`delete` need `SELECT, DELETE`.

```ts
await supabase.schema('pgmq_public').rpc('send', {
  queue_name: 'jobs',
  message: { task: 'resize' },
  sleep_seconds: 30,
})
```

## Local and self-hosted queue exposure

The hosted toggle exposes `pgmq_public` automatically, but local CLI and Docker Compose deployments must add the already-created schema to PostgREST and restart the stack.

```toml
[api]
schemas = ["public", "graphql_public", "pgmq_public"]
```

```dotenv
PGRST_DB_SCHEMAS=public,graphql_public,pgmq_public
```

## Long polling and message lease control

`pgmq.read_with_poll()` waits up to `max_poll_seconds` for work, while `pgmq.set_vt()` moves a message's visibility time to an offset from now. By contrast, `pgmq.pop()` deletes on read and therefore provides at-most-once delivery if processing subsequently fails.

```sql
select * from pgmq.read_with_poll('jobs', 60, 10, 5, 100);
select * from pgmq.set_vt('jobs', 42, 60);
```

## Preserving archives across extension removal

`pgmq.detach_archive()` removes a queue's archive table from extension ownership so `drop extension pgmq` will not delete it; detaching does not prevent later `archive()` calls from appending while the extension remains installed.

```sql
select pgmq.detach_archive('jobs');
```

## Management API OAuth authorization

Organization OAuth apps can obtain access and refresh tokens for Management API calls on a user's behalf; send users to `https://api.supabase.com/v1/oauth/authorize`, where the optional `organization_slug` preselects an organization, S256 PKCE is recommended, and `redirect_uri` plus `state` cannot exceed 4 KB. Exchange the code as form data at `POST /v1/oauth/token`, authenticate the client with HTTP Basic auth, and reuse the exact redirect URI.

```sh
curl https://api.supabase.com/v1/oauth/token \
  -u "$CLIENT_ID:$CLIENT_SECRET" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode grant_type=authorization_code \
  --data-urlencode code="$CODE" \
  --data-urlencode redirect_uri="$REDIRECT_URI" \
  --data-urlencode code_verifier="$CODE_VERIFIER"
```

## OAuth scope changes require renewed consent

Management API scopes are configured on the OAuth app rather than requested during authorization; the `scope` query parameter is deprecated. Scopes grant read and/or write access by resource family—such as Auth, Database, Edge Functions, Environment, Projects, Secrets, and Storage—and existing users must reauthorize after an app's scopes change.

## Programmatic project provisioning contract

`POST /v1/projects` accepts smart region groups (`americas`, `emea`, or `apac`), but callers should poll `GET /v1/projects/{ref}/health` until the service they need is `ACTIVE_HEALTHY` before configuring it. Database passwords must be unique and stored encrypted because the Management API cannot retrieve or programmatically change them; customers with Pico access must omit `desired_instance_size` to get scale-to-zero, which Micro and larger instances do not support.

## Enabling new API keys through the Management API

After provisioning, inspect `GET /v1/projects/{ref}/api-keys?reveal=true`; if the project lacks the new keys, create `publishable` and `secret` keys with separate `POST /v1/projects/{ref}/api-keys` calls. Creating the secret key accepts `"secret_jwt_template": { "role": "service_role" }`.

## Transactional Management API migrations and restore points

For customers with access, `POST /v1/projects/{ref}/database/migrations` records a migration in `supabase_migrations` and rolls back all its changes if execution fails. A restore-point undo reverts schema, seed rows, Auth users and tokens, and Storage pointer rows, but not configuration, secrets, stored objects, or deployed Edge Functions.

## Platform branch merge boundary

`POST /v1/branches/{branch_id_or_ref}/merge` promotes only database changes and deployed Edge Functions from the branch. Configuration, secrets, and other project state are outside this merge contract.

## OAuth project claim flow

For customers with access, `GET /v1/oauth/authorize/project-claim` transfers a project from a platform-owned organization to the user's organization while preserving the platform's access through its OAuth integration. Remove any custom configuration that the user should not inherit before starting the claim.

```text
/v1/oauth/authorize/project-claim?project_ref=<ref>&client_id=<client-id>&response_type=code&redirect_uri=<uri>
```

## Vercel Marketplace identity and role mapping

A Vercel team maps one-to-one to a Supabase organization; Vercel users receive linked Supabase accounts, with Vercel owners mapped to `owner` and members to `developer`. Manage those roles in Vercel—permissions for separately invited non-Vercel users are not synchronized.

## Vercel Marketplace synchronization boundaries

Marketplace-created projects automatically sync connection variables and server credentials, including `POSTGRES_PASSWORD`, `SUPABASE_SERVICE_ROLE_KEY`, and `SUPABASE_JWT_SECRET`, into connected Vercel projects. During the public alpha, projects can be created only in Vercel, billing and payments stay there, the organization is removed only by uninstalling the integration, owners cannot be added manually in Supabase, and custom domains are unsupported.

## ETL removal and initial-copy behavior

Removing a table from a publication does not delete its existing destination data. Generated columns and transformations are unsupported, and changes made during the initial copy accumulate in WAL before being replayed when streaming begins.

## Pipelines reach public alpha (1.26.08)

Supabase Pipelines has moved from private to public alpha and is available on all paid plans.

## Management API logs endpoint migration (1.26.08)

Clients that query project logs through `analytics/endpoints/logs.all` must migrate to the new logs endpoint.
