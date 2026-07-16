# SQL Language and Schema

## Changing constraints and triggers

- Since 3.53.0, `ALTER TABLE` can add or remove `NOT NULL` and `CHECK` constraints without a manual table rebuild. Verify the accepted grammar for named and unnamed constraints before generating migrations.
- The body of a TEMP trigger may query or modify objects in `main` (since 3.53.0), enabling connection-local trigger logic over the persistent database.
- A trigger's `RAISE()` message may be any SQL expression rather than only a string literal (since 3.47.0). Row values can therefore be included: `RAISE(ABORT, 'invalid order: ' || NEW.id)`.
- Syntax errors in `ALTER TABLE` consistently return public result code `SQLITE_ERROR`. Cases that returned internal-only `SQLITE_INTERNAL` were fixed in 3.46.1.

## Comments and attached databases

`SQLITE_DBCONFIG_ENABLE_ATTACH_CREATE`, `SQLITE_DBCONFIG_ENABLE_ATTACH_WRITE`, and `SQLITE_DBCONFIG_ENABLE_COMMENTS` were added in 3.49.0. All default to enabled. They independently control whether `ATTACH` may create a file, whether attached databases may be written, and whether newly submitted SQL may contain comments.

Disabling comments does not prevent SQLite from reading comments already stored in `sqlite_schema` (since 3.50.0). As of 3.50.3, comments are ignored correctly in every part of a `CREATE TRIGGER` statement.

## Literals and row constructors

- A single underscore may appear between digits in an SQL numeric literal and is ignored (since 3.46.0): `1_000_000` and `0xFFFF_FFFF` are valid.
- Large hexadecimal integer literals may be used as column defaults (since 3.46.0).
- Since 3.46.1, a `VALUES` clause is not capped by `SQLITE_LIMIT_COMPOUND_SELECT`. This also holds when double-quoted string literals cause values to resemble parameters.

## Generated columns and change observation

- Generated columns in a `STRICT` table have their declared type enforced (since 3.51.0). Reject a computed result when it cannot be converted to that type.
- Preupdate hooks correctly report a non-NULL default for a column added by `ALTER TABLE ADD COLUMN` (since 3.47.0); change-capture code sees the effective value.
- The session extension supports tables with generated columns (since 3.49.0). See [FTS5, sessions, and extensions](fts5-sessions-and-extensions.md).

## Aggregate and query results

- Windowed `group_concat()` returns an empty string when its input contains one or more empty strings (since 3.46.0).
- The ordinary aggregate form also returns an empty string, rather than `NULL`, when its only input is an empty string (since 3.47.0).
- Version 3.47.1 fixes wrong answers in certain `IN` queries caused by 3.47.0 optimizations.
- Version 3.50.2 fixes wrong answers for `RIGHT JOIN` queries involving transitive `IS` constraints.
- Version 3.50.3 fixes wrong answers caused by over-optimizing an `AND` expression.
- Versions 3.51.1 and 3.51.2 correct wrong results and related faults in the new `EXISTS`-to-join optimization.

## Floating-point text

SQLite converts floating-point values to text using 17 significant digits by default as of 3.53.0, up from 15. Use `SQLITE_DBCONFIG_FP_DIGITS` to select a different digit count when stable legacy presentation matters.

Version 3.47.2 fixes text-to-floating-point conversion on x64/i386 for affected values whose first 16 significant digits are `1844674407370955`; that regression began in 3.47.0.
