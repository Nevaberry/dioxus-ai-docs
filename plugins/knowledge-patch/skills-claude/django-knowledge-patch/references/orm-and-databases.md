# ORM and Databases

Load this reference for models, queries, expressions, migrations, backend settings,
or third-party database extension points.

## Model composite primary keys

### Declare and address the key (`5.2-guide`)

Define a virtual `pk` with ordered component names. Instance primary keys are
tuples; assignment and lookup values follow declaration order.

```python
class OrderLineItem(models.Model):
    pk = models.CompositePrimaryKey("product_id", "order_id")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

item = OrderLineItem.objects.get(pk=(1, "A755H"))
```

The virtual `pk` is omitted from `ModelForm`. `clean_fields(exclude={"pk"})`
does not exclude component fields, while `validate_unique(exclude={"pk"})` skips
the composite uniqueness check. Inspect `_meta.pk_fields` because component
fields' `primary_key` attributes remain false.

Most database functions that require one expression raise `ValueError` for a
composite `pk`. `Count("pk")` is explicitly supported.

### Plan schema and relations separately (`5.2-guide`)

Django migrations cannot convert a model to or from a composite primary key or add
or remove its component fields. Perform the backend-specific schema change, then
synchronize state with `--fake` or `SeparateDatabaseAndState`.

Foreign keys, generic relations, and the admin do not support composite-key models.
The internal `ForeignObject` workaround creates no columns, constraint, or index
and ignores `on_delete`.

### Use expanded query support (`6.0`)

`QuerySet.raw()` supports composite-key models. A subquery returning a composite
key can target `__exact` and other suitable lookups, not only `__in`.

## Configure backend behavior

### Connection and model options

- `DEFAULT_AUTO_FIELD` and `AppConfig.default_auto_field` now default to
  `django.db.models.BigAutoField` in framework behavior, not only in generated
  project and app templates. Projects already selecting `BigAutoField` can remove
  that boilerplate. (`6.0-guide`)
- SQLite `OPTIONS` accepts `init_command` for connection-time pragmas and
  `transaction_mode` for transaction behavior. (`5.1`)
- MySQL connections default to `utf8mb4`; legacy databases can request
  `utf8mb3` in `OPTIONS`. Oracle pooling is enabled with an `OPTIONS["pool"]`
  setting. (`5.2`)
- `CharField.max_length` is optional on SQLite because its `VARCHAR` is
  unlimited. (`5.2`)
- `BTreeIndex(deduplicate_items=...)` exposes PostgreSQL B-tree index
  deduplication. (`5.1`)

```python
from django.contrib.postgres.indexes import BTreeIndex

index = BTreeIndex(fields=["status"], deduplicate_items=True)
```

### Explain PostgreSQL queries

`QuerySet.explain()` accepts `generic_plan` on PostgreSQL 16+ (`5.1`) and
`memory` and `serialize` on PostgreSQL 17 (`5.2`).

## Build queries and expressions

### Preserve projection and transformed ordering

`values()` and `values_list()` produce `SELECT` columns in call-site order,
which makes combinations such as `union()` predictable. (`5.2`)

`order_by()` accepts transforms on annotations, including `JSONObject` keys and
`ArrayAgg` indexes. (`5.1`)

### Define window frames (`5.1`)

`RowRange` accepts a positive `start` and negative `end`. Both `RowRange`
and `ValueRange` accept `exclusion` to omit rows, groups, or ties from the frame.

### Construct and aggregate values

- `JSONArray` creates a JSON array from field names or expressions. (`5.2`)
- `StringAgg` is available from `django.db.models` on every supported backend.
  Its `delimiter` is an expression, so wrap literal text in `Value()`.
  (`6.0-guide`)

```python
from django.db.models import StringAgg, Value

StringAgg("chapter", delimiter=Value(","))
```

- `Aggregate` accepts `order_by` only for classes declaring
  `allow_order_by=True`. PostgreSQL's `OrderableAggMixin` is deprecated.
  (`6.0`)
- `AnyValue` returns an arbitrary non-null value on SQLite, MySQL, Oracle, and
  PostgreSQL 16+. (`6.0`)
- SQLite `JSONField` queries support negative array indexes. (`6.0`)
- Django 6.1 adds UUID4 and UUID7 database functions, deterministic-queryset
  detection, and cross-database bitwise aggregates. (`6.1`)

### Extend expressions safely

- Set `Expression.constraint_validation_compatible` when an expression must be
  ignored during constraint validation. (`5.1`)
- `GeneratedField` expressions participate in model-constraint validation.
  (`5.2`)
- Set `set_returning` on PostgreSQL set-returning expressions and
  `allows_composite_expressions` on expressions accepting composite values.
  (`5.2`)
- Custom lookup and expression `as_sql()`, `process_lhs()`, and
  `process_rhs()` methods must return parameters as tuples. Tuple-unpacking keeps
  compatibility with older components that still return lists. (`6.0`)

```python
params = (*lhs_params, *rhs_params)
return sql, params
```

## Control field loading and relationships

`QuerySet.fetch_mode()` selects what happens when code accesses an unloaded field:
`FETCH_ONE` fetches only the instance, `FETCH_PEERS` fetches the field for peer
instances from the same queryset, and `FETCH_RAISE` raises
`FieldFetchBlocked`. (`6.1`)

`ForeignKey.on_delete` accepts `DB_CASCADE`, `DB_SET_NULL`, and
`DB_SET_DEFAULT` for database-level referential actions. Ensure the target
database and migration plan match the requested action. (`6.1`)

## Handle values after saving

After `save()`, `GeneratedField` values and fields assigned database expressions
hold returned values immediately on SQLite, PostgreSQL, and Oracle. MySQL and
MariaDB mark them deferred and refresh transparently on first access.
(`6.0-guide`)

A forced update affecting no rows raises the model-specific `Model.NotUpdated`,
not `DatabaseError`. `Field.pre_save()` may run more than once during one save,
so custom implementations must be idempotent and avoid side effects. (`6.0`)

Django 6.0.8 fixes `bulk_create()` when a related object supplying a primary key
was assigned before that related object was saved on a backend returning
bulk-insert rows. (`6.0.8`)

## Author migrations and constraints

- Custom migration operations can assign `Operation.category` so
  `makemigrations` displays an appropriate symbol. (`5.1`)
- `AlterConstraint` updates model state without recreating the database
  constraint. `makemigrations` uses it for state-only changes such as
  `violation_error_message`. (`5.2-guide`)
- Squashed migrations can be re-squashed before becoming ordinary migrations.
  Serialization supports `zoneinfo.ZoneInfo` and deconstructible keyword names
  that are not valid Python identifiers. (`6.0`)
- Explicit `UniqueConstraint.violation_error_code` and
  `violation_error_message` values apply even to unconditional, field-based
  constraints. (`5.2`)
- Constraints implement a registered `check()` method. A multi-column
  `ForeignObject` raises a system-check error when used in an index, constraint,
  or `unique_together`. (`6.0`)
- User-manager creation methods and synchronous and async queryset
  create/bulk-create/get-or-create/update-or-create methods set
  `alters_data=True`, keeping templates from invoking them. (`5.2`)

## Maintain PostgreSQL extensions

`Lexeme` creates escaped full-text terms supporting `&`, `|`, and `~`
combinations, prefix matching, and weights. PostgreSQL extension migration
operations accept router `hints`. PostgreSQL fields, indexes, and constraints
check that `django.contrib.postgres` is installed. (`6.0`)

## Update third-party database backends

- `BaseDatabaseOperations.adapt_decimalfield_value()` is a no-op returning its
  input; do not rely on it for decimal adaptation. (`5.2`)
- Schema editors no longer append `CASCADE` when dropping columns. (`6.0`)
- Rename `return_insert_columns()` to `returning_columns()` and
  `fetch_returned_insert_rows()` to `fetch_returned_rows()`. The latter receives
  `cursor` and `returning_params`. `fetch_returned_insert_columns()` is removed.
  (`6.0`)
- Backends returning rows from updates can set
  `can_return_rows_from_update=True`. (`6.0`)
- `BaseDatabaseCreation.create_test_db(serialize)` is deprecated in favor of
  `serialize_db_to_string()`, and
  `BaseDatabaseOperations.field_cast_sql()` is removed. (`6.0`)
