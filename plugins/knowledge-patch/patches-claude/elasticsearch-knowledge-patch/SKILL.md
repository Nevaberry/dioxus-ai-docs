---
name: elasticsearch-knowledge-patch
description: Elasticsearch
version: "9.4.0"
license: MIT
metadata:
  author: Nevaberry
---


# Elasticsearch Knowledge Patch

Use this skill when upgrading, configuring, querying, securing, or operating
recent Elasticsearch clusters. Determine the exact server version, index mode,
license, deployment type, and client behavior first. Then open the topic
reference that matches the task; several defaults and APIs changed more than
once.

## Reference index

| Reference | Topics |
| --- | --- |
| [compatibility-and-known-issues.md](references/compatibility-and-known-issues.md) | Breaking changes, removals, deprecations, upgrade traps, and fixed-version workarounds |
| [data-streams-lifecycle-and-ingest.md](references/data-streams-lifecycle-and-ingest.md) | Data streams, failure stores, ILM, downsampling, reindexing, transforms, and ingest |
| [esql-and-querying.md](references/esql-and-querying.md) | ES\|QL commands, functions, joins, partial results, cross-cluster behavior, EQL, and external sources |
| [mappings-time-series-and-observability.md](references/mappings-time-series-and-observability.md) | Mappings, TSDB, LogsDB, histograms, metrics, Prometheus, OTLP, and diagnostics |
| [search-vectors-and-inference.md](references/search-vectors-and-inference.md) | Search, retrievers, vectors, semantic text, reranking, and inference integrations |
| [security-cluster-and-storage.md](references/security-cluster-and-storage.md) | Security, TLS, entitlements, cluster APIs, cross-project routing, snapshots, and repositories |

## Upgrade checks that prevent breakage

### Treat partial results as an explicit policy

ES|QL responses may be partial by default. Inspect `is_partial`; set
`allow_partial_results=false` per request or
`esql.query.allow_partial_results: false` cluster-wide when completeness is
required. EQL likewise defaults `allow_partial_search_results` to `true`.
With remote-cluster `skip_unavailable: true`, runtime failures, including a
missing index, can produce a skipped or partial cluster instead of a fatal
response.

### Revalidate index patterns and removed request options

Quote an entire ES|QL remote pattern or none of it: both
`FROM "remote:index"` and `FROM remote:index` are valid, while
`FROM remote:"index"` is not. Parentheses require quoting. Remove these legacy
uses:

- highlighting `force_source`;
- alias API `local`;
- the unfreeze endpoint and reads from frozen indices;
- the technical-preview `_knn_search` API;
- Watcher search `types`;
- `user_agent.ecs` and the removed GeoIP fallback option;
- metadata-field `type`, `fields`, `copy_to`, and `boost` definitions.

The `_source.mode` mapping attribute is a no-op. `random_score` without a field
now uses `_seq_no`, and `date_histogram` rejects boolean values.

### Account for changed defaults

- New indices exclude vectors from `_source` by default.
- LogsDB and TSDB text fields omit norms.
- Eligible `logs-*-*` data streams enable LogsDB by default.
- ES|QL and EQL permit partial results by default.
- Timeouts return HTTP 429, and byte sizes accept at most two decimal places.
- JDK 24 removes `TLS_RSA` ciphers and TLSv1.1 from defaults.
- A bind DN without its bind password prevents LDAP or Active Directory startup.
- API request `secret_parameters` cannot be overridden in 9.3.8 and 9.4.4.

### Make downsampling policy explicit

Starting in 9.4.0, ILM downsampling no longer force-merges its result by
default. Add a force-merge action or set `force_merge_index: true` when the old
behavior is required. OTLP histograms now map to `exponential_histogram`, and
normalized `keyword` fields use native synthetic source.

### Rework EC2 discovery configuration

`discovery-ec2` uses AWS SDK v2 and requires IMDSv2. It ignores
`discovery.ec2.protocol`; put `http://` in `discovery.ec2.endpoint` when needed.
Remove `aws.secretKey` and
`com.amazonaws.sdk.ec2MetadataServiceEndpointOverride`. Configure both
`discovery.ec2.access_key` and `discovery.ec2.secret_key`, or neither.

### Review platform and allocation removals

Remove `cluster.routing.allocation.disk.watermark.enable_for_single_data_node`.
Do not expect cluster state in `/_cluster/reroute` responses. Also remove
`client.type`, `tracing.apm.*`, and
`xpack.searchable.snapshot.allocate_on_rolling_restart`. Machine learning is
disabled on macOS x86_64, and the old `data_frame_transforms` roles are gone.

## Deprecation priorities

- Do not build new automation around ES|QL query logging; its use is deprecated
  from 9.4.2.
- Avoid the deprecated `logs` data-stream type and
  `aggregate_metric_double.default_metric` mapping parameter.
- Replace ILM `max_size` rollover conditions and remove
  `indices.merge.scheduler.use_thread_pool`.
- Supply strict `true` or `false` values in plugin analysis settings and boolean
  system properties.
- In ES|QL, write `METADATA _id, _index` without brackets.
- Migrate from the machine-learning flush API, the `elser` inference service,
  and Behavioral Analytics CRUD APIs.
- Recheck authorization assumptions around the built-in `reporting_user` role,
  which now derives authorization from reserved Kibana privileges.

## Known-version hazards

### Upgrade rather than preserve faulty behavior

- Upgrade 9.3.6 to 9.3.7 when valid trained-model requests hit overly strict
  field limits.
- Upgrade `repository-gcs` users of Application Default Credentials from 9.2.8
  to 9.2.9 or from 9.3.3 to 9.3.4; the compatibility reference contains the
  temporary entitlement-policy values.
- Upgrade mixed-GPU clusters from 9.3.1 to 9.3.2 to stop repeated usage
  serialization warnings.
- Do not upgrade directly from 9.1.10 to 9.2.4; use 9.2.5 or later.
- Upgrade shrunk TSDB or LogsDB indices from 9.1.0/9.1.1 to 9.1.2 before relying
  on force merge.
- On 9.1.0, disable `vector.rescoring.directio` when in-memory `bbq_hnsw`
  searches regress; remove the override in 9.1.1.
- On 9.0.3, keep `indices.merge.disk.check_interval` at `0s` to avoid shard-close
  hangs under low disk.

### Query correctness and old-cluster history

Two-key ES|QL `STATS` grouping can be wrong before 8.17.9, 8.18.7, and 9.0.4
when the first keyword has more than 65,000 values. Upgrade, put the
lower-cardinality key first, or filter cardinality. Match Windows filesystem
casing exactly under 9.0 entitlements. A cluster that once ran 7.10.0–7.12.1
may need stale Watcher templates deleted before Watcher can start.

## High-value capabilities

### Failure-store workflow

Enable a data-stream failure store through `PUT _data_stream/<name>/_options`
or `template.data_stream_options.failure_store.enabled`. Query failed documents
with `::failures`. New log, OTel, and APM streams may enable failure stores by
default; use `recover_failure_document` to remediate documents. Failure stores
have dedicated lifecycle controls and can participate in cross-cluster search.

### ES|QL joins, branches, views, and metrics

Use `LOOKUP JOIN` to enrich rows from lookup indices; later behavior supports
aliases, mixed numeric keys, multiple join fields, remote input, and expression
predicates. `FORK` runs rows through branches and adds `_fork`. Views expose
reusable pipelines as virtual indices, but cannot be queried with document- or
field-level security. `PROMQL`, `METRICS_INFO`, and `TS_INFO` support metrics
workflows; verify technical-preview status before making compatibility promises.

### Time-series storage and downsampling

Use `exponential_histogram` for OTel histograms and the T-Digest field type for
time-series metrics. Doc-values skippers default on for TSDB and LogsDB but are
off generally. Synthetic TSDB IDs avoid indexing `_id`; new TSDB indices disable
sequence numbers. The aggregate downsampling method preserves counter resets,
while `last_value` keeps its storage-oriented behavior.

### Vector search and semantic defaults

`semantic_text` integrates mapping and inference and supports standard text,
sparse-vector, kNN, highlighting, multi-fields, and configurable chunking.
Recent new fields default to DiskBBQ, BFloat16, and the Jina v5 inference
configuration. DiskBBQ is designed for lower memory use; tune kNN with
`num_candidates` or `visit_percentage`, and avoid it for low-dimensional
vectors. Check licensing when carrying `bbq_disk` indices forward from 9.2.

### Retriever and reranking choices

Choose RRF for rank fusion, linear retrievers for weighted normalized scores,
generic rescorers for request rescoring, `text_similarity_reranker` for semantic
reranking, and MMR for diversification. Search also supports pinned and scripted
retrievers, multi-vector `rank_vectors`, quantized-vector rescoring, and
contextual `chunk_rescorer` snippets.

## Working checklist

1. Read the server version from the cluster, not just a client dependency.
2. Identify index mode: standard, LogsDB, TSDB, lookup, failure store, or
   synthetic source.
3. Check whether the feature is generally available, technical preview, or
   experimental in the applicable release.
4. For distributed queries, decide whether partial results are acceptable and
   inspect per-cluster metadata.
5. For mapping changes, verify defaults on newly created indices separately
   from existing mappings.
6. For inference or vector work, verify endpoint task, chunking, vector element
   type, quantization, rescoring, memory, and license.
7. For lifecycle work, distinguish main backing indices from failure-store
   indices and make force merge explicit.
8. For repository or security changes, test credentials, secure settings,
   entitlements, TLS, and cloud SDK migration in a non-production cluster.
9. Before an affected upgrade, read the compatibility reference and choose a
   fixed target release instead of carrying a temporary workaround forward.
