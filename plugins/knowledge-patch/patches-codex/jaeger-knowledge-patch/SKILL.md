---
name: jaeger-knowledge-patch
description: Jaeger
version: "2.20.0"
license: MIT
metadata:
  author: Nevaberry
---


# Jaeger Knowledge Patch

Use this skill when migrating, configuring, extending, or operating Jaeger v2.
Start with the breaking-change checklist, then open the reference matching the
work at hand. Treat the project's manifests, configuration, generated APIs,
tests, and observed runtime behavior as authoritative.

## Reference index

| Reference | Topics |
| --- | --- |
| [runtime-configuration-and-migration.md](references/runtime-configuration-and-migration.md) | Unified runtime roles, Collector YAML, server configuration, named storage, base paths, source builds |
| [storage-backends-and-contracts.md](references/storage-backends-and-contracts.md) | Storage v2 and remote-storage contracts, memory, Badger, Cassandra, ClickHouse |
| [elasticsearch-and-opensearch.md](references/elasticsearch-and-opensearch.md) | Backend compatibility, mappings, aliases, rotation, lifecycle, authentication, summaries |
| [query-sampling-metrics-and-telemetry.md](references/query-sampling-metrics-and-telemetry.md) | Sampling, query APIs, normalization, Prometheus, SPM, internal telemetry |
| [operations-deployment-and-development.md](references/operations-deployment-and-development.md) | Pipelines, endpoints, Compose and Kubernetes assets, dashboards, platforms |
| [ui-and-integrations.md](references/ui-and-integrations.md) | Search, trace visualization, Monitor, themes, MCP, AI-assisted integrations |

## Breaking-change checklist

### Distribution and configuration

- Deploy the unified `jaeger` binary or image. Do not expect a separately
  published `jaeger-agent`, v1 service image, or `v1` image tag.
- Express runtime roles as Collector-style YAML. V1 environment variables are
  not automatically translated into v2 settings.
- Review query HTTP/TLS settings and assign separate listen ports to the HTTP
  and gRPC query servers.
- Select exactly one backend type in each trace- or metric-storage
  configuration.
- Replace Kafka receiver `traces.topic` with list-valued `traces.topics`.
- Use Go 1.25.7 for source builds and pnpm for UI or embedded-UI builds.

### Removed contracts and compatibility paths

- Remove the `grpc-plugin` storage type and migrate off `storage/v1/grpc`.
- Replace archive-specific storage interfaces with the unified storage
  factories.
- Update remote-storage implementations for streaming `GetTraces`, direct OTLP
  stream elements, current request/response fields, and
  `FindTraceIDsRequest`.
- Remove the metric-query gRPC service and the metric-store minimum-step API
  from custom integrations.
- Remove `sampling.strategies.bugfix-5270`; its corrected behavior is stable.
- Update remote-sampling clients that parse the removed legacy response.
- Do not script around `jaeger features`; that command was reverted.
- Replace imports that moved under Go `internal` packages.

### Storage and backend upgrades

- Upgrade Cassandra 3.x and Elasticsearch 6 before upgrading Jaeger.
- Recheck Elasticsearch/OpenSearch TLS, mappings, aliases, authentication,
  rotation, trace-duration, and legacy trace-ID settings.
- Plan for materialized `span.kind` and `span.status`, populated
  `parentspanid`, and mapped OTLP scope/link fields.
- Treat API keys, bearer tokens, and SigV4 as mutually constrained
  authentication choices; let validation reject incompatible combinations.
- Update custom dependency writers to accept and propagate context.

### Query and response behavior

- Expect trace adjusters to modify clock skew, duplicates, identifiers, and
  attribute/event ordering in API results.
- Treat invalid OTLP payloads as HTTP 400 request failures.
- Expect empty service queries to return an empty collection.
- Accept camel-case API v3 parameters while migrating away from deprecated
  snake-case aliases and `query.num_traces`.
- Treat trace IDs as opaque strings; query endpoints may receive base64
  identifiers.
- Update dashboards and alerts for the corrected counter suffix behavior and
  the newer SPM namespace.

## Runtime quick reference

### Override Collector YAML

Use environment interpolation for deploy-time values and `--set` for a dotted
path:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: "${env:JAEGER_LISTEN_HOST:-localhost}:4317"
```

```sh
jaeger --config config.yaml \
  --set=receivers.otlp.protocols.grpc.endpoint=0.0.0.0:4317
```

This also works for paths in the built-in all-in-one configuration. Remember
that the OTLP receiver can listen on all interfaces; bind and filter it
deliberately.

### Wire named storage

Register backends once in `jaeger_storage`, select them for reads in
`jaeger_query`, and select the trace backend for writes in
`jaeger_storage_exporter`:

```yaml
extensions:
  jaeger_storage:
    backends:
      trace_store:
        memory:
          max_traces: 100000
  jaeger_query:
    storage:
      traces: trace_store

exporters:
  jaeger_storage_exporter:
    trace_storage: trace_store
```

Configure exporter queueing and retries when storage failures or bursts must be
buffered.

### Configure path-prefixed deployments

`jaeger_query.base_path` describes the path Jaeger receives:

```yaml
extensions:
  jaeger_query:
    base_path: /jaeger
```

Leave it `/` if a reverse proxy strips the external prefix. Otherwise use the
forwarded prefix. The path must begin with `/` and must not contain `..` or
duplicate slashes. The UI can discover its browser prefix automatically, and
API v3 requests honor the prefix.

### Configure remote sampling

`adaptive_sampling` calculates service and endpoint probabilities.
`remote_sampling` serves a static file or adaptive store over HTTP or gRPC:

```yaml
extensions:
  remote_sampling:
    adaptive:
      sampling_store: sampling_store
      initial_sampling_probability: 0.1
    http:
    grpc:
```

Review inherited per-operation defaults and use a reload interval when a
strategy file must update without restart.

## Storage quick reference

### Remote storage

- Use the v2 factory and streaming contracts for trace, service, operation,
  dependency, and trace-ID operations.
- Forward tenant or authentication headers only when the backend expects them.
- Set `max_recv_msg_size_mib` when the default gRPC receive limit is too small:

  ```yaml
  max_recv_msg_size_mib: 64
  ```

- Keep the remote-storage server's write path on the normal OTLP
  receiver/exporter pipeline.

### Elasticsearch and OpenSearch

- Use the mapping generator embedded in `jaeger`. Select OpenSearch output with:

  ```sh
  jaeger esmapping-generator --backend opensearch
  ```

- Rollover initialization is idempotent, but rotation configuration has moved
  toward the new schema; legacy rotation and cleaner flags are deprecated.
- Use a disabled health check or bounded startup timeout only when the backend's
  startup behavior requires it.
- Apply `custom_headers` consistently, including host overrides, and ensure
  signed writes have replayable bodies.
- Prefer native trace summaries where supported; query falls back to aggregating
  full traces otherwise.

### Cassandra, memory, and ClickHouse

- Let Cassandra create its schema at session initialization, set replication as
  needed, and configure a non-default compaction window explicitly.
- Memory searches cover OTLP fields, link attributes, and string-form error
  filters.
- Treat ClickHouse support as experimental. Check the exact read, write,
  metadata, SPM, dependency, TTL, and TLS capabilities needed by the deployment.

## Query and UI quick reference

- Use `GET /api/v3/trace-summaries` for lightweight searches and
  `query.attributes` on `GET /api/v3/traces` for attribute filtering.
- Use storage capabilities, not configuration guesses, to decide whether SPM
  and the Monitor tab are available.
- Account for input sanitization of invalid UTF-8, empty services, negative
  durations, and empty span names.
- Search results default to a sortable table. Monitor filters persist through
  URL parameters, and trace views include aggregate logs, service filtering,
  and a native flamegraph.
- AI-assisted features are opt-in with `ai.enabled: true`. MCP tooling lives in
  `jaegerquery`, is session-scoped, and may enforce tenancy and response limits.

## Verification checklist

1. Start each configured role and confirm component validation succeeds.
2. Verify HTTP and gRPC query listeners use distinct, intended addresses.
3. Ingest OTLP over every enabled protocol and confirm normalized spans are
   searchable.
4. Exercise trace retrieval, summary search, services, operations,
   dependencies, and attribute filters against the selected backend.
5. Test archive behavior through the unified factory rather than old archive
   interfaces.
6. Validate proxy-prefix routing from browser URL through API v3.
7. Check storage authentication, forwarded headers, TLS, health timeout,
   queueing, retries, and message-size limits.
8. Reconcile dashboards, alerts, and scrape targets with current metric names,
   namespaces, ports, and storage capabilities.
9. Confirm the UI's browser, package-manager, theme, search, and optional AI
   requirements match the deployment policy.
