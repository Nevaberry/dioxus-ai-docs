# Data types and expressions

Use this reference for constructors, schema-sensitive behavior, nested data,
expressions, aggregation, and temporal operations.

## Construction and dtype inference

### Strict `Series` construction (1.0-upgrade)

`pl.Series` applies strict construction to inferred and declared dtypes.
Incompatible mixed values raise by default. With
`pl.Series([1, 2, 3.5], strict=False)`, Polars finds a common `Float64` dtype;
with an explicit integer dtype it casts the float rather than replacing it with
null.

### Explicit row orientation (1.0-upgrade)

`DataFrame` infers orientation from data and schema dimensions instead of value
types, and warns when it infers rows. Make heterogeneous rows explicit:

```python
pl.DataFrame([[1, "a"], [2, "b"]], orient="row")
```

### Zoned datetime construction (1.0-upgrade)

Constructing with a zoned datetime dtype always converts values to that zone; it
does not sometimes replace time-zone metadata. A naive `2020-01-01 00:00`
constructed as `pl.Datetime("us", "Europe/Amsterdam")` becomes `01:00 CET`, so
check code that assumes wall-clock preservation.

### Fixed-size arrays from 2-D input (1.0-upgrade)

`Series.reshape` and construction from a two-dimensional NumPy array produce
fixed-size `Array`, not `List`. Use `.arr.to_list()` where the old dtype is
required.

### Dtype instance attributes and local aliases (1.0-upgrade)

Properties such as `time_unit` and `time_zone` exist only on dtype instances;
`pl.Datetime.time_unit` raises. Class-aware code can use
`getattr(dtype, "time_unit", None)`. Public type aliases are no longer
re-exported from `polars` or `polars.datatypes`; define a local alias such as
`PolarsDataType = pl.DataType | type[pl.DataType]`.

### Byte scalar broadcasting (1.41.0)

The `DataFrame` constructor broadcasts byte scalars across rows instead of
treating them as non-broadcast input.

### NumPy conversion signatures (1.41.0)

`DataFrame.__array__` and `Series.__array__` match NumPy's signature and accept
the standard conversion arguments supplied by NumPy callers.

## Replacement, selection, and equality

### `replace` and `replace_strict` (1.0-upgrade)

`replace` preserves the existing dtype; its `default` and `return_dtype`
parameters are deprecated. Use
`s.replace_strict(old, new, default=s)` for a mapping that may change dtype.
Without `default`, `replace_strict` raises if any non-null input is unmapped.

### Name-insensitive series equality (1.0-upgrade)

`Series.equals` ignores series names by default. Pass `check_names=True` when
names are part of equality.

### Positional `nth` inputs (1.0-upgrade)

The former `columns` behavior was removed from `pl.nth`; every positional input
is an index. Use `pl.col("a").get(1)` rather than `pl.nth(1, "a")` to retrieve
an element from a named expression.

### Out-of-bounds indexing (1.0-upgrade)

All `get` and `gather` variants raise on out-of-bounds indices by default. Pass
`null_on_oob=True`, such as `s.list.get(1, null_on_oob=True)`, to produce null.

### Integer-typed assignment indices (1.40.0)

Series index assignment accepts every integer dtype.

### Strict Enum replacement (1.40.0)

`replace_strict` works with Enum data.

## Nested, categorical, and struct data

### RLE struct fields (1.0-upgrade)

The `rle` result fields are `len` and `value`, replacing `lengths` and `values`.
`len` uses the unsigned index dtype (`UInt32` by default), not `Int32`.

### Missing-aware nested comparison (1.10.0)

Equality and inequality-with-missing operations work for both `List` and
`Array` data.

### Null-aware nested membership (1.30.0)

`list.contains` and `arr.contains` accept `nulls_equal`. For example,
`pl.col("items").list.contains(None, nulls_equal=True)` lets a null search value
match null elements.

### Strict nested casts (1.30.0)

Strict casts enforce conversion failures inside nested values as well as at the
outer dtype. Invalid inner values no longer bypass `strict=True`.

### Enum category append behavior (1.30.0)

Appending Enum data does not merge differing category sets. Align category
definitions before appending inputs that do not already share one.

### Fixed-size arrays as grouping keys (1.30.0)

An `Array` column can be a grouping key, for example
`df.group_by("array_col").len()`.

### Explicit null policy for Boolean reductions (1.40.0)

List and Array `any`/`all` accept `ignore_nulls`, allowing callers to select
their null behavior explicitly.

### Nested uniqueness (1.40.0)

List and Array dtypes support `is_unique`.

### All-column unnesting (1.40.0)

Calling `unnest()` without column arguments operates on every applicable
column.

### Scalar `list.slice` broadcasting (1.41.0)

`list.slice` broadcasts scalar input so one scalar can apply across all rows of
a list column.

### Explicit categorical conversions (py-1.43.2-rs-0.55.1-0.55.2)

Use `Expr.cat.to` for explicit categorical conversion and
`Expr.cat.physical` to access the physical representation.

### Exact struct rename arity (py-1.43.2-rs-0.55.1-0.55.2)

Passing a different number of names than fields to `struct.rename_fields()` is
deprecated. Supply exactly one new name per field.

### List-packing expression (py-1.43.2-rs-0.55.1-0.55.2)

The `list` expression consistently packs its input elements into the `List`
dtype.

### Lexical categorical extrema (py-1.43.2-rs-0.55.1-0.55.2)

Categorical `fill_null(strategy="min"/"max")` and `top_k`/`bottom_k` honor
lexical category ordering.

## Aggregation, windows, and null behavior

### EWM null positions and clipping (1.0-upgrade)

`ewm_mean`, `ewm_std`, and `ewm_var` preserve null positions instead of
forward-filling them; append `.forward_fill()` to recover the earlier result. A
null lower or upper bound passed to `clip` leaves the original value unchanged
instead of producing null.

### Dynamic-window offset (1.0-upgrade)

`group_by_dynamic` defaults `offset` to zero rather than negative `every`. When
the leading old-style window is required, specify the negative interval, such
as `offset="-1d"` with `every="1d"`.

### Index-count rolling windows (1.10.0)

The `rolling_*_by` operations can define windows by index count as well as time.

### Cumulative Boolean extrema (1.10.0)

Cumulative minimum and maximum support Boolean data, including
`pl.col("flag").cum_min()` and `.cum_max()`.

### Nulls in bitwise aggregations (1.10.0)

Bitwise aggregations ignore null values.

### Global window expressions (1.30.0)

Calling `.over()` without `partition_by` treats the full input as one window:

```python
df.with_columns(total=pl.col("value").sum().over())
```

### Keyless global grouping (1.40.0)

`group_by()` can be called without key expressions, exposing the group-by
aggregation interface for one global group.

### Deprecated rolling correlation `ddof` (1.40.0)

`rolling_corr` ignores and deprecates `ddof`; passing it does not change the
result.

### Null-typed columns in `fill_null` (1.40.0)

`DataFrame.fill_null` operates on columns whose dtype is `Null`.

### Constant covariance and sampling seed (1.40.0)

Covariance involving a constant returns zero instead of `NaN`. `sample()`
respects the global random seed, so globally seeded sampling is reproducible.

### Wider decimal sums (1.41.0)

Decimal sum aggregation widens precision; the result need not keep the input
precision.

### Decimal overflow (py-1.43.2-rs-0.55.1-0.55.2)

Decimal sum aggregation raises on overflow rather than silently wrapping.

### Null keys in rolling-by operations (py-1.43.2-rs-0.55.1-0.55.2)

`rolling_*_by` propagates null values from the `by` column instead of dropping
their nullness from the result.

### Unbiased EWM initial values (py-1.43.2-rs-0.55.1-0.55.2)

The first value of unbiased `ewm_var` and `ewm_std` is null rather than zero.

### `Float16` group-by aggregation (py-1.43.2-rs-0.55.1-0.55.2)

Group-by aggregations support `Float16` values.

## Temporal and string expressions

### Fractional datetime parsing precision (1.0-upgrade)

`str.to_datetime` formats containing `%f` or `%.f` default to microsecond rather
than nanosecond precision. Excess fractional digits are truncated unless
precision is specified another way.

### Keyword-only decimal inference (1.20.0)

The `str.to_decimal` inference parameter is keyword-only. Write
`pl.col("amount").str.to_decimal(inference_length=100)`.

### Unicode normalization (1.20.0)

String expressions support Unicode normalization through `str.normalize`, for
example `df.select(pl.col("text").str.normalize())`.

### Epoch-aligned datetime truncation (1.30.0)

`dt.truncate` anchors buckets at the Unix epoch. Weekly buckets remain anchored
on Monday.

### Numeric validation for integer ranges (1.40.0)

`pl.int_ranges` raises on non-numeric input.

### Stable `Float16` (1.41.0)

`Float16` support is stable rather than experimental.

### Strict invalid-operation checks (py-1.43.2-rs-0.55.1-0.55.2)

Adding or subtracting temporal and non-temporal series raises. Imploding an
`Object` series also raises instead of constructing an invalid `List(Object)`.
