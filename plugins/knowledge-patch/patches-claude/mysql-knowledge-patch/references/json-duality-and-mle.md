# JSON Duality Views and MLE

Use this reference for relational-to-JSON mappings, DML through Duality Views,
or stored JavaScript and WebAssembly libraries.

## JSON Duality Views

### Define and inspect views

`CREATE JSON DUALITY VIEW` and `ALTER JSON DUALITY VIEW` expose relational data
as JSON documents. `DROP VIEW` and `SHOW CREATE VIEW` also work with these
views. Selected documents carry `_metadata.etag`.

Inspect mappings through these Information Schema tables:

- `JSON_DUALITY_VIEWS`
- `JSON_DUALITY_VIEW_TABLES`
- `JSON_DUALITY_VIEW_COLUMNS`
- `JSON_DUALITY_VIEW_LINKS`

### Control DML per table

A view definition can grant `INSERT`, `UPDATE`, or `DELETE` per table, or use
`NO INSERT`, `NO UPDATE`, and `NO DELETE` to prohibit individual operations.
Runtime DML is checked against those tags.

Community Server permits `INSERT`, `UPDATE`, and `DELETE` through JSON Duality
Views. DML also supports auto-increment columns, including automatic
primary-key value generation.

### Preserve coordinate reference systems

Implicit geometry-to-JSON conversion adds a `crs` attribute. This keeps
spatial-reference information in Duality View documents. `ST_AsGeoJSON()`
options 2 and 4 always include a CRS URN.

## Stored JavaScript SQL types

### Map ENUM, SET, DECIMAL, and BIT deliberately

Stored JavaScript supports `ENUM` and `SET` arguments and full
`DECIMAL`/`NUMERIC` input, output, bind, and return paths. Decimal values are
JavaScript strings by default; `decimalType=NUMBER` requests numbers and should
only be used when JavaScript precision is sufficient.

Stored JavaScript routines also accept MySQL `BIT` values.

### Understand locale lifetime

The JavaScript `Intl` API uses MySQL locale names with underscores converted to
dashes. A routine keeps the locale from its first invocation in a session until
the locale is reset.

## Database and transaction APIs

JavaScript routines can:

- call stored functions and procedures through `Schema.getFunction()` and
  `Schema.getProcedure()`;
- create `OUT` and `INOUT` arguments with `mysql.arg()`;
- access user variables as `session` properties;
- start, commit, and roll back transactions;
- control autocommit and savepoints and handle `SqlError`;
- call `rand()`, `sleep()`, `uuid()`, and `isUUID()` wrappers for the
  corresponding built-ins.

## Reusable libraries

### Create and evolve JavaScript libraries

`CREATE LIBRARY`, `DROP LIBRARY`, `SHOW CREATE LIBRARY`, and routine `USING`
clauses provide reusable MLE libraries. Later additions include
`ALTER LIBRARY`, `SHOW LIBRARY STATUS`, comments,
`ALTER PROCEDURE/FUNCTION ... USING`, and dynamic imports.

```javascript
let module = await import(`/db1/lib_${object_type}`)
return module.default.print()
```

### Import WebAssembly safely

MLE libraries can contain hexadecimal or base64-encoded WebAssembly through
`CREATE LIBRARY ... LANGUAGE WASM` and be imported from a routine's `USING`
clause.

```sql
CREATE LIBRARY math_wasm
  LANGUAGE WASM
  AS '0061736d...';
```

WebAssembly libraries cannot use MySQL-specific APIs or WASI system, clock, or
I/O services.

## Runtime and memory

MLE JavaScript supports ECMAScript 2025. For on-premises deployments,
`mle.memory_max` defaults to 5% of physical memory, bounded to the range from
0.4 GB through 32 GB. Set an explicit value when automatic memory sizing does
not fit the workload.
