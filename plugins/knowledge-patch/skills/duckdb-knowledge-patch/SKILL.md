---
name: duckdb-knowledge-patch
description: DuckDB
version: 1.5.0
license: MIT
metadata:
  author: Nevaberry
---

# DuckDB Knowledge Patch

Use this skill when writing DuckDB SQL, upgrading an existing database,
working with external files or lakehouse formats, configuring the CLI, or
using spatial data. Inspect the project's DuckDB version and load the relevant
topic reference before relying on defaults, return types, parser behavior,
storage compatibility, or extension behavior.

## How to apply this skill

1. Determine the exact DuckDB library, CLI, and extension versions in use.
2. Review the compatibility checks below before changing existing SQL or files.
3. Treat database storage versions separately from the engine version.
4. Check extension and platform requirements before generating deployment steps.
5. Load the topic reference that matches the task; it contains the complete
   semantics and directional caveats behind the quick reference.
6. Prefer project manifests, code, tests, and observed behavior if the project
   is newer than the frontmatter version.

## Reference index

| Reference | Topics |
|---|---|
| [Compatibility and migrations](references/compatibility-and-migrations.md) | Release-line support, changed SQL behavior, parser changes, deprecations, upgrade checks |
| [SQL and types](references/sql-and-types.md) | `VARIANT`, maps, `date_trunc`, `UNPACK`, secrets, direct database scans |
| [Storage, security, and remote files](references/storage-security-and-remote-files.md) | Storage versions, encryption, compression, external cache, CSV, Azure, `httpfs` |
| [Lakehouses and connectors](references/lakehouses-and-connectors.md) | DuckLake, Delta, Iceberg, ODBC, Teradata, database-wide copies |
| [CLI and platforms](references/cli-and-platforms.md) | Previous results, safe mode, direct file opening, installation, Linux requirements |
| [Spatial and geometry](references/spatial-and-geometry.md) | Axis-order migration, core `GEOMETRY`, CRS typing, WKB boundaries |

## Compatibility checks first

### Account for changed SQL results and types

- `date_trunc` on a `DATE` returns `TIMESTAMP`. Add an explicit cast when an
  application, schema, or client contract still requires `DATE`.
- `map['key']` returns the value itself and is equivalent to
  `map_extract_value`. Use `map_extract` only when the required result is a
  single-element list.
- `current_time` and `current_date` use the local timezone and require ICU.
- A fixed random seed does not reproduce sequences from engines that used the
  earlier generator state.
- Nested-structure serialization escapes quotes so values round-trip. Use
  `array_to_string` when code deliberately needs the old unquoted display.

```sql
SELECT typeof(date_trunc('month', DATE '2026-03-27')); -- TIMESTAMP
SELECT map(['k'], ['v'])['k'];                         -- 'v'
SELECT map_extract(map(['k'], ['v']), 'k');           -- ['v']
```

### Migrate deprecated lambda syntax

Prefer Python-style lambdas:

```sql
SELECT list_transform([1, 2, 3], lambda x: x + 1);
```

The single-arrow form `x -> x + 1` warns in 1.5. Use `lambda_syntax` only as
a deliberate migration control:

```sql
SET lambda_syntax = 'ENABLE_SINGLE_ARROW';
SET lambda_syntax = 'DISABLE_SINGLE_ARROW';
```

The arrow form is scheduled to be disabled by default in 2.0. Do not introduce
new uses merely because the compatibility setting can suppress the warning.

### Make spatial axis order explicit

Distance, perimeter, area, within, and `ST_Transform` operations are migrating
from legacy latitude/longitude coordinates to conventional x/y ordering. Set
the behavior instead of accepting an unset-value warning:

```sql
SET geometry_always_xy = true;  -- x = longitude, y = latitude
```

Use `false` only to pin legacy x-as-latitude behavior during migration. The
unset state is scheduled to become an error in 2.0, and `true` is scheduled to
become the default in 2.1.

### Audit parser and identifier assumptions

- `AT` and `LAMBDA` are reserved identifiers and must be quoted when used as
  names.
- `GRANT` is no longer reserved.
- RFC 4180-style strict CSV parsing is on by default. Opt out per irregular
  input with `strict_mode = false`; do not disable it globally by habit.

### Check runtime and release-line support

- DuckDB 1.5 is a non-LTS release line scheduled to reach end of life on
  2026-09-01.
- DuckDB 1.4 is an LTS line supported through September 2026.
- Beginning with 1.4, every other release line is LTS and receives one year of
  community support.
- Official Linux binaries from 1.3 require glibc 2.28 or newer. Extensions are
  no longer published for `linux_amd64_gcc4`; older systems must build from
  source.

## High-value SQL and type features

### Store heterogeneous values with `VARIANT`

`VARIANT` stores a typed binary value per row rather than JSON text. Cast
scalars, lists, and structs explicitly, inspect their type, and extract fields:

```sql
CREATE TABLE events (id INTEGER, data VARIANT);
INSERT INTO events VALUES
  (1, {'name': 'Alice', 'age': 30}::VARIANT);

SELECT variant_typeof(data), variant_extract(data, 'name')
FROM events;
```

Dot notation is also available for nested access. DuckDB reads Parquet
`VARIANT` columns, including shredded data. DuckLake and Delta support the type;
Iceberg support begins in 1.5.1.

### Query database files without attaching them

Use `read_duckdb` when the task is a direct scan rather than a persistent
catalog attachment. It accepts glob patterns:

```sql
SELECT min(i), max(i)
FROM read_duckdb('numbers*.db');
```

### Expand transformed column sets

`UNPACK` expands a computed `COLUMNS(*)` expression after operations such as a
cast, which the older leading `*COLUMNS(...)` form cannot do:

```sql
SELECT [UNPACK(COLUMNS(*)::VARCHAR)] AS values
FROM tbl;
```

### Keep credentials out of literal SQL

Fields in `CREATE SECRET` accept scalar expressions. Read a value from an
environment variable or another expression instead of embedding it in SQL that
may be logged:

```sql
CREATE SECRET http (
    TYPE http,
    BEARER_TOKEN getenv('MY_SECRET')
);
```

## Storage and security decisions

### Choose file compatibility deliberately

New storage features do not automatically change the file format. Opt in by
attaching with `STORAGE_VERSION`; that version becomes the oldest engine that
can open the file:

```sql
ATTACH 'modern.db' (STORAGE_VERSION 'v1.2.0');
SELECT database_name, tags FROM duckdb_databases();
```

To make an older-compatible copy, attach the destination with its required
storage version and copy from the source database to that destination.

### Encrypt all database-managed files

`ENCRYPTION_KEY` on `ATTACH` encrypts the database, WAL, and temporary files.
AES-256-GCM is the default. Loading `httpfs` selects the hardware-accelerated
OpenSSL implementation instead of the built-in implementation:

```sql
LOAD httpfs;
ATTACH 'encrypted.db' AS enc_db (ENCRYPTION_KEY 'quack_quack');
```

### Understand remote caching and HTTP behavior

Remote file data is cached automatically within the global memory limit.
Inspect it with `duckdb_external_file_cache()` or disable it for one connection:

```sql
FROM duckdb_external_file_cache();
SET enable_external_file_cache = false;
```

The default `httpfs` backend uses curl. OpenSSL and settings such as
`http_timeout` and `http_retries` remain available. Once curl-backed `httpfs`
is loaded, later extension installations use HTTPS through it; downloading
`httpfs` itself still uses `httplib`.

## CLI essentials

Reuse the previous query result as table `_` instead of rerunning work:

```sql
FROM ducks WHERE extinct_year IS NOT NULL;
FROM _;
```

For untrusted or constrained interactive work, start with `-safe` or enter
`.safe_mode`; safe mode blocks host-file-system interaction except for the
database initially opened.

Passing a Parquet, CSV, or JSON file in the database-path position creates a
temporary in-memory database with a `file` view and another view named after
the file stem:

```sh
duckdb region.parquet -c 'FROM region;'
```

Load the CLI reference before choosing a package or installer, especially on
musl Linux, older glibc systems, or Windows.

## Integration direction matters

- `COPY` writes to Azure Blob Storage through `az://` and ADLSv2 through
  `abfss://`.
- Copying an entire Iceberg database into DuckDB or DuckLake works directly.
  When copying in the other direction, create destination schemas first.
- Iceberg `CREATE TABLE ... WITH (...)` accepts table properties, with
  `format-version` and `location` promoted to dedicated fields.
- Load the lakehouse reference for DuckLake specification behavior, Delta
  write guarantees, Iceberg catalog headers, ODBC connection objects, and the
  Teradata connector.

For edge semantics, upgrade planning, storage compatibility, or connector
configuration, read the full topic reference rather than relying only on this
quick reference.
