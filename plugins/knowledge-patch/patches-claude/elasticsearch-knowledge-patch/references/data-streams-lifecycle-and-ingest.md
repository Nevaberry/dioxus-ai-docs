# Data Streams, Lifecycle, Reindexing, and Ingest

## Failure stores

### Enable and query rejected documents

Failure stores redirect documents rejected by ingest pipelines or mapping
conflicts. For an existing data stream (since 8.19.0):

```http
PUT _data_stream/logs-test-apache/_options
{
  "failure_store": {
    "enabled": true
  }
}
```

For new streams, set
`template.data_stream_options.failure_store.enabled` in a component or index
template. Query backing failure indices through `::failures`, for example
`logs-*::failures` in search or
`FROM my_data_stream*::failures` in ES|QL.

### Defaults, lifecycle, and recovery

Dedicated failure-store lifecycle configuration and default failure-index
retention are available since 9.1.0. The get data stream API also reports each
stream's index mode.

Since 9.2.0, new `logs-*-*`, OTel, and APM data streams enable failure stores
by default. When an invalid document is redirected for a matching new log
stream, indexing returns `201 Created` with `"failure_store": "used"` rather
than `400 Bad Request`. Existing streams still need explicit enablement.

The `recover_failure_document` processor can remediate failure-store documents.
Conditional processors can use the Fields API. Since 9.4.0, failure-store
indices can participate in cross-cluster search.

## Data-stream controls

### Streams and stream types

The data-stream `streams` feature (9.2.0) can be enabled only when no
conflicting indices exist. After enablement, indexing is restricted to child
streams. Data streams add `logs.otel` and `logs.ecs` stream types in 9.4.0.
The older `logs` stream type is deprecated.

### Migration reindexing

Since 9.0.0, REST and action support can create an index from a source index and
query, cancel, or throttle data-stream migration reindexing through
`requests_per_second`. `_create_from` removes index blocks by default; control
that behavior with `remove_index_block`. Migration ignores closed source
indices and filters deprecated settings from the destination.

Remote reindex accepts a convenience API-key parameter in 9.3.0. In 9.4.0,
remote reindexing adds a blocklist setting.

## ILM and data-stream lifecycle

### Searchable snapshots and per-index skipping

The ILM `searchable_snapshot` action accepts `replicate_for` (9.0.0).
Set `index.lifecycle.skip: true` to exclude an individual index from ILM
processing (9.1.0):

```http
PUT my-index/_settings
{
  "index.lifecycle.skip": true
}
```

### Time-series ordering

Before downsampling, ILM inserts an unfollow action when required. A follower
also waits for the leader's time-series end time before unfollowing (9.1.0).
ILM explain responses include `age_in_millis`, and the read-only action sets
`indexing_complete` to `true` (9.2.0).

### Downsampling methods and force merge

Data-stream lifecycle and ILM can select a downsampling method, and the
Downsample API has another sampling method (9.3.0). Force merge moved out of
the downsampling request and into the ILM action, where it can be disabled.

From 9.4.0, the downsample action defaults to leaving the result unmerged. Set
its `force_merge_index` parameter to `true` or add an explicit force-merge
action when a merged result is required. The `aggregate` downsampling method
stores the first counter value and auxiliary documents for detected resets so
rate calculations preserve resets; `last_value` retains storage-oriented
behavior.

### Rollover policy maintenance

ILM `max_size` is deprecated from 9.3.0. Replace it with supported rollover
conditions rather than aggregate index size.

## Index blocks, transforms, and long-running tasks

### Remove one block

The remove-block API deletes a named index block (9.1.0):

```http
DELETE /my-index/_block/write
```

### Transform behavior

Transforms add upgrade mode, automatic migration of `max_page_search_size`,
and `extended_stats` in 9.0.0. If a transform destination is an alias,
`delete_dest_index=true` deletes the alias's write index. A transform
preview-index request is available in 9.3.0.

The stop-datafeed API accepts `close_job` in 9.3.0. Stateful cross-cluster use
disables `_delete_by_query` and `_update_by_query`.

## Ingest processors and simulation

### Reroute, append, and CEF

The reroute processor can set `type`, and ingest simulation returns ignored
fields (9.0.0). The append processor gains `copy_from` and an option to ignore
empty values in 9.2.0.

The `cef` processor (9.3.0) parses Common Event Format into structured device
vendor, product, version, signature ID, name, severity, and extension fields.

### Simulation and validation

The simulate ingest API accepts `merge_type` and returns the effective mapping
in 9.2.0. It returns HTTP 400 for an invalid processor. Index templates,
component templates, and pipelines expose created and modified timestamps.

The Grok processor gains `validate_only` in 9.4.0, allowing validation without
field extraction. Text-structure endpoints accept nested NDJSON records. The
ICU transform analysis plugin accepts custom rulesets.

### Parse-error and Mustache limits

Create, index, update, and bulk requests accept `include_source_on_error` in
9.0.0. It controls whether parsing-error responses include the source and
defaults to `true`. Use `mustache.max_output_size_bytes` to limit Mustache
script result length.

## Operational behavior around lifecycle work

- Reindex metrics report seconds rather than milliseconds in 9.0.0.
- `replica_unassigned_buffer_time` defaults to five seconds rather than three
  in 9.0.0.
- Get snapshots can filter on the `state` query parameter (9.1.0).
- Persistent-task reassignment during node shutdown becomes opt-in in 9.4.0,
  and shutdown status reports shard snapshot pauses.
