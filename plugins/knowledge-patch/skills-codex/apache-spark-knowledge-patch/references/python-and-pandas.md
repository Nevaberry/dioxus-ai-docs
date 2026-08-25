# Python and pandas API on Spark

## Runtime and packaging

- PySpark no longer supports Python 3.8 in the 4.0 line and no longer supports
  Python 3.9 in the 4.1 line. Spark Classic, `pyspark-client`, and
  `pyspark-connect` support Python 3.14 as of `4.1.0`.
- pandas, NumPy, PyArrow, PyPy, and Arrow-default requirements change across
  migrations; use the migration reference before changing the environment.
- PyPI prerelease packages use the `dev1` suffix instead of `preview1`
  (`3.5.7`).
- PySpark accepts `py4j>=0.10.9.7,<0.10.9.10` (`3.5.8`).

## Operation control and DataFrame APIs

In `4.0.0`, PySpark adds:

- interruption by operation, tag, or globally;
- add, remove, get, and clear tag APIs;
- `addArtifact` and `addArtifacts`;
- reader time-travel options;
- writer `clusterBy`;
- DataFrame `groupingSets` and `metadataColumn`;
- `createDataFrame` from a PyArrow `Table`;
- `DataType.fromDDL`; and
- `CalendarIntervalType`.

In `4.2.0`, PySpark Connect adds `DataFrame.zipWithIndex`; PySpark also gains a
real-time Structured Streaming trigger and DataFrame access to CDC
`changes()`.

## Python UDFs and UDTFs

- Scalar Python or pandas UDFs and aggregate pandas UDFs accept named
  arguments (`4.0.0`).
- Grouped and cogrouped operations support `applyInArrow`.
- Arrow-native UDF and UDTF decorators execute directly with PyArrow without a
  pandas conversion (`4.1.0`). `@udf` can define vectorized UDFs,
  Arrow-optimized UDTFs may yield scalars, and integer returns can coerce to
  `DecimalType`.
- `applyInArrow` accepts an iterator of Arrow `RecordBatch` values, while
  `applyInPandas` accepts an iterator of pandas DataFrames.
- Arrow and pandas grouped-aggregation UDFs add iterator APIs and SQL
  registration in `4.2.0`.
- PySpark accepts PyCapsule objects through the Arrow C data interface.
- Arrow-optimized UDFs support UDT input and output directly. UDF and UDTF
  output coercion no longer performs an unnecessary pandas conversion.
- Columnar exchange, regular Python UDFs, and Python UDTFs use Arrow by default
  in 4.2; control each path with its specific `spark.sql.execution.*.enabled`
  setting.

## Schema and conversion behavior

- PySpark infers a user-defined type even when the first value is null, and
  the Arrow converter reads multiple record batches from one IPC stream
  (`4.0.1`).
- Safe Arrow conversion defaults on in the 4.1 migration. Overflow,
  truncation, and precision loss raise errors rather than being silently
  converted.
- `BinaryType` maps consistently to Python `bytes`, not `bytearray`.
- NumPy `ndarray` DataFrame creation uses Arrow directly and requires PyArrow
  in the 4.2 migration.
- Nullable integer columns with nulls arrive in pandas UDFs as nullable
  `Int8`, `Int16`, `Int32`, or `Int64` extension arrays rather than
  `float64`.
- A Python data source returning an Arrow type that differs from its declared
  schema fails with `DATA_SOURCE_RETURN_SCHEMA_MISMATCH`.
- `YearMonthIntervalType` collection returns interval values rather than raw
  integers; `PYSPARK_YM_INTERVAL_LEGACY=1` is the compatibility escape.
- Map schema inference merges every key-value pair rather than stopping at the
  first non-null pair.

## Exceptions and diagnostics

- `PySparkException.getCondition` replaces deprecated `getErrorClass`
  (`4.0.0`).
- `PySparkException` exposes SQLSTATE information (`4.2.0`).
- Connect Python exceptions expose gRPC status codes (`4.1.0`).
- Python worker logging covers pandas and Arrow UDFs, UDTFs, and driver-side
  workers. Spark can periodically dump worker tracebacks, profile iterator
  UDFs, redirect worker stdout or stderr to logging, and enable VizTracer with
  the provided daemon/worker script.
- PySpark exposes a UDF processing-time metric in `4.2.0`.
- The PySpark context logger no longer propagates to stdout (`4.0.1`), avoiding
  duplicate console records.

## pandas API method and property migrations

The following removals are part of `4.0-migration`:

- Replace `Int64Index` or `Float64Index` with `Index`.
- Replace `iteritems()` with `items()`.
- Replace DataFrame or Series `append` with `ps.concat`.
- `DataFrame.mad` and `Series.mad` have no listed replacement.
- Replace `Index.asi8` with `Index.astype`,
  `Index.is_type_compatible` with `Index.isin`, and `is_monotonic` with
  `is_monotonic_increasing`.
- Replace `DataFrame.get_dtype_counts` with `DataFrame.dtypes.value_counts()`.
- Replace group-by `backfill` and `pad` with `bfill` and `ffill`.
- `Index.is_all_dates` is removed.
- Replace `DataFrame.to_spark_io` with `DataFrame.spark.to_spark_io`.

Use `DataFrame.pandas_on_spark` instead of `.koalas`, and
`DataFrame.pandas_api` instead of `.to_koalas()` or
`.to_pandas_on_spark()`. Week access goes through `isocalendar().week`.
`pyspark.testing.assertPandasOnSparkEqual` moves to
`pyspark.pandas.testing.assert_frame_equal`.

Frequency aliases `Y`, `M`, `H`, `T`, and `S` are deprecated; use `YE`, `ME`,
`h`, `min`, and `s`.

## pandas API parameter migrations

- `na_sentinel` becomes `use_na_sentinel`.
- Categorical and categorical-index mutation drops `inplace`.
- `between_time` replaces `include_start` and `include_end` with `inclusive`.
- Remove `date_range(closed=...)`, plot `sort_columns`, CSV or Excel
  `squeeze`, LaTeX `col_space`, CSV `mangle_dupe_cols`, Excel
  `encoding`/`verbose`, and Excel `convert_float`/`mangle_dupe_cols`.
- Replace `DataFrame.info(null_counts=...)` with `show_counts`.
- Replace boolean `Series.between(inclusive=...)` with `"both"` or
  `"neither"`.

## pandas API result changes

- Datetime index attributes use `int32`.
- `Series.str.replace` defaults `regex=False`; an explicitly regex-enabled
  one-character pattern is treated as a regex.
- `value_counts` names its result `count` or `proportion` and names its index
  after the input.
- `MultiIndex.append` drops index names.
- List aggregation honors `as_index=False`.
- `DataFrame.stack` retains existing column order instead of sorting.
- Decimal-object `astype` converts an existing missing value to `True`, not
  `False`.
- Cross-frame operations default on.
- `DataFrame.drop` and `Series.drop` raise `KeyError` when any requested label
  is absent in the 4.2 migration; use `errors="ignore"` when intended.

## ANSI mode and deferred Connect errors

- pandas API on Spark initially fails under default ANSI mode unless
  `spark.sql.ansi.enabled=false`. `compute.fail_on_ansi_mode=False` forces
  execution but may produce unexpected behavior.
- `compute.ansi_mode_support=True` enables supported ANSI-mode operation in the
  4.1 migration. `compute.fail_on_ansi_mode` matters only when that support is
  disabled.
- Connect defers invalid column-name errors in Python: `__getitem__` changes in
  `4.1-migration`, followed by `__getattr__` in `4.2-migration`.
  `PYSPARK_VALIDATE_COLUMN_NAME_LEGACY=1` restores eager validation.

## Imports

`from pyspark.sql.functions import *` imports functions only. Import
`DataFrame`, `Column`, and `StructType` from `pyspark.sql` or
`pyspark.sql.types`.
