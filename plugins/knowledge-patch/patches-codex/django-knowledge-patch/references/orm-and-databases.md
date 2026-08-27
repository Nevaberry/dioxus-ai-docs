# ORM and Databases

## Declare composite primary keys

Create a virtual `pk` with component field names. Instance primary keys are tuples, and tuple
assignment and lookup follow declaration order (5.2-guide).

```python
class OrderLineItem(models.Model):
    pk = models.CompositePrimaryKey("product_id", "order_id")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

item = OrderLineItem.objects.get(pk=(1, "A755H"))
```

Reusable code should inspect `_meta.pk_fields`; component fields keep `primary_key=False`.

## Respect composite-key migration and relation limits

Django cannot migrate a model to or from a composite primary key or add or remove its components.
Perform the backend-specific schema change separately, then synchronize Django state with
`--fake` or `SeparateDatabaseAndState` (5.2-guide).

Foreign keys, generic relations, and the admin do not support a composite-key model. The internal
`ForeignObject` workaround creates no columns, constraint, or index, and ignores `on_delete`; do
not mistake it for database-enforced referential integrity.

## Validate and express composite keys

The virtual `pk` is omitted from `ModelForm`s. `clean_fields(exclude={"pk"})` does not exclude the
components, while `validate_unique(exclude={"pk"})` skips the composite uniqueness check.

Most functions that require one expression raise `ValueError` for a composite `pk`.
`Count("pk")` is supported. Custom expressions can opt into composite values with
`allows_composite_expressions` (since 5.2). `QuerySet.raw()` supports composite-key models, and a
subquery returning a composite key can feed lookups such as `__exact` as well as `__in`
(since 6.0).

## Configure database connections

SQLite database `OPTIONS` accepts `init_command` for connection-time pragmas and
`transaction_mode` for transaction behavior (since 5.1). SQLite also permits `CharField` without
`max_length`, using its unlimited `VARCHAR` support (since 5.2).

MySQL connections default to `utf8mb4` (since 5.2). A legacy database can explicitly request
`utf8mb3` in `OPTIONS`. Enable Oracle connection pooling with the `"pool"` database option.

## Define PostgreSQL indexes, search, and extensions

`BTreeIndex` exposes PostgreSQL index deduplication through `deduplicate_items` (since 5.1):

```python
from django.contrib.postgres.indexes import BTreeIndex

index = BTreeIndex(
    fields=["status"],
    deduplicate_items=True,
)
```

`Lexeme` builds escaped full-text search terms and combines them with `&`, `|`, and `~`; it also
supports prefix matching and weighting (since 6.0). PostgreSQL extension migration operations
accept `hints` for database routers. PostgreSQL fields, indexes, and constraints run checks to
ensure `django.contrib.postgres` is installed.

## Use window frames and transformed ordering

`RowRange` permits positive `start` and negative `end` values. Both `RowRange` and `ValueRange`
accept `exclusion` to omit rows, groups, or ties from a frame (since 5.1).

`QuerySet.order_by()` can order by annotation transforms, including `JSONObject` keys and
`ArrayAgg` indexes. PostgreSQL 16+ accepts `generic_plan` in `QuerySet.explain()` (since 5.1),
while PostgreSQL 17 adds `memory` and `serialize` explain options (since 5.2).

## Preserve projection order

`values()` and `values_list()` produce `SELECT` columns in call-site expression order (since 5.2).
This makes operations such as `union()` predictable. Do not reintroduce the former field/extra/
annotation grouping in compatibility code.

At the 7.0 boundary, `values_list(flat=True)` without a field name raises `TypeError`; name the
single projected field explicitly.

## Build aggregate and JSON expressions

`JSONArray` constructs a JSON array from field names or expressions (since 5.2). SQLite
`JSONField` queries support negative array indexes (since 6.0).

`StringAgg` is in `django.db.models` and works across supported backends (6.0-guide). Its
`delimiter` is an expression, so wrap a literal delimiter in `Value()`:

```python
from django.db.models import StringAgg, Value

chapters = StringAgg("chapter", delimiter=Value(","))
```

`Aggregate` accepts `order_by` only when its class sets `allow_order_by=True` (since 6.0).
PostgreSQL `OrderableAggMixin` is deprecated. Single-argument built-in aggregates raise
`TypeError` when called with the wrong number of arguments (since 5.2).

`AnyValue` returns an arbitrary non-null input value on SQLite, MySQL, Oracle, and PostgreSQL 16+
(since 6.0). Use it only where an arbitrary representative is semantically valid.

The 6.1 development API adds UUID4 and UUID7 database functions, bitwise aggregates across all
supported databases, and deterministic-queryset detection. Use the detection result when a stable
ordering is required rather than assuming an unordered queryset is deterministic.

## Validate constraints and generated expressions

Set `Expression.constraint_validation_compatible` when a custom expression must be ignored during
constraint validation (since 5.1). Constraints can validate expressions using `GeneratedField`,
and custom PostgreSQL set-returning expressions can set `set_returning` (since 5.2).

Explicit `UniqueConstraint.violation_error_code` and `violation_error_message` values are honored
even for an unconditional field-based constraint (since 5.2). Constraints implement a registered
`check()` method (since 6.0).

A multi-column `ForeignObject` with multiple `from_fields` triggers a system-check error when used
in an index, constraint, or `unique_together` (since 6.0).

## Make state-only constraint changes

`AlterConstraint` updates migration state without dropping or recreating the database constraint
(5.2-guide). `makemigrations` uses it for state-only changes such as
`violation_error_message`. Test both state and live schema so a state-only migration is not
mistaken for database enforcement work.

Custom migration operations can set `Operation.category`; `makemigrations` displays the category's
symbol for the operation (since 5.1). A squashed migration may be re-squashed before becoming a
normal migration (since 6.0).

## Read database-computed values after saving

After `save()`, `GeneratedField` values and fields assigned database expressions immediately hold
the returned database value on SQLite, PostgreSQL, and Oracle (6.0-guide). MySQL and MariaDB mark
them deferred; first access transparently refreshes the value.

A forced update affecting no rows raises the model-specific `Model.NotUpdated`, not
`DatabaseError` (since 6.0). `Field.pre_save()` may execute more than once in one save, so custom
implementations must be idempotent and free of one-time side effects.

## Handle files and related objects during bulk operations

Saving a `FileField` value without a name raises `FieldError` (since 5.1). After an `ImageField`
save, Django does not force a dimension refresh; storage that resizes the image can leave
`width_field` and `height_field` stale.

Django 6.0.8 fixes a 6.0 regression in which `bulk_create()` could crash on databases returning
rows from bulk inserts when an assigned related object supplying the primary key was saved only
after assignment. Use 6.0.8 or later for that object-assignment pattern.

## Control fetching and referential actions

The 6.1 development API adds `QuerySet.fetch_mode()` for access to unloaded fields:

- `FETCH_ONE` fetches only the accessed instance, preserving earlier behavior.
- `FETCH_PEERS` fetches the missing field for peer instances from the same queryset.
- `FETCH_RAISE` raises `FieldFetchBlocked` instead of performing the fetch.

Choose a mode around query-count and lazy-loading expectations, and test serialization code that
may touch deferred fields implicitly.

`ForeignKey.on_delete` also accepts `DB_CASCADE`, `DB_SET_NULL`, and `DB_SET_DEFAULT` in the 6.1
development API, delegating those actions to the database. Treat adoption as a schema and
migration decision, not just a Python callback substitution.

## Validate binary values strictly

`BinaryField` uses strict Base64 validation in the 6.1 development API. Inputs accepted only by
permissive decoding are rejected; validate or normalize external payloads before field cleaning.

## Implement third-party backends

`BaseDatabaseOperations.adapt_decimalfield_value()` is a no-op returning its input (since 5.2).
Backends must not rely on it for decimal adaptation.

Since 6.0, schema editors do not add `CASCADE` to column drops. Backend return hooks change as
follows:

- `return_insert_columns()` becomes `returning_columns()`.
- `fetch_returned_insert_rows()` becomes `fetch_returned_rows(cursor, returning_params)`.
- `fetch_returned_insert_columns()` is removed.
- A backend supporting UPDATE returning can set `can_return_rows_from_update=True`.

`BaseDatabaseCreation.create_test_db(serialize)` is deprecated; use
`serialize_db_to_string()`. `BaseDatabaseOperations.field_cast_sql()` is removed.

## Return SQL parameters as tuples

Custom lookup and expression implementations of `as_sql()`, `process_lhs()`, and `process_rhs()`
must return parameters as a tuple (since 6.0). Unpacking remains compatible with older list
results:

```python
params = (*lhs_params, *rhs_params)
return sql, params
```

Test the parameter container type as well as the SQL string in custom backend and ORM-extension
tests.

## Remove old extension hooks

Do not depend on joining-column fallbacks, removed `ForeignObject` and `ForeignObjectRel`
joining-column methods, `Prefetch.get_current_queryset()`, singular `get_prefetch_queryset()`,
`FieldCacheMixin.get_cache_name()`, or `FileSystemStorage.OS_OPEN_FLAGS` on 6.0. Use the current
plural prefetch API and supported field/storage extension points.

## Use asynchronous pagination

`AsyncPaginator` and `AsyncPage` are async counterparts to `Paginator` and `Page` (since 6.0).
Await their async operations in async code. Passing `orphans >= per_page` is deprecated for both
sync and async paginators and becomes unsupported at the 7.0 boundary.

Column aliases and annotation names containing `%` are also deprecated in 6.0 and become an
immediate `ValueError` at that boundary.
