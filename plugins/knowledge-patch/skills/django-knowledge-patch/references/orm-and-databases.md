# ORM and Databases

Batch attribution: `5.1`, `5.2-guide`, `5.2`, `6.0-guide`, `6.0`.

## Contents

- [Composite primary keys](#composite-primary-keys)
- [Migrations, constraints, and system checks](#migrations-constraints-and-system-checks)
- [Expressions, aggregates, and window frames](#expressions-aggregates-and-window-frames)
- [Query and save behavior](#query-and-save-behavior)
- [Database configuration and backend-specific features](#database-configuration-and-backend-specific-features)
- [PostgreSQL features](#postgresql-features)
- [Third-party backend and ORM extension contracts](#third-party-backend-and-orm-extension-contracts)

## Composite primary keys

### Declare and query a composite key

Define a virtual `pk` with component field names in tuple order (since `5.2-guide`):

```python
class OrderLineItem(models.Model):
    pk = models.CompositePrimaryKey("product_id", "order_id")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

item = OrderLineItem.objects.get(pk=(1, "A755H"))
item.pk = (2, "B991Q")
```

The instance primary key is a tuple. Assignment and lookup map tuple elements to component fields
in declaration order.

### Respect schema and relation limits

Django cannot create a migration that:

- Converts an existing model to or from a composite primary key.
- Adds or removes the composite primary key from an existing model.
- Adds or removes a component field of an existing composite primary key.

Perform the database-specific schema operation separately, then synchronize Django's migration
state with `--fake` or `SeparateDatabaseAndState`.

Foreign keys, generic relations, and the Django admin do not support composite-key models. The
internal `ForeignObject` workaround creates no columns, database constraint, or index, and its
`on_delete` setting has no effect; do not treat it as a full relational mapping.

### Handle forms, validation, expressions, and introspection

- The virtual `pk` is omitted from `ModelForm`s.
- `clean_fields(exclude={"pk"})` does not exclude the component fields.
- `validate_unique(exclude={"pk"})` does skip the composite uniqueness check.
- Most database functions that accept one source expression raise `ValueError` for composite
  `pk`; `Count("pk")` is explicitly supported.
- Custom expressions must opt into composite values with `allows_composite_expressions=True`.
- Inspect `model._meta.pk_fields` in reusable code. The component fields' own `primary_key`
  attributes remain false.

### Use expanded query support

`QuerySet.raw()` supports composite-key models (since `6.0`). A subquery returning a composite
key can feed lookups such as `__exact` as well as `__in`.

## Migrations, constraints, and system checks

### Categorize custom migration operations

Set `Operation.category` on a custom migration operation (since `5.1`). `makemigrations` uses the
category to display an informative symbol for the operation.

### Alter constraint state without database work

`AlterConstraint` updates migration/model state without dropping and recreating the database
constraint (since `5.2-guide`). `makemigrations` uses it for state-only changes such as a new
`violation_error_message`. Verify both migration state and the unchanged physical constraint.

Explicit `UniqueConstraint.violation_error_code` and `violation_error_message` values are honored
for unconditional, field-based constraints (since `5.2`).

### Re-squash and serialize migrations

A squashed migration can itself be squashed before it becomes a normal migration (since `6.0`).
Migration serialization also supports `zoneinfo.ZoneInfo` and keyword names on deconstructible
objects that are not valid Python identifiers.

### Apply new checks

- Constraints implement a registered `check()` method (since `6.0`).
- A multi-column `ForeignObject` with multiple `from_fields` triggers a system-check error if it
  is used in an index, constraint, or `unique_together`.
- PostgreSQL fields, indexes, and constraints check that `django.contrib.postgres` is installed.

## Expressions, aggregates, and window frames

### Window frames

`RowRange` accepts a positive `start` and a negative `end` (since `5.1`). Both `RowRange` and
`ValueRange` accept `exclusion` to omit rows, peer groups, or ties from the frame.

### Constraint validation

A custom expression can set `Expression.constraint_validation_compatible` (since `5.1`). Set it
accurately when the expression should be ignored during constraint validation.

Constraints can validate expressions involving `GeneratedField` (since `5.2`).

### JSON and set-returning expressions

- Use `JSONArray` to build a JSON array from field names or arbitrary expressions (since `5.2`).
- Set `Expression.set_returning=True` for a PostgreSQL set-returning function so query planning
  handles the expression correctly.
- SQLite `JSONField` lookups support negative array indexes (since `6.0`).

### Aggregate ordering

`Aggregate` accepts `order_by` when the aggregate class sets `allow_order_by=True` (since `6.0`).
This replaces the PostgreSQL-only `OrderableAggMixin` design.

`StringAgg` is available from `django.db.models` and works across supported databases (since
`6.0-guide`). Its `delimiter` is an expression; wrap a literal with `Value()`:

```python
from django.db.models import StringAgg, Value

StringAgg("chapter", delimiter=Value(","), order_by="chapter")
```

`AnyValue` returns an arbitrary non-null input on SQLite, MySQL, Oracle, and PostgreSQL 16+ (since
`6.0`). Use it where grouping rules permit a representative value rather than a deterministic one.

## Query and save behavior

### Ordering and projection

- `QuerySet.order_by()` can order by annotation transforms such as a `JSONObject` key or an
  `ArrayAgg` index (since `5.1`).
- `values()` and `values_list()` emit `SELECT` columns in the exact caller-specified expression
  order (since `5.2`). This makes operations such as `union()` predictable.
- A single-argument built-in aggregate raises `TypeError` when called with the wrong number of
  arguments.

### Generated and expression-assigned fields after save

After `save()`, `GeneratedField` values and fields assigned database expressions expose their
database-computed values immediately on SQLite, PostgreSQL, and Oracle through `RETURNING` (since
`6.0-guide`). MySQL and MariaDB mark the fields deferred; the first attribute access performs the
refresh transparently.

### Save failures and extension safety

- A forced update that affects no rows raises the model-specific `Model.NotUpdated`, not
  `DatabaseError` (since `6.0`).
- `Field.pre_save()` may execute more than once in one save operation. Make custom implementations
  idempotent and free of side effects.
- User-manager creation methods and synchronous and async `QuerySet` create, bulk-create,
  get-or-create, and update-or-create methods set `alters_data=True` (since `5.2`). Template
  resolution therefore refuses to invoke them.

## Database configuration and backend-specific features

### SQLite

- `DATABASES[alias]["OPTIONS"]` accepts `init_command` for connection-time pragmas and
  `transaction_mode` for transaction selection (since `5.1`).
- `CharField.max_length` can be omitted because SQLite supports unlimited `VARCHAR` (since `5.2`).
- Negative `JSONField` array indexes are supported (since `6.0`).

### MySQL and MariaDB

- MySQL connections default to `utf8mb4` rather than `utf8`/`utf8mb3` (since `5.2`). For a legacy
  database, request `utf8mb3` explicitly in database `OPTIONS`.
- MySQL gains the `coveredby` and `covers` spatial lookups in `5.2`; see
  [gis.md](gis.md) for later MariaDB spatial support.

### Oracle

Enable Oracle connection pooling by setting `"pool"` in the database `OPTIONS` mapping (since
`5.2`).

### PostgreSQL explain options

- PostgreSQL 16+ accepts `generic_plan` in `QuerySet.explain()` (since `5.1`).
- PostgreSQL 17+ accepts `memory` and `serialize` (since `5.2`).

## PostgreSQL features

### B-tree deduplication

`django.contrib.postgres.indexes.BTreeIndex` accepts `deduplicate_items` (since `5.1`):

```python
from django.contrib.postgres.indexes import BTreeIndex

index = BTreeIndex(fields=["status"], deduplicate_items=True)
```

This maps a model index definition to PostgreSQL's B-tree deduplication option.

### Full-text search lexemes

`Lexeme` creates escaped full-text search terms (since `6.0`). Combine them with `&`, `|`, and
`~`, and use their prefix-matching and weighting support rather than manually interpolating search
syntax.

### Routed extension operations

PostgreSQL extension migration operations accept `hints` (since `6.0`). Supply them when database
routers need context to decide where an extension operation may run.

## Third-party backend and ORM extension contracts

### Decimal adaptation

`BaseDatabaseOperations.adapt_decimalfield_value()` is a no-op returning its input unchanged
(since `5.2`). A custom backend must not rely on the base implementation to adapt decimals.

### Returning APIs

Schema editors no longer append `CASCADE` when dropping a column (since `6.0`). Update custom
backend assumptions about dependent objects.

The backend operations API renames:

- `return_insert_columns()` to `returning_columns()`.
- `fetch_returned_insert_rows()` to `fetch_returned_rows()`.

`fetch_returned_rows()` receives `cursor` and `returning_params`. The old
`fetch_returned_insert_columns()` hook is removed. A backend that can return rows from `UPDATE`
can set `can_return_rows_from_update=True`.

`BaseDatabaseOperations.field_cast_sql()` is removed. The `serialize` parameter of
`BaseDatabaseCreation.create_test_db()` is deprecated; implement or call
`serialize_db_to_string()` instead.

### SQL parameter sequence type

Custom lookup and expression implementations must return parameters as a tuple from `as_sql()`,
`process_lhs()`, and `process_rhs()` (since `6.0`). Normalize older list-like results through
unpacking so the code remains interoperable:

```python
params = (*lhs_params, *rhs_params)
return sql, params
```
