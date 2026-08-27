# Migrations and Local Development

## Nested migration discovery

Set `migrations_pattern` on a D1 binding when migrations are nested, such as
Drizzle’s `migrations/0001_init/migration.sql` layout.

The pattern:

- is relative to the Wrangler configuration file;
- requires `migrations_dir`;
- must start with that migration directory;
- defaults to `${migrations_dir}/*.sql` when omitted.

```jsonc
{
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "my-database",
      "database_id": "<UUID>",
      "migrations_dir": "migrations",
      "migrations_pattern": "migrations/*/migration.sql"
    }
  ]
}
```

`*` matches one path segment; `**` matches any number of path segments.

Applied migration names are recorded relative to `migrations_dir`.
`wrangler d1 migrations create` continues to create top-level files. If the
configured pattern matches nested files only, use the ORM’s migration generator
instead of Wrangler’s create command.

Coverage attribution: `2026-migrations-pattern`.

## Pages local D1 configuration

Pages local development cannot connect to a remote D1 database. Add a Wrangler
configuration at the project root and set `preview_database_id` to the binding
name:

```jsonc
{
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "my-database",
      "database_id": "<UUID>",
      "preview_database_id": "DB"
    }
  ]
}
```

Pass `--local` to D1 execute and migration commands when operating on the local
database. Without `--local`, those commands target the remote database.

## Persistent local state

Wrangler v3 persists local D1 data between `wrangler dev` runs by default. Use
`--persist-to` to choose the storage location:

```sh
wrangler dev --persist-to=/path/to/file
```

Wrangler 2.x instead requires `--persist` to retain data.
