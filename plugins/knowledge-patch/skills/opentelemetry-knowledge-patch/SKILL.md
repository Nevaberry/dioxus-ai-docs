---
name: opentelemetry-knowledge-patch
description: OpenTelemetry
version: null
license: MIT
metadata:
  author: Nevaberry
---

# OpenTelemetry Knowledge Patch

Use this skill when implementing, configuring, upgrading, or reviewing
OpenTelemetry specifications, semantic conventions, SDKs, or Collector
components. Start with the migration-critical changes, then open the topic
reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/specification-and-sdk.md](references/specification-and-sdk.md) | Context propagation, signal APIs, resources, attributes, declarative SDK configuration, Prometheus interoperability |
| [references/semantic-conventions-protocols.md](references/semantic-conventions-protocols.md) | Generative AI, RPC, exception logs, HTTP, GraphQL, browser, database, and Oracle conventions |
| [references/semantic-conventions-platforms.md](references/semantic-conventions-platforms.md) | Process, service, system, V8, Kubernetes, application, cloud, runtime, SDK, event, mainframe, NFS, and profile conventions |
| [references/collector-core-configuration.md](references/collector-core-configuration.md) | Collector schemas, reload, Go APIs, component names, error defaults, Host Metrics, self-telemetry, and OpAMP |
| [references/collector-pipelines-processing.md](references/collector-pipelines-processing.md) | OTTL, lookup and transform processors, W3C-aware sampling, component telemetry, profiles, and behavior corrections |
| [references/collector-exporters-extensions.md](references/collector-exporters-extensions.md) | Datadog, Elasticsearch, OpenSearch, Kafka, SignalFx, file and load-balancing exporters, encoding, OIDC, and database authentication |
| [references/collector-receivers.md](references/collector-receivers.md) | Receiver units and schemas, database receivers, AWS, Datadog, RabbitMQ, file stats, Journald, webhook, and timeout behavior |

## Breaking changes and deprecations

### Specification and SDK

- Treat the Jaeger and OT Trace propagators as deprecated and optional to
  implement.
- Treat the Zipkin exporter specification as deprecated and optional to
  implement.
- OpenTracing and OpenCensus compatibility requirements are deprecated.
- `TraceIdRatioBased` exists again, but it has a deprecation timeline.
  Do not confuse restoration with a long-term stability guarantee.
- Declarative signal configuration uses `enabled`, not `disabled`, in
  `TracerConfig`, `MeterConfig`, and `LoggerConfig`.
- Rename `ComponentProvider` to `PluginComponentProvider` and `CreatePlugin`
  to `CreateComponent`.
- Use these Prometheus exporter property names:
  `scope_info_enabled`, `target_info_enabled`, and
  `resource_constant_labels`. The older negative-form names are replaced.

### Semantic conventions

- Generative-AI attributes, metrics, events, and spans have moved out of the
  main semantic-conventions repository. Use the dedicated repository and its
  corresponding `schema_url`.
- RPC duration metrics are `rpc.client.call.duration` and
  `rpc.server.call.duration`; both are required and measured in seconds.
- Replace `rpc.service` plus a short `rpc.method` with one fully qualified
  `rpc.method`.
- Rename RPC metadata and status attributes to `rpc.request.metadata`,
  `rpc.response.metadata`, and `rpc.response.status_code`.
- Rename `rpc.system` to `rpc.system.name`; normalized values include
  `connectrpc` and `dubbo`.
- RPC spans and metrics no longer carry `network.type`,
  `network.protocol.name`, `network.protocol.version`, or
  `network.transport`.
- RPC server spans also drop `client.address` and `client.port`.
- RPC request/response size metrics and `rpc.message` are deprecated.
- Generic exception span events are deprecated. Use exception log records and
  the domain-specific exception events while migrating.
- `graphql.document` is Opt-In because it may expose sensitive, unbounded,
  high-cardinality input; sanitize it when capture is enabled.
- Replace `peer.service` with `service.peer.name` and, where needed,
  `service.peer.namespace`.
- Use `process.unix.file_descriptor.count` or
  `process.windows.handle.count`, not `process.open_file_descriptor.count`.
- Use the singularized and reordered system and Kubernetes metric names
  documented in the references; several old plural or word-order variants no
  longer match the conventions.

### Collector

- In Go code, replace `configgrpc.BalancerName` with
  `configgrpc.DefaultBalancerName`.
- Replace deprecated `xconfmap.WithForceUnmarshaler` with
  `confmap.WithForceUnmarshaler`.
- The failover connector no longer accepts `retry_gap` or `max_retries`.
- The JMX receiver code has been removed.
- Rename the AWS ECS attributes processor type from `awsecsattributes` to
  `aws_ecs_attributes`; there is no alias for the old name.
- `cumulativetodelta` and `spanpruning` survive only as deprecated aliases for
  `cumulative_to_delta` and `span_pruning`.
- Routing, filter, and transform processing now default top-level
  `error_mode` to `ignore`. The routing beta gate can temporarily restore
  `propagate`; filter and transform compatibility gates are scheduled for
  removal.
- Host Metrics now aggregates CPU time and utilization across logical CPUs by
  default, omits the `cpu` attribute, and enables
  `system.cpu.logical.count`.
- File exporter output is mode `0644`, including rotated files.
- Histogram dashboards must account for power-of-two buckets from 128 B
  through 16 MiB for both core batch-send-size metrics.

## High-value specification behavior

### Context and sampling

- Environment-variable carriers are Release Candidate. Normalize requested,
  carrier, and returned keys, read and return only normalized environment
  names, and normalize an empty name to `_`.
- Carrier caching is deliberately unspecified.
- Context propagation requires the W3C randomness flag.
- `AlwaysRecord` is stable.
- The Dynamic Sampling and Tail Sampling processors can consume W3C
  `ot=th` thresholds and `ot=rv` randomness; read the gate requirements before
  enabling Tail Sampling tracestate behavior.

### APIs and signals

- Stable enablement checks include Tracer `enabled`, synchronous instrument
  `Enabled`, and `LogRecordProcessor.Enabled`.
- Synchronous instruments have an in-development `Bind` API.
- Periodic exporting `MetricReader` has an in-development
  `maxExportBatchSize`.
- A View-provided metric stream name is exempt from instrument-name syntax
  validation.
- Logs add an optional ergonomic API. Logger `Emit` has a stable optional
  `Exception` parameter, and logger configuration adds `minimum_severity` and
  `trace_based`.
- Logs can bridge an event into a span event and can represent entity
  information as structured events.
- Profiles now have a signal specification, data model, and supplementary
  pprof guidance.

### Resources and attributes

- A Resource describes the observed entity, not necessarily the component
  that emitted the telemetry.
- Complex `AnyValue` attributes and their limits are stable.
- For non-OTLP paths, follow the specific guidance for byte arrays, empty
  values, arrays, maps, and nesting.
- JSON-object string representations for attributes and attribute collections
  remain in development.

## High-value Collector configuration

### Self-telemetry resource detection

Use the experimental resource-detection block under the Collector's own
telemetry. Supported detectors are `container`, `host`, `process`, and
`service`.

```yaml
service:
  telemetry:
    resource:
      detection/development:
        detectors:
          - host: {}
```

### Restore per-CPU Host Metrics

Select both `cpu` and `state` explicitly for each CPU metric:

```yaml
receivers:
  hostmetrics:
    scrapers:
      cpu:
        metrics:
          system.cpu.time:
            attributes: [cpu, state]
          system.cpu.utilization:
            attributes: [cpu, state]
```

### Partial reload

- Enable `--feature-gates=service.partialReload` for the alpha partial-reload
  path.
- `service.partialReloadReceivers` is beta.
- A reload restarts only receivers when processors, exporters, extensions,
  and all other non-receiver configuration are unchanged.

### Queue and delivery constraints

- With `exporter.kafka.useRequestType`, all signals become Kafka records when
  the exporter request is created, and `queue_batch.sizer: items` counts those
  records.
- Persistent `sending_queue.storage` is a startup error in Kafka request mode.
- With `datadog.serializerexporter.UseSyncForwarder`, serializer 4xx/5xx
  failures flow through `exporterhelper`; retry, queue-overflow, and
  failed-point telemetry then apply to that path.
- Elasticsearch document-level retries use
  `retry::retry_on_document_status`, independently of request-level retries.
- OpenSearch managed templates are accepted only in `otel-v1` mapping mode and
  are created idempotently without replacing existing templates.

## Implementation checklist

1. Identify whether the change targets the specification, semantic
   conventions, an SDK, Collector core, or Contrib.
2. Check stability labels and feature-gate defaults before treating a feature
   as generally available.
3. Audit renamed attributes, metrics, component types, and configuration keys
   before an upgrade.
4. Recheck metric units, aggregation, required attributes, and cardinality;
   several receiver and convention changes affect dashboards and alerts.
5. For sensitive fields such as exception messages, query parameters, and
   GraphQL documents, make capture an explicit and sanitized choice.
6. For Collector gates, distinguish default-on from default-off behavior and
   confirm mutually exclusive gates before deployment.
7. Open the matching reference for the complete conditions, allowed values,
   and receiver- or exporter-specific details.
