# PySpark, Arrow, and pandas API on Spark

Use this reference for Python dependency floors, type conversion, UDF and UDTF
execution, pandas API migration, error handling, inference, and operation
control.

## Runtime requirements

### Python and library floors (4.0-migration)

Python 3.8 is unsupported. Minimum library versions are pandas 2.0.0, NumPy
1.21, and PyArrow 11.0.0.

### Updated requirements (4.1-migration, 4.2-migration)

Python 3.9 is unsupported and minimum versions become pandas 2.2.0 and PyArrow
15.0.0 in 4.1-migration. PyArrow rises to 18.0.0 and PyPy is no longer
officially supported in 4.2-migration; use CPython.

Python 3.14 is supported by Spark Classic, `pyspark-client`, and
`pyspark-connect` (4.1.0).

## pandas API on Spark migrations

### Removed or renamed methods (4.0-migration)

- Use `Index` instead of `Int64Index` or `Float64Index`.
- Use `items()` instead of `iteritems()`.
- Use `ps.concat` instead of `DataFrame.append` or `Series.append`.
- `DataFrame.mad` and `Series.mad` have no listed replacement.
- Use `Index.astype` instead of `Index.asi8`.
- Use `Index.isin` instead of `Index.is_type_compatible`.
- Use `is_monotonic_increasing` instead of `is_monotonic`.
- Use `DataFrame.dtypes.value_counts()` instead of
  `DataFrame.get_dtype_counts`.
- Use `DataFrameGroupBy.bfill` instead of `backfill` and
  `DataFrameGroupBy.ffill` instead of `pad`.
- `Index.is_all_dates` was removed.
- Use `DataFrame.spark.to_spark_io` instead of `DataFrame.to_spark_io`.

### Removed or renamed parameters (4.0-migration)

- `na_sentinel` became `use_na_sentinel`.
- Categorical and categorical-index mutation methods no longer accept
  `inplace`.
- `between_time` uses `inclusive` instead of `include_start`/`include_end`.
- `date_range(closed=...)` is removed.
- Plotting no longer accepts `sort_columns`.
- CSV and Excel no longer accept `squeeze`.
- `DataFrame.info(null_counts=...)` is removed; use `show_counts`.
- Boolean `Series.between(inclusive=...)` uses `"both"` or `"neither"` rather
  than booleans.
- LaTeX no longer accepts `col_space`.
- Excel no longer accepts `encoding`, `verbose`, `convert_float`, or
  `mangle_dupe_cols`.
- CSV no longer accepts `mangle_dupe_cols`.

### Result changes (4.0-migration)

Datetime index attributes use `int32`. `Series.str.replace` defaults `regex`
to `False`, and a one-character pattern is treated as regex when regex is
explicitly enabled. `value_counts` names its result `count` or `proportion` and
names the index after the input.

`MultiIndex.append` drops index names. List aggregation honors
`as_index=False`. `DataFrame.stack` preserves column order instead of sorting.
Applying `astype` to a decimal object converts an existing missing value to
`True`, not `False`.

### Koalas, datetime, and testing names (4.0-migration)

Use `DataFrame.pandas_on_spark` instead of `.koalas`, and
`DataFrame.pandas_api` instead of `.to_koalas()` or
`.to_pandas_on_spark()`. Week access moved to
`DatetimeIndex.isocalendar().week` and `Series.dt.isocalendar().week`.
`pyspark.testing.assertPandasOnSparkEqual` moved to
`pyspark.pandas.testing.assert_frame_equal`.

Frequency aliases `Y`, `M`, `H`, `T`, and `S` are deprecated in favor of
`YE`, `ME`, `h`, `min`, and `s`.

### Cross-frame and ANSI defaults (4.0-migration, 4.1-migration)

`compute.ops_on_diff_frames` is enabled by default; set it to `false` to
reject cross-frame operations.

Because ANSI SQL is enabled by default, earlier pandas API on Spark raises
unless `spark.sql.ansi.enabled=false`. `compute.fail_on_ansi_mode=False` forces
execution under ANSI but can produce unexpected behavior (4.0-migration).
Later, pandas API on Spark supports ANSI mode because
`compute.ansi_mode_support=True` by default; `compute.fail_on_ansi_mode` is
consulted only when ANSI support is `False` (4.1-migration).

### Missing labels (4.2-migration)

`DataFrame.drop` and `Series.drop` raise `KeyError` when any requested label is
missing, rather than only when every label is missing. Validate labels or use
`errors="ignore"`.

## Python value and schema conversion

### Map inference and intervals (4.0-migration)

Map-column schema inference merges every key-value pair rather than using the
first non-null pair. Restore first-pair inference with
`spark.sql.pyspark.legacy.inferMapTypeFromFirstPair.enabled=true`.

Collecting `YearMonthIntervalType` no longer returns underlying integers. Set
`PYSPARK_YM_INTERVAL_LEGACY=1` for that legacy representation.

### Imports (4.0-migration)

`from pyspark.sql.functions import *` imports functions only. Import
`DataFrame` and `Column` from `pyspark.sql`, and types such as `StructType` from
`pyspark.sql.types`.

### DataFrame and type APIs (4.0.0)

Readers accept time-travel options; writers have `clusterBy`; DataFrames have
`groupingSets` and `metadataColumn`; and `createDataFrame` accepts a PyArrow
`Table`. PySpark adds `DataType.fromDDL` and `CalendarIntervalType`.

### Schema and Arrow fixes (4.0.1)

PySpark can infer a user-defined type when the first element is null. The Arrow
converter handles multiple record batches in a single IPC stream.

### Binary values (4.1-migration)

`BinaryType` maps to Python `bytes` by default across DataFrame APIs, data
sources, and regular or Arrow-optimized UDFs and UDTFs. Set
`spark.sql.execution.pyspark.binaryAsBytes=false` for earlier `bytearray`
mappings where applicable.

### NumPy and nullable integers (4.2-migration)

`SparkSession.createDataFrame` from a NumPy `ndarray` requires PyArrow rather
than pandas and converts through Arrow. Review schemas that formerly depended
on NumPy dtype mapping, particularly when Arrow had been disabled.

A nullable integer column containing nulls reaches a pandas UDF as nullable
`Int8`, `Int16`, `Int32`, or `Int64` extension dtype instead of `float64`.

### Arrow C data interface (4.2.0)

PySpark accepts PyCapsule values through the Arrow C data interface.

## UDF and UDTF execution

### Named arguments and grouped Arrow (4.0.0)

Scalar Python and pandas UDFs and aggregate pandas UDFs accept named
arguments. Grouped and cogrouped data can use `applyInArrow`.

Python data sources support Data Source V2 table creation and writing,
Arrow-based writers, metrics, and session-scoped registration.

### Arrow UDT compatibility (4.1-migration)

Arrow-optimized Python UDFs handle user-defined type inputs and outputs through
Arrow instead of falling back to regular UDF execution. To retain fallback,
set `spark.sql.execution.pythonUDF.arrow.legacy.fallbackOnUDT=true`.

Arrow-enabled UDFs and UDTFs avoid an unnecessary pandas conversion, which can
change coercion when actual output differs from the declared schema. Restore
the conversions with:

```properties
spark.sql.legacy.execution.pythonUDF.pandas.conversion.enabled=true
spark.sql.legacy.execution.pythonUDTF.pandas.conversion.enabled=true
```

### Safe conversion (4.1-migration)

`spark.sql.execution.pandas.convertToArrowArraySafely` defaults to enabled.
Integer overflow, floating-point truncation, and precision loss raise during
Arrow UDF serialization and DataFrame creation. Set it to `false` for previous
permissive conversion.

### Arrow-native APIs (4.1.0)

Arrow UDF and UDTF decorators execute directly with PyArrow, without pandas.
`@udf` can define vectorized UDFs, Arrow-optimized UDTFs may yield scalar
values, and PySpark UDFs can coerce integer returns to `DecimalType`.

`applyInArrow` accepts an iterator of Arrow `RecordBatch` objects;
`applyInPandas` accepts `Iterator[pandas.DataFrame]`.

### Arrow defaults (4.2-migration)

Columnar PySpark/JVM exchange and regular Python UDF and UDTF execution are
Arrow-based by default. Disable individual paths with:

```properties
spark.sql.execution.arrow.pyspark.enabled=false
spark.sql.execution.pythonUDF.arrow.enabled=false
spark.sql.execution.pythonUDTF.arrow.enabled=false
```

### Grouped aggregate iterators (4.2.0)

Arrow and pandas grouped-aggregation UDFs support iterator APIs and SQL
registration.

## Operation control and diagnostics

### Cancellation, tags, and artifacts (4.0.0)

PySpark can interrupt one operation, all operations with a tag, or every
operation. It provides add, remove, get, and clear tag APIs. `addArtifact` and
`addArtifacts` support artifact management.

### Exception conditions (4.0.0, 4.2.0)

Use `PySparkException.getCondition()` instead of deprecated `getErrorClass()`.
`PySparkException` also exposes SQLSTATE information as of 4.2.0.

### Context logging (4.0.1)

The PySpark context logger no longer propagates records to stdout, preventing
unexpected or duplicate console output.

### Worker diagnostics (4.1.0)

Python worker logging covers pandas and Arrow UDFs, UDTFs, and driver-side
workers. Spark can periodically dump worker tracebacks, profile iterator UDFs,
redirect stdout and stderr into logging, and enable VizTracer on daemons and
workers with a supplied script.

### UDF metrics (4.2.0)

PySpark exposes a UDF processing-time metric. Spark SQL reports last-attempt
metrics, and the web UI displays query IDs.
