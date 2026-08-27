# Expressions and Data Types

Use this reference for expression semantics, nested dtypes, null behavior,
temporal windows, categoricals, decimals, and numeric aggregation.

## Fixed-size arrays, lists, and structs

### Expect `Array` from fixed-width two-dimensional input

Since `1.0-upgrade`, `Series.reshape` and construction from a two-dimensional
NumPy array produce fixed-size `Array` values instead of `List` values. Convert
with `.arr.to_list()` when downstream code requires a variable-size list dtype.

### Compare nested values with missing data

Since `1.10.0`, equality and inequality-with-missing operations work for both
`List` and `Array` values.

### Control null equality in membership tests

Since `1.30.0`, `list.contains` and `arr.contains` accept `nulls_equal`. Use it
to decide whether a null search value matches null elements:

```python
pl.col("items").list.contains(None, nulls_equal=True)
```

### Group by fixed-size arrays

Since `1.30.0`, `Array` columns can be grouping keys:

```python
df.group_by("array_col").len()
```

### Select null behavior in Boolean reductions

Since `1.40.0`, `List` and `Array` `any`/`all` operations accept
`ignore_nulls`, making null handling explicit.

### Test nested uniqueness

Since `1.40.0`, `List` and `Array` dtypes support `is_unique`.

### Broadcast scalar list slices

Since `1.41.0`, `list.slice` broadcasts scalar input, allowing one scalar slice
argument to apply across all rows of a list column.

### Pack values with the list expression

The `py-1.43.2-rs-0.55.1-0.55.2` `list` expression consistently packs its
input elements into the `List` dtype.

### Rename every struct field

As of `py-1.43.2-rs-0.55.1-0.55.2`, passing a different number of names and
fields to `struct.rename_fields()` is deprecated. Supply one name for every
field.

## Null propagation and statistical behavior

### Preserve null positions in EWM output

Since `1.0-upgrade`, `ewm_mean`, `ewm_std`, and `ewm_var` preserve null positions
instead of forward-filling them. Append `.forward_fill()` only when the earlier
filled output is required.

In `py-1.43.2-rs-0.55.1-0.55.2`, the first value of unbiased `ewm_var` and
`ewm_std` became null rather than zero.

### Treat null clipping bounds as absent

Since `1.0-upgrade`, a null lower or upper bound passed to `clip` leaves the
original value unchanged instead of producing null.

### Ignore nulls in bitwise aggregation

Since `1.10.0`, bitwise aggregations ignore null values.

### Preserve null rolling keys

In `py-1.43.2-rs-0.55.1-0.55.2`, `rolling_*_by` operations began propagating
nulls from the `by` column instead of dropping their nullness in the result.

### Return zero covariance for constants

Since `1.40.0`, covariance involving a constant returns zero instead of `NaN`.

## Rolling, dynamic, and window expressions

### Restore the old dynamic-window offset explicitly

Since `1.0-upgrade`, `group_by_dynamic` defaults `offset` to zero instead of
negative `every`. Specify the negative interval when the earlier leading window
is required:

```python
df.group_by_dynamic("ts", every="1d", offset="-1d")
```

### Use index-count rolling windows

Since `1.10.0`, `rolling_*_by` operations can define the window by index count
as well as by time.

### Apply a global window

Since `1.30.0`, `.over()` may omit `partition_by`, treating the complete input
as one window:

```python
df.with_columns(total=pl.col("value").sum().over())
```

### Drop ignored `rolling_corr` parameters

Since `1.40.0`, `rolling_corr` ignores and deprecates `ddof`. Supplying it has no
effect.

## Temporal and string expressions

### Account for fractional datetime precision

Since `1.0-upgrade`, `str.to_datetime` formats containing `%f` or `%.f` default
to microsecond rather than nanosecond precision. Extra fractional digits are
truncated unless precision is otherwise specified.

### Anchor truncation at the Unix epoch

Since `1.30.0`, `dt.truncate` anchors buckets at the Unix epoch. Weekly buckets
remain anchored on Monday.

### Pass decimal inference by keyword

Since `1.20.0`, the argument to `str.to_decimal` is keyword-only:

```python
pl.col("amount").str.to_decimal(inference_length=100)
```

### Normalize Unicode text

Since `1.20.0`, string expressions support `str.normalize`:

```python
df.select(pl.col("text").str.normalize())
```

The equivalent SQL `NORMALIZE` function is also available.

### Replace deprecated temporal and list casts

In `py-1.43.2-rs-0.55.1-0.55.2`, string-to-temporal casts and casts from
non-nested values into `List` became deprecated. Parse temporal values and pack
list elements through explicit typed expressions instead.

### Reject invalid temporal arithmetic

In `py-1.43.2-rs-0.55.1-0.55.2`, adding or subtracting temporal and
non-temporal series raises rather than attempting an invalid coercion.

## Boolean and numeric expressions

### Accumulate Boolean extrema

Since `1.10.0`, cumulative minimum and maximum support Boolean data:

```python
df.select(pl.col("flag").cum_min(), pl.col("flag").cum_max())
```

### Avoid mixed integer/Boolean bitwise operations

In `py-1.43.2-rs-0.55.1-0.55.2`, bitwise operations between integer and
Boolean values became deprecated. Convert both operands to the intended common
dtype first.

### Aggregate `Float16`

Parquet decoding for `Float16` arrived in `1.10.0`; the dtype became stable in
`1.41.0`. As of `py-1.43.2-rs-0.55.1-0.55.2`, group-by aggregations support
`Float16` values.

## Decimal behavior

### Keep Arrow decimals as decimal

Since `1.0-upgrade`, `pl.from_arrow` converts Arrow decimal arrays to Polars
`Decimal`, not `Float64`. Decimal support no longer needs activation, and
`Config.activate_decimals` was removed.

### Widen decimal sum precision

Since `1.41.0`, decimal sum aggregation widens precision, so the aggregate
result need not retain the input precision.

### Raise on decimal sum overflow

As of `py-1.43.2-rs-0.55.1-0.55.2`, decimal sum aggregation raises on overflow
instead of silently wrapping.

## Enum and categorical behavior

### Align Enum categories before append

Since `1.30.0`, appending Enum data no longer merges different category sets.
Align categories before appending inputs with different definitions.

### Replace Enum values strictly

Since `1.40.0`, `replace_strict` handles Enum data correctly.

### Use explicit categorical conversion expressions

The `py-1.43.2-rs-0.55.1-0.55.2` categorical expression namespace provides:

- `Expr.cat.to` for explicit categorical conversion;
- `Expr.cat.physical` for access to the physical representation.

Casting categorical values to integer dtypes, casting numeric values to
categorical, `cat.get_categories()`, and `cat.to_local()` are deprecated.

### Honor lexical category order

As of `py-1.43.2-rs-0.55.1-0.55.2`, categorical
`fill_null(strategy="min"/"max")` and `top_k`/`bottom_k` honor lexical category
ordering.

## Strict nested conversion

Since `1.30.0`, strict casts enforce failures inside nested values as well as at
the outer dtype. Invalid inner values cannot bypass `strict=True`.

In `py-1.43.2-rs-0.55.1-0.55.2`, imploding an `Object` series raises rather
than constructing an invalid `List(Object)`.
