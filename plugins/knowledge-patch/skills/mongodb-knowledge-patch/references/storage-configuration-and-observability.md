# Storage, configuration, and observability

## Percentage-based WiredTiger cache sizing

WiredTiger can size its cache as a percentage. Use the command-line option
`--wiredTigerCacheSizePct` or the configuration key
`storage.wiredTiger.engineConfig.cacheSizePct`.

`storage.wiredTiger.engineConfig.zstdCompressionLevel` accepts values from `-7` through `22`.
Negative levels trade compression ratio for faster compression and decompression.

```yaml
storage:
  wiredTiger:
    engineConfig:
      cacheSizePct: 50
      zstdCompressionLevel: -3
```

## Query-statistics coverage and ticket delinquency

From 8.1, `$queryStats` collects shapes for `count` and `distinct`. In 8.2, its output also
reports execution-ticket waits that take too long through:

- `metrics.delinquentAcquisitions`;
- `metrics.totalAcquisitionDelinquencyMillis`; and
- `metrics.maxAcquisitionDelinquencyMillis`.

Use all three to distinguish frequency, cumulative delay, and worst-case delay.

## Disk-spill behavior and telemetry

From 8.1, MongoDB fails disk-spilling queries when disk space is low instead of continuing to
consume the remaining space.

Slow-query logs expose spill telemetry with an execution-part prefix:

- `<executionPart>Spills`;
- `<executionPart>SpilledBytes`;
- `<executionPart>SpilledDataStorageSize`; and
- `<executionPart>SpilledRecords`.

In 8.2, explain output for spilling stages standardizes the corresponding unprefixed names:

- `spills`;
- `spilledBytes`;
- `spilledDataStorageSize`; and
- `spilledRecords`.

Do not use one parser schema for both slow logs and explain output.

MongoDB 8.2.0 also has a crash condition when more than 1000 memory-intensive queries are
actively spilling. Raising `spillWiredTigerSessionMax` is the documented mitigation.

## Slow-query duration semantics

From 8.1, slow-log `durationMillis` includes authorization and command-parsing time. It therefore
measures more of the complete command duration than before. Revisit alert thresholds and
comparisons with older logs.

## Operation, connection, and validation inspection

- `$currentOp` exposes operation FCV information in `versionContext`.
- `connectionStatus.authInfo.UUID` identifies the current client connection.
- From 8.1, `validate.indexDetails` includes index specifications.
- In 8.2, `validate.repairMode` describes attempted inconsistency repairs.

Update strict decoders before consuming these expanded result documents.

## Expanded `serverStatus` metrics

The 8.2 output adds visibility into:

- range-deletion kills;
- `$bucketAuto` spills;
- cached-plan replanning;
- WiredTiger spilling;
- connection-establishment rate and queue outcomes; and
- average TLS, `hello`, and authentication timing.

Inspect the corresponding areas under `metrics.operation`, `metrics.query.bucketAuto`,
`planCache`, `spillWiredTiger`, `connections`, `queues.ingressSessionEstablishment`, and
`metrics.network`.

The 8.1 additions include:

- `prepareUnique` index tracking;
- pre-image purge and TTL-skip metrics;
- replication timestamps;
- express and idHack fast-path counters;
- expired-transaction kill results; and
- `wiredTiger.version`.

Consumers that enforce a fixed schema should allow these fields before rolling out newer
servers.

## Additional server controls

MongoDB 8.2 adds `ShardingTaskExecutorPoolMaxQueueDepth`.

MongoDB 8.1 adds:

- `enableAutoCompaction`;
- `upsertMaxRetryAttemptsOnDuplicateKeyError`;
- `AbortExpiredTransactionsSessionCheckoutTimeout`;
- `JWKSMinimumQuiescePeriodSecs`;
- catalog-cache collection, database, and index entry limits; and
- `wiredTigerSessionMax`.

Treat these as explicit tuning controls. Preserve exact parameter spelling, validate support on
the running binary, and measure the relevant queue, cache, storage, or transaction behavior
after a change.
