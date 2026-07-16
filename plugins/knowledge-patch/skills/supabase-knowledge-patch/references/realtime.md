# Realtime

## Client binding and publishing behavior

### Register Postgres Changes listeners before joining

As of `supabase-js` 2.101.0, a channel blocks adding `postgres_changes` listeners after join. Register all before `subscribe()`:

```ts
const channel = supabase
  .channel('database-changes')
  .on('postgres_changes', { event: '*', schema: 'public' }, handleChange)
  .subscribe()
```

### Copying Realtime bindings

Realtime provides `copyBindings` for copying registered event bindings.

### Database-triggered Realtime Broadcast

Database triggers can send Realtime Broadcast messages, allowing custom database-change payloads over a secure, scalable path.

### REST Broadcast without a WebSocket subscription

Servers can batch messages to `/realtime/v1/api/broadcast` with an API key and `messages`. Since `supabase-js` 2.37.0, send on an unsubscribed channel uses this REST route; remove the channel afterward.

```sh
curl -X POST "https://<project-ref>.supabase.co/realtime/v1/api/broadcast" \
  -H "apikey: <api-key>" -H "Content-Type: application/json" \
  --data '{"messages":[{"topic":"room-1","event":"notice","payload":{"text":"hi"}}]}'
```

## Authorization and replay

### Private-channel authorization contract

Realtime Authorization is public beta for Broadcast/Presence and needs `supabase-js` 2.44.0+. Add RLS to `realtime.messages`, join with `private: true`; `SELECT` permits receiving, `INSERT` sending, `realtime.topic()` gives requested topic, and `extension` distinguishes `broadcast`/`presence`. Disable **Allow public access** to require this for every channel.

```sql
create policy "room members receive broadcasts"
on realtime.messages for select to authenticated
using ((select realtime.topic()) = 'room-1'
  and realtime.messages.extension = 'broadcast');
```

Authorization probes roll back rather than storing messages. Read permission checks on join, write on first publish, then caches per connection. Sending a new JWT recomputes access; an unrefreshed expired JWT disconnects. Postgres Changes uses table RLS and ignores channel `private`; same-topic public/private channels stay isolated.

### Broadcast replay

Public-alpha replay works only on private channels and only for database-originated messages, not client/REST Broadcast. Messages remain in daily `realtime.messages` partitions for three days. Request required millisecond epoch `since` and optional positive `limit <= 25`; `payload.meta.replayed` marks history.

```ts
const channel = supabase.channel('room-1', {
  config: {
    private: true,
    broadcast: { replay: { since: Date.now() - 60_000, limit: 10 } },
  },
})
channel.on('broadcast', { event: 'notice' }, ({ meta, payload }) => {
  console.log(meta?.replayed ? 'history' : 'live', payload)
}).subscribe()
```

Minimum clients: JavaScript 2.74.0, Dart 2.10.0, Swift 2.34.0, Python 2.22.0. Kotlin lacks support.

## Resource budgets and quotas

### Realtime's database resource budget

Realtime always starts the authorization pool plus one DB connection and one replication slot for database Broadcast. Postgres Changes adds subscription, cleanup, and WAL-pull pools and may use a second slot.

Authorization-pool defaults by compute: 2 Nano/Micro, 5 Small–Large, 10 XL–4XL, 15 at 8XL+. Each of the three Changes pools defaults to 2, 4, 7, 9 respectively. Only authorization pool size is adjustable in Realtime Settings.

### Realtime quotas and payload overflow

Hosted defaults: Free 200 connections and 100 messages/joins per second; Pro 500 each; Pro without Spend Cap and Team 10,000 connections and 2,500 message/joins/sec. Presence is 20, 50, 1,000/sec respectively. All allow 100 channels/connection and 10 presence keys/object. Broadcast payload: 256 KB Free, 3,000 KB paid. Enterprise starts at highest and can request more.

Postgres Changes payload is 1,024 KB. Overflow reduces both `new` and `old` to fields whose individual values are <=64 bytes. Join errors: `too_many_channels`, `too_many_connections`, `too_many_joins`. Event overage emits `tenant_events` and disconnects; JavaScript reconnects after load drops.

### Realtime observability reports

Project Settings > Product Reports > Realtime shows clients, Broadcast/Presence/Changes volume, join rate, median payload, and HTTP count/errors/latency on all plans. Paid tiers also show DB-Broadcast lag and median private-channel read/write RLS time. Read RLS is join check; write RLS is first publish before cache.

### Realtime settings are connection-disrupting

Every settings change disconnects clients and restarts middleware. Settings control service enabled, public channels, authorization pool, concurrent clients, total events, Presence events, and payload size. Schedule a reconnect event.

## Wire protocol

### Realtime wire protocol 2.0

Custom clients opt into `vsn=2.0.0`; default stays 1.0.0. Text frames are exact arrays `[join_ref, ref, topic, event, payload]`. Send a `phoenix` heartbeat at least every 25 seconds:

```json
[null, "26", "phoenix", "heartbeat", {}]
```

Protocol 2 binary Broadcast frames support non-JSON payloads. Client pushes start `0x03` followed by byte lengths of join ref/ref/topic/event/metadata and encoding; server Broadcast starts `0x04` then topic/event/metadata lengths and encoding. Named fields/payload follow. Encoding 0 is binary, 1 JSON.

Send `access_token` to each joined topic to refresh auth and recalculate private authorization; it may also be in initial `phx_join`.

## Self-hosted release boundaries

### RLS role isolation

Realtime v2.112.10 fixes a role leak in `apply_rls`; treat it as security-sensitive.

### Restricted Realtime schema

Realtime v2.112.7 restricts the `realtime` schema. Verify privileges for custom roles/integrations.

### Equality-helper execution permission

Realtime v2.112.5 grants execute on `realtime.check_equality_op/5`.

### OrioleDB compatibility

Realtime v2.112.2 adds OrioleDB support; use it or later for OrioleDB-backed projects.
