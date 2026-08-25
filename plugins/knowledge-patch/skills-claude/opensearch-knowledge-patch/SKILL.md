---
name: opensearch-knowledge-patch
description: OpenSearch
version: 3.7.0
license: MIT
metadata:
  author: Nevaberry
---


# OpenSearch Knowledge Patch

Use this skill when designing, upgrading, querying, securing, or operating OpenSearch and OpenSearch Dashboards. Start with the migration checks below, then open the reference that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [Agents, ML Commons, and Flow Framework](references/agents-ml-and-flows.md) | Agents, tools, memory, connectors, inference, MCP, Flow Framework, Launchpad |
| [Cluster Operations and Data Lifecycle](references/cluster-operations-and-lifecycle.md) | Node roles, remote store, ingestion, ISM, replication, scheduling, transport, codecs |
| [Observability, Alerting, and Dashboards](references/observability-alerting-and-dashboards.md) | Metrics, traces, Discover, anomaly detection, alerting, notifications, dashboards |
| [PPL and SQL](references/ppl-and-sql.md) | Calcite routing, commands, functions, SQL, unified query APIs, result behavior |
| [Search, Relevance, and Query Insights](references/search-relevance-and-insights.md) | Search Relevance Workbench, experiments, Query Insights, workload groups, scoring |
| [Security and Multitenancy](references/security-and-multitenancy.md) | Authentication, authorization, API keys, DLS/FLS, audit logging, resource sharing, tenants |
| [Upgrades and Platform Compatibility](references/upgrades-and-platform.md) | Breaking changes, runtime requirements, removed settings, client and index compatibility |
| [Vector and Neural Search](references/vector-and-neural-search.md) | k-NN, Faiss, Lucene, compression, hybrid search, semantic fields, sparse retrieval |

## Check breaking changes first

### Prepare indexes before a 3.x upgrade

OpenSearch 3.0 cannot open indexes created before 2.x, including system indexes. Inventory and reindex them before upgrading. Also audit documents migrated from Elasticsearch OSS 6.8 for more than 10,000 nested JSON objects; those documents can block shard relocation under `index.mapping.nested_objects.limit`.

### Move searchable snapshots to warm nodes

Searchable snapshots cannot run on `search`-role nodes in 3.0. Every node that may hold those shards needs the `warm` role.

### Update the runtime and artifact trust

OpenSearch 3.0 requires JDK 21. Artifacts from 3.0.0 onward use the `release@opensearch.org` signing key; do not verify them with the key reserved for 2.x artifacts.

### Remove retired compatibility paths

Do not carry these into a 3.0 configuration or client:

- `compatibility.override_main_response_version`
- `_bulk?batch_size=...`
- `mmap.extensions`
- the `transport-nio` plugin
- `plugins.sql.pagination.api`
- OpenDistro endpoints or `opendistro`-prefixed SQL settings
- the `CatIndexTool`; use `ListIndexTool`

System indexes are no longer available through REST. SQL pagination defaults to Point in Time, while Scroll pagination is deprecated.

### Recheck parsers and response consumers

OpenSearch 3.0 limits JSON object and array nesting to 1,000 levels and property names to 50,000 bytes or characters depending on the input. It also enforces a 512-byte bulk `_id` limit. The Nodes API now returns a raw byte count in `total_indexing_buffer_in_bytes` and a formatted size in `total_indexing_buffer`.

### Update renamed workload controls

Query groups are now workload groups. Replace `wlm/query_group` with `wlm/workload_group`, `queryGroupID` with `workloadGroupID`, and the `wlm.query_group` settings prefix with `wlm.workload_group`.

## Apply search changes deliberately

### Pin the k-NN engine when behavior matters

Faiss is the implicit k-NN engine from 2.18. With cosine similarity and no explicit engine, vectors are normalized at index time. Pin `engine`, `space_type`, mode, compression, and rescore behavior when reproducibility matters.

### Treat vector representation as an API choice

`docvalue_fields` returns k-NN vectors as Base64 by default. Vector fields can also be ingested as Base64. If callers expect JSON arrays, set and test the representation explicitly.

### Respect hybrid-query composition limits

A `hybrid` query cannot be nested inside compound queries such as `function_score`, `constant_score`, or `script_score`. It also rejects `dfs_query_then_fetch`; choose a supported search type and put fusion in the search pipeline.

### Make rescore intent explicit

New on-disk indexes with 4x compression rescore by default. Set `rescore: false` to opt out. For Faiss efficient filters, a separate index setting can disable the exact-search phase after ANN search.

## Route PPL and SQL correctly

### Know which PPL engine handles the request

Calcite is the default PPL path. General Calcite failures no longer fall back to the v2 engine, but unsupported commands can route to v2. Test both syntax support and failure behavior rather than relying on a blanket fallback assumption.

### Use Point in Time for SQL pagination

The legacy SQL pagination setting is gone and PIT is the default. Under fine-grained access control, cursor continuation remains restricted to the indexes selected by the original query.

### Keep unified-query APIs query-only

The unified V2 path supports richer SQL planning but blocks DML and DDL. PPL supports cancellation through `_tasks/_cancel`, `fetch_size`, and a grammar bundle for query-tool integrations.

### Account for null and result-shape semantics

`NOT IN` and `NOT LIKE` exclude null or missing values. Final struct values are maps, missing `JSON_EXTRACT` paths return null, and double overflow to infinity returns null. Consumers should assert these shapes and null rules.

## Build agents and ML integrations safely

### Prefer current agent registration and transport

The unified registration API and `conversational_v2` agent are production-ready. The ML Commons MCP server uses Streamable HTTP and deprecates SSE for MCP transport; streaming inference and agent execution have separate streaming APIs, including gRPC methods.

### Validate connector substitutions and egress policy

Connector headers can substitute per-request `${parameters.*}` values. Connector paths enforce private-IP, ReDoS, and trusted-endpoint controls, so test final resolved URLs and headers against the cluster policy.

### Treat guardrail failures as denials

`ModelGuardrail` and `LocalRegexGuardrail` fail closed when evaluation fails. Existing integrations that previously continued on guardrail errors need explicit error handling.

### Bound memory and context

Agents support context hooks, truncation, summaries, sliding windows, structured conversation memory, and long-term retrieval. Configure limits and retention deliberately; retention policies remain disabled by default when used.

## Operate security and tenancy explicitly

### Scope API keys at creation

Long-lived API keys carry cluster and index permissions directly rather than inheriting user roles. Set expiration, keep grants minimal, and plan synchronous cluster-wide revocation.

### Protect writes under DLS

Enable `plugins.security.dls.write_blocked` when document-level restrictions must prohibit all writes. DLS can use lookup queries, and DLS/FLS variables can define fallback values.

### Validate security request sizes

Security-plugin PUT and PATCH requests enforce a 256-character limit on every text input. Validate generated configuration before submission.

### Review multitenant feature constraints

Alerting multi-tenancy disables unsupported email, findings, chained actions, scheduler indexes, and other actions. Anomaly Detection multi-tenant data sources also disable several result-index and historical-analysis paths; unsupported routes return 501.

## Keep operations observable

### Use Query Insights for live and historical work

Live Queries exposes inflight work and can retain recently finished queries on demand. Top-N records and Live Queries can include user and role identity; authorization filters determine which records non-admin users see.

### Separate alert scheduling modes

Alerting supports internal schedules and external EventBridge Scheduler with SQS. Configure the external two-role design with `execution_role_arn`, and set monitor trigger and lookback limits explicitly.

### Plan the PPL Alerting transition

Experimental PPL Alerting assets were removed while the API surface was refactored. Current Dashboards integration uses v1 endpoints rather than parallel legacy and PPL paths.

### Verify observability data contracts

Trace Analytics accepts the newer OpenTelemetry output layout, custom span and log indexes, cross-cluster trace correlation, and configurable service-map limits. Test field mappings when data is not in the standard OpenTelemetry schema.

## Upgrade checklist

1. Inventory index creation versions, system indexes, searchable snapshots, node roles, Java runtime, plugins, and signing keys.
2. Search configuration for removed settings, renamed workload-group paths, deprecated analyzers, notification prefixes, and resource-access filenames.
3. Pin vector engine, compression, rescore, response representation, and hybrid-search type.
4. Exercise PPL and SQL routing, pagination, null semantics, request limits, and response parsers.
5. Revalidate authentication, DLS/FLS writes, API keys, tenant constraints, resource sharing, and audit sinks.
6. Test agent connectors, MCP transport, guardrails, memory bounds, and external endpoint policy.
7. Compare live-query, alert, anomaly, trace, replication, ISM, and scheduler behavior before and after the change.
