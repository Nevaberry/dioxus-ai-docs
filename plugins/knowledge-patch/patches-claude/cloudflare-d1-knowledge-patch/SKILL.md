---
name: cloudflare-d1-knowledge-patch
description: Cloudflare D1
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Cloudflare D1 Knowledge Patch

Use this skill when designing, implementing, migrating, operating, or debugging
Cloudflare D1 databases. Check the project’s Wrangler configuration, binding
usage, database generation, account plan, and remote-versus-local command flags
before applying guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/binding-and-sql.md](references/binding-and-sql.md) | Binding conversions, prepared statements, result modes, `exec()`, SQLite extensions, PRAGMAs |
| [references/read-replication.md](references/read-replication.md) | Sessions, bookmarks, consistency, replication controls, replica placement, metadata, billing |
| [references/migrations-and-local-development.md](references/migrations-and-local-development.md) | Nested migration discovery, Pages bindings, local persistence, remote/local command safety |
| [references/backup-restore-and-transfer.md](references/backup-restore-and-transfer.md) | Alpha dumps, Time Travel, restore undo, SQLite imports, exports, long-term retention |
| [references/placement-jurisdictions-and-limits.md](references/placement-jurisdictions-and-limits.md) | Primary placement, location hints, jurisdictions, storage limits |
| [references/operations-and-debugging.md](references/operations-and-debugging.md) | HTTP API permissions, retries, result diagnostics, error handling and remediation |

## Breaking behavior and removed paths

### Require D1 write permission for HTTP API writes

Tokens that write through the D1 HTTP API must explicitly include `D1:Edit`.
`D1:Read` combined with an edit permission for another product does not grant D1
write access.

### Do not plan around alpha backup commands

`wrangler d1 backup` cannot create or access backups for alpha databases. An
alpha backup created before that access was removed may still be used to migrate
data into a new generally available database.

The binding’s `dump()` API is separate and works only for alpha-generation
databases. Confirm generation with:

```sh
wrangler d1 info <DATABASE_NAME>
```

### Treat Time Travel restore as destructive

A restore overwrites the database in place and cancels in-flight queries and
transactions. Capture the returned pre-restore bookmark so the operation can be
undone while that bookmark remains inside the retention window.

```sh
wrangler d1 time-travel restore app-db --timestamp=1785133133
wrangler d1 time-travel restore app-db --bookmark=<PREVIOUS_BOOKMARK>
```

### Choose jurisdictions only at creation

The `eu` and `fedramp` jurisdiction constraints cannot be added or changed after
database creation. If both a jurisdiction and a location hint are supplied, the
jurisdiction wins and the hint is ignored.

## Binding and SQL quick reference

### Bind only supported JavaScript values

- Booleans are stored as SQLite integers and read back as `0` or `1`.
- `ArrayBuffer` values and views become BLOBs and read back as arrays.
- `undefined` raises `D1_TYPE_ERROR`.
- `BigInt` is unsupported. Binding integer round trips are safe only through
  `Number.MAX_SAFE_INTEGER`, although D1 stores signed 64-bit integers.

### Use positional placeholders

D1 accepts anonymous `?` and ordered `?NNN` parameters, not named parameters.
Ordered placeholders select the corresponding argument passed to `bind()`.

```ts
const stmt = env.DB
  .prepare("SELECT * FROM jobs WHERE state = ?2 AND id = ?1")
  .bind(42, "ready");
```

### Choose the result mode deliberately

- `run<T>()` is an alias for `all<T>()`.
- `raw({ columnNames: true })` returns arrays with a leading column-name array
  and omits metadata.
- `first()` does not add `LIMIT 1`; put the limit in SQL when it matters.
- `first(columnName)` returns a scalar or `null` for no rows and raises
  `D1_ERROR` if the requested column is absent.

### Reserve `exec()` for unbound one-shot work

`exec()` accepts unbound SQL statements separated by newlines and returns
`{ count, duration }`. A failure reports query and error details, stops before
later statements, and does not make the sequence a general transaction API.

### Optimize after schema changes

D1 accepts `PRAGMA optimize`; run it after schema work such as creating an
index.

```sql
PRAGMA optimize;
```

## Read replication quick reference

Use Sessions to group a logical application’s queries under sequential
consistency. `withSession()` and `withSession("first-unconstrained")` allow the
first query to run on either the primary or a replica. Use `"first-primary"`
when the first query must see the latest primary version.

```ts
const bookmark = request.headers.get("x-d1-bookmark")
  ?? "first-unconstrained";
const session = env.DB.withSession(bookmark);
const result = await session.prepare(
  "SELECT * FROM Customers WHERE CompanyName = 'Bs Beverages'",
).run();
response.headers.set("x-d1-bookmark", session.getBookmark() ?? "");
```

Carry the bookmark forward when consistency must span sessions. Sessions exist
only on the Workers binding, remain usable if replication is disabled, and are
not exposed by the REST API.

## Migration and local-development quick reference

For nested ORM migration layouts, set both `migrations_dir` and a
`migrations_pattern` that is relative to the Wrangler config and begins with
that directory.

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

`*` matches one path segment and `**` matches any number. Without the setting,
the pattern is `${migrations_dir}/*.sql`. `wrangler d1 migrations create`
still creates top-level files, so use the ORM generator for a nested-only
pattern.

Pages local development cannot connect to remote D1. Put a Wrangler config at
the project root, set `preview_database_id` to the binding name, and use
`--local` for local execute and migration commands. Without `--local`, those
commands target the remote database.

## Backup and transfer quick reference

Production-backend databases have always-on Time Travel. History retention is
30 days on Workers Paid and 7 days on Workers Free. Confirm support by checking
for `version: production` in `wrangler d1 info`.

D1 cannot directly import a raw `.sqlite3` file. Dump it to SQL, remove
`BEGIN TRANSACTION`, `COMMIT`, and any `CREATE TABLE _cf_KV` statement, then
execute the SQL file against D1. An import file is limited to 5 GiB.

```sh
sqlite3 db.sqlite3 .dump > db.sql
npx wrangler d1 execute app-db --remote --file=db.sql
```

An export blocks other database requests. Any virtual table, including FTS5,
prevents export until removed; recreate it after exporting.

## Operational checks

- D1 automatically retries qualifying read-only queries up to two times and
  reports `total_attempts`; application retry policy is still needed for other
  business-level idempotent work.
- Inspect `served_by_region`, `served_by_primary`, and
  `timings.sql_duration_ms` for remote execution placement and SQL time.
- During local `wrangler dev`, serving-region metadata is `undefined`.
- Current D1 errors carry diagnostics in `Error.message`; Wrangler versions
  before 3.1.1 may instead use `cause.message`.
- Separate transient connectivity and reset failures from capacity, storage,
  memory, CPU, and queue failures before deciding to retry.

Read the topic reference before changing production data, consistency routing,
placement, or restore behavior; the quick reference intentionally omits edge
conditions.
