# SQL Language and Schema

## Statistics and optimization

### Bounded and all-table `PRAGMA optimize` (since 3.46.0)

`PRAGMA optimize` applies a temporary analysis limit so optimization does not
run excessively long on large databases. It automatically re-analyzes tables
without `sqlite_stat1` entries. Include option bit `0x10000` when every table
should be checked for possible updates.

```sql
PRAGMA optimize;
```

## Date and time edge cases (since 3.46.0)

`strftime()` supports `%G`, `%g`, `%U`, and `%V`. The `ceiling` and `floor`
modifiers select how ambiguous month or year shifts are resolved. `utc` and
`localtime` are no-ops when SQLite already knows the value is in the requested
time basis.

```sql
SELECT strftime('%G-W%V', '2024-01-01'),
       date('2024-02-29', '+1 year', 'floor');
```

## Column defaults and generated columns

### Large hexadecimal defaults (since 3.46.0)

Large hexadecimal numeric literals are accepted as table-column default
values.

```sql
CREATE TABLE flags(value INTEGER DEFAULT 0xFFFFFFFFFFFFFFFF);
```

### `STRICT` generated columns (since 3.51.0)

Generated columns in `STRICT` tables enforce their declared types.

```sql
CREATE TABLE measurements(
  raw TEXT,
  value INTEGER GENERATED ALWAYS AS (raw) STORED
) STRICT;
INSERT INTO measurements(raw) VALUES('not an integer'); -- datatype error
```

## Triggers

### Expression-based `RAISE()` messages (since 3.47.0)

The message argument to a trigger's `RAISE()` may be any SQL expression. It
can therefore include values from the affected row rather than requiring a
string literal.

```sql
CREATE TABLE orders(id INTEGER, total REAL);
CREATE TRIGGER check_total BEFORE INSERT ON orders
WHEN NEW.total < 0 BEGIN
  SELECT RAISE(ABORT, 'negative total for order ' || NEW.id);
END;
```

### TEMP triggers and `main` (since 3.53.0)

The body of a TEMP trigger may query and modify tables in the main schema.

## Constraint-changing `ALTER TABLE` (since 3.53.0)

`ALTER TABLE` can add and remove `NOT NULL` and `CHECK` constraints, allowing
schema migrations to make those changes directly.

## Expression-index repair and self-healing (since 3.53.0)

`REINDEX EXPRESSIONS` rebuilds expression indexes to repair stale stored
values. SQLite also self-heals stale expression indexes.

```sql
REINDEX EXPRESSIONS;
```

## Reserve bytes in `VACUUM INTO` (since 3.53.0)

When the target is a URI filename, its `reserve=N` parameter sets the
generated database's reserve amount. `N` must be from 0 through 255.

```sql
VACUUM INTO 'file:copy.db?reserve=32';
```
