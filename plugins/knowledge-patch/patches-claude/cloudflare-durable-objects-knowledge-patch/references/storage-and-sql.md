# Storage and SQL

## Consume SQL cursors before `await`

A `SqlStorageCursor` is not a stable snapshot across an `await`. Resumed
iteration can observe later mutations, including writes from a later implicit
transaction that ultimately rolls back. Materialize rows synchronously before
yielding.

```ts
const rows = this.ctx.storage.sql.exec("SELECT * FROM users").toArray();
await fetch("https://example.com", {
  method: "POST",
  body: JSON.stringify(rows),
});
```

## Understand `exec()` cursor and binding rules

One `exec()` call may contain semicolon-separated statements, but bindings
apply only to the last statement and the returned cursor represents only that
statement. The cursor and its `raw()` iterator consume one shared position.
`one()` throws unless exactly one row is returned.

## Use storage transaction callbacks

`sql.exec()` rejects transaction statements such as `BEGIN TRANSACTION` and
`SAVEPOINT`. Use `transactionSync()` for synchronous SQL or synchronous KV
work. Its callback must not return a promise, its value is returned to the
caller, and an exception rolls the transaction back.

```ts
this.ctx.storage.transactionSync(() => {
  this.ctx.storage.sql.exec(
    "UPDATE counters SET value = value + 1 WHERE id = ?",
    counterId,
  );
});
```

For SQLite-backed objects, direct `ctx.storage` operations—including SQL—join
`transaction()`. The older `txn` wrapper is obsolete for this backend.

## Use bundled SQLite extensions

The embedded database supports FTS5, including `fts5vocab`, as well as JSON
functions and operators and math functions. These can be used directly in an
object's private database.

## Point-in-time recovery

PITR bookmarks cover the whole SQLite database, including values written via
the KV API, and can target approximately any time in the preceding 30 days.
Bookmarks sort chronologically using ordinary lexical string comparison.

`onNextSessionRestoreBookmark()` schedules an exact restore for the next
restart and returns a pre-restore bookmark that can undo the operation.

```ts
const target = await this.ctx.storage.getBookmarkForTime(
  Date.now() - 2 * 24 * 60 * 60 * 1000,
);
const undo = await this.ctx.storage.onNextSessionRestoreBookmark(target);
this.ctx.abort("restore requested");
```

PITR is unavailable in local development. `ctx.abort()` forcibly resets the
object and logs an uncatchable error with its optional message; it too is
unavailable under `wrangler dev`.

## Synchronous KV on SQLite-backed objects

`ctx.storage.kv` exposes immediate `get`, `put`, `delete`, and `list` methods
without promises.

```ts
this.ctx.storage.kv.put("profile:42", { name: "Ada" });
const profile = this.ctx.storage.kv.get("profile:42");
```

`list()` returns key-value pairs in UTF-8 key order. It supports inclusive
`start`, exclusive `startAfter` and `end`, plus `prefix`, `reverse`, and
`limit`. An unbounded list loads all data into memory.

## Loopback exports

`ctx.exports` provides loopback bindings to the Worker's own top-level exports
with the same semantics as `ExecutionContext.ctx.exports`. Do not confuse this
runtime property with Wrangler's deployment-time class lifecycle map, which is
also named `exports`.
