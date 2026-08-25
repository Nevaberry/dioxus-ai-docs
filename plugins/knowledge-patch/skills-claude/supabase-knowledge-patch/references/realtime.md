# Realtime

Use this reference for channel setup, authorization, Broadcast, Presence, Postgres Changes, protocol behavior, and service limits.

## Supabase JS compatibility (`supabase-js-2.101.0`)

### Realtime bindings must precede subscription
As of 2.101.0, a joined channel blocks new `postgres_changes` listeners. Register every binding before calling `subscribe()`.

```ts
const channel = supabase
  .channel('database-changes')
  .on('postgres_changes', { event: '*', schema: 'public' }, handleChange)
  .subscribe()
```

### Realtime protocol and heartbeat updates
Realtime added its V2 serializer in 2.81.0 and made serializer version `2.0.0` the default in 2.91.0. Heartbeat callbacks can also receive the measured latency.

### Realtime REST and replay additions
Realtime gained an explicit REST-call path, configurable Broadcast Replay, and metadata on user broadcast pushes.

### Custom-JWT channel lifecycle
Channels using a custom JWT no longer require `setAuth()`, and retain that token across resubscription.

## Channel authorization, broadcasts, changes, and limits

### Private Broadcast and Presence authorization
Private channels require `supabase-js` 2.44.0 or later and RLS policies on `realtime.messages`: `SELECT` permits receiving, `INSERT` permits sending or tracking, `realtime.topic()` exposes the requested topic, and `extension` distinguishes `broadcast` from `presence`. Disable **Allow public access** and set `private: true`; these policies are cached at join, refreshed by a new access-token message, and do not apply to Postgres Changes.

```sql
create policy "members receive room broadcasts"
on realtime.messages
for select
to authenticated
using (
  extension = 'broadcast'
  and (select realtime.topic()) = 'room-1'
);
```

```ts
const room = supabase
  .channel('room-1', { config: { private: true } })
  .on('broadcast', { event: 'update' }, handleUpdate)
  .subscribe()
```

### Database-triggered Broadcast
`realtime.send(payload, event, topic, private)` emits an arbitrary database message, while `realtime.broadcast_changes()` formats row-change events for private channels. A trigger can address each record through its topic and publish inserts, updates, and deletes without a Postgres Changes subscription.

```sql
create or replace function public.broadcast_item_change()
returns trigger
security definer set search_path = ''
language plpgsql as $$
begin
  perform realtime.broadcast_changes(
    'item:' || coalesce(new.id, old.id)::text,
    tg_op, tg_op, tg_table_name, tg_table_schema, new, old
  );
  return null;
end;
$$;

create trigger broadcast_item_change
after insert or update or delete on public.items
for each row execute function public.broadcast_item_change();
```

### Postgres Changes payload and delete constraints
Set `REPLICA IDENTITY FULL` to receive old row values for updates and deletes, but with RLS a delete's old record still contains only primary keys; delete events cannot be filtered, and tables with spaces in their names are unsupported. If a Postgres Changes payload exceeds its 1,024 KB limit, `new` and `old` retain only fields whose individual values are at most 64 bytes.

```sql
alter table public.messages replica identity full;
```

### Realtime limit failure behavior
The Free and Pro columns list respectively 200/500 concurrent connections, 100/500 messages and joins per second, 20/50 Presence messages per second, and 256/3,000 KB Broadcast payloads; both cap a connection at 100 channels and a Presence object at 10 keys. Join refusal reports `too_many_channels`, `too_many_connections`, or `too_many_joins`; `tenant_events` disconnects over-throughput clients, and `supabase-js` reconnects after throughput falls below the limit.

### Settings changes disconnect clients
Every change in the Realtime Settings screen disconnects all connected clients so Realtime can apply the new channel restriction, authorization pool size, client, event, Presence, or payload limits.

## Realtime service compatibility

### RLS role isolation
Realtime 2.112.10 fixes a role leak while applying RLS in `apply_rls`; self-hosted deployments that depend on Realtime authorization should use 2.112.10 or later.

### OrioleDB compatibility
Realtime 2.112.2 adds support for OrioleDB-backed projects.

## JavaScript client behavior

### Postgres Changes are disabled on new projects
New projects enable Broadcast and Presence but disable database-change listening by default. Enable the relevant tables in Realtime replication before expecting a `postgres_changes` subscription to receive events.

## Platform capabilities (`1.26.08`)

### The `realtime` schema is protected
Creating, altering, or dropping objects in the `realtime` schema now fails with a permission error. Existing RLS policies on `realtime.messages` continue to work.
