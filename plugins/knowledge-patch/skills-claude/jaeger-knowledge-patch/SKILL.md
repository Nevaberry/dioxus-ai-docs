---
name: jaeger-knowledge-patch
description: Jaeger
version: 2.20.0
license: MIT
metadata:
  author: Nevaberry
---


# Jaeger Knowledge Patch

Use this skill when designing, migrating, configuring, extending, or operating
Jaeger. It focuses on the unified v2 runtime, storage API evolution, query and
sampling behavior, operational components, and current UI and AI integrations.

## Reference index

| Reference | Topics |
| --- | --- |
| [runtime-configuration.md](references/runtime-configuration.md) | Unified binary and roles, Collector-style YAML, overrides, server ports, image and build changes |
| [storage-backends.md](references/storage-backends.md) | Storage contracts, named wiring, Elasticsearch/OpenSearch, Cassandra, memory, gRPC, ClickHouse, Badger |
| [query-sampling-metrics.md](references/query-sampling-metrics.md) | Query APIs, trace adjustment, sampling, SPM, Prometheus, trace summaries |
| [ingestion-operations.md](references/ingestion-operations.md) | OTLP and Kafka ingestion, extensions, telemetry, sanitization, deployment and monitoring assets |
| [ui.md](references/ui.md) | Base paths, search, trace views, DAGs, themes, links, logs, Monitor filters, build tooling |
| [mcp-ai.md](references/mcp-ai.md) | MCP consolidation, tools and limits, AG-UI, AI feature gates, GenAI views and tracing |

## Start with the breaking migrations

### Move deployments to the unified runtime

- Run the `jaeger` binary or image. Do not plan around separately published v1
  collector, query, ingester, all-in-one, or agent artifacts.
- Express each role as a Collector-style YAML configuration. Existing v1
  environment variables are not automatically translated into v2 settings.
- Treat Jaeger as an OpenTelemetry Collector distribution. Add an upstream
  Collector only where a sidecar, host agent, or preprocessing tier is useful.
- Remove the retired `grpc-plugin` storage type and legacy
  `storage/v1/grpc` integration.
- Give query HTTP and gRPC servers distinct listen ports.

See [runtime-configuration.md](references/runtime-configuration.md) for role
composition, configuration overrides, image tags, and source-build changes.

### Revalidate storage wiring

V2 storage is name-based:

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

- Configure exactly one backend type per trace- or metric-storage entry.
- Use the same registered backend name from readers and writers.
- Replace archive-specific interfaces with the unified storage contract.
- Update experimental or custom v2 storage implementations for streaming trace
  reads, direct OTLP stream elements, current request messages, and
  context-aware dependency writes.
- Review Elasticsearch index mappings, aliases, rotation, authentication, and
  trace-duration settings before an upgrade.
- Remove Elasticsearch 6 and Cassandra 3 from supported deployment plans.

The backend-specific migration details are in
[storage-backends.md](references/storage-backends.md).

### Update API clients and extensions

- The metrics-query gRPC service and `metricsquery.proto` are gone.
- Trace request time fields and several storage-v2 request and response shapes
  changed; regenerate clients from the matching IDL.
- API v2 and v3 query handlers apply trace adjusters. Do not assume returned
  span ordering or timestamps are raw storage values.
- API v3 service-list success responses use empty collections instead of
  `null`.
- Prefer trace-summary search for lightweight result sets.
- Treat snake_case gateway parameters and `query.num_traces` as compatibility
  aliases; use camelCase and `query.search_depth`.
- Treat HTTP trace identifiers as opaque because base64 identifiers are valid.

See [query-sampling-metrics.md](references/query-sampling-metrics.md).

### Remove stale feature and configuration switches

- Remove `sampling.strategies.bugfix-5270`; the corrected behavior is stable.
- Do not script `jaeger features`; the briefly introduced command was removed.
- Replace Kafka receiver `traces.topic` with the list-valued `traces.topics`.
- Remove the Cassandra `namespace` option and the unused Badger namespace
  field.
- Migrate legacy Elasticsearch rotation flags to the newer rotation schema.
- Do not instantiate the former standalone `jaegermcp` extension; configure
  MCP through `jaegerquery`.

## Configure the unified runtime

Use environment interpolation for deploy-time values and `--set` for targeted
path overrides:

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

For a reverse proxy, set `jaeger_query.base_path` to the prefix Jaeger itself
receives. Leave it `/` when the proxy strips the external browser prefix.

## Build a storage pipeline

1. Register named trace and metric backends under `jaeger_storage`.
2. Point `jaeger_storage_exporter` at the trace backend used for writes.
3. Point `jaeger_query` at the corresponding read backend and optional metrics
   backend.
4. Configure exporter queueing and retry behavior for transient failures.
5. Validate backend authentication and forwarded headers independently for
   read, write, and administration paths.
6. Exercise trace, service, operation, dependency, and summary reads required
   by the chosen backend.

Backend maturity is not uniform. In particular, ClickHouse, data-stream
rotation, and several SPM paths are explicitly experimental; inspect
[storage-backends.md](references/storage-backends.md) before depending on them.

## Sampling and trace processing

- The distribution includes tail-based sampling and the filter processor.
- Use `adaptive_sampling` to calculate per-service and per-endpoint
  probabilities from observed traffic.
- Configure `remote_sampling` with a static strategy file or an adaptive store,
  then enable its HTTP or gRPC server.
- File strategies can reload periodically.
- Default per-operation strategies are inherited; review combinations of
  defaults and service-specific rules.
- The legacy remote-sampling response representation is unsupported.

```yaml
extensions:
  remote_sampling:
    adaptive:
      sampling_store: sampling_store
      initial_sampling_probability: 0.1
    http:
    grpc:
```

## Query, SPM, and metrics

- Supply optional time windows for trace lookup where supported.
- Use custom Prometheus query parameters, TLS, or SigV4 when the metrics
  backend requires them.
- Let storage capabilities determine whether the UI exposes SPM.
- Expect corrected OpenTelemetry metric names without a duplicated `_total`
  suffix.
- Use `/quality-metrics` and `/deep-dependencies` for their dedicated data.
- Keep dashboards and alerts aligned with the metrics-exporter and SPM assets.

## Operate ingestion safely

- The OTLP receiver may listen on all interfaces; bind it deliberately and
  align firewall or network-policy rules.
- Account for enabled UDP ports in all-in-one deployments.
- Invalid OTLP payloads return a client error, while malformed names, timing,
  UTF-8, and some tag forms are normalized or accepted.
- Use the health-check extension for health endpoints and `pprof` only with
  deliberate access controls.
- Configure Kafka TLS/authentication combinations, topic lists, and the
  ingester metrics port explicitly.
- Validate storage exporter queue and retry settings under failure.

See [ingestion-operations.md](references/ingestion-operations.md).

## Serve the UI behind a proxy

- Distinguish the prefix received by Jaeger from the prefix visible before a
  stripping proxy.
- The frontend can discover its URL prefix and its API v3 client honors the
  configured base path.
- Keep trace IDs opaque in UI integrations.
- Test current browsers only; legacy-browser support has ended.
- Use pnpm for UI and embedded-UI build workflows.

The UI reference also covers trace summaries, search tables, DAG and trace
layouts, flamegraphs, themes, trace-wide logs, and shareable Monitor filters.

## Enable MCP and AI deliberately

- Set `ai.enabled` explicitly when AI-assisted UI behavior is desired; its
  default is disabled.
- Configure the MCP endpoint in `jaegerquery`, with tenancy, CORS, handler
  limits, response limits, and session scope appropriate to the deployment.
- Expect tool results to report truncation and total counts where applicable.
- Trace the UI, gateway, and sidecar path with OTLP and propagated trace
  context when diagnosing AI-assisted behavior.

See [mcp-ai.md](references/mcp-ai.md) for tool evolution and experimental
surface details.

## Upgrade verification

Before promoting a changed deployment:

1. Validate the Collector configuration and component factories.
2. Confirm query HTTP and gRPC listeners use separate ports.
3. Exercise ingestion over every enabled OTLP, UDP, or Kafka path.
4. Write and retrieve a trace, then search services, operations, attributes,
   dependencies, and summaries as required.
5. Verify storage authentication, TLS, forwarded headers, health-check timeout,
   queueing, retry, and receive-size limits.
6. Compare dashboard and alert queries with emitted metric names.
7. Test UI routing through the real reverse proxy and browser prefix.
8. Gate experimental storage, MCP, AI, and trace-layout features separately
   from core collection and query readiness.
