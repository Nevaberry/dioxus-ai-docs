# Database and Data API

## Connections and configuration

### Dedicated pgBouncer poolers

Paid plans can use a co-located dedicated pgBouncer pooler. The choices are direct connections, shared Supavisor pooling, and dedicated pgBouncer pooling.

### Pooler capacity accounting

Supavisor session and transaction modes share one backend pool-size budget; dedicated pgBouncer has a separate budget of the same configured size. Running both at 30 can consume 60 backend connections, plus direct and platform connections. Client caps are separate; Supavisor session mode is also bounded per role/database pair.

### Serverless connection-string switches

Supavisor transaction mode uses port 6543 and has no prepared statements. Prisma runtimes need `?pgbouncer=true` plus a port-5432 direct or session URL for migrations. A manually configured Vercel Edge connection instead appends `?workaround=supabase-pooler.vercel` to the transaction URI.

### Hosted Postgres configuration lifecycle

`postgres-config update` merges system overrides unless `--replace-existing-overrides`; changes may restart primary and replicas. `--no-restart` leaves postmaster settings pending and risks replica divergence if nodes restart separately. SQL `RESET` does not remove CLI overrides—use `postgres-config delete`. Revisit overrides after compute changes because they supersede generated tuning.

```sh
supabase --experimental --project-ref <ref> postgres-config update \
  --config max_connections=200
supabase --experimental --project-ref <ref> postgres-config delete \
  --config max_connections
```

### Supautils privilege boundary

The preinstalled `supautils` lets project `postgres` change an allowlist of normally superuser-only role settings and create event triggers. It does not grant general superuser access: `COPY ... FROM PROGRAM` and `ALTER USER ... WITH SUPERUSER` remain unavailable.

### Database timeout layers

Dashboard/Data API query timeout is configurable only to 60 seconds. Default role limits are 3s `anon`, 8s `authenticated`, inherited 8s `service_role` if unset, and no role timeout for `postgres` under the two-minute global cap. Session settings require direct or Supavisor session connections. An RPC can set its own `statement_timeout`; API role changes require PostgREST reload.

```sql
create or replace function long_task() returns void
language sql set statement_timeout to '30s'
as $$ select pg_sleep(10) $$;
```

## Extensions and maintenance

### Packaged extension upgrades

A new packaged extension version reaches a project only after an Infrastructure software upgrade or General Settings restart. Pure-SQL extensions remain directly installable through SQL or `database.dev`.

### pg_net commit and retention behavior

`net.http_get/post/delete` enqueue only after the surrounding transaction commits. Queue/response tables are unlogged, responses expire after six hours, and the supported baseline is roughly 200 requests/sec. POST bodies must be JSON; PUT/PATCH are unavailable. Changing TTL or batch size needs worker restart.

```sql
alter role postgres set pg_net.ttl to '24 hours';
alter role postgres set pg_net.batch_size to 100;
select net.worker_restart();
```

### Hosted PGAudit restrictions

Hosted PGAudit is configurable only at role scope. `pgaudit.log_parameter` is unavailable because parameters may expose secrets. Audit all Data API write roles once by setting `pgaudit.log = 'write'` on `authenticator`.

### Dashboard CSV import limit

Dashboard CSV import stops at 100 MB. Use `pgloader` or `COPY` for larger data rather than the Data API.

### Prisma's dedicated database role

Use a separate `BYPASSRLS CREATEDB` Prisma login, scoped current/default privileges to Prisma-managed schemas, and grant it to `postgres` so Dashboard sees its DDL. Never let Prisma own `auth` or `storage`, or platform migrations appear as drift.

```sql
create user prisma with password '<password>' bypassrls createdb;
grant prisma to postgres;
grant usage, create on schema public to prisma;
grant all on all tables in schema public to prisma;
grant all on all routines in schema public to prisma;
grant all on all sequences in schema public to prisma;
alter default privileges for role postgres in schema public grant all on tables to prisma;
alter default privileges for role postgres in schema public grant all on routines to prisma;
alter default privileges for role postgres in schema public grant all on sequences to prisma;
```

### pg_repack without superuser

Hosted `pg_repack` 1.5.2+ works without superuser only when every invocation uses `-k`/`--no-superuser-check`. Full-table repack needs about twice table-plus-index disk and a primary key or non-partial unique index on non-null columns.

```sh
pg_repack -k -h db.<project-ref>.supabase.co -U postgres -d postgres \
  --no-order --table public.events
```

## Database engines and replication

### TimescaleDB removal in Postgres 17

TimescaleDB remains on Postgres 15 but not 17. Migrate every hypertable/dependency and drop it before upgrade. Use native partitioning, optionally `pg_partman`; unique keys must include partition keys and maintenance must be scheduled. `time_bucket()` and compression policies have no replacement.

```sql
call partman.run_maintenance_proc();
select cron.schedule('@hourly', $$call partman.run_maintenance_proc()$$);
```

### OrioleDB project type

OrioleDB is a separate Public Alpha Postgres image chosen only at project creation. It is the default storage engine for ordinary tables; every table has a primary key (hidden `ctid` if omitted). Only B-tree indexes are supported, excluding HNSW.

### Postgres 17 logical-replication access

Logical replication always uses direct connections. On Postgres 17+, `postgres` can grant a separate replication login and an external subscriber can subscribe to a read replica; older projects require `postgres` as replication user.

### Managed BigQuery replication

Dashboard Replication is a private-alpha Supabase ETL pipeline with BigQuery as its managed destination. Create a Postgres publication and attach it in Dashboard. Source tables need primary keys; custom types, automatic schema changes, and transformations are unsupported.

### BigQuery destination layout

Each table is a BigQuery view backed by a `_version` data table. Source `TRUNCATE` creates a new version and repoints the view. Rows cannot exceed 10 MB; table names cannot start or end with `_`.

### Replication pipeline lifecycle

Publication changes require restart, even with automatic new-table inclusion. Deleting a destination table during execution recreates it. Stopping queues WAL; restart can replay part of a long transaction and create duplicates without deduplication. Reset copy-phase table errors individually; streaming errors fail the pipeline until fixed and restarted.

### ETL removal and initial-copy behavior

Removing a table from a publication leaves destination data intact. Generated columns are unsupported. Writes during initial copy collect in WAL and replay when streaming begins.

### Nearest-replica Data API routing

PostgREST requests can route to the nearest read replica; load-balancer endpoints use this by default.

## Data API exposure and keys

### Secure-by-default Data API exposure

New projects made automatic exposure of new `public` tables opt-out on April 28, 2026 and secure-by-default on May 30. Explicit grants are now required for PostgREST/GraphQL. Project creation has a default-privileges switch; Dashboard can expose individual tables/functions.

```sql
grant select on table public.catalog to anon, authenticated;
```

### pg_graphql is now opt-in

New projects do not enable `pg_graphql`; projects older than 30 days without GraphQL requests may have it disabled. Enable in Extensions or preserve in migrations:

```sql
create extension pg_graphql;
```

### Restricting the exposed Data API schema

Disabling **Enable Data API** also disables client-library database access and REST/GraphQL. To replace `public` with `api`, remove `public` from Exposed schemas and Extra search path, disable `pg_graphql`, list `api` first, and grant deliberately. Custom schemas do not receive `public`'s automatic `anon`/`authenticated` privileges.

```sql
create schema if not exists api;
grant usage on schema api to anon, authenticated;
grant select on table api.catalog to anon;
grant select, insert, update, delete on table api.catalog to authenticated;
```

### Restricted OpenAPI schema visibility

With publishable keys, the complete OpenAPI table/column specification requires elevated permission; a public key is no longer also a schema-enumeration credential.

## Plans, errors, and request controls

### Data API execution plans

`.explain()` works for reads, writes, and RPCs but is off because plans reveal schema. Enable on `authenticator`, reload, and in production use `pgrst.db_pre_request` to restrict plan media types.

```sql
alter role authenticator set pgrst.db_plan_enabled to 'true';
notify pgrst, 'reload config';
```

```ts
const { data, error } = await supabase.from('instruments').select().explain()
```

### Data API error mapping and logs

Errors contain `code`, `details`, `hint`, `message`. `23503`/`23505` map to 409; `42501` to 401 unauthenticated or 403 authenticated; `PGRST003` to 504; `PGRST116` to 406. Ambiguity `PGRST201/203` is 300. Disabled aggregates `PGRST123` and max-affected `PGRST124/128` are 400.

PostgREST codes appear in logs only with PostgREST 14+: database failures in Postgres logs under `authenticator`; API codes as `proxy_status` in edge logs.

### Pre-request context and custom HTTP failures

`pgrst.db_pre_request` can read method, path, headers, cookies, and JWT settings via `current_setting()`. Register on `authenticator` and reload. `raise sqlstate 'PGRST'` accepts JSON `message` for code/message/details/hint and JSON `detail` for status/status_text/headers.

```sql
alter role authenticator set pgrst.db_pre_request = 'public.check_request';
notify pgrst, 'reload config';
```

Database-backed rate limit counters can write only during POST/PUT/PATCH/DELETE; GET/HEAD transactions are read-only and may use replicas.

## Generated and typed database clients

### Generated Python database types

CLI 2.66.0+ generates Pydantic row types and `TypedDict` insert/update payloads from hosted or local schemas.

```sh
npx supabase gen types --lang=python --project-id "$PROJECT_REF" \
  --schema public > database_types.py
npx supabase gen types --lang=python --local > database_types.py
```

### Typed JSON selectors in supabase-js

Since 2.48.0, replacing generated `Json` with a concrete JSON type infers nested `->` and text `->>` selections. Override row only or row/insert/update. `MergeDeep` needs `strictNullChecks`.

```ts
type AppDatabase = MergeDeep<DatabaseGenerated, {
  public: { Tables: { settings: { Row: {
    data: { bar: { baz: number }; en: 'ONE' | 'TWO' } | null
  } } } }
}>
const { data } = await createClient<AppDatabase>(url, key)
  .from('settings').select('data->bar->baz, data->>en')
```

### Postgres Language Server

The Postgres LSP supplies SQL completion, syntax diagnostics, type checking, and linting as a VS Code extension and npm package.

### Dashboard query and index assistance

The Table Editor has an Index Advisor, Explain/Analyze diagram rendering, preview natural-language filters, and query-performance suggestions.

### Staged Table Editor operations

The **Queue table operations** preview stages inserts/updates/deletes, displays a diff, and commits them in one transaction.

### New Foreign Data Wrapper capabilities

An Infura wrapper exposes live Ethereum data. Wrappers 0.6.0 adds an OpenAPI FDW, Snowflake timeouts, Clerk CRUD, and async streaming for Postgres FDWs.
