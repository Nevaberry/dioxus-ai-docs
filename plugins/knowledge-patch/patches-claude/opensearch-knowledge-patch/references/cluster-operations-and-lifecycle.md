# Cluster Operations and Data Lifecycle

Use this reference for nodes, remote stores, ingestion, gRPC transport, index policies, replication, schedulers, snapshots, remote metadata, and codecs.

## Node roles, remote store, and sandboxing

### Coordinating-only nodes

In 3.0.0, an empty role list means a coordinating-only node:

```yaml
node.roles: []
```

### Search-only remote-store indexes

OpenSearch 3.0.0 separates indexing and search traffic on remote-store-enabled clusters. The `_scale` API can stop all writers and make an index search-only, allowing independent scaling of reader and writer capacity.

### Java-agent security sandbox

OpenSearch 3.0.0 replaces Java Security Manager with an agent that intercepts privileged calls. The policy-file design remains: grant privileged actions to individual codebases.

## Ingestion and transport

### Pull-based ingestion

- In 3.0.0, disabled-by-default pull ingestion supports Apache Kafka and Amazon Kinesis with native backpressure.
- It becomes generally available in 3.6.0 and adds warmup settings and adaptive shard selection.

### gRPC transport

- In 3.0.0, Protobuf-over-gRPC is disabled by default as an experimental transport.
- In 3.2.0, it becomes production-ready for bulk ingestion, expands search and k-NN coverage, and supports encryption in transit.
- In 3.3.0, search coverage expands to term-level, full-text, geographic, Boolean, script, and nested queries. OpenSearch protobuf Python packages are published to PyPI.
- In 3.4.0, search adds `ConstantScoreQuery`, `FuzzyQuery`, `MatchBoolPrefixQuery`, `MatchPhrasePrefix`, `PrefixQuery`, and `MatchQuery`. Bulk requests accept CBOR, SMILE, and YAML documents.
- In 3.5.0, hybrid queries run over gRPC. Circuit breakers and Security JWT authentication protect the transport.
- In 3.6.0, Security adds Basic authentication for gRPC.
- In 3.8.0, ML Commons adds token-streaming `PredictModelStream` and `ExecuteAgentStream` over Protobuf and HTTP/2.

### Arrow Flight and HTTP/3

- A disabled-by-default 3.3.0 Apache Arrow Flight transport provides secured server-side node-to-node streaming through `StreamTransportService`.
- Server-side HTTP/3 is a disabled-by-default experiment in 3.5.0.

### Streaming aggregation

In 3.2.0, partial segment aggregation results stream to the coordinator rather than returning one response per shard. This moves high-cardinality reduction off data nodes.

## Index State Management and rollups

### Transition and pattern controls

- In 3.2.0, ISM transitions support `no_alias` and `min_state_age`.
- In 3.4.0, index patterns can contain exclusion patterns.
- In 3.8.0, rollover conditions accept `any_of` groups, allowing AND and OR condition groups in one policy.

### Search-only and remote conversion

In 3.5.0, `convert_index_to_remote` accepts optional `rename_pattern`, and a `search_only` action supports reader/writer separation. Rollups add cardinality metrics and multi-tier rollup.

### Policy simulation

The 3.7.0 ISM Simulate API evaluates every transition against live index metrics and reports the next state without mutating cluster state.

## Analyzer resource reloads

In 3.7.0, `_refresh_search_analyzers` accepts `reload_cached_resources` to hot-reload assets such as Hunspell dictionaries. It also works on metadata-write-blocked indexes, including CCR followers.

## Cross-cluster replication

### Lifecycle actions

- In 3.0.0, the ISM `unfollow` action invokes stop replication.
- In 3.7.0, every CCR REST API accepts `cluster_manager_timeout`. Stop, pause, start, and resume can clear stale persistent tasks. Replication leaves `number_of_replicas` unchanged when a follower uses `auto_expand_replicas`.
- In 3.8.0, start, stop, pause, and resume can act on several indexes matched by a pattern in one call.

### Autofollow naming

In 3.8.0, autofollow accepts `follower_index_pattern` with a `{{leader_index}}` placeholder for collision-free follower names.

## Job Scheduler and external scheduling

### Job and lock APIs

- In 3.2.0, `IntervalSchedule` accepts seconds. Job Scheduler can list jobs, optionally by node, list all locks, and retrieve one lock.
- In 3.3.0, Job Scheduler adds a Job History Service.

### External alert schedules

In 3.7.0, Alerting adds EventBridge Scheduler CRUD and SQS-backed external scheduling. The two-role design uses `execution_role_arn`.

## Snapshots

Snapshot Management 3.3.0 can delete snapshots that were created manually.

Searchable snapshots in 3.0.0 require `warm` nodes; the `search` role is insufficient.

## Remote metadata

### External metadata storage

The 2.19.0 Remote Metadata SDK and repository wrapper let plugins store metadata outside system indexes on stateful nodes.

### Concurrency and mutation

In 3.3.0, global resources are supported. Put and delete accept sequence-number and primary-term concurrency controls. Put, update, delete, and bulk operations accept refresh policies and timeouts.

### Encryption

In 3.4.0, the SDK can use customer-managed keys for encryption and decryption and assume a role for those key operations.

## Custom codecs

- In 3.1.0, OpenSearch Custom Codecs supports Intel QAT-accelerated Zstandard.
- In 3.2.0, Custom Codecs supports composite indexes.
- In 3.5.0, `AdditionalCodecs` lets plugins such as k-NN, Neural Search, and Security Analytics register codecs across plugin boundaries.
- In 3.6.0, vector metadata can use Zstandard compression.

## Remote vector builds

- Remote vector building is enabled by default in 3.1.0 through `index.knn.remote_index_build.enabled`.
- In 3.2.0, terminal remote-build failure does not fall back to CPU.
- In 3.7.0, remote builds support 1-bit scalar quantization.

## Platform data limits

OpenSearch 3.0.0 enforces a 512-byte bulk `_id` limit, maximum nested-query depth, JSON nesting to 1,000 levels, and property names to 50,000 bytes or characters depending on the source.
