# SQL Language and Schema

Use this reference for SQL semantics, schema migrations, defaults, triggers,
query behavior, and `STRICT` tables.

## Defaults and schema changes

### Large hexadecimal defaults (3.46.0)

Table-column defaults accept large hexadecimal numeric literals:

```sql
CREATE TABLE flags(value INTEGER DEFAULT 0xFFFFFFFFFFFFFFFF);
```

### Constraint-changing `ALTER TABLE` (3.53.0)

`ALTER TABLE` can add and remove `NOT NULL` and `CHECK` constraints directly.
Verify the precise grammar supported by the target SQLite before emitting a
migration, and exercise conversion and validation against existing rows.

## Trigger behavior

### Expression-based `RAISE()` messages (3.47.0)

The message argument to a trigger's `RAISE()` function may be any SQL
expression, so it can include values from the affected row:

```sql
CREATE TRIGGER check_total BEFORE INSERT ON orders
WHEN NEW.total < 0 BEGIN
  SELECT RAISE(ABORT, 'negative total for order ' || NEW.id);
END;
```

### TEMP trigger access to `main` (3.53.0)

The body of a TEMP trigger may query and modify objects in the main schema.

## Query and type correctness

### Generated-column types in `STRICT` tables (3.51.0)

Generated columns in a `STRICT` table enforce their declared type. A generated
value that cannot be converted is rejected:

```sql
CREATE TABLE measurements(
  raw TEXT,
  value INTEGER GENERATED ALWAYS AS (raw) STORED
) STRICT;

INSERT INTO measurements(raw) VALUES('not an integer'); -- datatype error
```

Test generated expressions when upgrading existing `STRICT` schemas.
