# Storage, Deletion, and Compaction

Use this reference for object-store clients, provider compatibility, index
creation, caching, delete-request persistence, deletion workers, marker storage,
and index-gateway routing.

## Use the shared Thanos object-store clients

Loki moved object-store access to the shared Thanos client in 3.4.0 and added
Swift support through `thanos.io/objstore`. Confirm whether a deployment uses
the Thanos or legacy client before applying provider-specific workarounds.

The storage configuration also gains:

- a request timeout for Alibaba Cloud OSS;
- age-based suppression of cache writeback for chunks fetched from storage;
- an in-memory-only mode for TSDB index creation.

Tune the OSS timeout to the deployment's request behavior. Use cache-writeback
age suppression to avoid repopulating the cache with fetched chunks too old to
be valuable. Treat in-memory TSDB index creation as a memory and durability
choice rather than a generic default.

## Configure storage prefixes

Helm object-store values use `object_store.storage_prefix` instead of
`object_store.prefix` as of 3.5.0. The Thanos object-store configuration accepts
dashes in `storage_prefix` as of 3.6.0. Rename the value and preserve legitimate
dashed prefixes when validating configuration.

## Use provider-specific endpoints and delimiters

As of 3.5.0, the S3 chunk delimiter can be configured for MinIO running on
Windows. Choose a delimiter compatible with that filesystem and keep readers
and writers consistent.

GCS storage can target a custom endpoint as of 3.5.0. Validate endpoint routing,
TLS, authentication, and bucket behavior against the non-default service.

The Operator can configure a TLS CA for Swift as of 3.5.0 and virtual-host-style
S3 access from secrets as of 3.6.0. Inspect the generated client configuration
rather than assuming chart and Operator values have identical shapes.

## Preserve S3 compatibility details

The S3 client preserves a region already supplied by its configuration chain in
3.7.0. Do not overwrite a valid discovered or injected region with an empty or
less-specific value.

Loki 3.7.2 adds a SHA-256 checksum to `PutObject` calls for S3 Object Lock
buckets. Include checksum behavior when testing locked-object uploads against
the target service or emulator.

Loki 3.7.4 fixes index filenames when the legacy S3 client uses
`chunk_delimiter`. Validate filenames and reads when maintaining a legacy-client
deployment with a non-default delimiter.

## Store delete requests in SQLite

Delete requests can use SQLite storage as of 3.5.0. With this backend, Loki
uses each request's stored completion time to reduce the set considered during
query-time filtering. Preserve completion timestamps when operating on the
database, because they affect query filtering work.

## Scale deletion processing horizontally

The experimental 3.6.0 deletion path allows the Compactor to delegate queued
delete work to workers. This helps large deletions and deep backlogs scale out.

Only deletion processing is delegated. Index compaction and retention remain in
the main singleton Compactor. Size and monitor the singleton responsibilities
separately from the worker pool, and do not deploy multiple primary Compactors
on the assumption that all duties became horizontally scalable.

Operator sizing in 3.5.0 keeps delete workers nonzero. Inspect generated values,
especially for small deployment sizes, so delete queues cannot stall through a
zero-worker configuration.

## Put deletion markers in object storage

As of 3.7.0, the Compactor can store chunk-deletion markers in object storage
instead of local disk. Use object-backed markers where workers or restarts must
share durable marker state, and grant the Compactor the required object-store
permissions.

Loki 3.7.4 repairs delete requests made through the Thanos object-store client
when using its filesystem backend. Include that maintenance fix when validating
filesystem-backed Thanos deletion behavior.

## Use index-gateway shuffle sharding

Index-gateway clients support shuffle sharding as of 3.7.0. Configure the shard
strategy with the deployment's tenancy and failure-domain goals, then verify
client routing and gateway availability under partial failure.

## Supply chart storage configuration

The 3.6.0 Helm chart exposes the full storage configuration, can bypass
generated S3, GCS, and Azure settings, and supports separate ruler storage.
When bypassing generated settings, supply every required client and schema
field explicitly.

The 3.7.0 chart no longer requires chunk bucket names when an S3 URL, MinIO, or
local disk is used. It also makes ruler bucket names optional for local ruler
storage. Do not invent placeholder buckets to satisfy obsolete validation.

## Coordinate CLI deletion with storage

`logcli` gains delete commands in 3.6.0. A submitted command creates deletion
work; completion depends on the configured request store, Compactor, workers,
and marker backend. Observe the full lifecycle instead of treating command
acceptance as physical deletion.

## Storage validation checklist

- Identify Thanos versus legacy clients for every object-store path.
- Test OSS timeouts, cache-writeback age, and in-memory index creation under
  realistic load.
- Render `storage_prefix`, endpoint, delimiter, Swift CA, and S3 addressing
  configuration.
- Verify S3 region-chain preservation, Object Lock checksums, and legacy index
  filenames where applicable.
- Preserve SQLite completion times and test query-time delete filtering.
- Exercise deletion backlogs while monitoring both workers and singleton
  Compactor duties.
- Restart deletion components and confirm object-backed markers remain usable.
- Test index-gateway shuffle sharding during gateway loss.
- Follow a CLI delete from submission through completion and query filtering.
