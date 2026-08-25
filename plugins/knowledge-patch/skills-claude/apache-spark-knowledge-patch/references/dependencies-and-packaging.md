# Dependencies, runtimes, and packaging

Use this reference when aligning dependency overrides, build exclusions,
language runtimes, package discovery, source builds, or client distribution.

## Bundled storage and messaging libraries

### Spark 3.5 dependency updates

- Spark 3.5.5 bundles Avro 1.11.4. Align Avro overrides or exclusions with
  that version.
- Spark 3.5.6 bundles ORC 1.9.6.
- Spark 3.5.7 bundles ORC 1.9.7 and Jetty 9.4.58.v20250814.
- Spark 3.5.8 bundles Avro 1.11.5, Jersey 2.47, and ORC 1.9.8.

### Spark 4.0.1 dependency updates

Spark 4.0.1 bundles Kafka 3.9.1, ORC 2.1.3, and ORC Format 1.1.1. Align
overrides and exclusions accordingly.

### Spark 4.2.0 dependency updates

Notable bundled versions include:

| Dependency | Version |
| --- | --- |
| Arrow Java | 19.0.0 |
| Hadoop | 3.5.0 |
| Jakarta Servlet | 6.0.0 |
| Jersey | 3.1.11 |
| Kubernetes client | 7.6.1 |
| Log4j | 2.25.4 |
| Netty | 4.2.13 |
| ORC | 2.3.0 |
| Parquet | 1.17.0 |
| Scala | 2.13.18 |

The old `gcs-connector` entry is removed and `hadoop-gcp` 3.5.0 is added.
Review exclusions and dependency overrides together rather than replacing only
one artifact.

## Python packaging and dependencies

### Runtime floors

- In 4.0-migration, Python 3.8 is unsupported; minimum versions are pandas
  2.0.0, NumPy 1.21, and PyArrow 11.0.0.
- In 4.1-migration, Python 3.9 is unsupported; minimum versions are pandas
  2.2.0 and PyArrow 15.0.0.
- In 4.2-migration, PyArrow 18.0.0 or newer is required and PyPy is no longer
  officially supported. Use CPython.

Python 3.14 is supported by Spark Classic, `pyspark-client`, and
`pyspark-connect` as of 4.1.0.

### Py4J range (3.5.8)

PySpark accepts `py4j>=0.10.9.7,<0.10.9.10`, allowing resolution anywhere in
that interval.

### Prerelease suffix (3.5.7)

Spark's PyPI prerelease package names use `dev1`, not `preview1`. Package
selection and publication automation must match the new suffix.

### Lightweight Connect package (4.0.0)

The approximately 1.5 MB `pyspark-client` package is a lightweight Python
Spark Connect client. A separate release tarball enables Connect by default.

## JVM and R runtimes

### Java 25 and R support (4.2.0)

Spark can build and run on Java 25, including SparkR. The Kubernetes image uses
a `25-jre` base. R 3.x is unsupported.

### JDK 8 tool lookup (3.5.8)

When Spark looks for `jmap` under JDK 8, it prefers the Java installation named
by `JAVA_HOME`.

## Build and distribution controls

### Isolated Ivy cache (4.0-migration)

The default Ivy user directory is `~/.ivy2.5.2`. Set
`spark.jars.ivy=~/.ivy2` to keep resolving through the previous directory.

### Optional SQL libraries (4.0-migration)

`hive-llap-common` is no longer bundled. Add it explicitly when LLAP support is
required.

### Source-build JAR collection (4.0.1)

The `sbt/package` build path recognizes `NO_PROVIDED_SPARK_JARS`, which controls
collection of `spark-avro.jar` and `spark-protobuf.jar`.

### YARN shuffle-service JAR (4.0.1)

The YARN external shuffle-service JAR includes `scala-library`, avoiding a
separate missing-runtime dependency.

### Servlet package transition (4.0-migration)

Servlet integrations and dependency declarations must use Jakarta rather than
the former Javax namespace.

## Format feature implications

When dependency overrides are unavoidable, test them against the Spark-facing
features that motivated the bundled line:

- ORC Brotli support and later Zstandard defaults and file-reader behavior;
- Avro logical-type registration, union prefixes, compression levels, and
  `schema_of_avro`;
- Parquet field IDs, Variant annotations, `NullType`, geospatial types, and
  `TIME`-related format support;
- Arrow-native Python exchange, UDFs, UDTFs, PyCapsule values, and CDC paths;
- Jakarta servlet APIs used by web UI, History Server, and server integrations.
