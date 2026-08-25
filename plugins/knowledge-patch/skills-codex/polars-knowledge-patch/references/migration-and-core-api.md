# Migration and Core API

Use this reference when upgrading constructors, frame and series operations,
exception handling, or deprecated interfaces.

## Construction and schema-sensitive behavior

### Construct `Series` values strictly by default

In `1.0-upgrade`, strict construction began applying to inferred as well as
declared dtypes. Incompatible mixed values therefore raise by default.

```python
import polars as pl

s = pl.Series([1, 2, 3.5], strict=False)  # common Float64 dtype
```

With an explicit integer dtype and `strict=False`, a floating value is cast
rather than replaced with null.

### Declare row-oriented frame input

Since `1.0-upgrade`, `DataFrame` infers orientation from the dimensions of the
data and schema, not from the types of the values. It warns whenever it infers
rows. Make heterogeneous row records explicit:

```python
df = pl.DataFrame([[1, "a"], [2, "b"]], orient="row")
```

### Expect constructor timezone conversion

Since `1.0-upgrade`, constructing a datetime column with a zoned dtype always
converts values to the requested zone. It does not merely replace timezone
metadata. A naive midnight constructed with
`pl.Datetime("us", "Europe/Amsterdam")` can therefore become `01:00 CET`.

### Broadcast byte scalars

Since `1.41.0`, the `DataFrame` constructor broadcasts byte scalars across rows
instead of treating them as non-broadcast inputs.

### Reject duplicate Arrow column names

Since `1.20.0`, constructing from a PyArrow table with duplicate column names
raises `DuplicateError`. Handle that exception as an invalid schema rather than
as a generic conversion failure.

### Preserve empty JSON schemas

Since `1.30.0`, constructing a frame from empty JSON preserves the known schema
instead of discarding it.

## Replacement, selection, and equality

### Distinguish `replace` from `replace_strict`

As of `1.0-upgrade`, `replace` preserves the existing dtype, and its `default`
and `return_dtype` parameters are deprecated. Use `replace_strict` for mappings
that may change dtype:

```python
out = s.replace_strict(old, new, default=s)
```

Without `default`, `replace_strict` raises if a non-null input is not mapped.
Since `1.40.0`, strict replacement also works correctly for Enum data.

### Pass only indices to `pl.nth`

The `columns` behavior was removed in `1.0-upgrade`; every positional input to
`pl.nth` is an index. Retrieve a row from a named expression with
`pl.col("a").get(1)` rather than `pl.nth(1, "a")`.

### Choose out-of-bounds behavior

Since `1.0-upgrade`, all `get` and `gather` variants raise on an out-of-bounds
index by default. Pass `null_on_oob=True` when null is the desired result, for
example `s.list.get(1, null_on_oob=True)`.

### Compare series names only when required

Since `1.0-upgrade`, `Series.equals` ignores names by default. Pass
`check_names=True` when names are part of equality.

### Assign with any integer index dtype

Since `1.40.0`, Series index assignment accepts every integer dtype.

### Generate unique dummy names

Since `1.10.0`, `Series.to_dummies` avoids duplicate output column names.

## Reshaping and structural APIs

### Update `pivot` arguments and output names

In `1.0-upgrade`, `DataFrame.pivot` renamed `columns` to `on`, made `on` the
first positional argument, and made `index` and `values` optional. Unspecified
columns are inferred. With multiple value columns, generated names omit the
redundant pivot-column name: for example, `test_1_maths` replaces
`test_1_subject_maths`.

Since `1.40.0`, pivot retains rows whose `on` value is null.

### Use the current run-length struct fields

Since `1.0-upgrade`, `rle` returns fields named `len` and `value`, replacing
`lengths` and `values`. `len` uses the unsigned index dtype (`UInt32` by
default), not `Int32`.

### Annotate one sorted column at a time

Since `1.0-upgrade`, `set_sorted` accepts one column because each annotation
promises that column is independently sorted. Chain calls for several columns:

```python
df = df.set_sorted("a").set_sorted("b")
```

### Unnest applicable columns by default

Since `1.40.0`, calling `unnest()` without column arguments operates on every
applicable column.

### Update implicit line-reader names

Since `1.40.0`, `scan_lines` and `read_lines` name their default column `line`,
not `lines`. Select the new name or rename it explicitly.

### Fill `Null`-typed columns

Since `1.40.0`, `DataFrame.fill_null` operates on columns whose dtype is
`Null`.

## Validation and exceptions

### Catch more specific failures

Beginning with `1.0-upgrade`, many failures that previously raised
`ComputeError` instead raise `InvalidOperationError` or `SchemaError`. Review
handlers around casts and schema-dependent operations.

Since `1.30.0`, Python exceptions crossing Polars execution retain their
original type and traceback, so specific handlers and diagnostics survive.

### Validate integer-range input

Since `1.40.0`, `pl.int_ranges` raises for non-numeric input instead of accepting
it.

### Reject structurally invalid operations

The `py-1.43.2-rs-0.55.1-0.55.2` changes make temporal/non-temporal addition or
subtraction raise. Imploding an `Object` series also raises rather than creating
an invalid `List(Object)`.

## Dtype introspection and public aliases

### Read parameters from dtype instances

As of `1.0-upgrade`, attributes such as `time_unit` and `time_zone` exist only
on dtype instances; `pl.Datetime.time_unit` raises. Class-aware code can use:

```python
time_unit = getattr(dtype, "time_unit", None)
```

Type aliases are no longer re-exported from `polars` or `polars.datatypes`.
Define public aliases locally, for example:

```python
PolarsDataType = pl.DataType | type[pl.DataType]
```

## Runtime and installation migration

### Update the Python floor and supported runtimes

Polars `1.10.0` requires Python 3.9 or newer. Python 3.13 is officially
supported as of `1.20.0`.

### Rename installation extras

The `1.0-upgrade` optional dependencies renamed extras used for `fastexcel`,
`gevent`, `matplotlib`, and `async`. The documented replacement for
`polars[fastexcel,gevent,matplotlib]` is `polars[calamine,async,graph]`.

### Surface deprecated APIs to static tooling

Since `1.30.0`, deprecated APIs participate in PEP 702, so compatible static
analysis can identify deprecated use.

## Deprecation checklist

### Avoid transitional dataframe interchange

Since `1.40.0`, the dataframe interchange protocol integration is deprecated.
Treat integrations that depend on it as transitional.

### Remove `StringCache`

Since `1.41.0`, `StringCache` is deprecated. Avoid it in new code and prepare
existing uses for removal.

### Pass graph and explode choices explicitly

In `py-1.43.2-rs-0.55.1-0.55.2`, calling `show_graph()` without `plan_stage` and
calling `.explode()` without `empty_as_null` became deprecated. Supply both
choices explicitly.

### Migrate categorical casts and helpers

In `py-1.43.2-rs-0.55.1-0.55.2`, the following became deprecated:

- casting `Categorical` values to integer dtypes;
- casting numeric values to `Categorical`;
- `cat.get_categories()`;
- `cat.to_local()`.

Use explicit categorical conversion expressions described in
[Expressions and Data Types](expressions-and-data-types.md).

### Replace deprecated casts and mixed operators

In `py-1.43.2-rs-0.55.1-0.55.2`, string-to-temporal casts, casts from
non-nested dtypes to `List`, and bitwise operations between integer and Boolean
values became deprecated. Convert the operands explicitly before applying the
temporal, list, or bitwise operation.

### Match struct field counts

In `py-1.43.2-rs-0.55.1-0.55.2`, calling `struct.rename_fields()` with a number
of names different from the number of fields became deprecated. Supply exactly
one new name per field.

### Remove `rolling_corr` degrees of freedom

Since `1.40.0`, `rolling_corr` ignores and deprecates `ddof`; providing it no
longer changes the result.

## Reproducibility

Since `1.40.0`, `sample()` respects the global random seed. A global seed now
makes sampling reproducible without a separate per-call seed.
