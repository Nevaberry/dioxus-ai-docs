# Cron, queues, and platform integrations

## Cron

### Cron installation and removal

Install `pg_cron` in `pg_catalog` and grant project `postgres` access to separate `cron` schema. Dropping extension permanently deletes every job.

```sql
create extension pg_cron with schema pg_catalog;
grant usage on schema cron to postgres;
grant all privileges on all tables in schema cron to postgres;
-- Destructive: also removes all jobs.
drop extension if exists pg_cron;
```

### Cron job identity and sub-minute schedules

Names are case-sensitive and immutable. Calling `cron.schedule()` with same name upserts/replaces. Dashboard accepts cron or natural language. Intervals 1–59 seconds need Postgres 15.1.1.61+.

```sql
select cron.schedule('process-work', '30 seconds', 'call process_work()');
```

### Editing, pausing, and retaining Cron history

`cron.alter_job()` changes schedule, command, DB, username, active by ID. `cron.unschedule()` removes job but retains `cron.job_run_details`; history is never auto-cleaned.

```sql
select cron.alter_job(
  job_id := (select jobid from cron.job where jobname = 'process-work'),
  schedule := '*/5 * * * *', active := false
);
select cron.unschedule('process-work');
```

## Queues

### Queue types, names, and storage

Queues uses `pgmq`, available Postgres 15.6.1.143+. Names lowercase with hyphens/underscores. Basic queue creates logged `pgmq.q_<name>` and `pgmq.a_<name>`; unlogged keeps only active `q_` unlogged and archive durable. Partitioned queues unavailable.

```sql
create extension pgmq;
select from pgmq.create('work_items');
select pgmq.create_unlogged('transient_work');
```

### PGMQ sends and visibility-based reads

`send()`/`send_batch()` accept optional delay seconds and return IDs. `read(queue, vt, qty)` returns records and hides them for `vt` without deletion; records include `msg_id`, `read_ct`, `enqueued_at`, `vt`, JSONB `message`.

```sql
select * from pgmq.send('work_items', '{"task":"resize"}'::jsonb, 10);
select * from pgmq.read('work_items', 60, 5);
```

### Long polling and destructive pops

`read_with_poll()` waits up to five seconds by default and polls every 100ms, configurable. `pop()` atomically reads/deletes one, giving at-most-once delivery if consumer fails.

```sql
select * from pgmq.read_with_poll('work_items', 60, 5, 10, 250);
select * from pgmq.pop('work_items');
```

### Queue completion, archival, and operations

Delete/archive one ID or arrays. `purge_queue()` clears active; `drop_queue()` deletes active/archive tables. `set_vt()` moves visibility relative to now. `list_queues()`, `metrics()`, `metrics_all()` show inventory, depth, ages, lifetime count, scrape time. `detach_archive()` removes archive from extension ownership but future archives still use it, preserving it across extension drop.

### Queue Data API boundary and permissions

Queues are Postgres-only by default. **Expose Queues via PostgREST** creates `pgmq_public` wrappers for send/batch/read/pop/archive/delete, not create/drop. Wrapper `sleep_seconds` means send delay or read visibility timeout.

Each exposed `pgmq.q_*` needs RLS/policies. Sends need SELECT+INSERT; read/pop SELECT+UPDATE; archive/delete SELECT+DELETE. Never expose `postgres`/`service_role`.

```ts
await supabase.schema('pgmq_public').rpc('send', {
  queue_name: 'work_items', message: { task: 'resize' }, sleep_seconds: 10,
})
const { data } = await supabase.schema('pgmq_public').rpc('read', {
  queue_name: 'work_items', sleep_seconds: 60, n: 5,
})
```

### Exposing queues locally and when self-hosting

Local/Compose do not expose wrappers automatically. Add `pgmq_public` to API schemas and restart:

```toml
[api]
schemas = ["public", "graphql_public", "pgmq_public"]
```

```dotenv
PGRST_DB_SCHEMAS=public,graphql_public,pgmq_public
```

## Management API OAuth

### Management API OAuth apps

Platform integrations use `https://api.supabase.com/v1/oauth/authorize` and `/v1/oauth/token`, separate from project Auth OAuth. `organization_slug` may preselect organization; `redirect_uri` plus `state` must remain under 4 kB; PKCE S256 recommended. Token exchange requires exact original redirect URI. Revocation breaks access and refresh, so handle unauthorized.

```sh
curl https://api.supabase.com/v1/oauth/token \
  --user "$CLIENT_ID:$CLIENT_SECRET" \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode grant_type=authorization_code \
  --data-urlencode code="$CODE" \
  --data-urlencode redirect_uri="$CALLBACK" \
  --data-urlencode code_verifier="$CODE_VERIFIER"
```

### Management API OAuth scopes and dynamic callbacks

App-configured resource permissions cover Auth, DB, Domains, Functions, Environment, Organizations, Projects, REST, Secrets, Storage, generally read/write. Authorize URL `scope` is deprecated; scope changes require reauthorization. For per-installation destinations, register one callback and put desired destination in integrity-protected `state`; verify before following.

### Database credentials for platform integrations

Management API returns project API keys but not database password. Direct integration must collect existing password; project creator must retain supplied `db_pass`, which cannot be changed programmatically.

```text
postgresql://postgres:[DB-PASSWORD]@db.[REF].supabase.co:5432/postgres
```

## Provisioning and transfer

### Programmatic project provisioning

Use `POST /v1/projects`, get capacity regions at `/available-regions`, poll `/health` until needed service is `ACTIVE_HEALTHY`. Smart groups: `americas`, `emea`, `apac`. Pico alone scales to zero and is requested by omitting `desired_instance_size`.

After create, request `/api-keys?reveal=true`. If modern keys absent, POST separate `publishable` and `secret`; a server key may use `secret_jwt_template: { "role": "service_role" }`.

### Managed development branches and restore points

Restricted `/database/migrations` records SQL in `supabase_migrations` and rolls back failure. Platform can seed via `/database/query`, deploy Functions, merge via `/v1/branches/{id_or_ref}/merge`; only DB changes and deployed Functions promote.

Restricted restore points capture DB only. Undo reverts schema, seed, Auth users/tokens, Storage metadata pointers—not config, secrets, objects, or deployed Functions.

### Transferring a platform-owned project to a user

Restricted `/v1/oauth/authorize/project-claim` moves a project to a user-selected organization while authorizing integration to retain API access. Remove configuration users should not inherit first.

## Marketplace and data integrations

### Vercel Marketplace ownership and environment sync

One Vercel team maps to one Supabase organization. Resource creator/Vercel owners become owners; Vercel members developers; role changes remain in Vercel. Separately invited users do not sync.

Connected projects receive DB URLs/credentials, `SUPABASE_URL`, publishable/service-role keys, JWT secret, and `NEXT_PUBLIC_SUPABASE_*`. Marketplace projects can be created only in Vercel; owners cannot be added in Supabase; uninstall removes organization. Billing is in Vercel though Supabase cycle remains/reset on plan changes. Custom domains unsupported.

### Stripe Sync Engine integration

Dashboard one-click Stripe Sync Engine synchronizes customers, subscriptions, invoices, payments for SQL queries. The open-source engine is maintained in Stripe's GitHub organization.
