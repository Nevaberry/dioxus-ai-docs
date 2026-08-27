---
name: opensearch-knowledge-patch
description: OpenSearch
version: "3.7.0"
license: MIT
metadata:
  author: Nevaberry
---


# OpenSearch Knowledge Patch

Use this skill when designing, upgrading, configuring, or debugging OpenSearch clusters, OpenSearch Dashboards, search pipelines, vector and semantic search, ML Commons, agents, Query Insights, Alerting, Anomaly Detection, Security, SQL, or PPL.

## How to use this skill

1. Determine the deployed OpenSearch and Dashboards versions from manifests or cluster APIs.
2. Identify the affected subsystem and read its topic reference below.
3. Apply guidance only when the referenced version is at or below the deployed version.
4. Treat disabled-by-default and experimental features as opt-in; verify their settings before relying on them.
5. For upgrades, inventory indexes, node roles, plugins, clients, settings, and saved Dashboards workflows before changing the cluster.
6. Prefer explicit engines, query options, and compatibility settings when behavior changed between releases.
7. Validate migrations on representative documents and queries, including security-filtered and multi-tenant paths.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrades-and-core.md](references/upgrades-and-core.md) | Upgrade blockers, runtime and artifact requirements, core settings, index lifecycle, replication, schedulers, and codecs |
| [vector-hybrid-and-relevance.md](references/vector-hybrid-and-relevance.md) | k-NN, vector engines, semantic and hybrid search, star-tree, Learning to Rank, and Search Relevance Workbench |
| [agents-ml-and-flows.md](references/agents-ml-and-flows.md) | ML Commons, connectors, agents, memory, tools, MCP, Flow Framework, and Launchpad |
| [operations-observability-and-alerting.md](references/operations-observability-and-alerting.md) | Query Insights, workload management, observability, Discover, Alerting, Anomaly Detection, and notifications |
| [ppl-sql-and-transport.md](references/ppl-sql-and-transport.md) | PPL, SQL, unified query APIs, gRPC, Arrow, and pull-based ingestion |
| [security-and-multitenancy.md](references/security-and-multitenancy.md) | Authentication, authorization, audit, resource sharing, remote metadata, and multi-tenancy |

## Upgrade blockers and breaking changes

### Prepare for the 3.x runtime and index boundary

- Run the cluster on JDK 21 or later and account for the Lucene 10.1.0 baseline.
- Reindex every index created before 2.x, including system indexes, before a 3.0 upgrade.
- Verify 3.x artifacts with `release@opensearch.org`; the older signing key applies to 2.x artifacts.
- Replace removed system-index REST access with supported plugin APIs.
- Audit documents for JSON nesting beyond 1,000 levels, oversized property names, and `_id` values beyond 512 bytes.
- Remove `_bulk` `batch_size`, `mmap.extensions`, the `transport-nio` plugin, and the main-response compatibility override.

### Review node and storage roles

- Configure coordinating-only nodes with an empty role list:

```yaml
node.roles: []
```

- Assign `warm` rather than `search` to every node that serves searchable-snapshot shards.
- For remote-store indexes, use `_scale` and the search-only lifecycle only after verifying reader/writer separation and recovery procedures.

### Update renamed and removed behavior

- Replace query-group API paths, response fields, and `wlm.query_group` settings with workload-group equivalents.
- Replace `CatIndexTool` with `ListIndexTool`.
- Use `path_hierarchy`, not the deprecated `PathHierarchy` tokenizer name.
- Replace Security whitelist settings with allowlist settings and grant `cluster:monitor/shards` where `_cat/shards` requires it.
- Move SQL pagination to Point in Time; legacy Scroll pagination and OpenDistro endpoints/settings are obsolete.
- Remove dependencies on the old Discover experience setting and DataGrid table.
- Reindex Romanian text after the analyzer's cedilla-to-comma Unicode normalization change.
- Revalidate Blake2b hash fixtures after the Security salt-handling correction.

### Check platform and plugin dependencies

- OpenSearch 2.0 Alerting notification actions require `notifications-core` and `notifications`; Dashboards management also requires `notificationsDashboards`.
- Plan migrations away from retired or announced-for-deprecation operating-system baselines, including Ubuntu 20.04 and Amazon Linux 2 where applicable.
- Review Dashboards plugins against the Node.js 22 and Rspack transition; Node.js 20 is deprecated.

## Search and vector quick reference

### Make engine and rescore choices explicit

- The implicit k-NN engine changed to Faiss in 2.18. Explicitly choose Faiss, Lucene, or a supported legacy engine when index behavior must be stable.
- With Faiss cosine space, indexing normalizes vectors; use inner product for already-normalized vectors when equivalent scoring is desired without implicit normalization.
- A mapping backed by a trained vector artifact must not declare both its identifier and `dimension`.
- `index.knn` is immutable after index creation, and derived vector source cannot be enabled when it is false.
- New OnDisk 4x-compressed indexes rescore by default; specify `rescore: false` when preserving the prior behavior.
- A terminal remote-vector-build failure does not fall back to a CPU build.

### Respect hybrid-query constraints

- Do not nest `hybrid` under compound queries such as `function_score`, `constant_score`, or `script_score`.
- Do not use `dfs_query_then_fetch` with a hybrid query.
- Invalid nested hybrid structures are rejected; test parent-join, collapse, and `inner_hits` combinations explicitly.
- Choose normalization deliberately: min-max supports lower and upper bounds, Z-score is available, and RRF supports rank-based fusion and custom weights.

### Control vector payloads

- Derived vector source removes vectors from stored `_source` and reconstructs them on reads; validate supported flat, object, and single-level nested mappings.
- Use `docvalue_fields` when retrieving float, byte, or binary vectors without reindexing; the default representation is Base64 binary.
- Base64 vector ingestion avoids JSON arrays, and a search request processor can exclude vector fields from `_source` responses.

### Validate semantic and sparse retrieval

- A neural sparse query cannot specify both an analyzer and a model identifier.
- Semantic fields expose chunking, analyzers, generated dense-vector parameters, ingest batching, prune strategies, embedding reuse, and sparse output format controls.
- SEISMIC supports sparse approximate retrieval, nested fields, explanation, and optional method parameters.
- Batch semantic highlighting of nested `inner_hits` requires request-level opt-in.

## Query language and transport quick reference

### Account for Calcite routing

- Calcite is the default PPL path. Unsupported commands may route to the v2 path, but general Calcite query failures do not fall back by default.
- `query.size_limit` limits final results, not intermediate processing.
- With `plugins.ppl.syntax.legacy.preferred=false`, `join` defaults to `max=1`.
- Zero or negative `subsearch.maxout` means unlimited; set an intentional positive ceiling when resource bounds matter.
- PPL final structs are maps, missing or null `JSON_EXTRACT` paths return null, and overflow to double infinity returns null.

### Treat pagination and cancellation as protocol choices

- SQL pagination defaults to Point in Time.
- PPL accepts `fetch_size` and can be cancelled through `_tasks/_cancel`.
- The query-only unified V2 SQL path blocks DML and DDL.
- SQL cursor continuation remains confined to the original query indexes under fine-grained access control.

### Gate optional transports

- Protobuf-over-gRPC bulk ingestion and search are production-ready, with encryption and Security authentication options.
- Apache Arrow Flight streaming remains disabled by default.
- Pull-based Kafka and Kinesis ingestion is production-ready only after its later lifecycle transition; configure warmup and adaptive shard selection.

## Agents and ML quick reference

### Select current agent protocols

- Agentic search and persistent agentic memory are production-ready; preserve memory identifiers and session metadata when building multi-turn experiences.
- Unified registration and `conversational_v2` are production-ready and honor `inferenceConfig.model_parameters`.
- Use Streamable HTTP for MCP; SSE transport is deprecated for MCP even though separate prediction and agent streaming APIs may still use SSE.
- Treat AG-UI, retention policies, and other explicitly experimental capabilities as disabled unless enabled.

### Validate connectors and guardrails

- Connector actions can use custom names plus PUT and DELETE, and headers can substitute per-request parameters.
- Enforce trusted endpoint patterns and private-IP/ReDoS protections on outbound connector paths.
- `ModelGuardrail` and `LocalRegexGuardrail` fail closed when evaluation fails; design error handling accordingly.
- Inline connectors need no name, but schema-declared strings must remain strings during validation.

## Operations and security quick reference

### Preserve observability and alert semantics

- Query Insights spans historical top-N, live queries, profiling, recommendations, identities, workloads, and remote export; apply authorization filters to its records.
- Alerting's temporary list-of-findings publication was reverted; consumers should expect individual findings.
- Multi-tenant Alerting disables unsupported email, findings, chained actions, scheduler-index, and other paths, returning 501 where specified.
- PPL Alerting assets and API routes changed during their transition; do not assume the experimental assets remain installed.

### Apply access controls deliberately

- Scoped API keys carry their own cluster and index permissions and support expiration and synchronous revocation.
- `plugins.security.dls.write_blocked` can block all writes under document-level restrictions.
- Security configuration supports dynamic resource settings, versioned views and rollback, resource sharing, and explicit protected resources.
- Resource-access configuration uses `resource-access-levels.yml`; review notification prefixes and multi-tenancy settings during upgrade.
- Security plugin PUT and PATCH requests limit every text input to 256 characters.

## Verification checklist

- Confirm cluster, Dashboards, plugin, Java, and index-creation versions.
- Run representative full-text, hybrid, vector, semantic, PPL, SQL, and gRPC requests.
- Compare scores, rescoring, collapse, `inner_hits`, pagination, and null behavior before and after upgrade.
- Exercise DLS, FLS, field masking, tenant isolation, API keys, JWT, certificate, and audit paths.
- Test Alerting, Anomaly Detection, Query Insights, workload groups, schedulers, and replication under failure.
- Verify experimental flags and disabled-by-default settings explicitly.
- Read all relevant topic references before shipping a migration or compatibility-sensitive change.
