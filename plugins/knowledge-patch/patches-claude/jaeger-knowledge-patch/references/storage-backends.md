# Storage Backends and Contracts

## Register and select named storage

The **v2-runtime-model** uses the `jaeger_storage` extension to register named
trace and metric backends. `jaeger_query` selects names for reads, APIs, and the
UI; `jaeger_storage_exporter` selects a trace backend for pipeline writes.

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

Since **2.15.0**, each trace- or metric-storage entry must select exactly one
backend type. A single named entry that configures multiple types is invalid.

## Storage API and extension migrations

- Since **2.0.0**, the `grpc-plugin` storage type is removed. Existing
  configurations that select it require a different storage integration.
- Since **2.0.0**, v1 and v2 gRPC storage configuration is consolidated and
  tenant data is propagated to the gRPC backend. Remote multi-tenant
  implementations must consume and preserve that tenant context.
- Since **2.1.0**, the v2 interface includes a read path.
- In **2.1.0**, v2 `ArchiveTraceRequest` time fields became non-nullable. The
  v1 `GetTraceRequest` gained a time window whose start and end values are no
  longer pointers. Update implementations and regenerated clients.
- Since **2.2.0**, the experimental storage-v2 read API is streaming and the
  method formerly called `GetTrace` is `GetTraces`. Clients must consume a
  result stream.
- Since **2.3.0**, primary and archive storage use one contract. The
  remote-storage handler no longer exposes separate archive readers or writers,
  and v2 query obtains archive access from regular factory methods. Remove
  archive-specific integration code.
- Since **2.4.0**, the v2 remote-storage IDL covers trace and dependency
  storage, including `GetTraces`, `GetServices`, and `GetOperations`.
  `FindTraceIDs` results include trace start and end timestamps in storage-v2
  and remote storage. Update protocol implementations and generated clients.
- Since **2.4.0**, the storage extension retains v2 factories and provides
  helpers for retrieving purger and sampling-store factories.
- Since **2.5.0**, the experimental v2 gRPC implementation includes a factory,
  writer, dependency reader, and reader operations `FindTraces`, `GetTraces`,
  `FindTraceIDs`, `GetOperations`, and `GetServices`.
- Since **2.5.0**, remote-storage streaming sends OTLP traces directly; the
  `traceschunk` wrapper was removed. Regenerate both ends or change the stream
  element type manually.
- Since **2.6.0**, the experimental remote-storage server registers a v2 gRPC
  handler backed by v2 factories. Writes use the normal OTLP receiver/exporter
  path; handlers cover trace, service, dependency, and trace-ID operations. Its
  backend configuration no longer contains `jaeger_query`; remove that
  extension from old experimental configurations.
- Since **2.14.0**, `storage/v1/grpc` is removed and remote storage uses YAML
  based on the shared storage configuration package. Migrate legacy gRPC
  integrations and non-YAML remote-storage configuration.
- Since **2.18.0**, the v2 dependency writer accepts a context. Implementations
  must update their signature and propagate cancellation, deadlines, and values.
- Since **2.19.0**, storage-v2 `FindTraceIDs` accepts
  `FindTraceIDsRequest`. Update custom servers and generated callers.
- Since **2.19.0**, the gRPC storage client accepts
  `max_recv_msg_size_mib` to bound or raise its receive limit:

```yaml
max_recv_msg_size_mib: 64
```

## Elasticsearch and OpenSearch

### Configuration and transport

- Since **2.0.0**, Elasticsearch/OpenSearch configuration is reorganized and
  TLS uses OpenTelemetry configuration. The storage exporter also supports
  queueing; migrate both connection and buffering settings.
- Since **2.6.0**, storage traffic can use gzip compression. This addition was
  classified as breaking, so validate both Jaeger and backend behavior before
  enabling it.
- Since **2.7.0**, the health check can be disabled and an explicit
  `replicas=0` is honored. Use zero deliberately for single-node indexes rather
  than relying on omission behavior.
- Since **2.7.0**, storage-cleaner settings can be overridden with an
  environment variable.
- Since **2.9.0**, Elasticsearch supports API-key authentication. Reloadable
  bearer-token handling is shared by multiple storage backends.
- Since **2.12.0**, storage supports AWS SigV4 HTTP authentication and custom
  request headers.
- Since **2.16.0**, the startup health check has a configurable timeout, which
  bounds backend wait time without disabling the probe.
- Since **2.18.0**, configured headers can be forwarded to
  Elasticsearch/OpenSearch, and the gRPC backend has configurable header
  forwarding. Preserve only required authentication, tenancy, or proxy
  metadata.
- Since **2.18.0**, SigV4 write requests expose a replayable body to the signer,
  fixing authentication failures caused by an unavailable request body.
- Since **2.20.0**, Elasticsearch administration commands accept bearer-token
  and API-key CLI options. Storage validation rejects mutually exclusive
  authentication methods. `custom_headers` apply to every Elasticsearch client
  and honor the host override.

### Compatibility and mappings

- Since **2.3.0**, the main binary includes `esmapping-generator`.
- Since **2.7.0**, v2 actively uses the v2 Elasticsearch/OpenSearch
  implementation. In **2.6.0**, the earlier experimental implementation had
  already added trace writes, retrieval and search, trace-ID search, service
  and operation lookup, and dependency reads and writes.
- Since **2.8.0**, mappings materialize `span.kind` and `span.status`. This is a
  breaking mapping and consumer change; review templates and tag queries.
- Since **2.9.0**, Jaeger supports Elasticsearch 9 range queries and template
  creation by reusing the Elasticsearch 8 template, plus OpenSearch 3.x.
- Since **2.19.0**, templates include previously missing OTLP scope and link
  fields.
- Since **2.20.0**, Elasticsearch 6 is unsupported; upgrade that backend before
  upgrading Jaeger.
- Since **2.20.0**, `esmapping-generator --backend opensearch` emits
  OpenSearch-specific mappings:

```sh
jaeger esmapping-generator --backend opensearch
```

- Since **2.20.0**, Elasticsearch writes populate `parentspanid`. A feature
  gate controls the reference-compatibility write path during migration.

### IDs, aliases, cleanup, and rotation

- Since **2.4.0**, the rollover command is idempotent when its target index or
  alias already exists, so bootstrap jobs can retry it.
- Since **2.5.0**, the span reader can disable legacy trace-ID handling. The
  `jaeger.es.disablelegacyid` path became stable in **2.8.0**; deployments that
  still store legacy IDs must retain compatibility deliberately.
- Since **2.5.0**, index cleanup can use current time as its deletion basis.
- Since **2.14.0**, configure `indexspanalias` and `indexservicealias` to choose
  span and service aliases explicitly.
- Since **2.20.0**, rotation and index-cleaner feature gates are beta. A new
  index-rotation schema deprecates legacy flags, and storage has
  `max_trace_duration` for revised time-range handling. Revisit rotation and
  trace-duration settings together.
- Since **2.20.0**, generated OpenSearch ISM configuration emits
  `rollover_alias`.
- Since **2.20.0**, experimental `datastreamrotation` provides a
  data-stream-aware span write path.

### Search, summaries, and metrics storage

- In **2.8.0**, the experimental Elasticsearch SPM path supported call-rate
  retrieval and included a skeleton metrics implementation.
- In **2.9.0**, experimental Elasticsearch/OpenSearch SPM added error-rate and
  latency retrieval, optimized time ranges, an OpenSearch option, and
  `metrics_storage` configuration.
- Since **2.20.0**, Elasticsearch has a native trace-summary reader, avoiding
  query-service full-trace aggregation for summary search.

## Cassandra

- Since **2.0.0**, Cassandra 3.x is unsupported and Cassandra 5.x is supported;
  v2 configuration follows OpenTelemetry conventions.
- Since **2.1.0**, session initialization creates the schema. The default
  compaction window is two hours; configure a different window explicitly.
- Since **2.3.0**, the schema script accepts a replication parameter during
  creation.
- Since **2.14.0**, the experimental v2 backend implements `GetServices` and
  `GetOperations`. The deprecated Cassandra `namespace` option is removed.
- Since **2.18.0**, Cassandra implements the v2 trace writer. When timeouts are
  omitted, Jaeger preserves gocql driver defaults instead of overwriting them.

## Memory and Badger

- Since **2.0.0**, Badger options and namespace configuration are consolidated;
  the unused Badger `namespace` field is removed. Badger and memory
  configuration are validated.
- The v2 memory backend added writes plus service and operation lookup in
  **2.6.0**, then `FindTraces`, `FindTraceIDs`, `GetTraces`, and
  `GetDependencies` in **2.7.0**. Since **2.8.0**, Jaeger v2 actively uses the
  storage-v2 memory implementation.
- Since **2.14.0**, memory search understands OTLP first-class fields.
- Since **2.16.0**, memory tag search includes span-link attributes.
- Since **2.17.0**, memory trace search accepts error filters in string form.

## ClickHouse experimental backend

Treat this backend as experimental throughout these changes.

- In **2.7.0**, its reader implemented `GetServices` and `GetOperations` and
  its schema was reworked.
- In **2.8.0**, it added `GetTraces`.
- In **2.11.0**, it added a minimally configured factory and writer. Its span
  table stores span, event, and complex attributes.
- In **2.12.0**, it joined the storage extension, and its writer preserved
  trace links, events, and scope and resource attributes.
- In **2.14.0**, it implemented `FindTraces`; `FindTraceIDs` can filter by
  primitive and complex attributes, timestamps, and duration and populate
  trace bounds. The schema added `trace_id_timestamps` plus materialized views
  for trace-ID timestamps and attribute metadata.
- In **2.15.0**, it added event-attribute metadata materialization and attribute
  type lookup for string attributes.
- In **2.17.0**, its trace-ID timestamp schema and query deduplicated trace IDs.
- In **2.18.0**, ClickHouse metric storage joined the extension and implemented
  SPM call-rate, error-rate, and latency queries. The backend also added
  dependency writes and configurable TTL expiry.
- In **2.19.0**, it added TLS configuration.

## Remote endpoint and exporter resilience

- Since **2.7.0**, the remote-storage gRPC endpoint can be selected through an
  environment variable.
- Since **2.7.0**, `jaeger_storage_exporter` supports retry configuration in
  addition to the queueing introduced with v2. Tune retry and queue capacity
  together, then test transient and prolonged backend outages.
