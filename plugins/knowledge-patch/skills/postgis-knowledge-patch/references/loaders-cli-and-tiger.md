# Loaders, CLI, and Tiger Geocoder

Batch attribution: `3.5.0`, `3.6.0`, and `2025.1`.

## Database-wide `postgis` commands

The `postgis` script adds these discovery commands:

```text
postgis list-enabled
postgis list-all
```

Its existing operational commands now work across databases:

```text
postgis status
postgis upgrade
```

`status` reports across all databases. `upgrade` upgrades every database that
needs an extension update.

## Tiger extension packaging

`postgis_tiger_geocoder` 2025.1 is the first standalone release after the
geocoder split from the PostGIS source tree. It:

- Requires PostgreSQL 16 or later.
- Works with any supported PostGIS version.
- Loads the Census TIGER 2025 dataset.
- Starts a versioning scheme that follows the current Census TIGER dataset
  year.

PostGIS 3.6 is the last series that bundles the geocoder. PostGIS 3.7 omits it,
so install the standalone extension when moving beyond the bundled series.

## Upgrade the standalone extension

Use the ordinary extension update path first:

```sql
ALTER EXTENSION postgis_tiger_geocoder UPDATE;
```

If PostgreSQL reports that no path to 2025.1 exists, or the installed version
is a development build, bridge through the special `ANY` version:

```sql
ALTER EXTENSION postgis_tiger_geocoder UPDATE TO "ANY";
ALTER EXTENSION postgis_tiger_geocoder UPDATE;
```

## Search path, schemas, and indexes

- The standalone extension no longer adds `tiger` to the database search path.
  Set the path in the calling context or schema-qualify its objects.
- Loader-generated SQL quotes supplied schema and table identifiers.
- Shell loaders create the `tiger_data` schema.
- `missing_indexes_generate_script()` emits SP-GiST indexes for the geocoder's
  `LIKE` search helpers.
- On PostgreSQL 16 and newer, the 3.6 Tiger extension schema-qualifies
  dependent extensions through their extension schemas. Account for this when
  dependencies use non-default schemas.
- Tiger tables now use typmod geometry columns. Update tools that inspect
  legacy column constraints.

## Address and intersection input

`normalize_address()` now:

- Strips trailing country names.
- Escapes user address fragments before inserting them into regular
  expressions.
- Improves country-aware parsing while preserving ZIP+4 and country details.

State highways accept `SH` and compact forms such as `SH121`.
`geocode_intersection()` tolerates irregular highway spacing such as `I- 635`
and `I-635`.

## Build-time omission

Pass `--without-tiger` when building PostGIS without the bundled Tiger
geocoder.
