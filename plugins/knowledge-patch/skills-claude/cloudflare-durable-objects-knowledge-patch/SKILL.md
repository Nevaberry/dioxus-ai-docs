---
name: cloudflare-durable-objects-knowledge-patch
description: Cloudflare Durable Objects
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Cloudflare Durable Objects

Use this skill when designing, configuring, deploying, migrating, or testing
Cloudflare Durable Objects. Check the project configuration and compatibility
date first, then use the topic reference that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [deployment-lifecycle.md](references/deployment-lifecycle.md) | SQLite namespace creation, declarative exports, tombstones, renames, transfers, environments, and rollout compatibility |
| [storage-and-sql.md](references/storage-and-sql.md) | SQL cursors and transactions, SQLite extensions, PITR, synchronous KV, and loopback exports |
| [identity-and-placement.md](references/identity-and-placement.md) | Object names, jurisdictions, ID spaces, and placement hints |
| [concurrency-eviction-and-alarms.md](references/concurrency-eviction-and-alarms.md) | Gates, atomic writes, hibernation eligibility, eviction, uniqueness, schema migration, shutdown, alarms, and local persistence |
| [websocket-hibernation.md](references/websocket-hibernation.md) | Hibernation handlers, attachments, tags, auto-responses, event timeouts, and closing sockets |
| [testing.md](references/testing.md) | Vitest configuration, binding types, HTTP integration, storage isolation, alarm execution, and eviction helpers |

## Breaking and lifecycle decisions

### Create new namespaces with SQLite storage

Use `new_sqlite_classes` in legacy migrations, or `storage: "sqlite"` in the
declarative `exports` map. SQLite-backed objects are the recommended default
for new classes and are the only backend with SQL and point-in-time recovery.

Do not assume an existing KV-backed namespace can be converted to SQLite.
Accounts without an existing KV-backed namespace cannot create their first one
with `new_classes`.

```toml
[[migrations]]
tag = "v1"
new_sqlite_classes = ["Room"]
```

### Choose exactly one class-lifecycle system

Use either the ordered `migrations` array or Wrangler's current-state `exports`
map in one Worker, never both. Existing Workers can retain migrations. Moving
from migrations to exports preserves namespace data but is one-way, and the
declared storage backend cannot later be changed in place.

```jsonc
{
  "exports": {
    "Room": { "type": "durable-object", "storage": "sqlite" }
  }
}
```

Every desired or provisioned namespace needs an `exports` entry. Live entries
need matching code plus `storage`; tombstones must omit `storage`.

### Stage renames and transfers

For a zero-downtime rename, deploy an old-name code alias first. Then deploy an
old-name `renamed` tombstone and the new live entry while keeping the alias.
Remove the alias only after rollout.

For a cross-Worker declarative transfer, deploy the target's
`expecting-transfer` entry first, then the source's `transferred` tombstone.
Make the target live and update bindings only after the handoff commits.

Keep lifecycle tombstones until reconciliation explicitly reports them safe to
remove. Lifecycle changes require a full `wrangler deploy`; they cannot use a
versions-only upload or gradual deployment, and rollback cannot cross them.

## Storage and transaction quick reference

### Materialize SQL cursors before yielding

A SQL cursor is not a stable snapshot across `await`. Convert it to an array
synchronously before external I/O so resumed iteration cannot observe later
mutations or rolled-back writes.

```ts
const rows = this.ctx.storage.sql.exec(
  "SELECT * FROM users",
).toArray();
await sendRows(rows);
```

### Use storage transaction callbacks

Do not send `BEGIN`, `SAVEPOINT`, or related transaction statements through
`sql.exec()`. Use `transactionSync()` for synchronous SQL or KV work. Its
callback must not return a promise; throwing rolls the transaction back.

Consecutive writes without an intervening `await` are coalesced into an atomic
implicit transaction. Awaiting non-storage I/O allows another request to
interleave, so revalidate dependent state before writing.

### Treat destructive reset and restore as lifecycle events

On compatibility date `2026-02-24` or later, `ctx.storage.deleteAll()` also
deletes the alarm. PITR applies to the whole SQLite database, including values
written through the KV API, and a scheduled restore takes effect on the next
session. PITR and `ctx.abort()` are unavailable in local development.

## Identity and placement quick reference

Use `getByName()` when identity is derived from an application name. Such an
object can read that name through `ctx.id.name`, subject to the documented
access and length restrictions.

Use `namespace.jurisdiction("us" | "eu" | "fedramp")` for residency. Each
jurisdiction has a distinct ID space, so never pass a scoped ID to another
scoped namespace. The unscoped namespace can resolve restricted IDs.

Location hints affect only first placement and never relocate an existing
object. Treat every hint as best effort.

## Concurrency and durability quick reference

Storage awaits receive input-gate protection; `fetch()`, R2, and other
non-storage awaits do not. Output gates delay outgoing responses and requests
until pending storage writes finish.

Do not rely on process memory for durable truth. Eligible idle objects can
hibernate, eviction discards memory, and there is no shutdown finalizer. Save
checkpoints incrementally and rebuild transient state in the constructor.

Run SQLite schema migrations in `blockConcurrencyWhile()` and track versions
in a normal table because `PRAGMA user_version` is unsupported.

Alarms are at-least-once, non-recurring work. Make the handler idempotent and
schedule the next alarm explicitly.

## WebSocket hibernation quick reference

For inbound hibernating WebSockets, accept the server endpoint with
`ctx.acceptWebSocket()` and implement Durable Object handlers such as
`webSocketMessage()` and `webSocketClose()`. Calling standard `ws.accept()`
does not enable hibernation, and outbound WebSockets cannot hibernate.

Persist small connection metadata with `serializeAttachment()` whenever it
changes. Use Durable Object storage for state larger than 16,384 bytes or state
that must outlive a closed connection.

Use tags for bounded grouping, auto-responses for simple request/response pairs
that should not wake the object, and an event timeout when hibernatable handler
runtime must be capped.

## Deployment compatibility

Worker and Durable Object code can be temporarily mismatched during rollout,
for seconds to minutes and longer with gradual deployment. Keep HTTP and RPC
contracts compatible across adjacent releases.

Named environments inherit top-level lifecycle exports unless overridden, but
each environment has separate namespaces and tombstones. Verify the intended
environment before any rename, deletion, or transfer.

## Testing quick reference

Use the Workers Vitest configuration plugin, augment `ProvidedEnv` for typed
bindings, call `exports.default.fetch()` for Worker-level integration, and use
`env` bindings for direct stub tests.

Eviction helpers reset running instances while retaining durable storage.
Storage also persists across tests in the same test file for the same object
ID, so use distinct IDs when isolation matters.

Use `runDurableObjectAlarm(stub)` to execute a scheduled alarm immediately and
assert its boolean result. Restart `wrangler dev` after editing alarm code if
local alarm methods fail following a hot reload.
