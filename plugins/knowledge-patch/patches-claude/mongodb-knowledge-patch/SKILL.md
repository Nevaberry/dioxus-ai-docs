---
name: mongodb-knowledge-patch
description: MongoDB
version: "8.2"
license: MIT
metadata:
  author: Nevaberry
---


# MongoDB knowledge patch

Use this patch before changing MongoDB deployment compatibility, upgrade or downgrade
procedures, aggregation pipelines, geospatial indexes, sharding behavior, encryption,
validation, search, WiredTiger settings, or operational telemetry. Check the deployed binary
and maintenance release before applying version-dependent guidance.

## Reference index

| Reference | Read for |
| --- | --- |
| [Compatibility, upgrades, and known issues](references/compatibility-upgrades-and-known-issues.md) | Linux compatibility, FCV sequencing, downgrade limits, and patch-level hazards |
| [Aggregation, queries, and search](references/aggregation-queries-and-search.md) | New expressions and accumulators, `$merge`, geospatial keys, query settings, catalog access, and Search |
| [Sharding, replication, and networking](references/sharding-replication-and-networking.md) | Orphan cleanup, initial sync, mirrored reads, consistency diagnoses, connection limiting, and audit identity |
| [Encryption, validation, and Stable API](references/encryption-validation-and-stable-api.md) | Queryable Encryption preview constraints, `mongocryptd`, encrypted lookups, validation, and API V1 |
| [Storage, configuration, and observability](references/storage-configuration-and-observability.md) | WiredTiger sizing and compression, spill behavior, query statistics, inspection output, metrics, and server controls |

## Breaking compatibility and patch-level hazards

### Avoid the Linux kernel 6.19 combination

MongoDB 8.0 and newer can crash during startup on Linux kernel 6.19 because of the bundled
TCMalloc version. The risk applies to official packages, package-manager installations, and
containers. Do not deploy this combination until the MongoDB build contains the patched
allocator.

### Treat encrypted string-query data as disposable

Queryable Encryption prefix, suffix, and substring queries are public preview functionality.
Do not use them in production or expect data compatibility with the GA design. A collection
that enables the preview will have to be dropped.

For `mongosh`, provide the Automatic Encryption Shared Library 8.2 or newer:

```console
mongosh --cryptSharedLibPath /path/to/mongo_crypt_v1.so
```

### Route around affected `mongocryptd` releases

- On Windows, `mongocryptd` 8.2.0 does not start with `--logpath NUL`. This also breaks the
  .NET/C# driver's default launch. Use a real log path, use the Automatic Encryption Shared
  Library, or upgrade to 8.2.1 or newer.
- Releases 8.2.4 and 8.2.5 limit `mongocryptd` messages to 16 KiB. Skip those releases or use
  the shared library when encrypted commands can be larger.

### Mitigate the 8.2.0 spill-session crash

MongoDB 8.2.0 can crash when more than 1000 memory-intensive queries are spilling at once.
Raise `spillWiredTigerSessionMax` as the documented mitigation, and prefer a fixed maintenance
release when possible.

### Enforce the trim character-set limit

Starting in 8.2.8, the `chars` argument to `$trim`, `$ltrim`, and `$rtrim` cannot exceed 4096
characters. Validate generated character sets before sending a pipeline.

## Upgrade and downgrade guardrails

Before upgrading an 8.0 deployment to 8.2, ensure the feature compatibility version is `8.0`:

```javascript
db.adminCommand({ getParameter: 1, featureCompatibilityVersion: 1 })
```

Apply all of these constraints:

- Only a single-version downgrade from 8.2 to 8.0 is supported.
- Community Edition does not support binary downgrades.
- FCV cannot be downgraded to or from a minor release.
- After changing FCV, an Enterprise binary downgrade requires support assistance.

## Changed defaults and operational semantics

### Protect secondary reads during orphan cleanup

`terminateSecondaryReadsOnOrphanCleanup` defaults to `true`. During migrated-range cleanup,
MongoDB terminates secondary reads that started before the chunk migration committed and are
still active before orphaned documents are deleted. This avoids the older behavior in which
those reads could silently omit the documents.

The default `orphanCleanupDelaySecs` is therefore `3600`, increased from `900`. Account for the
longer retention window when sizing storage and planning cleanup.

### Rebuild affected geospatial indexes

When a document contains both GeoJSON and legacy numeric coordinates, geospatial index key
generation prioritizes GeoJSON. Rebuild affected indexes and verify query results if existing
keys depended on legacy numeric coordinates appearing first.

### Size initial-sync index builds deliberately

In 8.2, 8.0.13, and 7.0.26, initial-sync index builds use 10% of available RAM by default,
bounded by 200 MB and 16 GB. Tune the policy with:

- `initialSyncIndexBuildMemoryPercentage`
- `initialSyncIndexBuildMemoryMinMB`
- `initialSyncIndexBuildMemoryMaxMB`

## High-value query and aggregation features

### Use server time in a pipeline

`$currentDate` returns the current time on the server:

```javascript
db.events.aggregate([
  { $project: { observedAt: { $currentDate: {} } } }
])
```

### Accumulate arrays directly

Use `$concatArrays` or `$setUnion` as accumulators:

```javascript
db.events.aggregate([
  {
    $group: {
      _id: "$tenant",
      all: { $concatArrays: "$values" },
      unique: { $setUnion: "$values" }
    }
  }
])
```

### Allow nullable `$merge` keys only with the right index

Fields named by `$merge.on` may be missing or `null` when the supporting index is non-sparse.
A sparse supporting index does not permit this behavior. Inspect the actual index before
depending on nullable merge keys.

### Inspect the cluster catalog

Use `$listClusterCatalog` as a database-level aggregation stage:

```javascript
db.aggregate([{ $listClusterCatalog: {} }])
```

### Use Search on eligible standard views

Search-index create, update, drop, and list operations work on standard views only when the
view pipeline contains `$addFields`, `$set`, or `$match` wrapping `$expr`. Eligible views can
run `$search`, `$searchMeta`, and `$vectorSearch`; explain output includes execution statistics
for these stages.

## Storage and compression configuration

WiredTiger can size its cache as a percentage. Configure either
`--wiredTigerCacheSizePct` or `storage.wiredTiger.engineConfig.cacheSizePct`.
`storage.wiredTiger.engineConfig.zstdCompressionLevel` accepts values from `-7` through `22`;
negative levels exchange compression ratio for faster compression and decompression.

```yaml
storage:
  wiredTiger:
    engineConfig:
      cacheSizePct: 50
      zstdCompressionLevel: -3
```

## Connection and cache-warming controls

Enable ingress connection-establishment limiting when connection surges threaten CPU:

- `ingressConnectionEstablishmentRateLimiterEnabled`
- `ingressConnectionEstablishmentRatePerSec`
- `ingressConnectionEstablishmentBurstCapacitySecs`
- `ingressConnectionEstablishmentMaxQueueDepth`

Use the related `serverStatus` connection and ingress-session queue fields to observe
admissions, rejections, exemptions, disconnects, queue time, and tokens.

`mirrorReads.targetedMirroring` can select tagged nodes, including hidden nodes. Mirroring may
originate from a primary or a secondary, allowing selected node caches to be warmed.

## Validation and API additions

- `validationAction: "errorAndLog"` rejects an invalid insert or update and logs the violation.
- `renameCollection` and `db.collection.renameCollection()` are part of Stable API V1.
- One `$lookup` can reference multiple encrypted collections under Client-Side Field Level
  Encryption or Queryable Encryption.
- `setQuerySettings` accepts a comment so the operational reason travels with the setting.

```javascript
db.runCommand({
  collMod: "orders",
  validationAction: "errorAndLog"
})
```

## Observability checkpoints

- `$queryStats` includes shapes for `count` and `distinct`, plus execution-ticket delinquency
  counts and durations.
- Slow-log `durationMillis` includes authorization and command-parsing time.
- Low disk space causes disk-spilling queries to fail; log and explain spill field names differ
  as detailed in the observability reference.
- `$currentOp.versionContext` exposes operation FCV information.
- `connectionStatus.authInfo.UUID` identifies the current client connection.
- `validate.indexDetails` includes index specifications, and `validate.repairMode` reports
  attempted inconsistency repairs.
- `serverStatus` includes expanded query, plan-cache, spilling, replication, transaction,
  connection, network-timing, and WiredTiger metrics.

## Verification checklist

- Confirm exact server, shell, encryption-library, and kernel versions before deployment.
- Verify FCV before an upgrade and recheck edition-specific downgrade support before rollback.
- Rebuild and test mixed-format geospatial indexes.
- Load-test initial sync, query spilling, and connection admission with production-like limits.
- Treat preview encrypted string-query collections as temporary and disposable.
- Verify index sparsity before allowing missing or null `$merge.on` values.
- Recheck telemetry parsers for expanded fields and changed duration semantics.
- Open the matching topic reference before changing a parameter or relying on a new output field.
