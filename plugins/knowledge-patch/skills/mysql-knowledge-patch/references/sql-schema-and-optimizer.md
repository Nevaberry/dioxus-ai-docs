# SQL, Schema, and Optimizer

Use this reference for generated keys, `ALTER TABLE`, stored-program syntax,
collation resolution, subquery rewrites, EXPLAIN parsing, temporal values,
grouping, and optimizer selection.

## Keys and DDL

### `UNIQUE NOT NULL` is a primary-key equivalent

For `CREATE` and `ALTER` in batch 9.7.0, a `UNIQUE NOT NULL` key counts as a
primary-key equivalent. It prevents an extra generated invisible primary key
when `sql_generate_invisible_primary_key=ON` and satisfies
`sql_require_primary_key=ON`.

```sql
CREATE TABLE events (
  event_id BIGINT NOT NULL UNIQUE,
  payload JSON
);
```

### Empty-table column changes prefer INPLACE

For an empty InnoDB table in batch 9.2-9.3, `ALTER TABLE ... ADD COLUMN` and
`DROP COLUMN` choose `INPLACE` rather than `INSTANT` by default. This avoids
incrementing the row version. Specify an algorithm only when the deployment
requires a particular execution path.

### `BINLOG` is no longer an unquoted label

`BINLOG` cannot be used as an unquoted label in a stored program in batch
9.2-9.3. Quote or rename affected labels before upgrade:

```sql
label_loop: LOOP
  LEAVE label_loop;
END LOOP;
```

## Expression and query semantics

### `IFNULL()` collation resolution

In batch 9.4-9.6, the `NONE` collation derivation is weaker than every other
derivation. The other operand therefore determines comparison collation in
expressions such as `IFNULL(...) LIKE ...`, instead of raising
`ER_CANT_AGGREGATE_2COLLATIONS`.

Collation aggregation considers only collations tied at the highest strength,
and the former `IGNORABLE` derivation is renamed `NULL`.

### More quantified subqueries become derived tables

With `subquery_to_derived` enabled in batch 9.2-9.3, derived-table
transformations cover:

- `>`, `>=`, `<`, and `<=` with `ANY`;
- the same operators with `ALL`;
- the existing `=ANY`; and
- the existing `<>ALL`.

The transformation can apply in both `SELECT` and `WHERE`.

### `GROUPING()` no longer requires `ROLLUP`

`GROUPING()` is permitted in queries without `ROLLUP` in batch 9.4-9.6. SQL
generators do not need to add a synthetic rollup merely to call the function.

### Binary-protocol temporal values are validated

Invalid temporal values received through the binary protocol are rejected even
in non-strict SQL mode in batch 9.4-9.6. A client can no longer depend on silent
adjustment simply because the session is non-strict.

## EXPLAIN output contracts

### JSON format version 2

With `explain_json_format_version=2`, JSON EXPLAIN in batch 9.2-9.3:

- identifies schema `2.0`;
- leaves only query attributes at the top level; and
- adds `lookup_references` for index lookups.

Version 1 output remains unchanged. In batch 9.4-9.6, `explain_format` defaults
to `TREE` and `explain_json_format_version` defaults to version `2`. Pin formats
in machine consumers and update JSON decoders before accepting the defaults.

## Hypergraph Optimizer

The Hypergraph Optimizer is available in Community Edition in batch 9.7.0. It
can be selected at session, global, persisted, startup, or per-statement scope.
For a session:

```sql
SET optimizer_switch='hypergraph_optimizer=on';
```

Measure plan and execution changes at the same scope at which the optimizer will
be enabled. Option Tracker distinguishes usage of both optimizer types.
