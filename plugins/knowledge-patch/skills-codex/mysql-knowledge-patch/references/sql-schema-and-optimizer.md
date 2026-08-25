# SQL, Schema, and Optimizer

## Keys and DDL algorithms

### Primary-key equivalents (9.7.0)

For both `CREATE` and `ALTER`, a `UNIQUE NOT NULL` key is a primary-key
equivalent. It satisfies `sql_require_primary_key=ON` and prevents creation of an
extra generated invisible primary key when
`sql_generate_invisible_primary_key=ON`.

```sql
CREATE TABLE events (
  event_id BIGINT NOT NULL UNIQUE,
  payload JSON
);
```

### Empty InnoDB tables (9.2-9.3)

On an empty InnoDB table, `ALTER TABLE ... ADD COLUMN` and `DROP COLUMN` choose
`INPLACE`, rather than `INSTANT`, by default. This avoids incrementing the row
version. Request an algorithm explicitly when automation requires one.

## Parser and expression compatibility

### Stored-program labels (9.2-9.3)

`BINLOG` cannot be an unquoted label in a stored program. Quote or rename affected
labels before upgrading.

### `IFNULL()` collation resolution (9.4-9.6)

The `NONE` derivation is weaker than every other collation derivation, so the
other operand determines comparison collation in expressions such as
`IFNULL(...) LIKE ...` instead of raising `ER_CANT_AGGREGATE_2COLLATIONS`.
Aggregation considers only collations tied at the highest strength, and the old
`IGNORABLE` derivation is named `NULL`.

### Temporal values over the binary protocol (9.4-9.6)

Invalid temporal values sent through the binary protocol are rejected even when
SQL mode is non-strict; they are no longer silently adjusted.

### `GROUPING()` use (9.4-9.6)

`GROUPING()` is valid in queries that do not use `ROLLUP`.

### Keyword changes (9.7.2)

`CUBE`, `EXTERNAL`, `QUALIFY`, and `TABLESAMPLE` are reserved keywords. Quote or
rename identifiers using them. `MANUAL` and `PARALLEL` are recognized as
non-reserved keywords.

## Subqueries and optimizer selection

### Quantified comparisons (9.2-9.3)

With `subquery_to_derived` enabled, derived-table transformation covers `>`,
`>=`, `<`, and `<=` combined with `ANY` or `ALL`, in addition to `=ANY` and
`<>ALL`. It can apply in both `SELECT` and `WHERE`.

### Hypergraph Optimizer (9.7.0)

The Hypergraph Optimizer is available in Community Edition. Select it at session,
global, persisted, startup, or per-statement scope. For example:

```sql
SET optimizer_switch='hypergraph_optimizer=on';
```

## EXPLAIN contracts

### JSON format version 2 (9.2-9.3)

When `explain_json_format_version=2`, JSON EXPLAIN identifies schema `2.0`, keeps
only query attributes at the top level, and adds `lookup_references` for index
lookups. Version 1 output is unchanged.

### New default formats (9.4-9.6)

`explain_format` defaults to `TREE`, and `explain_json_format_version` defaults to
`2`. Update parsers and snapshot tests that assumed traditional or JSON v1
output.

## Spatial JSON output

### CRS preservation (9.4-9.6)

Implicit geometry-to-JSON conversion adds a `crs` member so spatial-reference
information survives in JSON Duality Views. `ST_AsGeoJSON()` options `2` and `4`
always include a CRS URN.

## Foreign-key execution

### SQL-layer enforcement (9.4-9.6)

Foreign-key constraints and cascades run in the SQL layer, making their changes
fully visible in the binary log and replication. Use the startup option
`innodb_native_foreign_keys` to retain InnoDB-native handling.
