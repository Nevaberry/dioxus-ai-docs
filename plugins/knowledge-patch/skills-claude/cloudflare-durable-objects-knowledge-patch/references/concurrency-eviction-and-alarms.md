# Concurrency, eviction, and alarms

## `deleteAll()` can clear the alarm

With compatibility date `2026-02-24` or later, `ctx.storage.deleteAll()`
deletes both stored data and the alarm on KV- and SQLite-backed objects (2026).
A separate `deleteAlarm()` is unnecessary for a complete reset.

## Know when an object can hibernate

Timers, an in-progress awaited `fetch()`, standard WebSocket API use, or an
unfinished request or event prevent hibernation. A plain `fetch()` subrequest
does not keep the object alive merely because its returned body is streaming.

An otherwise eligible object currently hibernates after 10 seconds without an
event, discards its memory, and runs its constructor on the next event while
hibernatable client WebSockets stay connected.

## Active outbound connections defer eviction

An active connection created through `connect()` or an outbound WebSocket
keeps the object alive (2026). Once all such connections close, the ordinary
70–140 second inactivity window begins. Each connection blocks eviction for at
most 15 minutes; after that, normal eviction rules resume even if it stays open.

## Distinguish storage and non-storage awaits

Awaited Durable Object storage operations receive input-gate protection.
Awaiting `fetch()`, R2, or other non-storage I/O permits another request to
interleave. After external I/O, revalidate a version or other precondition
before committing dependent storage changes.

## Rely on output gates and write coalescing

Outgoing responses and network requests wait for pending storage writes to
finish. Consecutive writes without an intervening `await` are coalesced into
one atomic implicit transaction. An intervening `await`, including one between
legacy KV writes, ends the coalescing boundary.

```ts
this.ctx.storage.sql.exec(
  "UPDATE accounts SET balance = balance - ? WHERE id = ?", amount, from,
);
this.ctx.storage.sql.exec(
  "UPDATE accounts SET balance = balance + ? WHERE id = ?", amount, to,
);
return "transferred";
```

## Migrate SQLite schemas under a concurrency block

Durable Object SQLite does not support `PRAGMA user_version`. Track applied
migrations in a normal table and run constructor migrations inside
`blockConcurrencyWhile()` so no request observes a partial schema.

```ts
constructor(ctx: DurableObjectState, env: Env) {
  super(ctx, env);
  ctx.blockConcurrencyWhile(async () => {
    await this.migrateUsingVersionTable();
  });
}
```

## Understand instance uniqueness during replacement

The runtime rechecks global uniqueness at event start and whenever an event
accesses storage. A stale HTTP or RPC event that never touches storage may
finish after a replacement instance starts, but a later storage access stops it
with an error. WebSocket requests are terminated during shutdown, and requests
affected by a runtime update have at most 30 seconds to finish.

## Persist without a shutdown finalizer

There is no shutdown hook before deployment, eviction, or runtime-driven
replacement. Persist checkpoints incrementally; never rely on an end-of-process
flush.

## Build alarms as idempotent, non-recurring work

Alarms may be delivered more than once and do not recur automatically. The
handler must schedule its next run and be idempotent. Use
`AlarmInvocationInfo.retryCount` to schedule a fresh alarm before remaining
retries are exhausted.

Under local `wrangler dev`, alarm methods can fail after hot reload. Restart the
command after editing alarm code.

## Understand local persistence with `script_name`

By default, `wrangler dev` reads Durable Object storage but holds writes in
memory without modifying persistent data. When a binding explicitly sets
`script_name`, development writes do affect persistent storage, and Wrangler
emits a warning.
