---
name: elasticsearch-knowledge-patch
description: Elasticsearch
version: "9.4.0"
license: MIT
metadata:
  author: Nevaberry
---


# Elasticsearch Knowledge Patch

Use this skill when implementing, upgrading, or operating Elasticsearch and
the answer may depend on recent API, mapping, query-language, inference,
vector-search, lifecycle, security, or platform behavior. Start with the
breaking-change and deprecation checks, then load every topic reference that
matches the task.

## Reference index

| Reference | Topics |
|---|---|
| [breaking-changes.md](references/breaking-changes.md) | Removed APIs and settings, changed defaults, migration requirements, protocol and response changes |
| [data-mappings-and-ingest.md](references/data-mappings-and-ingest.md) | Data streams, failure stores, mappings, time-series data, ingest processors, LogsDB, and OTLP |
| [deprecations-and-known-issues.md](references/deprecations-and-known-issues.md) | Deprecation migrations, affected-version defects, workarounds, and fixed versions |
| [esql.md](references/esql.md) | ES|QL commands, joins, functions, time-series analytics, external sources, PromQL, and partial results |
| [inference.md](references/inference.md) | Inference tasks, providers, endpoint controls, chunking, credentials, and semantic defaults |
| [lifecycle-snapshots-and-storage.md](references/lifecycle-snapshots-and-storage.md) | ILM, downsampling, reindexing, snapshots, repositories, transforms, and index controls |
| [search-and-vectors.md](references/search-and-vectors.md) | Retrievers, rescoring, dense and sparse vectors, semantic fields, cross-project search, and diagnostics |
| [security-cluster-and-operations.md](references/security-cluster-and-operations.md) | Authentication, authorization, TLS, cluster APIs, runtime baselines, metrics, connectors, and operational settings |

## Triage breaking changes first

Before an upgrade or rollout, inspect
[breaking-changes.md](references/breaking-changes.md) in full. In particular:

- Treat ES|QL and EQL results as potentially partial unless the request or
  cluster setting explicitly requires completeness; always inspect the
  partial-result indicator.
- Quote an ES|QL remote index pattern as one unit or leave the entire pattern
  unquoted. Do not quote only the remote or index component.
- Expect timeouts to return HTTP 429, invalid ingest simulation to return
  HTTP 400, and byte-size parsing to accept at most two decimal places.
- Plan for vectors to be excluded from `_source` by default on new indices,
  while reindexing still carries vector values.
- Reconfigure `discovery-ec2` for AWS SDK v2 and IMDSv2, remove unsupported
  credentials and protocol settings, and supply both access-key fields or
  neither.
- Add explicit force merging after ILM downsampling when the policy requires
  merged output; downsampling no longer force-merges by default.
- Remove APIs and options that no longer exist: the unfreeze endpoint,
  `_knn_search`, highlighting `force_source`, alias `local`, ingest
  `user_agent.ecs`, and the removed GeoIP fallback option.
- Remove retired settings including `client.type`, `tracing.apm.*`, and
  `xpack.searchable.snapshot.allocate_on_rolling_restart`.
- Validate TLS configurations without TLSv1.1 or `TLS_RSA`, and provide a bind
  password whenever LDAP or Active Directory uses a bind DN.

## Migrate deprecated behavior

Before introducing or retaining a dependency, read
[deprecations-and-known-issues.md](references/deprecations-and-known-issues.md).
High-priority migrations include:

- stop building operations around the ES|QL query log;
- replace the deprecated `logs` data-stream type with a supported stream type;
- omit `aggregate_metric_double.default_metric` from new mappings;
- replace ILM's deprecated `max_size` rollover condition;
- pass strict `true` or `false` values to plugin analysis settings and boolean
  system properties;
- remove `indices.merge.scheduler.use_thread_pool`;
- list ES|QL `METADATA` fields directly, without brackets;
- retire dependencies on the machine-learning flush API, the `elser`
  inference service, and Behavioral Analytics CRUD APIs.

## Handle partial and asynchronous results deliberately

- Async ES|QL can return partial results on demand, formats async-get output,
  and reports cross-cluster metadata while work is in progress.
- ES|QL may return partial results by default. Set
  `allow_partial_results=false` per request or
  `esql.query.allow_partial_results: false` cluster-wide when correctness
  requires every shard or cluster.
- With `skip_unavailable: true`, remote runtime failures—including a missing
  index—become non-fatal and the remote cluster is marked skipped or partial.
- EQL defaults `allow_partial_search_results` to `true`; opt out for
  all-shards-required workflows.
- Async result retrieval can use `return_intermediate_results`, and async task
  status exposes `keep_alive`.

## Use current ES|QL primitives

Read [esql.md](references/esql.md) before composing recent pipelines.

- Use `LOOKUP JOIN` for lookup-index enrichment; it supports aliases, mixed
  numeric keys, multiple fields, remote input, and preview expression
  predicates, subject to the documented index-mode and remote-enrich rules.
- Use `FORK` to branch every input row and merge results with an `_fork`
  discriminator. Cross-cluster branches are supported.
- Use `INLINE STATS` for inline grouped analytics, `LIMIT BY` for per-group
  limits, and `SET approximate` for approximate analysis where preview status
  is acceptable.
- Use `METRICS_INFO` and `TS_INFO` after `TS` to discover metrics and series.
- Use `PROMQL` and the Prometheus-compatible plugin endpoints only with their
  technical-preview status in mind.
- Use `TEXT_EMBEDDING`, `RERANK`, vector functions, and dense-vector
  expressions with their current availability and usage constraints.
- Expect `RENAME` to process sequentially and text output to omit null columns.

## Configure semantic and vector search consciously

Read [search-and-vectors.md](references/search-and-vectors.md) and
[inference.md](references/inference.md) together for semantic search.

- `semantic_text` is generally available and participates in `match`,
  `sparse_vector`, kNN, highlighting, multi-fields, and the text field family.
- New `semantic_text` fields use current inference, DiskBBQ, BFloat16, and
  chunking defaults; pin choices explicitly when stable behavior matters.
- DiskBBQ is designed for lower-memory search, accepts floating-point vectors,
  uses quantization, and should not be the automatic choice for
  low-dimensional data.
- Tune DiskBBQ with `num_candidates` or `visit_percentage`; configure its
  quantization level where supported.
- Use `on_disk_rescore` when raw vectors exceed RAM. Use direct I/O only after
  evaluating whether vectors fit in memory, because it can trade page-cache
  pressure for slower searches.
- Set `oversample: 0` to bypass quantized-vector oversampling and rescoring.
- Account for the Enterprise-license requirement before creating new
  DiskBBQ indices migrated from affected earlier versions.

## Build reliable data-stream and ingest flows

Read [data-mappings-and-ingest.md](references/data-mappings-and-ingest.md).

- Enable failure stores through data-stream options for existing streams or
  `template.data_stream_options.failure_store.enabled` for new streams.
- Query rejected documents with the `::failures` selector and remediate them
  with `recover_failure_document`.
- Do not assume a failure-store write is an error response: eligible new log,
  telemetry, and APM streams can return `201 Created` with
  `"failure_store": "used"`.
- Use `include_source_on_error` to control source exposure in parse errors.
- Use ingest simulation's effective mapping and merge behavior to validate
  pipelines; malformed processors now fail simulation with HTTP 400.
- Treat OTLP histograms as `exponential_histogram` by default and use the
  field's supported ES|QL aggregations.
- Check LogsDB, TSDB, synthetic-source, doc-values-skipper, sequence-number,
  and synthetic-ID defaults instead of carrying assumptions from older
  indices.

## Plan lifecycle and repository changes

Read [lifecycle-snapshots-and-storage.md](references/lifecycle-snapshots-and-storage.md)
before changing retention, migration, or backup policy.

- Use `index.lifecycle.skip` to exclude a single index from ILM.
- Account for automatic unfollow ordering before downsampling and for the
  leader time-series end-time wait.
- Choose the downsampling method explicitly and decide whether an ILM force
  merge is needed.
- Test S3 repository configuration after the AWS SDK v2 migration. Use IMDSv2,
  conditional-write protections, idle-timeout controls, and API-call timeouts
  as appropriate.
- Filter snapshots by `state` and use `replicate_for` when searchable-snapshot
  replication must persist for a defined duration.
- Review the known GCS ADC, S3 analysis, upgrade, merge, and low-disk defects
  before operating on affected versions.

## Verify security and platform assumptions

Read [security-cluster-and-operations.md](references/security-cluster-and-operations.md)
for cluster or deployment work.

- Store secure settings through Elasticsearch's secure-settings mechanism,
  never in YAML.
- Treat Entitlements—not the Java SecurityManager—as the runtime permission
  system, and preserve exact filesystem path casing on Windows.
- Recheck connector roles, cross-cluster key trust and signing, SAML/JWT
  behavior, API-key cloning, and service-account-token availability.
- Expect the bundled JDK, Lucene baseline, container base, and FIPS defaults to
  affect plugins, images, and compliance validation.
- Inspect thread-pool utilization and queue latency, indexing pressure,
  document expansion, document-size limits, query logs, and watchdog hot
  threads when diagnosing load.

## Check affected-version defects

Do not deploy a workaround without matching its exact affected version in
[deprecations-and-known-issues.md](references/deprecations-and-known-issues.md).
That reference contains exact fixed versions and, where required, JVM policy
or logger overrides for trained-model limits, GCS ADC, mixed GPU clusters,
node-shutdown metadata, DiskBBQ licensing, TSDB/LogsDB merges, direct I/O,
low-disk shard closure, ES|QL grouping, Windows entitlements, Active Directory,
Watcher templates, and S3 repository analysis.
