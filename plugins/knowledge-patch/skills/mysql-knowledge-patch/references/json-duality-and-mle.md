# JSON Duality Views and MLE

Use this reference for relational-to-JSON mappings, DML through Duality Views,
stored JavaScript routines, database APIs, reusable libraries, localization, and
WebAssembly.

## JSON Duality View definition and metadata

Batch 9.4-9.6 adds:

```sql
CREATE JSON DUALITY VIEW ...
ALTER JSON DUALITY VIEW ...
```

`DROP VIEW` and `SHOW CREATE VIEW` also apply to JSON Duality Views. Documents
selected from a view contain `_metadata.etag`.

Inspect mappings through these Information Schema tables:

- `JSON_DUALITY_VIEWS`;
- `JSON_DUALITY_VIEW_TABLES`;
- `JSON_DUALITY_VIEW_COLUMNS`; and
- `JSON_DUALITY_VIEW_LINKS`.

### Per-table DML tags

A view definition can allow `INSERT`, `UPDATE`, or `DELETE` per table, or deny
operations with `NO INSERT`, `NO UPDATE`, and `NO DELETE`. Runtime DML is checked
against the tags.

In batch 9.7.0, Community Server permits `INSERT`, `UPDATE`, and `DELETE`
through JSON Duality Views. DML also supports auto-increment columns, including
automatic generation of primary-key values.

### Preserve spatial reference information

Implicit geometry-to-JSON conversion adds a `crs` attribute in batch 9.4-9.6,
so spatial-reference information survives in JSON Duality Views.
`ST_AsGeoJSON()` options 2 and 4 now always include a CRS URN.

## Stored JavaScript SQL types

In batch 9.2-9.3, stored JavaScript programs add:

- `ENUM` and `SET` arguments;
- complete `DECIMAL` and `NUMERIC` input, output, bind, and return support.

Decimals become JavaScript strings by default. Use `decimalType=NUMBER` only
when conversion to a JavaScript number and its precision tradeoff are intended.

Batch 9.4-9.6 adds the MySQL `BIT` type and brings the runtime to ECMAScript
2025.

## Localization

The JavaScript `Intl` API uses MySQL locale names with underscores converted to
dashes. A routine retains the locale from its first invocation in a session
until the locale is reset. Reset or isolate sessions when locale-sensitive code
must change behavior between calls.

## Database and transaction APIs

JavaScript routines in batch 9.2-9.3 can:

- obtain stored functions with `Schema.getFunction()`;
- obtain stored procedures with `Schema.getProcedure()`;
- pass `OUT` and `INOUT` values through `mysql.arg()`; and
- access user variables as `session` properties.

The transaction API provides start, commit, rollback, autocommit, savepoints,
and `SqlError`. The runtime also exposes `rand()`, `sleep()`, `uuid()`, and
`isUUID()` for the corresponding built-ins.

## Reusable JavaScript libraries

The initial library DDL in batch 9.2-9.3 includes:

- `CREATE LIBRARY`;
- `DROP LIBRARY`;
- `SHOW CREATE LIBRARY`; and
- routine `USING` clauses.

MySQL 9.3 adds `ALTER LIBRARY`, `SHOW LIBRARY STATUS`, library comments,
`ALTER PROCEDURE/FUNCTION ... USING`, and dynamic imports:

```javascript
let module = await import(`/db1/lib_${object_type}`)
return module.default.print()
```

## WebAssembly libraries

In batch 9.4-9.6, an MLE library can contain hexadecimal or base64-encoded
WebAssembly:

```sql
CREATE LIBRARY example_wasm
  LANGUAGE WASM
  AS '0061736d...';
```

Import it through a routine's `USING` clause. WebAssembly libraries cannot use:

- MySQL-specific APIs;
- WASI system calls;
- WASI clock calls; or
- WASI I/O calls.

## Runtime memory

On-premises `mle.memory_max` defaults to 5% of physical memory in batch
9.4-9.6, bounded to at least 0.4 GB and at most 32 GB. Include that automatic
allocation when planning server memory.
