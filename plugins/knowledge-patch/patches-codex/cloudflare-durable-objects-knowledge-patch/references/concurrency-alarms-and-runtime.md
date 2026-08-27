# Concurrency, alarms, and runtime lifecycle

## Hibernation requires quiescence

Timers, an in-progress awaited `fetch()`, standard WebSocket API use, and an
unfinished request or event prevent an idle object from hibernating. A plain
`fetch()` subrequest does not keep the object alive solely because its returned
body is still streaming. An otherwise eligible object currently hibernates
after 10 seconds without an event: memory is discarded, the constructor runs
again on the next event, and hibernatable client WebSockets remain connected.

## Input gates cover storage, not external I/O

Awaited Durable Object storage operations receive input-gate protection.
Awaiting `fetch()`, R2, or other non-storage I/O allows another request to
interleave. After external I/O, revalidate a version or other precondition
before committing storage changes that depend on the earlier read.

## Output gates and implicit transactions

Outgoing responses and network requests wait until pending storage writes
finish. Consecutive writes with no intervening `await` are coalesced into one
atomic implicit transaction. An intervening `await`, including one between
legacy KV writes, ends that coalescing boundary.

```ts
this.ctx.storage.sql.exec(
  "UPDATE accounts SET balance = balance - ? WHERE id = ?",
  amount,
  from,
);
this.ctx.storage.sql.exec(
  "UPDATE accounts SET balance = balance + ? WHERE id = ?",
  amount,
  to,
);
return "transferred";
```

## SQLite schema migrations

Durable Object SQLite does not support `PRAGMA user_version`. Keep an applied
version in an ordinary table. Run constructor migrations inside
`blockConcurrencyWhile()` so no event observes a partially migrated schema.

```ts
constructor(ctx: DurableObjectState, env: Env) {
  super(ctx, env);
  ctx.blockConcurrencyWhile(async () => {
    await this.migrateUsingVersionTable();
  });
}
```

## Instance uniqueness and replacement

Global uniqueness is checked when an event begins and whenever it accesses
storage. A stale HTTP or RPC event that never touches storage can finish after a
replacement instance starts; if it later accesses storage, the runtime stops it
with an error. WebSocket requests are terminated during shutdown. Requests
interrupted by a runtime update receive at most 30 seconds to finish.

## No shutdown finalizer

There is no shutdown hook before deployment, eviction, or runtime-driven
replacement. Persist progress and checkpoints incrementally instead of relying
on a final memory flush.

## Mixed-version rollout window

Worker and Durable Object code deploy with eventual consistency. For seconds to
minutes, new Worker code can call an older Durable Object version; gradual
deployment lengthens the overlap. Keep HTTP and RPC contracts forward- and
backward-compatible across adjacent releases.

## Active outbound connections and eviction

An active connection opened by `connect()` or an outbound WebSocket keeps the
object alive (since 2026). Once all such connections close, the usual 70–140
second inactivity window starts. Any one connection blocks eviction for at most
15 minutes; normal eviction rules resume afterward even if it remains open.

## Alarms

Alarms do not recur automatically and may be delivered more than once. Schedule
the next occurrence explicitly and make the handler idempotent.
`AlarmInvocationInfo.retryCount` can guide creation of a new alarm before the
remaining retries are exhausted.

With compatibility date `2026-02-24` or later, `ctx.storage.deleteAll()` removes
the object's alarm as well as all stored data on both KV- and SQLite-backed
objects. A separate `deleteAlarm()` is unnecessary for a full reset.

```js
await this.ctx.storage.deleteAll();
```

Under local `wrangler dev`, alarm methods may fail after hot reload. Restart the
development command after editing alarm code.
