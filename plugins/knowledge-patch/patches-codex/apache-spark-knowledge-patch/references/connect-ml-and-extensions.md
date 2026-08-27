# Spark Connect, ML, and Extension APIs

## Spark Connect packaging and mode

Spark `4.0.0` adds:

- the approximately 1.5 MB `pyspark-client` lightweight Python package;
- a separate release tarball with Connect enabled by default;
- `spark.api.mode` for choosing Connect or classic operation;
- Java full client API compatibility; and
- Scala Dataset and DataFrame API parity.

Keep client, server, artifact, and operation-lifecycle behavior aligned when
switching application modes.

## Request and session lifecycle

- Repeating `ExecutePlan` with the same operation ID and plan reattaches to the
  existing operation (`4.0.1`).
- Connect treats JDBC options case-insensitively and uses the
  `DataFrameReader` default format when none is supplied.
- `CloneSession` is available in `4.1.0`. Python Connect exceptions expose
  gRPC status codes, and the Scala client can pass optional JVM arguments.
- Client and server implement `GetStatus` in `4.2.0`; Connect executions are
  visible in a History Server tab.
- `SPARK_CONNECT_RELEASE_SESSION_ON_EXIT` releases the remote session when the
  client process exits.

## Connect API coverage

- A Spark Connect JDBC driver is available in `4.1.0`.
- Scala Connect adds `Dataset.zipWithIndex`, PySpark Connect adds
  `DataFrame.zipWithIndex`, and the lightweight Python client adds
  `DataFrame.toJSON` in `4.2.0`.
- Connect JSON, XML, and CSV readers can use a DataFrame as their input.
- Data Source V2 CDC is exposed through the Connect `changes()` API.
- Python Connect column-name validation is deferred during plan construction;
  see the Python reference for the legacy eager-validation switch.

## Machine learning

- PMML export uses the PMML 4.4 XML schema after `4.0-migration`.
- The fix in `3.5.6` allows third-party Spark ML libraries to run through
  Spark Connect.
- Spark ML over Connect is GA for the Python client in `4.1.0`.
- Model save and load through `pyspark.ml.connect` no longer uses pickle
  (`3.5.8`).

## Declarative Pipelines

Spark Declarative Pipelines arrives in `4.1.0`. A pipeline declares datasets
and queries while Spark derives the execution graph and manages dependency
ordering, parallelism, checkpoints, and retries.

In `4.2.0`, Python and Connect APIs add Auto CDC flows for streaming SCD Type 1
upserts.

## Encoders and Scala or Java API interop

- Affected Scala function APIs carry the missing `@varargs` annotations,
  exposing Java varargs forwarders (`3.5.5`).
- Scala adds `Encoders.udtAPI`, and `TransformingEncoder` supports primitive
  types (`4.1.0`).
- UDAFs returning `Option[Product]` no longer risk corrupt output or a
  segmentation fault (`4.0.1`).

## Extension compatibility

- The `PartitionedFileUtil` simplification is rolled back in `3.5.5` because
  it increased out-of-memory risk. Extension code must use the restored API
  shape.
- Binary compatibility is restored for ML `Param` and `parseDataType` in
  `4.0.1`, reducing linkage failures for already-compiled extensions.
- Data Source V2 `CustomTaskMetric.mergeWith` sums by default in the 4.2
  migration. Override it for non-additive metrics.
- The Kubernetes resource-manager API becomes Stable in `4.2.0`, including
  `SparkPod`, Kubernetes configuration utilities, driver specifications, and
  builders. It provides Java-friendly factories and getters.
