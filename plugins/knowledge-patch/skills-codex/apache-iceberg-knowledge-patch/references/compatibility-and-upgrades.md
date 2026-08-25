# Compatibility and upgrades

Use this reference before changing Iceberg libraries, engine runtime artifacts,
or catalog deployments. It focuses on upgrade blockers and behavior that can
invalidate an otherwise compiling migration.

## Runtime and integration support

### Spark, Flink, Java, Hadoop, and Hive

- In 1.8.0, Spark 3.3 support is deprecated and the Hive runtime is removed.
  Move workloads off both before taking later upgrades.
- In 1.9.0, Spark 3.3 support is removed and the build drops Hadoop 2 support.
  Do not expect compatibility artifacts for either runtime.
- In 1.10.0, Spark 4.0 and Flink 2.0 support are added, while Flink 1.18
  support is removed.
- In 1.11.0-guides, Java 17 becomes the minimum Java runtime, Spark 4.1 and
  Flink 2.1 are supported, Spark 3.4 is deprecated, and Flink 1.19 is removed.

Pin the engine-specific runtime artifact to the engine actually deployed. A
generic library upgrade does not make an unsupported Spark or Flink runtime
valid.

### Comet transition

Spark gained support for the Comet vectorized Parquet reader in 1.8.0. The
Apache DataFusion Comet integration is removed from the Spark module in
1.11.0-guides. Treat this as a removal during upgrades; do not assume the
earlier integration remains transitively available.

### Removed APIs

The 1.10.0 update removes deprecated APIs scheduled for that boundary across
AWS, core, Flink, and Parquet. It also makes deprecated `DynConstructors` and
`DynMethods` methods non-public. Replace calls before upgrading instead of
depending on reflection or former visibility.

## Packaging and reported-version caveats

### Version API in 1.9.0

A build-system bug makes Iceberg 1.9.0 report its version as `unknown` through
the version API. The behavior is specific to 1.9.0 and is fixed in 1.9.1.
Identify an affected deployment from resolved artifacts or build metadata
rather than rejecting it solely because the API result is `unknown`.

### Open API runtime artifact

The Open API module stops building and deploying its runtime JAR in 1.11.0.
Consumers must stop depending on that artifact and select the API or concrete
implementation artifact required by their code.

## Changed failure and validation behavior

### Hive namespaces and views

As of 1.10.0, listing a nonexistent Hive namespace throws
`NoSuchNamespaceException`; earlier behavior returned an empty list. Update
callers that used an empty result to infer absence.

In 1.11.0-guides, replacing a view updates its query in the Hive Metastore.
Registering a table at a name occupied by a view fails instead of overwriting
the view. Code should distinguish registration, replacement, and conflicting
object types.

### REST endpoint assumptions

As of 1.9.0, the default REST routes no longer include namespace, table, or
view `HEAD` endpoints. A client must not use successful `HEAD` registration as
a universal capability test; use the catalog's supported contract.

In 1.11.0-guides, `/v1/config` returns 404 when the requested warehouse does
not exist. Treat this as a missing warehouse, not as proof that the config
route is globally unsupported.

### Spark validation changes

- Spark reports `ADD COLUMN` with a default value as unsupported in 1.10.0,
  even though the table specification and schema APIs support defaults.
- Spark explicitly rejects migration of bucketed tables in 1.11.0 instead of
  attempting an unsupported conversion.
- `SnapshotTableAction` validates source/destination location overlap in
  1.11.0 and rejects invalid layouts.
- `maxRecordPerMicrobatch` is a soft limit in 1.10.0, not a strict cap for
  every microbatch.

## Format and writer migration cautions

Format-v3 tables require row lineage, including tables upgraded from an older
format. An upgrade plan must account for lineage fields, engine support, and
delete handling before setting the format version.

Position-delete files carrying embedded deleted-row data are deprecated in
1.11.0. New writers should not depend on row values being present in position
deletes.

Deletion vectors have lifecycle requirements beyond read compatibility:
rewrites, cleanup, and statistics maintenance must preserve or remove them
consistently with their referenced data files.

## Upgrade checklist

1. Resolve the deployed Java, Spark, Flink, Hadoop, and Iceberg artifacts.
2. Inventory removed runtime modules and direct uses of deprecated APIs.
3. Check every table's format version and delete-file forms.
4. Exercise missing-namespace, missing-warehouse, and conflicting-view paths.
5. Replace strict assumptions about Spark streaming limits.
6. Test object-location validation and unsupported table migrations.
7. Verify the deployed artifact independently when the 1.9.0 version API
   returns `unknown`.

