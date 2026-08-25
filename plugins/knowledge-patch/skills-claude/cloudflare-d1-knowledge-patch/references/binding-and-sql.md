# Binding and SQL

## JavaScript value conversion

D1 permanently converts values passed through the Workers binding:

| Bound value | Stored/read behavior |
| --- | --- |
| Boolean | Stored as a SQLite integer and read as `0` or `1` |
| `ArrayBuffer` or a view | Stored as a BLOB and read as an array |
| `undefined` | Raises `D1_TYPE_ERROR` |
| `BigInt` | Unsupported |

Although D1 stores signed 64-bit integers internally, JavaScript integer round
trips through the binding are safe only through `Number.MAX_SAFE_INTEGER`.

## Prepared-statement placeholders

D1 currently supports only SQLite’s anonymous `?` and ordered `?NNN`
parameters. Named parameters are unsupported. `?NNN` selects the corresponding
argument passed to `bind()`, so query order may differ from binding order.

```ts
const stmt = env.DB
  .prepare("SELECT * FROM jobs WHERE state = ?2 AND id = ?1")
  .bind(42, "ready");
```

## Result modes

`run<T>()` is an alias of `all<T>()`.

`raw({ columnNames: true })` omits metadata and returns arrays with a column-name
array prepended:

```ts
const rows = await stmt.raw({ columnNames: true });
```

`first(columnName)` returns the first row’s named column as a scalar. It returns
`null` when there are no rows and raises `D1_ERROR` when that column is absent.
`first()` does not add `LIMIT 1` to the SQL, so add an explicit limit when the
database should stop after one row.

```ts
const id = await env.DB
  .prepare("SELECT id FROM jobs ORDER BY id LIMIT 1")
  .first("id");
```

For a statement that returns no rows, `D1Result.results` is an empty array. It
is `null` when results do not apply.

## Multi-statement `exec()`

`exec()` accepts unbound SQL statements separated by newline characters and
returns `{ count, duration }`.

```ts
const result = await env.DB.exec(
  "CREATE TABLE audit (id INTEGER PRIMARY KEY);\nCREATE INDEX audit_id ON audit(id);",
);
```

If one statement fails, D1 throws with query and error details and stops before
later statements. Because it provides no bindings and has stop-on-error
behavior, reserve it for maintenance and one-shot tasks.

## Supported SQLite extension subset

D1 explicitly provides:

- FTS5 full-text search, including `fts5vocab`
- JSON functions and operators
- SQLite math functions

Do not infer availability of another extension solely from general SQLite
compatibility.

## PRAGMA support

D1 accepts `PRAGMA optimize`; run it after a schema change such as creating an
index.

```sql
PRAGMA optimize;
```

Coverage attribution: `2025`.

D1 supports a selected PRAGMA set whose effects apply only to the current
transaction. The documented introspection and integrity PRAGMAs are:

- `table_list`, `table_info`, and `table_xinfo`
- `index_list`, `index_info`, and `index_xinfo`
- `quick_check`
- `foreign_key_check` and `foreign_key_list`

The documented behavior controls are:

- `case_sensitive_like`
- `ignore_check_constraints`
- `legacy_alter_table`
- `recursive_triggers`
- `reverse_unordered_selects`
- `foreign_keys`
- `defer_foreign_keys`

`PRAGMA defer_foreign_keys = on` postpones constraint checks until the
transaction ends; it does not disable them. Unresolved violations fail the
transaction, and `ON DELETE CASCADE` actions still run.

```sql
PRAGMA defer_foreign_keys = on;
-- Run schema changes that temporarily violate constraints.
PRAGMA defer_foreign_keys = off;
```
