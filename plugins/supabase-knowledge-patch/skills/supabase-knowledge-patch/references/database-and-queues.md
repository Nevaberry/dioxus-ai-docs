# Database & Queues

## OrioleDB Storage Engine

Supabase offers OrioleDB as an alternative Postgres storage engine. Select "OrioleDB Public Alpha" as the Postgres version when creating a new project. Tables use OrioleDB by default in this mode — standard `CREATE TABLE` syntax works unchanged.

Key differences from default heap storage:
- **No vacuuming** — MVCC uses an undo log instead of dead tuples
- **B-tree indexes only** — HNSW (pgvector), GIN, GiST etc. not yet supported
- **Index-organized tables** — data stored in the index structure, faster PK lookups
- **Row-level WAL** — reduced write amplification

```sql
-- Works identically to normal Postgres
create table posts (
  id int8 primary key,
  title text not null,
  body text not null
);

-- Only B-tree indexes supported
create index posts_title on posts (title);
```

## CLI Postgres Configuration

Configure Postgres parameters that require superuser access via the Supabase CLI. Uses the `--experimental` flag and requires Owner/Admin org privileges.

```bash
# Update a setting
supabase --experimental --project-ref \
  update --config shared_buffers=250MB <ref >postgres-config

# Update multiple, replacing all existing overrides
supabase --experimental --project-ref \
  update --config max_parallel_workers=3 \
  --replace-existing-overrides <ref >postgres-config

# Delete specific overrides (revert to defaults)
supabase --experimental --project-ref \
  delete --config shared_buffers,work_mem <ref >postgres-config

# Defer restart for settings that require it
supabase --experimental --project-ref \
  update --config max_connections=200 --no-restart <ref >postgres-config
```

CLI-only parameters (not settable via SQL): `shared_buffers`, `max_connections`, `max_worker_processes`, `max_replication_slots`, `max_wal_senders`, `wal_keep_size`, `max_wal_size`, `checkpoint_timeout`, `hot_standby_feedback`, `session_replication_role`, `track_activity_query_size`, `track_commit_timestamp`, `max_locks_per_transaction`, `max_standby_archive_delay`, `max_standby_streaming_delay`, `max_slot_wal_keep_size`, `wal_sender_timeout`.

Settings requiring restart are automatically detected. Both primary and read replicas restart together unless `--no-restart` is used.

## Managed Replication Pipelines (Supabase ETL)

Stream database changes to external data warehouses using Postgres logical replication, managed through the Dashboard. Powered by [Supabase ETL](https://github.com/supabase/etl). Currently BigQuery is the only supported destination.

Setup requires: a Postgres publication, enabling replication in Dashboard, and configuring a destination.

```sql
-- Publication for specific tables
create publication pub_analytics for table users,
orders;

-- Publication for all tables in a schema
create publication pub_all_public for tables in schema public;

-- Column filtering
create publication pub_users_subset for table users (id, email, created_at);

-- Row filtering
create publication pub_active_users for table users
where
  (status = 'active');

-- Add/remove tables from running pipeline (requires pipeline restart)
alter publication pub_analytics
add table products;

alter publication pub_analytics
drop table orders;
```

Pipeline management via Dashboard actions: Start, Stop, Restart, Edit, Delete. Tables must have primary keys. Custom data types and automatic schema changes (DDL) are not supported.

## WebAssembly Foreign Data Wrappers

Supabase Wrappers now includes a Wasm runtime for running sandboxed foreign data wrappers. This enables building and distributing custom FDWs as WebAssembly modules, which can be used on the Supabase platform. See [Wrappers documentation](https://supabase.github.io/wrappers/) for building custom Wasm FDWs.

## Supabase Queues (pgmq + pgmq_public)

Supabase wraps the `pgmq` Postgres extension with a managed `pgmq_public` schema that exposes queue operations via the Data API with RLS support. Requires Postgres >= 15.6.1.143.

**Queue types**: Basic (logged/durable), Unlogged (better perf, may lose messages on crash). Both create `pgmq.q_<name>` (active messages) and `pgmq.a_<name>` (archived messages) tables.

**Client-side access** uses `supabase.schema('pgmq_public').rpc(...)`:

```typescript
// Send a message (with optional delay)
const { data } = await supabase.schema('pgmq_public').rpc('send', {
  queue_name: 'tasks',
  message: { type: 'process', id: 123 },
  sleep_seconds: 0, // delay visibility by N seconds
});

// Read messages (with visibility timeout)
const { data: messages } = await supabase.schema('pgmq_public').rpc('read', {
  queue_name: 'tasks',
  sleep_seconds: 30, // visibility timeout — hidden from other consumers for 30s
  n: 5, // read up to 5 messages
});

// Pop (read + delete atomically)
const { data } = await supabase.schema('pgmq_public').rpc('pop', {
  queue_name: 'tasks',
});

// Delete after processing
await supabase.schema('pgmq_public').rpc('delete', {
  queue_name: 'tasks',
  msg_id: message.msg_id,
});

// Archive (move to archive table instead of deleting)
await supabase.schema('pgmq_public').rpc('archive', {
  queue_name: 'tasks',
  message_id: message.msg_id,
});

// Batch send
await supabase.schema('pgmq_public').rpc('send_batch', {
  queue_name: 'tasks',
  messages: [{ a: 1 }, { a: 2 }],
  sleep_seconds: 0,
});
```

**Security setup** for client-side access:
1. Enable "Expose Queues via PostgREST" in Dashboard (creates `pgmq_public` schema)
2. Enable RLS on `pgmq.q_*` tables and create policies
3. Grant permissions to `pgmq_public` functions per role:
   - `send`/`send_batch` -> SELECT + INSERT
   - `read`/`pop` -> SELECT + UPDATE
   - `archive`/`delete` -> SELECT + DELETE

**Local/self-hosted exposure** — add `pgmq_public` to exposed schemas:

```toml
# config.toml (Supabase CLI)
[api]
schemas = ["public", "graphql_public", "pgmq_public"]
```

```bash
# .env (Docker Compose)
PGRST_DB_SCHEMAS=public,graphql_public,pgmq_public
```

## Raw pgmq Extension API

The underlying `pgmq` extension provides additional functions not exposed via `pgmq_public`:

```sql
-- Create queues (pgmq_public doesn't expose queue management)
SELECT pgmq.create('my_queue');
SELECT pgmq.create_unlogged('fast_queue');

-- Long-poll: wait up to 5s for messages, polling every 100ms
SELECT * FROM pgmq.read_with_poll('my_queue', 30, 1, 5, 100);

-- Change visibility timeout of a specific message
SELECT * FROM pgmq.set_vt('my_queue', 11, 30);

-- Queue metrics
SELECT * FROM pgmq.metrics('my_queue');
-- Returns: queue_length, newest/oldest_msg_age_sec, total_messages

-- Purge all messages
SELECT pgmq.purge_queue('my_queue');

-- Drop queue and archive table
SELECT pgmq.drop_queue('my_queue');

-- Detach archive from extension (survives DROP EXTENSION)
SELECT pgmq.detach_archive('my_queue');
```

## Cron + Queues Pattern

Combine pg_cron with Edge Functions to process queue messages on a schedule:

```sql
-- Invoke an Edge Function every 30 seconds to drain the queue
SELECT cron.schedule(
  'process-queue',
  '30 seconds',
  $$
  SELECT net.http_post(
    url := 'https://project-ref.supabase.co/functions/v1/queue-worker',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || 'YOUR_ANON_KEY'
    ),
    body := jsonb_build_object('time', now()),
    timeout_milliseconds := 5000
  ) AS request_id;
  $$
);
```

Sub-minute scheduling (e.g., `'30 seconds'`) requires Postgres >= 15.1.1.61. The `pg_net` extension must be enabled for HTTP requests from cron jobs.
