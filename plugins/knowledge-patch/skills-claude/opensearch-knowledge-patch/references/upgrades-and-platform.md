# Upgrades and Platform Compatibility

Use this reference for runtime baselines, removed behavior, index compatibility, client parsing, and migration checks.

## Runtime, packaging, and operating systems

### Java and Lucene

- In 3.0.0, OpenSearch requires JDK 21 and uses Lucene 10.1.0.
- OpenSearch and OpenSearch Dashboards announced in 2.19.0 that Ubuntu 20.04 support would be deprecated. Dashboards also announced Amazon Linux 2 deprecation as its Node.js baseline moved beyond Node.js 18.
- In 3.5.0, Dashboards deprecates Node.js 20 while moving to Node.js 22. Its bundler changes from Webpack 4 to the webpack-compatible Rspack without observed customer-facing API breaks.
- In 3.8.0, OpenSearch announces the planned deprecation of Amazon Linux 2 as a build image and supported OS after its June 30, 2026 end of life. Plan an OS migration.

### Artifact signing

Artifacts for 3.0.0 and later use the `release@opensearch.org` PGP key, which expires March 6, 2027. The `opensearch@amazon.com` key remains for 2.x artifacts.

## Index and data compatibility

### Reindex before 3.0

OpenSearch 3.0.0 cannot open indexes created before 2.x, including system indexes. Reindex all of them before upgrading.

When migrating from Elasticsearch OSS 6.8 to OpenSearch 1.x, audit each document for the total count of nested JSON objects across all fields. Elasticsearch 6.8 did not enforce OpenSearch's default `index.mapping.nested_objects.limit` of 10,000, and an over-limit document can block shard relocation.

### JSON and document limits

OpenSearch 3.0.0 limits object and array nesting to 1,000 levels. Property names are limited to 50,000 bytes or characters depending on the input source. Bulk indexing also enforces a 512-byte `_id` limit. Reshape or reject incompatible content before upgrade.

### Searchable snapshots

In 3.0.0, searchable snapshots cannot run on nodes with the `search` role. Every node that handles their shards must have the `warm` role.

### Date-field skip lists

OpenSearch 3.3.1 automatically sets `skip_list=true` for new `@timestamp` fields created since 3.3.0. Existing indexes with `@timestamp` or index-sort date fields retain `skip_list=false`; test upgraded and newly created indexes separately.

### Romanian analyzer

The 3.0.0 `romanian` analyzer normalizes cedilla forms to modern comma-based Unicode characters. Reindex existing Romanian text to keep analysis consistent across old and new documents.

## Removed and renamed configuration

### Core removals

OpenSearch 3.0.0 removes:

- the deprecated `_bulk` `batch_size` parameter;
- the `mmap.extensions` setting;
- the `transport-nio` plugin;
- the `compatibility.override_main_response_version` switch;
- REST access to system indexes.

Nested queries also gain a maximum depth. An empty role list now explicitly configures a coordinating-only node:

```yaml
node.roles: []
```

### Tokenizers and scoring

- In 3.0.0, use `path_hierarchy`; the camel-case `PathHierarchy` tokenizer name is deprecated.
- The default scorer changes from `LegacyBM25Similarity` to `BM25Similarity` in 3.0.0. Recheck score-sensitive tests and thresholds.

### Workload-group rename

OpenSearch 3.0.0 renames query groups to workload groups:

| Old | New |
| --- | --- |
| `wlm/query_group` | `wlm/workload_group` |
| `queryGroupID` | `workloadGroupID` |
| `wlm.query_group` settings prefix | `wlm.workload_group` settings prefix |

### Security and SQL terminology

- The 3.0.0 Security plugin removes its OpenSSL provider and replaces whitelist settings with allowlist settings.
- SQL removes `plugins.sql.pagination.api`, deprecated OpenDistro endpoints, and legacy `opendistro`-prefixed settings in 3.0.0. Scroll pagination is deprecated and Point in Time is the default.

### Discover removals

OpenSearch Dashboards 3.0.0 removes the `discover:newExperience` setting and the DataGrid table feature. Update saved workflows that depend on either.

### Agent tool replacement

ML Commons removes `CatIndexTool` in 3.0.0. Use `ListIndexTool` in agent and tool configurations.

## Response and behavior compatibility

### Nodes API indexing buffers

In 3.0.0, `total_indexing_buffer_in_bytes` is a raw number such as `53687091`; `total_indexing_buffer` is formatted text such as `51.1mb`. Update consumers that assumed the inverse or parsed both as one format.

### Wildcard queries

The 2.5 fix for `case_insensitive` wildcard queries on text fields removes matches that earlier releases returned incorrectly. Expect some result sets and tests to shrink after upgrade.

### Blake2b salts

The 3.0.0 Security plugin corrects Blake2b salt handling, so identical inputs can hash differently than on older versions. Adjust integrations and fixtures that compare generated hashes.

### Cardinality execution hints

OpenSearch 2.19.1 adds a cardinality-aggregation execution hint. Only send it to versions that support the option.

## Plugin and application transitions

### Notification dependencies in 2.0

Alerting notification actions require the `notifications-core` and `notifications` backend plugins. Dashboards management also requires `notificationsDashboards`.

### OpenSearch 3.0 migration notices from 2.19.0

- Performance Analyzer RCA is replaced by Telemetry.
- Gantt Charts is removed from the Dashboards bundle.
- Legacy Observability notebooks are unsupported.
- SQL deprecates its OpenSearch DSL format and several settings, and removes the SparkSQL connector and `DELETE`.
- k-NN deprecates NMSLIB in favor of Faiss or Lucene.

### Feature lifecycle checkpoints

- Search Relevance Workbench becomes generally available in 3.5.0.
- Pull-based ingestion becomes generally available in 3.6.0 and adds warmup settings and adaptive shard selection.

## Nested text-embedding migration

In 2.19.0, the `text_embedding` processor stops substituting nested `_ingest._value` paths. Map the complete nested input path:

```json
"field_map": {
  "books.title": "title_embedding"
}
```
