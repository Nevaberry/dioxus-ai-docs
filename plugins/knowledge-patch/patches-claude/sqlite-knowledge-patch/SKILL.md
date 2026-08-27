---
name: sqlite-knowledge-patch
description: SQLite
version: "3.53.0"
license: MIT
metadata:
  author: Nevaberry
---


# SQLite Knowledge Patch

Use this skill for SQLite SQL, C API, CLI, build, storage, FTS5, session,
JSON, and JSONB work where current compatibility details affect the answer.
Load only the reference files relevant to the task, and preserve the stated
conditions and limits when applying their guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [C APIs and configuration](references/c-api-and-configuration.md) | Prepare flags, connection controls, limits, locks, status, hooks, changegroups |
| [CLI, builds, and utilities](references/cli-build-and-utilities.md) | Configure systems, Tcl, shell behavior, `sqlite3_rsync`, output, platforms |
| [Core scalar functions](references/core-scalar-functions.md) | `iif()`, formatting, string and numeric functions, planner hints |
| [FTS5, sessions, and extensions](references/fts5-sessions-and-extensions.md) | Tokenizers, contentless tables, auxiliary APIs, sessions, changegroups |
| [JSON and JSONB](references/json-and-jsonb.md) | Operators, validation, traversal, mutation, JSON5, edge cases |
| [SQL language and schema](references/sql-language-and-schema.md) | Schema changes, triggers, expression indexes, dates, defaults, `VACUUM` |
| [Storage, locking, and correctness](references/storage-locking-and-correctness.md) | Withdrawn release, VFS compatibility, database pages, maintenance fixes |

## Highest-risk compatibility changes

### Do not target the withdrawn release

SQLite 3.52.0 was withdrawn because new features caused backward-
compatibility issues. Its planned features moved to 3.53.0. Do not target
3.52.0.

### Use the corrected maintenance releases

- On the 3.51 line, use 3.51.3 or later because that release fixes a
  WAL-reset database-corruption bug.
- Use 3.50.1 or later for `sqlite3_rsync`; 3.50.0 can omit the replica's final
  page.
- Account for the query-result and memory-safety corrections listed in
  [Storage, locking, and correctness](references/storage-locking-and-correctness.md).

### Preserve OPFS SAHPool compatibility direction

The corrected filename digest creates a one-way compatibility boundary:
3.50.0 can read databases made by older SAHPool VFS versions, but older
SAHPool VFS versions cannot read databases created by 3.50.0 or later.

### Update `.indexes` consumers

The `.indexes PATTERN` argument matches index names rather than indexed-table
names. Existing shell scripts can therefore return different results.

### Account for changed output and formatting

- Floating-point-to-text conversion defaults to 17 significant digits rather
  than 15. `SQLITE_DBCONFIG_FP_DIGITS` changes it per connection.
- Interactive CLI sessions default to Unicode box output and right-justify
  numbers in tabular modes; batch sessions keep the legacy format.
- Built-in `printf()` and SQL `format()` suppress a negative-zero sign for a
  `#` format without `+` when every displayed digit is zero.

### Respect new type and limit behavior

- Generated columns in `STRICT` tables enforce their declared types.
- `SQLITE_LIMIT_LENGTH` cannot be set below 30.
- The SQL-function argument limit is 1000 rather than 127.

## Schema and SQL quick reference

### Change constraints directly

`ALTER TABLE` can add and remove `NOT NULL` and `CHECK` constraints.

### Repair expression indexes

Use the expression-index repair command when stored expression-index values
are stale:

```sql
REINDEX EXPRESSIONS;
```

SQLite also self-heals stale expression indexes.

### Use expression-based trigger messages

The message argument to a trigger's `RAISE()` may be any SQL expression, so
it can include values from the affected row:

```sql
SELECT RAISE(ABORT, 'negative total for order ' || NEW.id);
```

### Optimize all tables when requested

`PRAGMA optimize` uses a temporary analysis limit and automatically
re-analyzes tables without `sqlite_stat1` entries. Include option bit
`0x10000` when every table should be checked for possible updates.

### Choose ambiguous date shifts

Use `ceiling` or `floor` after a month or year shift to select how an
ambiguous date is resolved:

```sql
SELECT date('2024-02-29', '+1 year', 'floor');
```

## JSON and JSONB quick reference

### Insert array elements

Use `json_array_insert()` for JSON and `jsonb_array_insert()` for JSONB.

### Preserve JSONB during traversal

`jsonb_each()` and `jsonb_tree()` parallel the text traversal functions while
keeping array and object rows as JSONB in the `value` column.

### Count backward in arrays

A negative integer on the right of `->>` selects an array element from the
end:

```sql
SELECT '["first","middle","last"]' ->> -1;
```

### Treat numeric-looking text keys as labels

For `->` and `->>`, a text right operand that looks numeric remains an object
label rather than becoming an integer array index:

```sql
SELECT '{"0":"zero"}' -> '0';
```

### Choose validation depth deliberately

For two-argument `json_valid()`, flag `6` accepts JSON5 text or plausible
JSONB using a superficial check; flag `8` performs a linear-time deep JSONB
check. Read [JSON and JSONB](references/json-and-jsonb.md) for all modes and
malformed-input behavior.

## C API and configuration quick reference

### Prepare without log noise

Use `SQLITE_PREPARE_DONT_LOG` with `sqlite3_prepare_v3()` when test-compiling
SQL so ill-formed input does not send warnings to SQLite's error log.

### Prepare schema-derived SQL

Virtual-table implementations can pass `SQLITE_PREPARE_FROM_DDL` to
`sqlite3_prepare_v3()` for schema-derived SQL.

### Separate lock timeouts

On builds that support blocking locks, `sqlite3_setlk_timeout()` sets the
blocking-lock timeout independently of `sqlite3_busy_timeout()`.

### Control newly submitted comments

Disabling `SQLITE_DBCONFIG_ENABLE_COMMENTS` blocks comments only in newly
submitted SQL. Comments already stored in `sqlite_schema` remain readable.

## CLI and build quick reference

### Run scripts and one-shot controls

A non-empty `.sql` or `.txt` command-line argument is executed as a script.
Use `.timer once` for only the next SQL statement and `.progress --timeout S`
to interrupt statements after `S` seconds.

### Replace the removed Windows console option

`SQLITE_USE_STDIO_FOR_CONSOLE` is removed. Windows command-line-tool builds
can define `SQLITE_USE_W32_FOR_CONSOLE_IO` to use Win32 console APIs without
affecting the SQLite core.

### Enable bundled extensions explicitly

The amalgamation contains `carray` and `percentile`, but they remain disabled
unless built with `SQLITE_ENABLE_CARRAY` or `SQLITE_ENABLE_PERCENTILE`.

## Apply details without extrapolation

When a task touches a listed edge case, use the exact semantics from its
reference. Keep version-specific fixes, build conditions, default states,
directional compatibility, experimental status, and `may`/`should`/`must`
wording intact. If the references state only that behavior changed, do not
invent a cause or replacement.
