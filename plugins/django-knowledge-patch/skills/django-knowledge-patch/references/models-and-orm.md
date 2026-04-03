# Models & ORM

## Composite Primary Keys

*Since 5.2 (April 2025)*

New `CompositePrimaryKey` field for multi-column primary keys. The `pk` attribute becomes a tuple.

```python
class OrderLineItem(models.Model):
    pk = models.CompositePrimaryKey("product_id", "order_id")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField()

# pk is a tuple
item = OrderLineItem.objects.create(product=product, order=order, quantity=1)
item.pk  # (1, "A755H")

# Filter by tuple
OrderLineItem.objects.filter(pk=(1, "A755H"))
```

**Limitations:**
- Cannot migrate to/from composite PK
- `ForeignKey`/`OneToOneField`/`ManyToManyField`/`GenericForeignKey` cannot target composite PK models — use `ForeignObject` with `from_fields`/`to_fields` as workaround
- Not supported in Django admin
- Use `_meta.pk_fields` (not `field.primary_key`) to introspect PK fields

## Cross-database `StringAgg` and `Aggregate.order_by`

*Since 6.0 (December 2025)*

`StringAgg` is now available from `django.db.models` for all backends. **Breaking:** `delimiter` now requires a `Value()` expression.

```python
from django.db.models import Value
from django.db.models.aggregates import StringAgg

MyModel.objects.aggregate(
    names=StringAgg("name", delimiter=Value(", "), order_by="name")
)
```

New `order_by` argument on `Aggregate` base class (replaces the deprecated PostgreSQL-specific `ordering` kwarg).

## `AnyValue` Aggregate

*Since 6.0 (December 2025)*

Returns an arbitrary non-null value from a group. Supported on SQLite, MySQL, Oracle, and PostgreSQL 16+.

```python
from django.db.models import AnyValue

Book.objects.values("author").annotate(sample_title=AnyValue("title"))
```

## Auto-refresh of Expression Fields After `save()`

*Since 6.0 (December 2025)*

`GeneratedField` values and fields assigned expressions (e.g., `obj.updated_at = Now()`) are automatically refreshed from the database after `save()`. On backends with `RETURNING` (SQLite, PostgreSQL, Oracle): done in a single query. On MySQL/MariaDB: fields are marked deferred.

Previously, you had to call `refresh_from_db()` manually.

## `Model.NotUpdated` Exception

*Since 6.0 (December 2025)*

`Model.save()` now raises `Model.NotUpdated` (instead of generic `DatabaseError`) when a forced update (`force_update=True` / `update_fields`) affects zero rows.

## `JSONArray` Database Function

*Since 5.2 (April 2025)*

Returns a JSON array from field names/expressions.

## `QuerySet.values()`/`values_list()` Ordering

*Since 5.2 (April 2025)*

SELECT now matches specified order of expressions (was unpredictable before — affects `.union()`).

## `DEFAULT_AUTO_FIELD` Default Changed

*Since 6.0 (December 2025)*

The framework default changed from `AutoField` (32-bit) to `BigAutoField` (64-bit). Projects that already set `DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"` explicitly can remove it.
