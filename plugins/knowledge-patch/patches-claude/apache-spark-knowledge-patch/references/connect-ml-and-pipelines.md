# Spark Connect, ML, and Declarative Pipelines

Use this reference for remote client mode, operation lifecycle, protocol and
JDBC clients, Spark ML compatibility, and declaratively managed dataflows.

## Choosing Connect or classic mode

### Packaging and application mode (4.0.0)

The approximately 1.5 MB `pyspark-client` package provides a lightweight
Python Connect client. A separate release tarball enables Connect by default.
`spark.api.mode` switches an application between Connect and classic mode.

Java has full client API compatibility, while Scala has Dataset and DataFrame
API parity.

## Request and session behavior

### Execute-plan reattachment (4.0.1)

Repeating `ExecutePlan` with the same operation ID and plan reattaches to the
existing operation instead of starting another one.

Connect treats JDBC options case-insensitively and uses the
`DataFrameReader` default format when the caller does not specify a format.

### Column validation timing (4.1-migration, 4.2-migration)

Python Connect `DataFrame.__getitem__` no longer validates a column name
eagerly, so an invalid name can fail at analysis or execution time
(4.1-migration). Attribute-style access through `DataFrame.__getattr__` is also
deferred (4.2-migration). Set `PYSPARK_VALIDATE_COLUMN_NAME_LEGACY=1` while
migrating code that depends on eager validation.

### Client and protocol APIs (4.1.0)

Connect adds `CloneSession`, exposes gRPC status codes through Python Connect
exceptions, and lets the Scala client pass optional JVM arguments.

### Status and lifecycle (4.2.0)

Client and server implement `GetStatus`. Connect executions appear in a
History Server tab. `SPARK_CONNECT_RELEASE_SESSION_ON_EXIT` releases the remote
session when the client process exits.

### RDD-style and reader coverage (4.2.0)

Connect adds Scala `Dataset.zipWithIndex`, PySpark
`DataFrame.zipWithIndex`, and Python-client `DataFrame.toJSON`. JSON, XML, and
CSV Connect readers can take a DataFrame as input.

## Spark Connect clients

### JDBC driver (4.1.0)

Spark Connect has a JDBC driver, allowing JDBC clients to execute through a
Connect server.

### Supported Python runtimes (4.1.0)

Python 3.14 is supported by `pyspark-client` and `pyspark-connect`, as well as
Spark Classic.

## Spark ML and export

### PMML schema (4.0-migration)

MLlib PMML export emits the PMML 4.4 XML schema instead of PMML 4.3.

### Third-party libraries (3.5.6)

The failure that prevented third-party Spark ML libraries from running through
Spark Connect is fixed.

### ML general availability (4.1.0)

Spark ML over Connect is GA for the Python client.

### Model persistence (3.5.8)

Saving and loading models through `pyspark.ml.connect` no longer uses pickle.

## Declarative Pipelines

### Managed graph execution (4.1.0)

Spark Declarative Pipelines defines datasets and queries declaratively. Spark
derives the execution graph and manages dependency ordering, parallelism,
checkpoints, and retries.

### Auto CDC flows (4.2.0)

Declarative Pipelines adds Python and Spark Connect APIs for Auto CDC flows.
These implement streaming slowly changing dimension Type 1 upserts.

## Related remote-operation APIs

PySpark can interrupt an operation, operations carrying a tag, or all
operations and can add or remove artifacts (4.0.0). Combine those APIs with
stable operation IDs, reattachment, status calls, and explicit session-release
policy when building a resilient remote client.
