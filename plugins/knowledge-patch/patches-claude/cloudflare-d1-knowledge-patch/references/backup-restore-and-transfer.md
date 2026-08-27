# Backup, Restore, and Transfer

## Alpha database backup and dump paths

As of 2025-07-01, `wrangler d1 backup` can no longer create or access backups
for alpha databases. Alpha backups made before removal can still migrate data
into a new generally available D1 database.

The Workers binding’s `dump()` method is a separate, alpha-only facility. Check
database generation before calling it:

```sh
wrangler d1 info <DATABASE_NAME>
```

For a supported alpha database, `dump()` returns an SQLite-compatible file in
an `ArrayBuffer`:

```ts
const dump = await env.DB.dump();
return new Response(dump, {
  headers: { "Content-Type": "application/octet-stream" },
});
```

Coverage attribution: `2025`.

## Time Travel support and retention

Production-backend databases have Time Travel enabled automatically. Restore
history is retained for:

- 30 days on Workers Paid;
- 7 days on Workers Free.

Use `version: production` from `wrangler d1 info` to confirm that a database
supports Time Travel.

A Unix-seconds or RFC3339 timestamp maps deterministically to a bookmark:

```sh
wrangler d1 time-travel info app-db \
  --timestamp="2026-07-27T11:18:53.000+03:00"
```

## Restore and undo

A Time Travel restore overwrites the database in place and cancels in-flight
queries and transactions. The restore command returns the database’s
pre-restore bookmark. Save it for a possible undo:

```sh
wrangler d1 time-travel restore app-db --timestamp=1785133133
wrangler d1 time-travel restore app-db --bookmark=<PREVIOUS_BOOKMARK>
```

Restoring does not remove older bookmarks. Any bookmark still inside the
retention window remains usable.

Time Travel cannot clone or fork a database. For retention beyond its history
window, export D1 data to R2 through the REST API and Cloudflare Workflows.

## Importing an SQLite database

D1 does not import a raw `.sqlite3` file. Convert it to SQL first:

```sh
sqlite3 db.sqlite3 .dump > db.sql
npx wrangler d1 execute app-db --remote --file=db.sql
```

Before executing the dump, remove:

- `BEGIN TRANSACTION`;
- `COMMIT`;
- any `CREATE TABLE _cf_KV` statement.

Each import file is limited to 5 GiB.

## Selective exports and blocking behavior

`d1 export` can export a whole database or one table. Use `--no-data` for
schema-only output or `--no-schema` for data-only output.

```sh
npx wrangler d1 export app-db --remote --output=database.sql
npx wrangler d1 export app-db --remote --table=users --no-data \
  --output=users-schema.sql
```

An export blocks all other database requests while it runs. Any virtual table,
including an FTS5 table, prevents export. Remove the virtual table before the
export and recreate it afterward.
