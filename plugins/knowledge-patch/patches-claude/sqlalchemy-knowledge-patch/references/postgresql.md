# PostgreSQL

## asyncpg isolation inheritance

When SQLAlchemy has no client isolation level configured, the asyncpg wrapper
passes `None` to the driver. The server-level isolation setting then applies
instead of SQLAlchemy forcing `READ COMMITTED`. Configure an explicit client
level only when the application intends to override the server.

## JSONB subscript rendering and expression indexes

On PostgreSQL 14 and later, JSONB subscripts render with square brackets:

```sql
data['key']
```

JSON expressions still use arrow syntax. PostgreSQL requires a textual match
between a query expression and an expression index, so indexes made with the
older JSONB arrow text are not selected for newly rendered expressions.

During an upgrade, identify every affected JSONB expression index, drop it,
and recreate it with the new expression text. Inspect SQL generation and query
plans before and after the migration. This behavior is from 2.0.51.

## Constraint options

`UniqueConstraint` and `PrimaryKeyConstraint` accept
`postgresql_include`:

```python
UniqueConstraint("email", postgresql_include=["id"])
```

Foreign-key `ON DELETE SET NULL` and `ON DELETE SET DEFAULT` actions also
support column lists. Preserve the requested column list when expressing
either action in schema metadata.

## Typed empty arrays

For an empty PostgreSQL array literal, supply `type_`:

```python
array([], type_=Integer)
```

This renders the cast required by PostgreSQL, such as
`ARRAY[]::INTEGER`.

## Richer reflection

Reflected PostgreSQL types retain non-default collations. Reflected index
dictionaries expose non-default operator classes in
`dialect_options["postgresql_ops"]`, keyed by column name. Preserve these
values when comparing, copying, or regenerating reflected schema objects.
