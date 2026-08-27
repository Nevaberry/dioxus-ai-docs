# Migrations and local development

## Nested migration layouts

The `2026-migrations-pattern` update added `migrations_pattern` to a D1
binding. It lets `wrangler d1 migrations apply` discover layouts such as
`migrations/0001_init/migration.sql`:

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

The glob:

- is relative to the Wrangler configuration file;
- requires `migrations_dir` and must start with that directory;
- defaults to `${migrations_dir}/*.sql` when omitted;
- uses `*` for one path segment and `**` for any number of segments.

Applied migration names are stored relative to `migrations_dir`.
`wrangler d1 migrations create` still creates only top-level files. If the
pattern accepts nested files only, use the ORM's generator to create them.

## Pages local bindings

Pages local development cannot connect to a remote D1 database. Add Wrangler
configuration at the project root and make `preview_database_id` match the
binding name:

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

Pass `--local` to D1 execute and migration commands for local state. Without
`--local`, those commands target the remote database.

## Persistent local state

Wrangler v3 persists local D1 data between `wrangler dev` runs by default.
Use `wrangler dev --persist-to=/path/to/file` to choose the persistence
location. Wrangler 2.x instead requires `--persist` to retain local data.
