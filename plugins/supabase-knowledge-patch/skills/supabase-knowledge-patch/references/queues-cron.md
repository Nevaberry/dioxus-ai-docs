# Cron Jobs & Queues

## Sub-Minute Cron Scheduling

pg_cron on Supabase supports sub-minute intervals using seconds syntax (requires Postgres 15.1.1.61+):

```sql
-- Run every 30 seconds
select
  cron.schedule (
    'fast-poll',
    '30 seconds',
    'SELECT process_pending()'
  );

-- Invoke Edge Function every 30 seconds via pg_net
select
  cron.schedule (
    'invoke-function-every-half-minute',
    '30 seconds',
    $$
  select net.http_post(
    url := 'https://project-ref.supabase.co/functions/v1/function-name',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || 'YOUR_ANON_KEY'
    ),
    body := jsonb_build_object('time', now()),
    timeout_milliseconds := 5000
  ) as request_id;
  $$
  );
```

Valid range: 1–59 seconds (e.g., `'1 seconds'`, `'45 seconds'`).

## Supabase Queues (`pgmq_public` Schema)

Supabase wraps the `pgmq` extension with a managed `pgmq_public` schema that exposes queue operations to client-side consumers via the Data API (PostgREST). This prevents direct access to `pgmq` tables (which don't have RLS by default).

Available `pgmq_public` functions: `send`, `send_batch`, `read`, `pop`, `delete`, `archive`.

Client-side usage via supabase-js:

```typescript
// Send a message (with optional delay)
const { data } = await supabase.schema('pgmq_public').rpc('send', {
  queue_name: 'my_queue',
  message: { hello: 'world' },
  sleep_seconds: 0,
});

// Read messages (with visibility timeout)
const { data: messages } = await supabase.schema('pgmq_public').rpc('read', {
  queue_name: 'my_queue',
  sleep_seconds: 30, // visibility timeout
  n: 5, // max messages to read
});

// Pop (read + delete atomically)
const { data } = await supabase.schema('pgmq_public').rpc('pop', {
  queue_name: 'my_queue',
});

// Delete after processing
await supabase.schema('pgmq_public').rpc('delete', {
  queue_name: 'my_queue',
  msg_id: message.msg_id,
});

// Archive instead of delete (for retention)
await supabase.schema('pgmq_public').rpc('archive', {
  queue_name: 'my_queue',
  message_id: message.msg_id,
});
```

## Exposing Queues via PostgREST

Queues are NOT exposed to the Data API by default. To enable client-side access:

1. Enable `pgmq` extension (available on Postgres 15.6.1.143+)
2. Toggle "Expose Queues via PostgREST" in Dashboard (creates `pgmq_public` schema)
3. Enable RLS on queue tables (`pgmq.q_<queue_name>`)
4. Grant permissions to `pgmq_public` functions per role

For local dev (CLI), add `pgmq_public` to config.toml:

```toml
[api]
schemas = ["public", "graphql_public", "pgmq_public"]
```

For self-hosted (Docker), update `.env`:

```
PGRST_DB_SCHEMAS=public,graphql_public,pgmq_public
```

## Queue Permissions Model

Each `pgmq_public` function requires specific table-level permissions on the underlying `pgmq.q_<queue_name>` table:

| Operation | Required Permissions |
|-----------|---------------------|
| `send`, `send_batch` | SELECT + INSERT |
| `read`, `pop` | SELECT + UPDATE |
| `archive`, `delete` | SELECT + DELETE |

Queue creation/deletion is NOT exposed via `pgmq_public` — only server-side via `pgmq.create()` / `pgmq.drop_queue()`.
