# Sharding, replication, and networking

## Secondary reads during orphan cleanup

`terminateSecondaryReadsOnOrphanCleanup` defaults to `true`. MongoDB terminates secondary reads
that meet all of these conditions:

1. the read began before a chunk migration committed;
2. the read is still active before orphaned documents from the migrated range are deleted; and
3. cleanup of that migrated range is proceeding.

The older behavior could let such a read silently omit those documents. The default
`orphanCleanupDelaySecs` is consequently `3600`, increased from `900`.

Account for terminated reads in retry behavior and for the longer orphan-retention period in
storage planning.

## Initial-sync index-build memory

In 8.2, 8.0.13, and 7.0.26, index builds during initial sync use 10% of available RAM by default.
The default lower and upper bounds are 200 MB and 16 GB. Tune all three parts with:

- `initialSyncIndexBuildMemoryPercentage`;
- `initialSyncIndexBuildMemoryMinMB`; and
- `initialSyncIndexBuildMemoryMaxMB`.

Consider both the percentage and the bounds when predicting memory use on very small or very
large hosts.

## Consistency diagnoses

- MongoDB 8.1 added `CollectionAuxiliaryMetadataMismatch`.
- MongoDB 8.2 added `RangeDeletionMissingShardKeyIndex`. It is reported when a sharded
  collection has a pending range-deletion task but lacks an index compatible with the shard key.

Treat the latter as both an index-definition problem and a blocker for range-deletion work.

## Targeted mirrored reads

`mirrorReads.targetedMirroring` can direct mirrored reads to tagged nodes, including hidden
nodes. Mirroring can originate from a primary or a secondary. This permits deliberate cache
warming of selected replica-set members rather than untargeted mirroring.

## Ingress connection-establishment limiting

MongoDB 8.2 can limit connection establishment to protect CPU during connection surges. The
controls are:

- `ingressConnectionEstablishmentRateLimiterEnabled`;
- `ingressConnectionEstablishmentRatePerSec`;
- `ingressConnectionEstablishmentBurstCapacitySecs`; and
- `ingressConnectionEstablishmentMaxQueueDepth`.

Related `serverStatus` connection and ingress-session queue fields report admissions,
rejections, exemptions, disconnects, queue time, and tokens. Monitor these fields while tuning
the rate, burst window, and maximum queue depth.

## Load-balancer audit identity

From 8.1, audit events for clients that reach `mongos` through a load balancer include both ends
of the proxied hop: the originating client's IP address and port, and the load balancer's IP
address and port. Audit parsers should preserve both identities.

## Sharding executor control

MongoDB 8.2 adds `ShardingTaskExecutorPoolMaxQueueDepth`. Set it only with an understanding of
the expected sharding-task backlog and monitor queue behavior after changing it.
