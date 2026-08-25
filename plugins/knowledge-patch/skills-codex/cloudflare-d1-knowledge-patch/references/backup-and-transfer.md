# Backup, recovery, and transfer

## Alpha backup and dump boundaries

Since 2025-07-01, `wrangler d1 backup` cannot create or access backups for
alpha databases. Alpha backups created before that date can still be used to
migrate data into a new generally available D1 database.

The Workers binding `dump()` has a different boundary: it works only for
databases created during D1's alpha period. Check the database generation with
`wrangler d1 info <DATABASE_NAME>`. For a supported database, `dump()` returns
an SQLite-compatible file as an `ArrayBuffer`:

```ts
const dump = await env.DB.dump();
return new Response(dump, {
  headers: { "Content-Type": "application/octet-stream" },
});
```

## Time Travel support

Production-backend databases have Time Travel enabled automatically. Restore
history is retained for 30 days on Workers Paid and 7 days on Workers Free.
Use `version: production` from `wrangler d1 info` to confirm support.

A Unix-seconds or RFC3339 timestamp maps deterministically to a bookmark:

```sh
wrangler d1 time-travel info app-db \
  --timestamp="2026-07-27T11:18:53.000+03:00"
```

## Restore and undo

A Time Travel restore overwrites the database in place and cancels in-flight
queries and transactions:

```sh
wrangler d1 time-travel restore app-db --timestamp=1785133133
wrangler d1 time-travel restore app-db --bookmark=<PREVIOUS_BOOKMARK>
```

The restore command returns the pre-restore bookmark. Preserve it to undo the
restore. Restoring does not remove older bookmarks; each remains usable while
it is still inside the retention window.

Time Travel cannot clone or fork a database. For history beyond the retention
window, export D1 to R2 through the REST API and Cloudflare Workflows.

## Importing SQLite data

D1 cannot import a raw `.sqlite3` file. Convert it to SQL:

```sh
sqlite3 db.sqlite3 .dump > db.sql
npx wrangler d1 execute app-db --remote --file=db.sql
```

Before execution, remove `BEGIN TRANSACTION`, `COMMIT`, and any
`CREATE TABLE _cf_KV` statement from the dump. Each import file is limited to
5 GiB.

## Export behavior

`d1 export` can export the entire database or one table. `--no-data` creates
schema-only output, while `--no-schema` creates data-only output:

```sh
npx wrangler d1 export app-db --remote --output=database.sql
npx wrangler d1 export app-db --remote --table=users --no-data \
  --output=users-schema.sql
```

An export blocks other database requests while it runs. Any virtual table,
including an FTS5 table, prevents export. Remove the virtual table first and
recreate it after the export.
