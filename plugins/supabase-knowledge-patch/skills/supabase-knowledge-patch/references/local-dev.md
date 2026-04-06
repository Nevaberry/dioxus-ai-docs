# Local Development

## Declarative Database Schemas

Manage database schemas declaratively instead of writing imperative migrations. Put SQL files in `supabase/schemas/` defining the desired state, then generate migrations automatically.

```sql
-- supabase/schemas/employees.sql
create table "employees" (
  "id" integer not null,
  "name" text,
  "age" smallint not null
);

create view "profiles" as
select
  id,
  name
from
  "employees";
```

Generate a migration by diffing current migrations against declared schema:

```bash
supabase db diff -f create_employees_table
```

Control schema file ordering via `config.toml` (default: lexicographic):

```toml
[db.migrations]
schema_paths = ["./schemas/employees.sql", "./schemas/*.sql"]
```

Glob patterns are evaluated, deduplicated, and sorted lexicographically. Append new columns to the end of tables to avoid messy diffs with views and enums.

Rollback to a specific migration version during development:

```bash
supabase db reset --version 20241005112233
```

Known limitations (uses `migra` diff tool): DML not captured, view ownership/grants not tracked, `alter policy` not tracked, materialized views not supported, comments/partitions not tracked.

## Storage Bucket Seeding

Define storage buckets declaratively in `config.toml` and seed files from a local directory:

```toml
[storage.buckets.images]
public = false
file_size_limit = "50MiB"
allowed_mime_types = ["image/png", "image/jpeg"]
objects_path = "./images"
```

Upload files from `supabase/images` to the `images` bucket:

```bash
supabase seed buckets
```

## Seed File Splitting

Split seed data across multiple files with `[db.seed]` config:

```toml
[db.seed]
enabled = true
sql_paths = ['./seeds/*.sql']
```

Files are processed in declaration order. Glob matches are sorted lexicographically. Base folder is `supabase/` (so `./seeds/*.sql` matches `supabase/seeds/*.sql`). Duplicate matches are deduplicated.

## Local Backup Restoration

Restore a downloaded backup to your local Supabase instance:

```bash
supabase init
echo '15.6.1.115' >supabase/.temp/postgres-version
supabase db start --from-backup db_cluster.backup
```

Set the Postgres version to match the backup's image version (shown in dashboard). Earliest supported version: `15.1.0.55`. After restoration, connect via `psql 'postgresql://postgres:postgres@localhost:54322/postgres'`.
