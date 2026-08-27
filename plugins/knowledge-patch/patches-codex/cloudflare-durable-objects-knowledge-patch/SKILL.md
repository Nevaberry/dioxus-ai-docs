---
name: cloudflare-durable-objects-knowledge-patch
description: Cloudflare Durable Objects
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Cloudflare Durable Objects

Use this skill when designing, configuring, deploying, testing, or debugging
Cloudflare Durable Objects. Start with the quick references below, then load the
topic file that matches the task. Treat project configuration, installed package
types, runtime behavior, and tests as the final authority for this rolling
service surface.

## How to use this skill

1. Identify the namespace's storage backend and whether the Worker uses legacy
   `migrations` or the declarative `exports` lifecycle map.
2. Preserve already-provisioned namespace state. A code export alone does not
   create a namespace, storage backends cannot be changed in place, and lifecycle
   operations need deliberately ordered deployments.
3. Check the Worker's compatibility date before relying on date-gated behavior.
4. Read the relevant reference file before changing concurrency, storage,
   placement, WebSockets, lifecycle declarations, alarms, or test isolation.
5. Exercise restart, eviction, and mixed-version behavior where correctness
   depends on in-memory state or a coordinated rollout.

## Reference index

| Reference | Topics |
| --- | --- |
| [deployment-and-class-lifecycle.md](references/deployment-and-class-lifecycle.md) | SQLite adoption, `exports`, migrations, renames, deletion, transfers, environments, deployment restrictions |
| [storage-sql-and-recovery.md](references/storage-sql-and-recovery.md) | SQL cursors, transactions, synchronous KV, extensions, point-in-time recovery, loopback exports |
| [identity-and-placement.md](references/identity-and-placement.md) | Names, jurisdictions, ID spaces, placement hints |
| [concurrency-alarms-and-runtime.md](references/concurrency-alarms-and-runtime.md) | Input/output gates, hibernation, eviction, schema migrations, alarms, shutdown, rollout compatibility |
| [websocket-hibernation.md](references/websocket-hibernation.md) | Hibernatable handlers, attachments, tags, auto-responses, event timeouts, close behavior |
| [testing-and-local-development.md](references/testing-and-local-development.md) | Workers Vitest setup, typed bindings, HTTP integration, storage lifetime, alarms, eviction, local persistence |

## Deployment and storage decisions

### Prefer SQLite for new namespaces

Create new classes with SQLite storage. In legacy lifecycle configuration, use
`new_sqlite_classes`; in declarative lifecycle configuration, set
`"storage": "sqlite"` on each live class.

```toml
[[migrations]]
tag = "v1"
new_sqlite_classes = ["ChatRoom"]
```

SQLite-backed objects provide SQL, point-in-time recovery, and synchronous KV
access. Existing KV-backed namespaces remain usable, but there is no in-place
migration from their storage to SQLite. New KV namespace creation is restricted,
so do not choose `new_classes` for a new deployment.

### Choose one lifecycle system

Wrangler accepts either the ordered `migrations` array or the declarative
`exports` map, never both. Under `exports`, every desired or existing namespace
needs an entry; live entries need `storage`, and lifecycle tombstones must omit
it. A live configured class missing from Worker code causes deployment to fail.

```jsonc
{
  "exports": {
    "ChatRoom": {
      "type": "durable-object",
      "storage": "sqlite"
    }
  }
}
```

Migration-to-`exports` conversion preserves namespace data when every active
class is declared with its original backend (`sqlite` or `legacy-kv`), but the
switch is one-way. Read the lifecycle reference before converting, renaming,
deleting, or transferring a class.

### Stage lifecycle operations

- For a rename, first deploy the new implementation under both class names;
  then deploy the old-name `renamed` tombstone and new live entry; remove the
  code alias only after the rollout.
- For a cross-Worker transfer, deploy `expecting-transfer` on the target first,
  commit with `transferred` on the source, then make the target entry live and
  change bindings last.
- Keep tombstones until reconciliation explicitly reports them safe to remove.
  Deletion is blocked while code exports the class or any Worker still binds to
  its namespace.
- Apply lifecycle changes only with a full `wrangler deploy`. Upload-only,
  gradual deployment, and rollback across a lifecycle change are unsupported.

## SQL and transaction safety

### Materialize cursors before yielding

A `SqlStorageCursor` is not a stable snapshot across `await`. Convert results
with `toArray()` or otherwise exhaust the cursor synchronously before external
I/O; resumed iteration can observe later writes, even from a transaction that
eventually rolls back.

```ts
const rows = this.ctx.storage.sql.exec("SELECT * FROM users").toArray();
await sendRows(rows);
```

Within a multi-statement `exec()`, bindings and the returned cursor belong only
to the final statement. Cursor iteration and `raw()` share one position, and
`one()` requires exactly one returned row.

### Use storage transaction APIs

Do not issue `BEGIN`, `SAVEPOINT`, or other transaction-control SQL through
`sql.exec()`. Use `transactionSync()` for synchronous SQL or KV work; its
callback cannot return a promise, passes its return value through, and rolls
back when it throws.

```ts
this.ctx.storage.transactionSync(() => {
  this.ctx.storage.sql.exec(
    "UPDATE counters SET value = value + 1 WHERE id = ?",
    counterId,
  );
});
```

On SQLite-backed objects, direct storage operations participate in
`transaction()`; do not retain the obsolete `txn` wrapper. For schema changes,
track versions in an ordinary table—`PRAGMA user_version` is unsupported—and
run constructor migrations inside `blockConcurrencyWhile()`.

## Concurrency and lifecycle safety

Storage awaits receive input-gate protection; external `fetch()`, R2, and other
non-storage awaits do not. After such I/O, re-read or revalidate any version or
precondition before committing dependent state.

Pending storage writes hold outgoing responses and network requests behind the
output gate. Consecutive writes without an intervening `await` are coalesced
into one atomic implicit transaction; an `await` ends that boundary.

Do not depend on a shutdown callback—none exists for eviction, deployment, or
runtime replacement. Persist checkpoints incrementally. Also keep Worker-to-
object request and RPC contracts compatible across adjacent releases because
rollouts can temporarily pair new Worker code with an older object instance.

Alarms are non-recurring and can run more than once. Schedule the next alarm
explicitly, make handlers idempotent, and use `retryCount` when deciding whether
to install a fresh alarm before retries are exhausted.

## Identity and placement

Use `namespace.jurisdiction()` for residency constraints. Jurisdiction scopes
have distinct ID spaces: an ID belongs to its scope, although an unscoped
namespace can resolve a restricted ID. The same name therefore maps to different
IDs in `eu`, `us`, and `fedramp`.

`ctx.id.name` exists only when the object was reached by name, subject to the
documented length and lookup limitations. `ctx.id.jurisdiction` survives string
round-trips. Placement `locationHint` values affect only first placement and do
not move an existing object.

## WebSocket hibernation

Enable hibernation with `ctx.acceptWebSocket(server)` and handle messages and
closes in Durable Object class methods. Calling the standard `ws.accept()` does
not enable hibernation, and outbound WebSockets cannot hibernate.

Persist per-connection state with `serializeAttachment()` within its 16,384-byte
limit, and write longer-lived or larger state to Durable Object storage. Use
tags for bounded grouping, auto-responses for wake-free request/reply pairs,
and the hibernatable event timeout when a handler needs an explicit runtime cap.

## Testing essentials

Workers Vitest 4 uses the `cloudflareTest()` Vite plugin and a Wrangler config
that declares the bindings and lifecycle configuration. Type test `env` through
`ProvidedEnv`. Exercise the Worker's public HTTP route with
`exports.default.fetch()` and call a binding from `env` for direct stub tests.

Eviction helpers reset instances while preserving storage. Use
`evictDurableObject()` for a named stub, its `{ webSockets: "close" }` option for
the non-hibernating socket path, and `evictAllDurableObjects()` for all running
instances. `runDurableObjectAlarm()` reports whether it found and ran an alarm.

## Pre-deployment checklist

- Confirm every live namespace and retained tombstone is represented in the
  chosen lifecycle configuration.
- Verify storage backend declarations against the namespaces that already
  exist; never infer them from the current class implementation.
- Audit all `await` boundaries between reads and dependent writes.
- Verify alarms are idempotent and reschedule themselves when recurring work is
  intended.
- Test a fresh construction, hibernation wake-up, explicit eviction, and any
  WebSocket close path the application relies on.
- Keep lifecycle tombstones and compatibility shims through the entire rollout,
  then remove them only when reconciliation or deployment sequencing permits.
