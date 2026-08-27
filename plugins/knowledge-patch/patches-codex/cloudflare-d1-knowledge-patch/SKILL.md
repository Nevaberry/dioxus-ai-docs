---
name: cloudflare-d1-knowledge-patch
description: Cloudflare D1
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Cloudflare D1

Use this skill when designing, implementing, reviewing, or debugging Cloudflare
D1 databases, Workers bindings, Wrangler workflows, replication, placement, or
recovery. Start with the quick reference, then open the task-specific reference
instead of assuming general SQLite behavior applies to D1.

## Reference index

| Reference | Topics |
| --- | --- |
| [`query-api-and-sql.md`](references/query-api-and-sql.md) | Binding conversions, `exec()`, prepared statements, result modes, supported SQL, PRAGMAs, automatic retries |
| [`replication-and-location.md`](references/replication-and-location.md) | Sessions, bookmarks, replica controls and billing, placement hints, jurisdictions |
| [`migrations-and-local-development.md`](references/migrations-and-local-development.md) | Nested migration patterns, Pages local bindings, local persistence |
| [`backup-and-transfer.md`](references/backup-and-transfer.md) | Alpha backups and dumps, Time Travel, SQLite imports, exports |
| [`operations-and-debugging.md`](references/operations-and-debugging.md) | API authorization, storage limits, result diagnostics, retry versus optimization |

## Breaking and compatibility-sensitive behavior

### Use D1-specific write authorization

HTTP API writes require an API token with `D1:Edit`. A token with `D1:Read`
and `Edit` for another Cloudflare product is not sufficient.

### Bind only supported JavaScript values

- Booleans are permanently stored as SQLite integers and read back as `0` or
  `1`.
- `ArrayBuffer` values and views become BLOBs and read back as arrays.
- `undefined` raises `D1_TYPE_ERROR`.
- `BigInt` is unsupported. Although D1 stores signed 64-bit integers, binding
  round trips are safe only through `Number.MAX_SAFE_INTEGER`.

Do not promise round-trip preservation of the original JavaScript type.

### Use positional placeholders

D1 supports anonymous `?` and ordered `?NNN` parameters, not named
parameters. Ordered placeholders refer to the matching `bind()` argument:

```ts
const stmt = env.DB
  .prepare("SELECT * FROM jobs WHERE state = ?2 AND id = ?1")
  .bind(42, "ready");
```

### Do not treat `exec()` as a batch abstraction

`exec()` takes unbound statements separated by newlines. It stops at the first
failure, throws query and error details, and does not run later statements.
Reserve it for maintenance or one-shot work; use prepared statements for
application data.

### Respect creation-time data-location decisions

A database jurisdiction can be set only at creation and cannot be added or
changed later. If both a jurisdiction and location hint are supplied, the
jurisdiction wins and the hint is ignored.

### Keep local and remote targets explicit

Pages local development cannot connect to remote D1. Supply a project-root
Wrangler binding with `preview_database_id` equal to the binding name. Pass
`--local` to local execute and migration commands; omitting it targets the
remote database.

## Query and result quick reference

### Choose the intended result mode

- `run<T>()` is an alias for `all<T>()`.
- `raw({ columnNames: true })` returns arrays with a leading column-name array
  and omits metadata.
- `first(columnName)` returns a scalar, returns `null` for no rows, and throws
  `D1_ERROR` when the column is absent.
- `first()` does not add `LIMIT 1`; add the limit in SQL when it matters.
- `D1Result.results` is `[]` for a query with no rows and `null` when results
  do not apply.

### Use documented SQLite features only

D1 includes FTS5 and `fts5vocab`, JSON functions and operators, and SQLite math
functions. Do not infer availability of other extensions from SQLite
compatibility alone.

### Treat PRAGMAs as transaction-scoped

Only the documented PRAGMA subset is supported, and its effects apply to the
current transaction. `PRAGMA defer_foreign_keys = on` delays validation; it
does not disable constraints or `ON DELETE CASCADE` actions.

Run `PRAGMA optimize;` after schema changes such as creating an index.

## Read consistency quick reference

### Use Sessions for sequential consistency

Create a session with `env.DB.withSession()` and route the logical sequence of
queries through it. Carry `session.getBookmark()` into a later
`withSession(bookmark)` when sequential consistency must cross session
boundaries.

`withSession()` is equivalent to `withSession("first-unconstrained")`, so the
first query can run on a primary or replica. Use
`withSession("first-primary")` when the first query must observe the latest
primary database version.

### Keep Sessions and REST boundaries clear

Sessions are available through the Workers binding, not the REST API. They
remain usable when replication is disabled. D1 creates and routes replicas;
applications select consistency through the session constraint and bookmark.

### Interpret serving metadata correctly

Remote results expose `served_by_region` and `served_by_primary` whether or not
Sessions or replication are in use. Both values are `undefined` in local
`wrangler dev`. `timings.sql_duration_ms` measures SQL execution only and
excludes network time.

## Migration quick reference

Set both `migrations_dir` and `migrations_pattern` when migrations live in
nested directories:

```jsonc
{
  "d1_databases": [{
    "binding": "DB",
    "database_name": "my-database",
    "database_id": "<UUID>",
    "migrations_dir": "migrations",
    "migrations_pattern": "migrations/*/migration.sql"
  }]
}
```

The pattern is relative to the Wrangler configuration, must start with
`migrations_dir`, uses `*` for one path segment and `**` for any number, and
defaults to `${migrations_dir}/*.sql`. Applied names are relative to
`migrations_dir`. `wrangler d1 migrations create` still creates top-level
files, so use the ORM generator for nested-only layouts.

## Recovery and transfer quick reference

### Prefer Time Travel for supported databases

Production-backend databases have Time Travel automatically. Workers Paid
retains 30 days and Workers Free retains 7 days. Confirm
`version: production` with `wrangler d1 info`.

A restore overwrites the database, cancels in-flight work, and returns the
pre-restore bookmark. Save it for undo. Restore does not erase older bookmarks
inside the retention window, but it cannot clone or fork a database.

### Convert SQLite files before importing

D1 does not import a raw `.sqlite3` file. Dump it to SQL; remove
`BEGIN TRANSACTION`, `COMMIT`, and any `CREATE TABLE _cf_KV` statement; then
execute the SQL remotely. Each import file is limited to 5 GiB.

### Plan exports as blocking operations

An export blocks other database requests. Any virtual table, including FTS5,
prevents export until removed; recreate it afterward. Exports can target the
whole database or one table and can select schema-only or data-only output.

## Retry and debugging quick reference

D1 automatically retries classified read-only `SELECT`, `EXPLAIN`, and `WITH`
queries up to two times after retryable errors. Inspect `meta.total_attempts`.
If a retried attempt modifies data, D1 rolls it back. Applications must still
retry other business-level idempotent operations deliberately.

Catch ordinary `Error` objects and read `message`. When supporting Wrangler
before 3.1.1, fall back to `cause.message`.

Retry lost connections and transient infrastructure failures. Optimize,
spread load, reduce operation size, or shard for timeouts, overload,
isolate-memory resets, and CPU-limit resets. Resolve capacity errors by
deleting data, upgrading the plan, or sharding rather than blindly retrying.
