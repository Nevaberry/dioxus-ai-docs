# Database and Data API

## Nearest-replica routing for the Data API (launch-week-14)

Data API (PostgREST) requests can route to the nearest read replica to reduce network latency. This is the default for all load-balancer endpoints.

## Dedicated database poolers (launch-week-14)

Paid plans can use a database-co-located pgBouncer pooler. Projects now have three connection options: direct connections, the shared Supavisor pooler, or the dedicated pgBouncer pooler.

## Pooler connection budgets are independent

Supavisor and the dedicated PgBouncer pooler each receive the configured pool-size budget independently, so a size of 30 can produce 60 pooled backend connections in addition to direct connections. Compute-tier client limits are also enforced separately for each pooler.

## Vercel Edge pooler workaround

When a Vercel Edge application uses the transaction-pooler URI as `POSTGRES_URL`, append the Supabase pooler workaround query parameter.

```dotenv
POSTGRES_URL="postgres://postgres.<ref>:<password>@<region>.pooler.supabase.com:6543/postgres?workaround=supabase-pooler.vercel"
```

## Hosted Postgres configuration lifecycle

`postgres-config update` merges overrides by default; `--replace-existing-overrides` replaces them, and CLI v2 reloads or restarts the primary and replicas according to each setting's context. `--no-restart` can leave `postmaster` settings pending and replicas inconsistent, while any custom override supersedes Supabase's compute-specific optimization and should be reviewed after a compute change.

```sh
supabase --experimental --project-ref <ref> postgres-config update --config shared_buffers=250MB
```

## Data API timeout layers

Dashboard and client queries have a maximum configurable timeout of 60 seconds; defaults are 3 seconds for `anon`, 8 seconds for `authenticated`, inherited 8 seconds for an unset `service_role`, and a global two-minute cap for `postgres`. A session timeout works only over direct or session-mode port 5432, while role changes used by PostgREST require a config reload.

```sql
alter role authenticated set statement_timeout = '10s';
notify pgrst, 'reload config';
```

## API query plans are opt-in

Client-library `.explain()` works for reads, RPCs, and writes but is disabled by default because plans expose database structure. Enable `pgrst.db_plan_enabled` on `authenticator`; production deployments should use `pgrst.db_pre_request` to reject `application/vnd.pgrst.plan` requests except from trusted callers.

```sql
alter role authenticator set pgrst.db_plan_enabled = 'true';
notify pgrst, 'reload config';
```

## Hypothetical indexes must stay in one connection

HypoPG indexes are visible only in the connection that created them. Because Supabase commonly connects through a pooler, submit `hypopg_create_index(...)` and the corresponding `EXPLAIN` together in one query.

## Hosted PGAudit is role-scoped

Supabase permits PGAudit configuration only at role scope; setting `pgaudit.log = 'write'` on `authenticator` captures PostgREST writes made as `anon`, `authenticated`, or `service_role`. `pgaudit.log_parameter` is unavailable because it can leak secrets, and `pgaudit.log_rows` should be avoided unless logged row counts are truly needed.

```sql
alter role authenticator set pgaudit.log to 'write';
```

## `pg_net` starts work after commit

`net.http_get`, `net.http_post`, and `net.http_delete` enqueue requests that begin only after the transaction commits; responses live in the unlogged `net._http_response` table for six hours by default. The default request timeout is two seconds and the supported rate is 200 requests per second; POST bodies must be JSON, and PATCH/PUT are unsupported.

```sql
alter role postgres set pg_net.ttl = '24 hours';
alter role postgres set pg_net.batch_size = 500;
select net.worker_restart();
```

## Planner-cost guardrails

`pg_plan_filter` is already loaded through `shared_preload_libraries`; set `plan_filter.statement_cost_limit` to reject plans above a chosen estimated total cost. `plan_filter.limit_select_only = true` is not a read-only guarantee because a `SELECT` can call a mutating function.

## Online repacking on hosted projects

Hosted projects require `pg_repack` 1.5.2 or newer and every CLI invocation must use `-k`/`--no-superuser-check`. A full-table repack also needs a primary key or non-null unique index and roughly twice the table-plus-index size in free disk space.

## `pgsodium` is pending deprecation

Do not start new `pgsodium` or Transparent Column Encryption deployments on Supabase; a migration cycle is planned because of operational complexity and misconfiguration risk. Vault is not being deprecated and its public interface remains unchanged when its implementation moves away from `pgsodium`.

## Postgres 17 extension migration

TimescaleDB is unavailable on Supabase Postgres 17, so migrate hypertables to native partitioned tables before upgrading; `pg_partman` can pre-create partitions and apply retention only if `run_maintenance_proc()` is scheduled regularly. `pgjwt` is likewise deprecated on Postgres 17 and must be dropped before the upgrade.

## OrioleDB projects are a separate public alpha

OrioleDB must be selected when creating a new project, where it becomes the default table storage engine and supplies a hidden `ctid` primary key if none is declared. The alpha supports only B-tree indexes, so extension index types such as pgvector HNSW are unavailable.

## Wrappers do not provide RLS

Foreign tables created through Supabase Wrappers must live in a private, unexposed schema because FDWs do not enforce Row Level Security. Expose only filtered `SECURITY DEFINER` functions with an empty `search_path`, and revoke their default `public`/`anon` execute privileges before granting access deliberately.

## Managed replication currently targets BigQuery

Supabase ETL replication is a private alpha whose only managed destination is BigQuery; Analytics Buckets replication is no longer available. Source tables need primary keys, custom types and automatic schema changes are unsupported, rows are capped at 10 MB, and BigQuery table names cannot begin or end with `_`; replicated data uses versioned backing tables behind stable views so truncation can switch versions.

## Replication pipelines require explicit lifecycle handling

Restart a pipeline after changing its publication, including automatic additions from `FOR ALL TABLES` or `FOR TABLES IN SCHEMA`; deleting a destination table while the pipeline runs recreates it. Stopping during a transaction lasting more than a few minutes can replay the whole transaction and duplicate changes already sent, so downstream consumers must deduplicate when exactly-once behavior matters.

## Restricting the exposed Data API schema

Disabling the Data API also disables REST, GraphQL, and database access through the client libraries. To expose a dedicated schema instead, remove `public` from both **Exposed schemas** and **Extra search path**, disable `pg_graphql`, put the new schema first in the exposed list, and grant schema and table privileges explicitly.

```sql
create schema if not exists api;
grant usage on schema api to anon, authenticated;
grant select on table api.catalog to anon;
grant select, insert, update, delete on table api.catalog to authenticated;
```

## Data API error mapping and logs

Data API errors use either PostgreSQL SQLSTATE values or grouped `PGRST` codes: foreign-key and uniqueness violations map to `409`, undefined functions or tables to `404`, insufficient privilege to `401` for anonymous callers or `403` for authenticated callers, and `PGRST003` means a `504` connection-pool wait timeout. Database failures appear in `postgres_logs` under the `authenticator` role, while API failures appear in `edge_logs` through `proxy_status`; PostgREST codes are captured in logs only on version 14 or later.

## Pre-request context and custom HTTP failures

Set `pgrst.db_pre_request` on `authenticator` and reload PostgREST to run a function before every Data API request; it can inspect `request.method`, `request.path`, `request.headers`, `request.cookies`, and JWT settings through `current_setting()`. Raising SQLSTATE `PGRST` with JSON `message` and `detail` values controls the response body, status, and headers; database-writing rate limits cannot cover `GET` or `HEAD` because those requests run read-only and may use read replicas.

```sql
create function public.check_request()
returns void
language plpgsql
security definer
as $$
begin
  if current_setting('request.headers', true)::json->>'x-plan' is null then
    raise sqlstate 'PGRST' using
      message = json_build_object(
        'code', 'quota', 'message', 'Payment Required')::text,
      detail = json_build_object('status', 402)::text;
  end if;
end;
$$;

alter role authenticator
  set pgrst.db_pre_request = 'public.check_request';
notify pgrst, 'reload config';
```

## Secure-by-default Data API exposure

New projects no longer automatically expose new tables in `public`: explicit Postgres grants are required before PostgREST or GraphQL can reach them. The dashboard also has per-table and per-function exposure toggles plus a project-creation switch for default privileges; this secure behavior becomes the default for all new projects on May 30, 2026.

## GraphQL is now opt-in

New projects no longer enable `pg_graphql` automatically, and existing projects older than 30 days with no GraphQL requests can also have it disabled; projects that use GraphQL must enable the extension deliberately.

```sql
create extension pg_graphql;
```

## Read-only OpenAPI retrieval

A Management API endpoint can retrieve a project's database OpenAPI specification with only the **Read-only project database access** permission, allowing CLI and third-party integrations to inspect it without broader project access.

## Transactional Table Editor staging

The **Queue table operations** feature preview stages inserts, updates, and deletes, shows them in a diff, and commits the batch in one transaction instead of saving each edit immediately.

## Dashboard query and index assistance

The dashboard adds Explain/Analyze diagrams and an Index Advisor, while feature-preview table filters can translate natural-language requests into Postgres filters and the Assistant can suggest query optimizations.

## Expanded Foreign Data Wrapper capabilities

Wrappers 0.6.0 adds an OpenAPI FDW, Snowflake timeout support, and Clerk CRUD; the Infura wrapper exposes live Ethereum data to SQL, and Postgres FDWs now support asynchronous streaming.

## Extension version pinning is ignored (1.26.08)

From August 5, explicit versions in `CREATE EXTENSION` or `ALTER EXTENSION` no longer select the installed version; Supabase installs the default version and emits a warning.
