# Lifecycle, Snapshots, Reindexing, and Repositories

## Reindexing and index migration

### Data-stream migration controls (9.0.0)

REST and action APIs can create an index from a source and query, cancel, or
throttle a data-stream migration reindex with `requests_per_second`.
`_create_from` removes index blocks by default; control this with
`remove_index_block`. Migration ignores closed source indices and filters
deprecated settings from the destination.

### Remove an index block (9.1.0)

Use the remove-block API for a named block:

```http
DELETE /my-index/_block/write
```

### Reindex API controls (9.3.0 and 9.4.0)

Remote reindex accepts a convenience API-key parameter as of 9.3.0. It gains a
remote blocklist setting in 9.4.0.

## ILM, data-stream lifecycle, and transforms

### Searchable-snapshot replication (9.0.0)

The ILM `searchable_snapshot` action accepts `replicate_for`.

### Transform upgrade and deletion behavior (9.0.0)

Transforms have upgrade mode, automatic migration of `max_page_search_size`,
and `extended_stats`. When `delete_dest_index=true`, deleting a transform whose
destination is an alias deletes that alias's write index.

### Skip ILM for one index (9.1.0)

Set the index-scoped `index.lifecycle.skip` flag:

```http
PUT my-index/_settings
{
  "index.lifecycle.skip": true
}
```

### Time-series ILM ordering (9.1.0)

ILM injects an unfollow action before downsampling when needed. A follower also
waits until its leader's time-series end time passes before unfollowing.

### Index resolution and lifecycle responses (9.2.0)

`_resolve/index` filters by index mode and returns the mode. ILM explain adds
`age_in_millis`. The read-only action sets `indexing_complete` to `true`.

### Downsampling controls (9.3.0)

Data-stream lifecycle and ILM can choose among downsampling methods, and the
Downsample API adds a sampling method. Force merge moves out of the downsample
request and into the ILM action, where it can be disabled.

### Other lifecycle controls (9.3.0)

The stop-datafeed API accepts `close_job`; transforms add a preview-index
request. Stateful cross-cluster operation disables `_delete_by_query` and
`_update_by_query`.

### Persistent tasks during shutdown (9.4.0)

Persistent-task reassignment during node shutdown is opt-in. Shutdown status
reports shard snapshot pauses.

## Snapshots, archives, and repositories

### Archive compatibility (9.0.0)

Archive and searchable-snapshot indices may come from N-2 versions, including
supported 7.x segment cases used as archives in 8.x or 9.x.

### S3 metadata support (9.0.0)

The `repository-s3` plugin supports IMDSv2.

### `repository-s3` uses AWS SDK v2 (8.19.0)

The plugin migrated from AWS SDK v1 to v2. Because behavior and configuration
differ, test production repository settings before upgrading.

### Snapshot state filtering (9.1.0)

The get snapshots API accepts a `state` query parameter.

### Safer S3 repositories (9.2.0)

S3 repositories use conditional writes to avoid accidental overwrites and
repository corruption, including on fully compatible S3 implementations. The
S3 connection maximum idle time is configurable.

### Repository operational settings (9.3.0)

S3 repositories support an API-call timeout setting.

Known defects affecting GCS ADC and S3 analysis are documented in
[deprecations-and-known-issues.md](deprecations-and-known-issues.md).
