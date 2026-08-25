# SQL, Schema, and Optimizer

Use this reference when generating DDL, validating SQL during an upgrade,
parsing EXPLAIN output, or relying on optimizer and collation behavior.

## DDL and schema requirements

### Treat UNIQUE NOT NULL as a primary-key equivalent

For both `CREATE` and `ALTER`, a `UNIQUE NOT NULL` key counts as a primary-key
equivalent. It satisfies `sql_require_primary_key=ON` and prevents an extra
generated invisible primary key when
`sql_generate_invisible_primary_key=ON`.

```sql
CREATE TABLE events (
  event_id BIGINT NOT NULL UNIQUE,
  payload JSON
);
```

### Expect INPLACE for empty-table column changes

For an empty InnoDB table, `ALTER TABLE ... ADD COLUMN` and `DROP COLUMN`
select `INPLACE`, not `INSTANT`, by default. This avoids incrementing the row
version. Request an algorithm explicitly only when the migration requires it.

## Upgrade-sensitive SQL syntax

### Quote BINLOG labels

`BINLOG` can no longer be an unquoted label in a stored program. Quote or
rename such labels before upgrading.

### Update keyword handling

In 9.7.2, `CUBE`, `EXTERNAL`, `QUALIFY`, and `TABLESAMPLE` are reserved
keywords; quote or rename existing identifier uses. `MANUAL` and `PARALLEL`
are recognized as non-reserved keywords.

### Validate binary-protocol temporal values

Invalid temporal values received through the binary protocol are rejected even
in non-strict SQL mode instead of being silently adjusted. Validate or sanitize
bound values in clients that previously relied on adjustment.

## Expressions and query behavior

### Apply the revised IFNULL collation rules

The `NONE` collation derivation is weaker than every other derivation, so the
other operand controls comparison collation in expressions such as
`IFNULL(...) LIKE ...` rather than raising
`ER_CANT_AGGREGATE_2COLLATIONS`. Collation aggregation considers only
collations tied at the highest strength, and the former `IGNORABLE` derivation
is named `NULL`.

### Use expanded quantified-subquery transformations

With `subquery_to_derived` enabled, derived-table transformations cover `>`,
`>=`, `<`, and `<=` with either `ANY` or `ALL`, in addition to `=ANY` and
`<>ALL`. They can apply in both `SELECT` and `WHERE`.

### Use GROUPING without ROLLUP

`GROUPING()` is permitted in queries that do not use `ROLLUP`.

### Preserve spatial reference data in GeoJSON

Implicit geometry-to-JSON conversion adds a `crs` attribute so spatial
reference information survives in JSON Duality Views. `ST_AsGeoJSON()` options
2 and 4 always include a CRS URN.

## Optimizer and EXPLAIN

### Opt into the Hypergraph Optimizer

The Hypergraph Optimizer is available in Community Edition. It can be selected
at session, global, persisted, startup, or per-statement scope.

```sql
SET optimizer_switch='hypergraph_optimizer=on';
```

### Expect the new default EXPLAIN formats

`explain_format` defaults to `TREE`, and `explain_json_format_version` defaults
to version `2`.

With `explain_json_format_version=2`, JSON output identifies schema `2.0`,
keeps only query attributes at the top level, and adds `lookup_references` for
index lookups. Version 1 output is unchanged. Update parsers before changing
the server default or preserve version 1 explicitly during migration.
