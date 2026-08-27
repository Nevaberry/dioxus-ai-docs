# Upgrades and Core Compatibility

## Planning major upgrades

### Runtime, artifacts, and index compatibility

OpenSearch 3.0.0 requires JDK 21 and uses Lucene 10.1.0. Verify artifacts from 3.0.0 onward with the `release@opensearch.org` PGP key, which expires March 6, 2027; the `opensearch@amazon.com` key is reserved for 2.x artifacts.

OpenSearch 3.0 cannot open indexes created before 2.x, including system indexes. Reindex all of them before upgrading. System indexes are no longer exposed through REST APIs, so replace direct access with supported plugin interfaces.

The Java Security Manager is replaced by an intercepting Java agent. The policy-file approach remains: grant each codebase only the privileged actions it needs.

### Request and parser limits

For 3.0.0, enforce these limits in producers and migration tests:

- Bulk `_id` values are limited to 512 bytes, and `_bulk` rejects the removed `batch_size` parameter.
- Nested queries have a maximum depth.
- JSON objects and arrays are limited to 1,000 nested levels.
- JSON property names are limited to 50,000 bytes or characters, depending on the input source.

When migrating from Elasticsearch OSS 6.8, audit documents for more than 10,000 nested objects across all fields. OpenSearch enforces the default `index.mapping.nested_objects.limit`, which can otherwise block shard relocation.

### Removed core settings and components

In 3.0.0, remove `mmap.extensions`, the `transport-nio` plugin, and `compatibility.override_main_response_version`. Consumers of the Nodes API must treat `total_indexing_buffer_in_bytes` as a raw byte count such as `53687091` and `total_indexing_buffer` as a human-readable value such as `51.1mb`.

The default scorer changed from `LegacyBM25Similarity` to `BM25Similarity`; compare relevance baselines before rollout. The `PathHierarchy` tokenizer spelling is deprecated; use `path_hierarchy` in new or updated analyzers.

The `romanian` analyzer now normalizes cedilla characters to modern comma-based Unicode forms. Reindex existing Romanian content so analysis is consistent across old and new documents.

### Dashboards and platform transitions

OpenSearch 2.19.0 announced the removal or deprecation of several 3.0-era components: Performance Analyzer RCA is replaced by Telemetry, Gantt Charts leaves the Dashboards bundle, legacy Observability notebooks lose support, SQL's OpenSearch DSL format and several settings are deprecated, the SparkSQL connector and SQL `DELETE` are removed, and NMSLIB is deprecated in favor of Faiss or Lucene.

OpenSearch Dashboards 3.0 removes `discover:newExperience` and the DataGrid table. Saved workflows that use either need adjustment. Ubuntu 20.04 support for OpenSearch and Dashboards and Amazon Linux 2 support for Dashboards were announced for deprecation as the Node.js baseline moved beyond 18.

By 3.5.0, Dashboards deprecates Node.js 20 for Node.js 22 and replaces Webpack 4 with the compatible Rspack bundler, with no observed customer-facing API break. OpenSearch 3.8.0 also announces Amazon Linux 2 deprecation as a build image and supported OS after its June 30, 2026 end of life.

## Configuring node roles and remote storage

### Coordinating-only nodes

Since 3.0.0, an empty role list creates a coordinating-only node:

```yaml
node.roles: []
```

### Searchable snapshots and search-only indexes

In 3.0.0, searchable snapshots require the `warm` role on every node serving their shards; the `search` role is insufficient.

Remote-store clusters can separate indexing and search traffic. The `_scale` API can disable every writer and turn an index search-only. In 3.5.0, Index State Management adds a `search_only` action for the same reader/writer separation, while `convert_index_to_remote` gains an optional `rename_pattern`.

### Index State Management policies

- Since 3.0.0, `unfollow` invokes stop replication for cross-cluster replication.
- Since 3.2.0, transitions accept `no_alias` and `min_state_age`.
- Since 3.4.0, index patterns can contain exclusion patterns.
- Since 3.8.0, rollover conditions accept grouped `any_of` syntax, allowing mixed AND/OR logic in one policy.

The 3.7.0 ISM Simulate API evaluates every transition against live index metrics and reports the next state without changing cluster state.

### Cross-cluster replication

Since 3.7.0, all replication REST APIs accept `cluster_manager_timeout`. Stop, pause, start, and resume can clear stale persistent tasks, and replication no longer changes `number_of_replicas` when the follower uses `auto_expand_replicas`.

Since 3.8.0, start, stop, pause, and resume can target multiple indexes by pattern. Autofollow also accepts `follower_index_pattern` with a `{{leader_index}}` placeholder to prevent follower-name collisions.

## Maintaining analyzers, aggregations, and codecs

### Analyzer resource reloads

In 3.7.0, `_refresh_search_analyzers` accepts `reload_cached_resources` for resources such as Hunspell dictionaries. It also works on metadata-write-blocked indexes, including cross-cluster-replication followers.

### Aggregation execution and streaming

OpenSearch 2.19.1 adds a cardinality-aggregation execution hint. Only send it to versions that support the option.

Since 3.2.0, segment-level partial aggregation results can stream to the coordinating node instead of producing one response per shard, moving high-cardinality reduction work away from data nodes.

Rollups add cardinality metrics and multi-tier rollup support in 3.5.0.

### Date-field skip lists

OpenSearch 3.3.1 automatically gives newly created `@timestamp` fields `skip_list=true` after the 3.3.0 change. Existing indexes with `@timestamp` or index-sort date fields retain `skip_list=false`; test both old and newly created indexes during upgrades.

### Compression and plugin codecs

OpenSearch Custom Codecs adds Intel QAT-accelerated Zstandard compression in 3.1.0. In 3.2.0 it adds composite-index support. The AdditionalCodecs registration path in 3.5.0 lets plugins such as k-NN, Neural Search, and Security Analytics use custom codecs.

## Operating schedulers and snapshots

### Job Scheduler

Since 3.2.0, `IntervalSchedule` accepts seconds. Job Scheduler exposes REST APIs for listing jobs, optionally by node, listing all locks, and retrieving a single lock. A Job History Service follows in 3.3.0.

### Snapshot Management

Since 3.3.0, Snapshot Management can delete snapshots that were created manually.

## Compatibility details that change outputs

### Wildcards and text analysis

The 2.5 correction to `case_insensitive` wildcard queries on text fields can reduce result counts that older behavior returned incorrectly. Update assertions and saved queries rather than assuming equivalent matches.

### Text embedding field maps

Since 2.19.0, the `text_embedding` processor does not substitute nested `_ingest._value` paths. Map the nested source path directly:

```json
"field_map": {
  "books.title": "title_embedding"
}
```

### Workload group and agent-tool renames

OpenSearch 3.0.0 renames query groups to workload groups: `wlm/query_group` becomes `wlm/workload_group`, responses use `workloadGroupID` instead of `queryGroupID`, and related cluster settings move to the `wlm.workload_group` prefix.

The same release removes `CatIndexTool`; agent and tool configuration must use `ListIndexTool`.

### Blake2b hashes

The Security plugin's 3.0.0 Blake2b salt correction can change hashes for identical inputs. Recompute fixtures and integration expectations.

### Geospatial validation

Since 3.5.0, input validation enforces coordinate limits for lines, polygons, and polygon holes. Validate generated geometry before submission.

## Notification plugin prerequisites

OpenSearch 2.0 notification actions require the backend `notifications-core` and `notifications` plugins. Managing notification actions in Dashboards also requires `notificationsDashboards`.
