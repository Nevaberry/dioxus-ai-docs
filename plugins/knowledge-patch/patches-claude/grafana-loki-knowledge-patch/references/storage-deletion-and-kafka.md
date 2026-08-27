# Storage, deletion, and Kafka

## Thanos object-store clients (3.4.0)

Loki moves object-store access to the shared Thanos client and adds Swift
support through `thanos.io/objstore`.

Storage configuration also includes:

- an Alibaba Cloud OSS request timeout;
- age-based suppression of cache writeback for fetched chunks; and
- an in-memory-only mode for TSDB index creation.

Treat these as distinct controls: provider request behavior, cache policy, and
index materialization solve different operational problems.

## SQLite delete-request storage (3.5.0)

Delete requests can be stored in SQLite. With this backend, Loki uses each
request's stored completion time to reduce the requests considered during
query-time filtering.

## Tenant-specific Kafka topics (3.5.0)

Kafka-backed ingestion supports tenant-specific topics. Keep topic selection
aligned with tenant routing and isolation.

## Object-store compatibility controls (3.5.0)

The S3 chunk delimiter is configurable for MinIO running on Windows. GCS
storage can use a custom endpoint. Set these only for the relevant compatible
backend rather than treating them as provider-neutral defaults.

## Horizontally scalable deletion processing (3.6.0)

The experimental horizontally scalable compactor delegates queued deletion
work to workers, allowing large deletes and backlogs to scale out. Index
compaction and retention remain in the main singleton Compactor.

Scale deletion workers independently while preserving the singleton ownership
of index compaction and retention.

## Kafka consumption and block building (3.6.0)

Components can consume Kafka records and maintain multiple Kafka clients. The
Helm chart exposes `block_builder` configuration for deploying the associated
path. Model client ownership, topic routing, consumers, and block builders as
one ingestion design.

## Storage-prefix compatibility (3.6.0)

Thanos object storage accepts dashes in `storage_prefix`. Do not reject an
otherwise valid prefix solely because it contains a dash.

## Object-backed deletion markers (3.7.0)

The compactor can store chunk-deletion markers in object storage rather than on
local disk. This enables marker persistence to follow the object-backed
deployment design.

Loki 3.7.4 repairs delete requests made through the Thanos object-store client
when its filesystem backend is used. Include that repair when this exact
combination is deployed.

## S3 configuration and compatibility (3.7.0)

The S3 client preserves a region already supplied by the configuration chain.
Do not overwrite or duplicate a valid region supplied earlier in that chain.

Loki 3.7.2 adds a SHA-256 checksum to `PutObject` calls for Object Lock
buckets. Loki 3.7.4 fixes index filenames when the legacy S3 client uses
`chunk_delimiter`.

## Helm storage validation (3.7.0)

Chunk bucket names are not required when using an S3 URL, MinIO, or local disk.
Ruler bucket names are optional when ruler storage is local. Keep validation
conditional on the selected storage mode.
