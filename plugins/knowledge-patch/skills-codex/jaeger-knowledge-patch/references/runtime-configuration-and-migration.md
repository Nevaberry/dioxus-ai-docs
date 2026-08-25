# Runtime Configuration and Migration

## Distribution and role migration

- **Unified v2 distribution (2.0.0):** Deploy the `jaeger` binary or image. The
  `jaeger-agent` artifact is gone, so remove packages, launch units, and image
  references that expect it. Jaeger no longer publishes `v1` or `v1.x` image
  tags or an unversioned tag; `latest` is attached only to versioned main-branch
  images.
- **Retired v1 services (2.14.0):** The v1 `collector`, `query`, `ingester`, and
  `all-in-one` components are no longer published, and the v1 ingester's
  Kafka-specific code is removed. Move deployments and Compose definitions to
  the unified binary. Remaining v1 utilities use v2.x.x versions.
- **Runtime roles:** One v2 runtime can be configured as collector, query
  service, Kafka ingester, all-in-one, or agent. Collector receives and stores
  traces; query serves APIs and the UI; ingester reads Kafka and stores traces;
  all-in-one combines collector and query. For an agent that also processes
  metrics or logs, use the standard OpenTelemetry Collector.
- **Collector distribution:** The Jaeger binary is a customized OpenTelemetry
  Collector distribution containing upstream, contrib, and Jaeger components.
  It does not require a separate Collector in front. Keep an upstream Collector
  when a sidecar, host agent, or remote tier must enrich or sample data, or use
  OpenTelemetry Collector Builder to make a custom Jaeger distribution.

## YAML, servers, and components

- **Collector-style configuration:** V2 uses OpenTelemetry Collector YAML and
  does not automatically translate v1 Jaeger environment variables. Interpolate
  environment variables with defaults and use `--set` for dotted-path
  overrides, including built-in all-in-one paths:

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

- **Query server migration (2.0.0):** Query HTTP/TLS server settings use
  OpenTelemetry configuration, and the wider query-service configuration was
  refactored. Review every v1 query-server setting explicitly.
- **Listen-host override (2.1.0):** Container deployments can parameterize and
  override the listen host. Check explicit host values when sharing a
  configuration between container and non-container environments.
- **Separate query ports (2.4.0):** HTTP and gRPC query servers cannot share a
  listen port. Assign distinct ports before starting the upgraded service.
- **Included components:** The distribution includes the Collector
  `filterprocessor` and `pprof` extension (since 2.6.0), and its component
  factory registers the `basicauth` extension (since 2.13.0).
- **Exactly one backend type (2.15.0):** Each trace- or metric-storage
  configuration must select exactly one backend type. Multiple selected types
  fail validation.
- **Kafka receiver key (2.16.0):** Replace singular `traces.topic` with the
  list-valued `traces.topics`:

  ```yaml
  traces:
    topics:
      - jaeger-spans
  ```

## Named storage wiring

The `jaeger_storage` extension registers named trace and metric backends shared
by readers and writers. `jaeger_query` selects names for APIs and UI, while
`jaeger_storage_exporter` selects a named trace backend for pipeline writes:

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

## Reverse proxies and base paths

- `jaeger_query.base_path` is the internal prefix on routes received by Jaeger,
  not necessarily the external browser prefix. Leave it `/` when a proxy strips
  the external prefix; otherwise set it to the forwarded prefix.
- The value must start with `/` and cannot contain `..` or duplicate slashes.

  ```yaml
  extensions:
    jaeger_query:
      base_path: /jaeger
  ```

- The UI API v3 client honors the configured prefix (since 2.16.0). The query
  frontend and UI can also discover the URL prefix from the browser URL at page
  load (since 2.18.0), reducing the need for a separately configured UI path.

## Source and extension compatibility

- **Internal Go packages (2.5.0):** Many former imports moved under `internal`:
  `pkg/{testutils,otelsemconv,cassandra,adjuster,es,distributedlock,httpmetrics,gogocodec,httpfs,bearertoken,boundqueue,metrics,kafka,prometheus,version,gzipfs,jtracer,telemetry,fswatcher,config,healthcheck,hostname,recoveryhandler,tenancy}`,
  `model/proto`, `model/converter`, `model/json/model.go`, and `proto-gen`.
  `pkg/netutils` was removed, and `pkg/normalizer` moved into the collector.
  External modules must replace or own dependencies on these repository paths.
- **Build toolchain (2.16.0):** Source builds require Go 1.25.7.
- **UI toolchain (2.20.0):** Jaeger UI and embedded-UI builds use pnpm rather
  than npm; update contributor and build automation.
