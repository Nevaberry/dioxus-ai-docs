# Migration and Configuration

Use this reference to audit changed defaults and compatibility controls. The
entries are grouped by the subsystem being changed, not by release.

## Runtime, deployment, and storage defaults

- Servlet types move from `javax` to `jakarta`; rebuild servlet-facing
  integrations against the Jakarta namespace (`4.0-migration`).
- Mesos support is removed. Event logs roll and compress by default, and
  workers periodically clean worker and stopped-application directories. The
  transition switches are `spark.eventLog.rolling.enabled=false`,
  `spark.eventLog.compress=false`, and `spark.worker.cleanup.enabled=false`.
- The external shuffle service defaults to RocksDB and deletes obsolete blocks
  from deallocated executors. Use
  `spark.shuffle.service.db.backend=LEVELDB` and
  `spark.shuffle.service.removeShuffle=false` for the earlier behavior.
- Kubernetes allocation changes from batches of 5 to 10; PVCs default to
  `ReadWriteOncePod`; executor health checks cover every pod container. Restore
  the earlier behavior with `spark.kubernetes.allocation.batch.size=5`,
  `spark.kubernetes.legacy.useReadWriteOnceAccessMode=true`, and
  `spark.kubernetes.executor.checkAllContainers=false`.
- Ivy defaults to `~/.ivy2.5.2`; set `spark.jars.ivy=~/.ivy2` to retain the old
  cache. The task-name MDC key is `task_name`; set
  `spark.log.legacyTaskNameMdc.enabled=true` for `mdc.taskName`.
- Speculation defaults to multiplier `3` and quantile `0.9`, replacing `1.5`
  and `0.75`. `spark.shuffle.unsafe.file.output.buffer` remains accepted but is
  deprecated in favor of `spark.shuffle.localDisk.file.output.buffer`.
- The Master REST API is enabled by default, RDD checkpoints are compressed,
  the S3A Magic Committer is enabled for every bucket, and native Netty I/O is
  used (`4.1-migration`). The respective transition settings are
  `spark.master.rest.enabled=false`, `spark.checkpoint.compress=false`,
  `spark.hadoop.fs.s3a.committer.magic.enabled=false`, and
  `spark.io.mode.default=NIO`.
- Alternative configuration names containing `*.blacklist.*` are ignored; use
  the current configuration names introduced in Spark 3.1.
- On Java 21 or later, Master REST uses virtual threads by default
  (`4.2-migration`). Set `spark.master.rest.virtualThread.enabled=false` for
  legacy threading.
- Kubernetes allocation rises from 10 to 20 per batch and Spark creates an
  executor-ingress `NetworkPolicy`. Set the batch size explicitly or exclude
  `org.apache.spark.deploy.k8s.features.NetworkPolicyFeatureStep` through
  `spark.kubernetes.driver.pod.excludedFeatureSteps`.
- SQL detects inconsistent output from indeterminate shuffle retries and
  rolls back dependent stages, or fails when rollback is impossible. Disable
  both `spark.sql.shuffle.orderIndependentChecksum.enabled` and
  `spark.sql.shuffle.orderIndependentChecksum.enableFullRetryOnMismatch` only
  to restore the old risk profile.
- Derby as a JDBC data source is deprecated. `CustomTaskMetric.mergeWith`
  defaults to summing values; connectors must override it for maxima,
  averages, ratios, or gauges.

## File, table, and format compatibility

- Table reads use `spark.sql.files.ignoreCorruptFiles` and
  `spark.sql.files.ignoreMissingFiles`, not `spark.files.*`.
  `AccessControlException` and `BlockMissingException` always fail.
- Bare `CREATE TABLE` uses `spark.sql.sources.default`; use
  `spark.sql.legacy.createHiveTableByDefault=true` or
  `SPARK_SQL_LEGACY_CREATE_HIVE_TABLE=true` to temporarily restore the Hive
  default.
- Hive metastore versions older than 2.0.0 are unsupported, and
  `hive-llap-common` must be added explicitly. Parquet uses `lz4_raw`, not
  `lz4raw`; ORC compression defaults to `zstd`.
- Replace removed legacy-prefixed datetime rebase names with
  `spark.sql.parquet.int96RebaseModeInWrite`,
  `spark.sql.parquet.datetimeRebaseModeInWrite`,
  `spark.sql.parquet.int96RebaseModeInRead`,
  `spark.sql.avro.datetimeRebaseModeInWrite`, and
  `spark.sql.avro.datetimeRebaseModeInRead`.
- Each file-source table read honors that query's options. Set
  `spark.sql.legacy.readFileSourceTableCacheIgnoreOptions=true` only if the old
  first-plan option caching is required.
- When every projected field is missing from a Parquet struct, Spark reads a
  present field to distinguish a null struct (`4.1-migration`). Use
  `spark.sql.legacy.parquet.returnNullStructIfAllFieldsMissing=true` for the
  former always-null result.
- With `ignoreCorruptFiles=true`, a file-reading `java.lang.InternalError` is
  now ignorable rather than fatal.

## SQL semantics and parser behavior

- ANSI SQL is enabled by default (`4.0-migration`). Set
  `spark.sql.ansi.enabled=false` or `SPARK_ANSI_SQL_MODE=false` only where
  permissive overflow and invalid-operation behavior is intentional.
- Map constructors and concatenation normalize `-0.0` keys to `0.0`; use
  `spark.sql.legacy.disableMapKeyNormalization=true` for the old distinction.
- `spark.sql.maxSinglePartitionBytes` defaults to `128m`, not
  `Long.MaxValue`. Set `9223372036854775807` for the previous unlimited cap.
- In non-ANSI mode, narrowing an overflowing timestamp to `byte`, `short`, or
  `int` returns `NULL`, not a wrapped value.
- `encode` and `decode` accept US-ASCII, ISO-8859-1, UTF-8, UTF-16BE,
  UTF-16LE, UTF-16, and UTF-32. Unmappable input raises
  `MALFORMED_CHARACTER_CODING`; legacy JDK charsets and replacement behavior
  can be restored separately with `spark.sql.legacy.javaCharsets=true` and
  `spark.sql.legacy.codingErrorAction=true`.
- Format-string argument indexes are one-based; the
  `spark.sql.legacy.allowZeroIndexInFormatString` escape is deprecated.
- CTE precedence and time parsing default to `CORRECTED`. Inner CTEs shadow
  outer CTEs; timestamp parse failures raise `CANNOT_PARSE_TIMESTAMP` in ANSI
  mode and return `NULL` otherwise.
- `expr ! IN`, `expr ! BETWEEN`, and `col ! NULL` are invalid; use `NOT`.
  `spark.sql.legacy.bangEqualsNot=true` temporarily restores acceptance.
- Views compensate for underlying type changes with casts. Set
  `spark.sql.legacy.viewSchemaCompensation=false` for up-cast-only behavior;
  `spark.sql.legacy.viewSchemaBindingMode=false` disables schema binding and
  removes its clause from descriptions and DDL.
- `sentences` uses `Locale(language)` when the country is null, rather than
  `Locale.US`.
- Thrift `GetColumns` ordinals are one-based (`4.1-migration`). Set
  `spark.sql.legacy.hive.thriftServer.useZeroBasedColumnOrdinalPosition=true`
  for a legacy client.
- `system.builtin` contains built-ins and injected functions;
  `system.session` contains temporary objects and session variables
  (`4.2-migration`). Two-part `builtin.*` and `session.*` resolve there first.
  Qualify a persistent catalog or set
  `spark.sql.legacy.persistentCatalogFirst=true` when names collide.
- Temporary views and functions accept only `session` or `system.session`
  qualifiers; other qualifiers fail with `INVALID_TEMP_OBJ_QUALIFIER`.
- SQL path resolution adds `SET PATH`, `current_path()`, and lookup of
  unqualified routines, relations, and variables. Enable
  `spark.sql.path.enabled=true` and optionally set `spark.sql.defaultPath`.
- Duplicate names in one `WITH` clause fail with `DUPLICATED_CTE_NAMES`
  regardless of case-sensitivity configuration. `NATURAL JOIN`, separately,
  honors `spark.sql.caseSensitive` when finding common columns.
- A SQL UDF parameter cannot shadow bare `current_user`, `current_date`,
  `current_time`, `current_timestamp`, `user`, `session_user`, or
  `grouping__id`. Rename it or use
  `spark.sql.legacy.allowUdfParameterToShadowParameterlessFunction=true`.
- `SET CATALOG name` resolves an unquoted session variable first. Use
  `SET CATALOG 'name'` for a literal catalog name.
- Empty grouping sets, `CUBE()`, and `ROLLUP()` return one grand-total row on
  empty input. The old zero-row behavior is available through
  `spark.sql.analyzer.lowerEmptyGroupingSetToGlobalAggregate.enabled=false`.

## JDBC mappings

The following mapping changes are part of `4.0-migration`:

- PostgreSQL `TIMESTAMP WITH TIME ZONE` reads as `TimestampType` regardless of
  `preferTimestampNTZ`, and `TimestampType` writes with time zone. Use
  `spark.sql.legacy.postgres.datetimeMapping.enabled=true` for both old paths.
- MySQL `TIMESTAMP` reads as `TimestampType`; `TimestampNTZType` writes as
  `DATETIME`. `SMALLINT`, unsigned `MEDIUMINT`, `FLOAT`, and multi-bit `BIT`
  map to `ShortType`, `IntegerType`, `FloatType`, and `BinaryType`;
  `ShortType` writes as `SMALLINT`. Compatibility settings are
  `spark.sql.legacy.mysql.timestampNTZMapping.enabled` and
  `spark.sql.legacy.mysql.bitArrayMapping.enabled`.
- Oracle `TimestampType` writes as `TIMESTAMP WITH LOCAL TIME ZONE`; use
  `spark.sql.legacy.oracle.timestampMapping.enabled=true` for `TIMESTAMP`.
- SQL Server `TINYINT` and `DATETIMEOFFSET` read as `ShortType` and
  `TimestampType`; use the `numericMapping` and `datetimeoffsetMapping`
  settings under `spark.sql.legacy.mssqlserver`.
- DB2 `SMALLINT` reads as `ShortType` and `BooleanType` writes as `BOOLEAN`;
  use the `numericMapping` and `booleanMapping` settings under
  `spark.sql.legacy.db2`.

## Structured Streaming migration checks

- `AvailableNow` falls back to single-batch execution if any source does not
  support it. Relative writer paths resolve on the driver.
- `spark.sql.streaming.ratioExtraSpaceAllowedInCheckpoint` defaults to `0.3`
  for stale version files pending batched deletion; set it to `0` for the
  previous headroom.
- AQE is enabled for stateless streaming (`4.1-migration`). Set
  `spark.sql.adaptive.streaming.stateless.enabled=false` to retain fixed
  planning.
- A checkpoint with offset or commit logs but no metadata file fails with
  `STREAMING_CHECKPOINT_MISSING_METADATA_FILE` (`4.2-migration`). Restore the
  metadata, choose a new checkpoint, or explicitly disable
  `spark.sql.streaming.checkpoint.verifyMetadataExists.enabled`.
- `SimpleDataSourceStreamReader.read()` must advance the end offset for every
  non-empty batch or it fails with
  `SIMPLE_STREAM_READER_OFFSET_DID_NOT_ADVANCE`.

## Python and pandas API migration checks

- The 4.0 runtime drops Python 3.8 and requires pandas 2.0.0, NumPy 1.21, and
  PyArrow 11.0.0 (`4.0-migration`). The 4.1 runtime drops Python 3.9 and
  requires pandas 2.2.0 and PyArrow 15.0.0 (`4.1-migration`). PyArrow rises to
  18.0.0 and official PyPy support ends in `4.2-migration`.
- Replace `Int64Index` and `Float64Index` with `Index`, `iteritems` with
  `items`, append methods with `ps.concat`, `Index.asi8` with `astype`,
  `is_type_compatible` with `isin`, and `is_monotonic` with
  `is_monotonic_increasing`. `mad` and `Index.is_all_dates` are removed.
- Replace `get_dtype_counts` with `dtypes.value_counts`, group-by `backfill`
  and `pad` with `bfill` and `ffill`, and `to_spark_io` with
  `spark.to_spark_io`.
- Parameter migrations include `na_sentinel` to `use_na_sentinel`,
  `between_time` start/end booleans to `inclusive`, and `info(null_counts=...)`
  to `show_counts`. Categorical mutation no longer accepts `inplace`.
  Removed CSV, Excel, plotting, date-range, LaTeX, and `Series.between`
  parameters must be deleted or replaced with their current forms.
- Expect `int32` datetime-index attributes, literal-by-default
  `str.replace`, renamed `value_counts` results, unnamed `MultiIndex.append`
  output, `as_index=False` list aggregation, and order-preserving `stack`.
  Decimal-object `astype` converts an existing missing value to `True`.
- Replace Koalas names with `pandas_on_spark` and `pandas_api`; use
  `isocalendar().week`; import
  `pyspark.pandas.testing.assert_frame_equal`. Frequency aliases migrate from
  `Y`, `M`, `H`, `T`, and `S` to `YE`, `ME`, `h`, `min`, and `s`.
- Map inference examines every key-value pair; set
  `spark.sql.pyspark.legacy.inferMapTypeFromFirstPair.enabled=true` for the old
  first-pair rule. Cross-frame pandas operations default on.
- Collected year-month intervals no longer expose raw integers; use
  `PYSPARK_YM_INTERVAL_LEGACY=1` temporarily. Wildcard function imports no
  longer import SQL types.
- pandas API on Spark initially requires ANSI SQL off unless
  `compute.fail_on_ansi_mode=False`. In 4.1,
  `compute.ansi_mode_support=True` enables supported ANSI execution.
- Connect column lookup validation is deferred first for `__getitem__` and
  then for `__getattr__`; `PYSPARK_VALIDATE_COLUMN_NAME_LEGACY=1` restores
  eager validation.
- Arrow UDFs handle UDTs directly; use
  `spark.sql.execution.pythonUDF.arrow.legacy.fallbackOnUDT=true` for fallback.
  Legacy pandas coercion for UDFs and UDTFs is controlled by the corresponding
  `spark.sql.legacy.execution.*.pandas.conversion.enabled` settings.
- Binary values map to `bytes`; set
  `spark.sql.execution.pyspark.binaryAsBytes=false` for earlier mappings.
  Checked Arrow conversion defaults on and can be disabled with
  `spark.sql.execution.pandas.convertToArrowArraySafely=false`.
- Arrow becomes the default for PySpark exchange, Python UDFs, and Python
  UDTFs. The individual controls are
  `spark.sql.execution.arrow.pyspark.enabled`,
  `spark.sql.execution.pythonUDF.arrow.enabled`, and
  `spark.sql.execution.pythonUDTF.arrow.enabled`.
- NumPy DataFrame creation requires PyArrow and uses Arrow inference. Nullable
  integer inputs to pandas UDFs use pandas `Int8`, `Int16`, `Int32`, or `Int64`
  extension dtypes rather than `float64`.
- pandas API `drop` raises `KeyError` if any requested label is missing; pass
  `errors="ignore"` when appropriate. Python data sources reject Arrow types
  that differ from the declared schema with
  `DATA_SOURCE_RETURN_SCHEMA_MISMATCH`.

## ML export

PMML export emits the PMML 4.4 schema rather than 4.3
(`4.0-migration`).
