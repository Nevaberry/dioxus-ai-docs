# Query API and SQL

## Binding conversions

D1 permanently converts values passed through the Workers binding:

| JavaScript input | Stored/read behavior |
| --- | --- |
| `boolean` | Stored as a SQLite integer and read as `0` or `1` |
| `ArrayBuffer` or a view | Stored as a BLOB and read as an array |
| `undefined` | Rejected with `D1_TYPE_ERROR` |
| `BigInt` | Unsupported |

D1 internally stores signed 64-bit integers, but binding round trips through
JavaScript numbers are safe only up to `Number.MAX_SAFE_INTEGER`.

## Prepared statements and parameters

D1 supports only SQLite anonymous `?` and ordered `?NNN` parameters. Named
parameters are unsupported. `?NNN` selects the corresponding argument to
`bind()`, so query order can differ from binding order:

```ts
const stmt = env.DB
  .prepare("SELECT * FROM jobs WHERE state = ?2 AND id = ?1")
  .bind(42, "ready");
```

Result modes differ:

- `run<T>()` is an alias for `all<T>()`.
- `raw({ columnNames: true })` omits metadata and prepends a column-name array
  to the returned row arrays.
- `first(columnName)` returns one scalar, `null` when there are no rows, and
  throws `D1_ERROR` if that column is absent.
- `first()` does not rewrite the query with `LIMIT 1`.

`D1Result.results` is an empty array for a query with no rows and `null` when
results do not apply.

## Multi-statement execution

`exec()` accepts unbound SQL statements separated by `\n` and returns
`{ count, duration }`:

```ts
const result = await env.DB.exec(
  "CREATE TABLE audit (id INTEGER PRIMARY KEY);\nCREATE INDEX audit_id ON audit(id);",
);
```

When a statement fails, `exec()` throws query and error details, stops, and
does not execute later statements. It is best suited to maintenance and
one-shot tasks.

## Supported SQL extensions

D1 explicitly provides:

- FTS5 full-text search, including `fts5vocab`
- JSON functions and operators
- SQLite math functions

Other SQLite extensions are not implied merely by SQLite compatibility.

## PRAGMA behavior

D1 supports a selected PRAGMA set, with effects scoped to the current
transaction.

Introspection and integrity PRAGMAs are:

- `table_list`, `table_info`, and `table_xinfo`
- `index_list`, `index_info`, and `index_xinfo`
- `quick_check`
- `foreign_key_check` and `foreign_key_list`

Behavior controls are:

- `case_sensitive_like`
- `ignore_check_constraints`
- `legacy_alter_table`
- `recursive_triggers`
- `reverse_unordered_selects`
- `foreign_keys`
- `defer_foreign_keys`

`PRAGMA defer_foreign_keys = on` postpones constraint checks until the
transaction ends. An unresolved violation still fails the transaction, and
`ON DELETE CASCADE` actions still run:

```sql
PRAGMA defer_foreign_keys = on;
-- Perform schema changes that temporarily violate constraints.
PRAGMA defer_foreign_keys = off;
```

The 2025 update also added `PRAGMA optimize`. Run it after schema changes such
as creating an index:

```sql
PRAGMA optimize;
```

## Automatic read-only retries

D1 automatically makes up to two retry attempts after retryable failures for
queries it classifies as read-only. The classifier currently covers statements
containing only `SELECT`, `EXPLAIN`, and `WITH`. The result metadata reports
the execution count as `total_attempts`.

Automatic retries are side-effect guarded: if an attempted retry modifies
data, D1 rolls it back. Applications remain responsible for deliberately
retrying other business-level idempotent queries.
