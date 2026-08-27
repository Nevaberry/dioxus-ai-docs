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
components. Start with migration-sensitive changes, then open the reference
that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/specification-and-sdk.md](references/specification-and-sdk.md) | Context propagation, signal APIs, resources, attributes, declarative SDK configuration, Prometheus interoperability, and exporter limits |
| [references/semantic-conventions-protocols.md](references/semantic-conventions-protocols.md) | Generative AI, RPC, exceptions, HTTP, GraphQL, browser, database, and messaging conventions |
| [references/semantic-conventions-platforms.md](references/semantic-conventions-platforms.md) | Process, service, system, V8, Kubernetes, application, cloud, runtime, event, mainframe, NFS, and profile conventions |
| [references/collector-core-configuration.md](references/collector-core-configuration.md) | Collector schemas, reload, Go APIs, component names, error defaults, Host Metrics, self-telemetry, and service integration |
| [references/collector-pipelines-processing.md](references/collector-pipelines-processing.md) | OTTL, lookup and transform processors, W3C-aware sampling, component telemetry, profiles, and behavior corrections |
| [references/collector-exporters-extensions.md](references/collector-exporters-extensions.md) | Datadog, Elasticsearch, OpenSearch, Kafka, SignalFx, file, load-balancing, CloudWatch, Azure Monitor, Prometheus Remote Write, encoding, OIDC, and storage extensions |
| [references/collector-receivers.md](references/collector-receivers.md) | Receiver units and schemas, database receivers, AWS, Datadog, RabbitMQ, File Log and File Stats, Journald, webhook, Apache, DNS, and timeout behavior |

## Breaking changes and deprecations

### Specification and SDK

- Treat the Jaeger and OT Trace propagators as deprecated and optional to
  implement.
- Treat the Zipkin exporter specification as deprecated and optional to
  implement.
- OpenTracing and OpenCensus compatibility requirements are deprecated.
- `TraceIdRatioBased` exists again, but it has a deprecation timeline. Do not
  mistake restoration for a long-term stability guarantee.
- Declarative signal configuration uses `enabled`, not `disabled`, in
  `TracerConfig`, `MeterConfig`, and `LoggerConfig`.
- Rename `ComponentProvider` to `PluginComponentProvider` and `CreatePlugin`
  to `CreateComponent`.
- Use `scope_info_enabled`, `target_info_enabled`, and
  `resource_constant_labels` for Prometheus exporter properties; replace the
  older negative-form names.

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
  domain-specific exception events during migration.
- `graphql.document` is Opt-In because it may expose sensitive, unbounded,
  high-cardinality input; sanitize it whenever capture is enabled.
- Replace `peer.service` with `service.peer.name` and, where needed,
  `service.peer.namespace`.
- Use `process.unix.file_descriptor.count` or
  `process.windows.handle.count`, not `process.open_file_descriptor.count`.
- Audit system, Kubernetes, V8, browser Web Vitals, and paging-fault metric
  names and types; several plural, reordered, and body-field forms changed.

### Collector

- In Go code, replace `configgrpc.BalancerName` with
  `configgrpc.DefaultBalancerName`.
- Replace deprecated `xconfmap.WithForceUnmarshaler` with
  `confmap.WithForceUnmarshaler`.
- The failover connector no longer accepts `retry_gap` or `max_retries`.
- The JMX receiver and Kafka Topics Observer have been removed.
- Rename the AWS ECS attributes processor type from `awsecsattributes` to
  `aws_ecs_attributes`; there is no alias for the old name.
- `cumulativetodelta` and `spanpruning` survive only as deprecated aliases for
  `cumulative_to_delta` and `span_pruning`.
- Rename exporter type `azuremonitor` to `azure_monitor`. Rename receiver type
  `sqlquery` to `sql_query`; the old receiver type remains a deprecated alias.
- Routing, filter, and transform processing now default top-level `error_mode`
  to `ignore`. Read the gate details before relying on compatibility behavior.
- Host Metrics aggregates CPU time and utilization across logical CPUs by
  default, omits the `cpu` attribute, and enables
  `system.cpu.logical.count`.
- File Log `ordering_criteria.top_n: 0` now selects all files. Set `1`
  explicitly to preserve the earlier single-file behavior.
- Go integrations for Collector core 0.159 must use named zpages and HTTP auth
  fields instead of relying on promoted embedded fields.

## High-value specification behavior

### Context and sampling

- Environment-variable carriers are Release Candidate. Normalize requested,
  carrier, and returned keys; read and return only normalized environment
  names; normalize an empty name to `_`.
- Carrier caching is deliberately unspecified.
- Context propagation requires the W3C randomness flag.
- `AlwaysRecord` is stable.
- Dynamic Sampling and Tail Sampling can consume W3C `ot=th` thresholds and
  `ot=rv` randomness. Check their gate and shutdown behavior before enabling
  tracestate-aware sampling.

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
- Logs can bridge an event into a span event and represent entity information
  as structured events.
- Profiles have a signal specification, data model, and supplementary pprof
  guidance.
- Standard OTLP exporter configuration includes maximum request- and
  response-size controls.

### Resources, entities, and attributes

- A Resource describes the observed entity, not necessarily the component
  that emitted the telemetry.
- Entity is defined by the specification and supported by the Resource SDK.
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

### Reload and delivery constraints

- Enable `--feature-gates=service.partialReload` for the alpha partial-reload
  path; `service.partialReloadReceivers` is beta.
- A partial reload restarts only receivers when every non-receiver part of the
  configuration is unchanged.
- With `exporter.kafka.useRequestType`, all signals become Kafka records when
  the exporter request is created and `queue_batch.sizer: items` counts those
  records. Persistent `sending_queue.storage` is a startup error in this mode.
- With `datadog.serializerexporter.UseSyncForwarder`, serializer 4xx/5xx
  failures flow through `exporterhelper`, so retry, queue-overflow, and
  failed-point telemetry apply.
- Elasticsearch document-level retries use
  `retry::retry_on_document_status`, independently of request-level retries.
- OpenSearch managed templates are accepted only in `otel-v1` mapping mode
  and are created idempotently without replacing existing templates.
- Prometheus Remote Write nested `http` settings override flat settings;
  deadline expiration is retriable and idle exporters flush buffered WAL
  entries.

## Upgrade checklist

1. Identify whether the change targets the specification, semantic
   conventions, an SDK, Collector core, or Contrib.
2. Check stability labels and feature-gate defaults before treating a feature
   as generally available.
3. Audit renamed attributes, metrics, component types, configuration keys,
   Go fields, and event-body layouts before an upgrade.
4. Recheck metric units, instrument types, aggregation, required attributes,
   and cardinality; several receiver and convention changes affect dashboards
   and alerts.
5. Treat exception messages, query parameters, GraphQL documents, raw logs,
   and database queries as sensitive capture surfaces.
6. For Collector gates, distinguish default-on from default-off behavior and
   verify mutual exclusions and staged migrations before deployment.
7. Open the matching reference for complete conditions, values, and
   receiver- or exporter-specific details.
