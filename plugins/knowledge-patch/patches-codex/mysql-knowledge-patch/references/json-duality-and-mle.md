# JSON Duality Views and MLE

## JSON Duality View definition and inspection

### View DDL and metadata (9.4-9.6)

`CREATE JSON DUALITY VIEW` and `ALTER JSON DUALITY VIEW` expose relational data
as JSON documents. `DROP VIEW` and `SHOW CREATE VIEW` apply to them. Selected
documents contain `_metadata.etag`.

Inspect mappings through these Information Schema tables:

- `JSON_DUALITY_VIEWS`
- `JSON_DUALITY_VIEW_TABLES`
- `JSON_DUALITY_VIEW_COLUMNS`
- `JSON_DUALITY_VIEW_LINKS`

Implicit geometry-to-JSON conversion preserves spatial reference information in
a `crs` member, and `ST_AsGeoJSON()` options `2` and `4` always emit a CRS URN.

## Duality View DML

### Per-table permissions (9.4-9.6)

A view definition can allow `INSERT`, `UPDATE`, or `DELETE` per mapped table, or
deny operations with `NO INSERT`, `NO UPDATE`, and `NO DELETE`. Runtime DML is
checked against those tags.

### Community DML and generated keys (9.7.0)

Community Server supports `INSERT`, `UPDATE`, and `DELETE` through JSON Duality
Views. Auto-increment columns are supported, including automatic primary-key
value generation.

## Stored JavaScript types and localization

### SQL types, decimals, and locale lifetime (9.2-9.3)

Stored JavaScript routines accept `ENUM` and `SET`, and support full
`DECIMAL`/`NUMERIC` input, output, binding, and return paths. Decimal values are
JavaScript strings by default; use `decimalType=NUMBER` only when loss of decimal
precision is acceptable.

The `Intl` API maps MySQL locale underscores to dashes. A routine retains the
locale from its first invocation in a session until the locale is reset.

### `BIT`, language level, and memory (9.4-9.6)

Stored JavaScript accepts MySQL `BIT` and supports ECMAScript 2025. On premises,
`mle.memory_max` defaults to 5% of physical memory, bounded to the range 0.4 GB
through 32 GB.

## Database and transaction APIs

### Routine calls and session state (9.2-9.3)

Use `Schema.getFunction()` and `Schema.getProcedure()` to call stored functions
and procedures. Use `mysql.arg()` for `OUT` and `INOUT` parameters. User variables
are available as properties on `session`.

The transaction API supports start, commit, rollback, autocommit, and savepoints,
and exposes `SqlError`. The `rand()`, `sleep()`, `uuid()`, and `isUUID()` APIs
provide the corresponding server operations.

## Reusable libraries

### JavaScript libraries and dynamic imports (9.2-9.3)

`CREATE LIBRARY`, `DROP LIBRARY`, `SHOW CREATE LIBRARY`, and routine `USING`
clauses provide reusable libraries. Additions include `ALTER LIBRARY`, `SHOW
LIBRARY STATUS`, comments, `ALTER PROCEDURE/FUNCTION ... USING`, and dynamic
imports:

```javascript
let module = await import(`/db1/lib_${object_type}`)
return module.default.print()
```

### WebAssembly libraries (9.4-9.6)

Create a hexadecimal- or base64-encoded module with `CREATE LIBRARY ... LANGUAGE
WASM`, then import it through a routine's `USING` clause. WebAssembly libraries
cannot call MySQL-specific APIs or WASI system, clock, or I/O services.
