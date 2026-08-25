# PostgreSQL

## asyncpg server isolation inheritance

As of 2.0.51, when no client isolation level is configured, SQLAlchemy's
asyncpg wrapper passes `None` to the driver. The server-level isolation setting
then applies instead of SQLAlchemy forcing `READ COMMITTED`. Configure a client
isolation level explicitly only when the application intends to override the
server.

## JSONB subscripting and expression indexes

On PostgreSQL 14 and later with SQLAlchemy 2.0.51, JSONB subscripts render with
square brackets:

```sql
data['key']
```

JSON expressions continue to render with arrow syntax. PostgreSQL requires a
textual match when selecting an expression index, so an index created from the
older JSONB arrow text will not be used for the newly rendered expression.
Find, drop, and recreate every affected JSONB expression index during the
upgrade. Inspect generated SQL and query plans before and after migration.

## Constraint dialect options

In 2.0.51, `UniqueConstraint` and `PrimaryKeyConstraint` accept
`postgresql_include`:

```python
UniqueConstraint("email", postgresql_include=["id"])
```

Foreign keys also support a column list in `ON DELETE SET NULL (...)` and
`ON DELETE SET DEFAULT (...)` actions.

## Typed empty arrays

An empty PostgreSQL array literal can use `type_` in 2.0.51 to emit the cast
required by PostgreSQL:

```python
array([], type_=Integer)
```

This renders the equivalent of `ARRAY[]::INTEGER`.

## Richer reflection metadata

PostgreSQL reflection in 2.0.51 retains non-default type collations. Reflected
index dictionaries also expose non-default operator classes in
`dialect_options["postgresql_ops"]`, keyed by column name.
