# Storage Backends and Extension Contracts

## Storage API and remote-storage contracts

- **Removed plugin type (2.0.0):** The `grpc-plugin` storage type is gone;
  configurations selecting it cannot be migrated unchanged.
- **gRPC consolidation and tenancy (2.0.0):** V1 and v2 gRPC storage
  configuration was consolidated, and tenant information is propagated to the
  remote backend.
- **V2 read path (2.1.0):** The v2 storage interface supports trace reads.
  `ArchiveTraceRequest` time fields are non-nullable. In storage v1,
  `GetTraceRequest` gained a time window and non-pointer start/end values.
- **Streaming read transition (2.2.0):** Experimental storage v2 renamed
  `GetTrace` to `GetTraces` and made reads streaming.
- **Primary/archive unification (2.3.0):** Primary and archive storage no longer
  have separate interfaces. The remote handler removed archive-specific
  readers/writers, and query creates archive access through normal factory
  methods.
- **Completed v2 protocol (2.4.0):** Remote-storage IDL covers trace and
  dependency storage, including `GetTraces`, `GetServices`, and
  `GetOperations`. `FindTraceIDs` returns trace start/end timestamps in both v2
  and remote APIs. The storage extension holds v2 factories and exposes helpers
  for the purger and sampling-store factory.
- **V2 gRPC implementation (experimental, 2.5.0):** The factory, trace writer,
  dependency reader, and trace reader implement `FindTraces`, `GetTraces`,
  `FindTraceIDs`, `GetOperations`, and `GetServices`. Trace streams now carry
  OTLP traces directly; the `traceschunk` wrapper was removed.
- **Remote server (experimental, 2.6.0):** The remote-storage server registers
  a v2 gRPC handler backed by v2 factories, uses the normal OTLP
  receiver/exporter path for writes, and handles trace, service, dependency, and
  trace-ID operations. Remove `jaeger_query` from its backend configuration.
- **Legacy gRPC removal (2.14.0):** `storage/v1/grpc` is removed. Remote storage
  uses YAML based on the shared storage configuration package.
- **Dependency writer (2.18.0):** The v2 dependency-store writer accepts a
  context; implementations must update the signature and propagate it.
- **Trace-ID request (2.19.0):** Storage-v2 `FindTraceIDs` uses
  `FindTraceIDsRequest`; update generated code and custom implementations.
- **gRPC client limits (2.19.0):** Configure `max_recv_msg_size_mib` to bound or
  raise the receive limit:

  ```yaml
  max_recv_msg_size_mib: 64
  ```

- **Header forwarding (2.18.0):** The gRPC backend can forward configured
  headers for authentication, tenancy, or proxy metadata.

## Memory and Badger

- **Configuration validation (2.0.0):** Badger options and namespace settings
  were consolidated, the unused Badger `namespace` field was removed, and both
  Badger and memory configurations gained validation.
- **V2 memory progression:** The v2 memory backend added writes plus service and
  operation lookup in 2.6.0; `FindTraces`, `FindTraceIDs`, `GetTraces`, and
  `GetDependencies` in 2.7.0; and became Jaeger v2's active memory
  implementation in 2.8.0.
- **OTLP-aware search (2.14.0):** Memory searches include OTLP first-class
  fields.
- **Link and error filters:** Tag searches include span-link attributes
  (since 2.16.0), and error filters accept string form (since 2.17.0).

## Cassandra

- **Compatibility and configuration (2.0.0):** Cassandra 3.x support is
  removed, 5.x support is added, and v2 configuration follows OpenTelemetry
  configuration.
- **Initialization (2.1.0):** Sessions create the schema on initialization.
  Default compaction window is two hours; configure another value explicitly.
- **Schema tooling (2.3.0):** The Cassandra schema script accepts a replication
  parameter.
- **V2 lookups (experimental, 2.14.0):** The v2 backend implements
  `GetServices` and `GetOperations`. The deprecated Cassandra `namespace`
  option is removed.
- **V2 writes and timeouts (2.18.0):** The backend implements the v2 trace
  writer. Omitted Cassandra timeout settings preserve gocql driver defaults.

## ClickHouse

- **Reads and schema (experimental):** Version 2.7.0 added `GetServices` and
  `GetOperations` with a reworked schema; 2.8.0 added `GetTraces`.
- **Writes and attributes (experimental):** Version 2.11.0 added a minimally
  configured factory and writer; the span table stores span, event, and complex
  attributes. In 2.12.0 the backend joined the storage extension and its writer
  preserved links, events, scope attributes, and resource attributes.
- **Trace search (experimental, 2.14.0):** `FindTraces` is implemented.
  `FindTraceIDs` filters primitive/complex attributes, timestamps, and duration
  and fills trace start/end timestamps. Schema additions include
  `trace_id_timestamps` and materialized views for trace-ID timestamps and
  attribute metadata.
- **Event metadata (experimental, 2.15.0):** A materialized view covers event
  attributes, and string-attribute lookup resolves stored attribute types.
- **Trace-ID deduplication (experimental, 2.17.0):** The timestamp schema and
  query deduplicate trace IDs.
- **SPM, dependencies, and TTL (experimental, 2.18.0):** Metric storage is
  integrated and implements call-rate, error-rate, and latency queries;
  dependency writes and configurable TTL are supported.
- **TLS (experimental, 2.19.0):** ClickHouse connections accept TLS
  configuration.
