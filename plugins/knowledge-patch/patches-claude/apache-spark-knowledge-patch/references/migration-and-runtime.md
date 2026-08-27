# Migration and runtime behavior

Use this reference for core configuration changes, compatibility switches,
extension-facing APIs, shuffle behavior, and runtime correctness fixes.

## Process and service defaults

### Servlet namespace and resource managers (4.0-migration)

Servlet references moved from `javax` to `jakarta`; integrations that touch
Spark servlet types must migrate their imports and dependencies. Apache Mesos
is no longer supported as a resource manager.

### Event logs, worker cleanup, and shuffle service (4.0-migration)

Event logs roll incrementally and are compressed by default. Workers also
periodically clean worker and stopped-application directories. Restore the
older behavior with:

```properties
spark.eventLog.rolling.enabled=false
spark.eventLog.compress=false
spark.worker.cleanup.enabled=false
```

The external shuffle service now uses RocksDB rather than LevelDB and deletes
unneeded shuffle blocks for deallocated executors. Compatibility settings are:

```properties
spark.shuffle.service.db.backend=LEVELDB
spark.shuffle.service.removeShuffle=false
```

It can fetch RDD blocks stored on remote disks (3.5.6).

### Speculation and shuffle buffers (4.0-migration)

Speculation defaults are less aggressive:
`spark.speculation.multiplier=3` and `spark.speculation.quantile=0.9`; the old
values were `1.5` and `0.75`. The setting
`spark.shuffle.unsafe.file.output.buffer` remains accepted but is deprecated;
use `spark.shuffle.localDisk.file.output.buffer`.

### Checkpoint and decommission behavior (4.0.0)

`spark.checkpoint.dir` supplies a configuration-level checkpoint location.
`spark.stage.ignoreDecommissionFetchFailure` defaults to enabled, changing
recovery when stage fetch failures involve decommissioned executors.

### Master REST API and checkpoints (4.1-migration)

The Master daemon exposes its REST API by default. Set
`spark.master.rest.enabled=false` to retain the earlier behavior. RDD
checkpoints are compressed by default; use `spark.checkpoint.compress=false`
to write uncompressed checkpoints.

On Java 21 or later, Master REST handling uses virtual threads by default
(4.2-migration). Disable them with
`spark.master.rest.virtualThread.enabled=false`.

### S3A committer and Netty I/O (4.1-migration)

The Hadoop S3A Magic Committer is enabled for every S3 bucket by default. Use
`spark.hadoop.fs.s3a.committer.magic.enabled=false` for the earlier behavior.
Native Netty I/O is also the default; use `spark.io.mode.default=NIO` where NIO
is required.

### Removed configuration aliases (4.1-migration)

Alternative names containing `*.blacklist.*` are ignored. Replace them with
the corresponding current names, available since Spark 3.1.

### Binary byte-size units (4.2.0)

Spark byte-size configuration values accept `KiB`, `MiB`, `GiB`, `TiB`, and
`PiB` suffixes.

## Correctness and recovery

### Partition pruning and replacement tables (3.5.6)

Queries affected by partition-pruning handling no longer fail with
`Expected only partition pruning predicates`. `ReplaceTableAsSelect` now
overwrites the replacement table rather than appending to it.

### Shuffle retry consistency (4.2-migration)

Spark SQL checks indeterminate shuffle retries for inconsistent output. On a
mismatch it rolls back and reruns all dependent succeeding stages, or fails
when rollback is impossible. Restore the prior behavior only by disabling both:

```properties
spark.sql.shuffle.orderIndependentChecksum.enabled=false
spark.sql.shuffle.orderIndependentChecksum.enableFullRetryOnMismatch=false
```

### Shuffle cleanup without AQE (4.0.1)

`RemoveFiles` shuffle cleanup works when Adaptive Query Execution is disabled.

### Observation behavior (3.5.8, 4.2-migration)

The observation deadlock is fixed and `Observation` has a safety check that
prevents blocking (3.5.8). `Observation.get` now surfaces the underlying Scala
or Python exception when metric collection fails instead of returning an empty
result (4.2-migration).

## APIs used by extensions

### Java varargs and restored file API (3.5.5)

Affected Scala function APIs have `@varargs` annotations and therefore expose
Java-friendly forwarders. Spark 3.5.5 also restored the earlier
`PartitionedFileUtil` API shape after simplified APIs increased out-of-memory
risk; callers must use the restored shape.

### Configuration deprecation (3.5.5)

The incorrect configuration introduced by SPARK-49699 follows a graceful
deprecation path rather than disappearing immediately. Existing deployments
have a transition window but should migrate away from it.

### Compatibility restoration (4.0.1)

Binary compatibility was restored for the ML `Param` class and
`parseDataType`, reducing linkage failures for extensions compiled against an
earlier Spark runtime. Scala UDAFs returning `Option[Product]` no longer risk
corrupted data or a segmentation fault.

### Custom task metrics (4.2-migration)

`CustomTaskMetric.mergeWith` has a default implementation that sums values.
Connector authors must override it for maxima, averages, compression ratios,
gauges, and every other non-additive metric.

### Kubernetes resource-manager API (4.2.0)

The Kubernetes resource-manager API is Stable. `SparkPod`, Kubernetes
configuration utilities, driver specifications, and builders expose
Java-friendly factories and getters.

## Launch and local tool behavior

### Ivy directory (4.0-migration)

The default Ivy user directory is `~/.ivy2.5.2`. Set
`spark.jars.ivy=~/.ivy2` when dependency resolution must continue using the old
directory.

### Launcher properties and JPMS (4.0.1)

Launcher remote-mode detection respects properties files and
`--load-spark-defaults`. JPMS arguments are applied to processes that were not
started through `SparkSubmit` as well.

### JDK 8 tool discovery (3.5.8)

When locating `jmap` for JDK 8, Spark prefers the Java home named by
`JAVA_HOME`.

### SparkSubmit exit behavior (4.1.0)

An opt-in SparkSubmit flag can call `System.exit` automatically after the user
application's `main` method returns.
