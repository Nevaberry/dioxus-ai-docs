# Storage, SQL, and recovery

## Exhaust SQL cursors before `await`

A `SqlStorageCursor` is not a stable snapshot across an `await`. If iteration
resumes after the object yields, it can observe later mutations, including
writes made in a later implicit transaction that ultimately rolls back.
Materialize the result synchronously before yielding.

```ts
const rows = this.ctx.storage.sql.exec("SELECT * FROM users").toArray();
await fetch("https://example.com", {
  method: "POST",
  body: JSON.stringify(rows),
});
```

## `exec()` and cursor semantics

One `exec()` call may contain semicolon-separated statements, but parameter
bindings apply only to the last statement and the returned cursor represents
only that statement. The cursor's object iterator and `raw()` iterator consume
the same position. `one()` throws unless the result has exactly one row.

## Transactions use storage callbacks

`sql.exec()` rejects transaction-control statements such as `BEGIN TRANSACTION`
and `SAVEPOINT`. Use `transactionSync()` for synchronous SQL or synchronous KV
operations. Its callback must not return a promise; its value becomes the
transaction's return value, and a thrown exception rolls the transaction back.

```ts
this.ctx.storage.transactionSync(() => {
  this.ctx.storage.sql.exec(
    "UPDATE counters SET value = value + 1 WHERE id = ?",
    counterId,
  );
});
```

For SQLite-backed objects, direct `ctx.storage` operations—including SQL
queries—participate in `transaction()`. The older `txn` wrapper is obsolete on
this backend.

## Embedded SQLite extensions

The private database supports FTS5, including `fts5vocab`, as well as SQLite's
JSON functions and operators and math functions. These can be called directly
from the object's SQL.

## Point-in-time recovery

PITR bookmarks cover the whole SQLite database, including values written using
the KV API. A bookmark can target approximately any point in the previous 30
days. `onNextSessionRestoreBookmark()` schedules an exact restore for the next
session and returns a pre-restore bookmark that can reverse it. Ordinary lexical
string comparison orders bookmarks chronologically.

```ts
const DAY_MS = 24 * 60 * 60 * 1000;
const target = await this.ctx.storage.getBookmarkForTime(
  Date.now() - 2 * DAY_MS,
);
const undo = await this.ctx.storage.onNextSessionRestoreBookmark(target);
this.ctx.abort("restore requested");
```

PITR is unavailable in local development. `ctx.abort()` forcibly resets the
object and logs an uncatchable error carrying its optional message; it is also
unavailable under `wrangler dev`.

## Synchronous KV on SQLite

`ctx.storage.kv` supplies immediate `get`, `put`, `delete`, and `list` methods
without promises. `list()` returns key-value pairs ordered by UTF-8 key bytes.
Its bounds are inclusive `start`, exclusive `startAfter` and `end`, plus
`prefix`, `reverse`, and `limit`. An unbounded list loads every matching value
into memory, so apply a limit for large keyspaces.

```ts
this.ctx.storage.kv.put("profile:42", { name: "Ada" });
const profile = this.ctx.storage.kv.get("profile:42");
```

## Loopback Worker exports

`ctx.exports` exposes loopback bindings to the Worker's own top-level exports
with the same semantics as `ExecutionContext.ctx.exports`. Do not confuse this
runtime property with Wrangler's deployment-time Durable Object lifecycle map,
which is also named `exports`.
