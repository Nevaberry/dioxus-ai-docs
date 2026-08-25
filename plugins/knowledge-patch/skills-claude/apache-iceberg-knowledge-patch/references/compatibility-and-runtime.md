# Compatibility and Runtime Changes

## Engine and platform compatibility

### Spark, Hive, and Hadoop

- In 1.8.0, Spark 3.3 support was deprecated and the Hive runtime was
  removed. Move users of that runtime to a supported Spark integration or away
  from the removed Hive runtime.
- In 1.9.0, Spark 3.3 support was removed and the build dropped Hadoop 2
  support.
- In 1.10.0, Spark 4.0 support was added.
- Spark 4.1 support was added and Spark 3.4 was deprecated in the
  `1.11.0-guides` batch.
- The Apache DataFusion Comet integration was removed from the Spark module in
  the same guidance. This follows earlier 1.8.0 support for using the Comet
  vectorized Parquet reader, so do not carry that older configuration into the
  current Spark module.

### Flink

- In 1.10.0, Flink 2.0 support was added and Flink 1.18 support was removed.
- Flink 2.1 support was added and Flink 1.19 support was removed in the
  `1.11.0-guides` batch.

### Java

Java 17 is the minimum runtime in the `1.11.0-guides` guidance. Upgrade the
runtime before upgrading an installation that still starts on an older Java
release.

## Removed APIs and artifacts

Iceberg 1.10.0 removes deprecated APIs that had been scheduled for removal
across AWS, core, Flink, and Parquet. Deprecated `DynConstructors` and
`DynMethods` methods are no longer public. Audit direct use of these APIs before
upgrading.

In 1.11.0, the Open API module stops building and deploying its runtime JAR.
Consumers must not retain a runtime dependency on that removed artifact.

## Version API caveat

Iceberg 1.9.0 reports its version as `unknown` when queried through the version
API because of a build-system bug. The bug is fixed in 1.9.1. When diagnosing a
1.9.0 deployment, identify the installed artifact by dependency or packaging
metadata rather than treating `unknown` as proof that Iceberg is absent.

## Upgrade checks

1. Verify the Java runtime before loading Iceberg libraries.
2. Match the Iceberg runtime artifact to the exact Spark or Flink line.
3. Remove Hadoop 2, Spark 3.3, old Flink, Hive-runtime, and Comet-module
   assumptions as applicable.
4. Compile against the remaining public dynamic-construction APIs.
5. Remove dependencies on the Open API runtime JAR.
6. Treat the 1.9.0 version API result as a known exception during inventory.

