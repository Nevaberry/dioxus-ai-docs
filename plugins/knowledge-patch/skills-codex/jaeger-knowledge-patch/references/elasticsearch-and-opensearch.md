# Elasticsearch and OpenSearch

## Migration and supported backends

- **V2 configuration (2.0.0):** Elasticsearch/OpenSearch configuration was
  reorganized and TLS moved to OpenTelemetry configuration. The storage
  exporter also gained queueing configuration.
- **Version compatibility (2.9.0):** Elasticsearch 9 range queries and index
  templates are supported, using the Elasticsearch 8 template, and OpenSearch
  3.x is supported.
- **Elasticsearch 6 removal (2.20.0):** Elasticsearch 6 is unsupported. Upgrade
  that backend before moving Jaeger to 2.20.
- **Active v2 implementation (2.7.0):** Jaeger v2 uses the storage API v2
  Elasticsearch/OpenSearch implementation. Earlier experimental coverage
  arrived in 2.6.0 with trace writes, retrieval and search, trace-ID search,
  service and operation lookup, and dependency reads and writes.

## Index mappings, templates, and aliases

- **Mapping generator:** Since 2.3.0, `esmapping-generator` is part of the main
  `jaeger` binary. In 2.20.0 it gained `--backend` for OpenSearch-specific
  output:

  ```sh
  jaeger esmapping-generator --backend opensearch
  ```

- **Classification tags (2.8.0):** Storage materializes `span.kind` and
  `span.status`. This mapping change is breaking; review mappings and consumers.
- **Scope and links (2.19.0):** Index templates include the previously missing
  OTLP scope and link fields.
- **Explicit aliases (2.14.0):** Configure `indexspanalias` and
  `indexservicealias` when span and service index aliases must be selected
  directly.
- **Parent-span compatibility (2.20.0):** Writes populate `parentspanid`.
  A feature gate controls the reference-compatibility write path during
  migration.
- **OpenSearch rollover aliases (2.20.0):** ISM generation emits
  `rollover_alias`.

## Rotation, cleanup, and lifecycle

- **Idempotent rollover (2.4.0):** The rollover command checks whether the
  target index or alias exists. Bootstrap jobs may safely retry initialization.
- **Index cleanup (2.5.0):** The cleaner can delete indices using current time
  as its time basis.
- **Rotation schema (2.20.0):** Rotation and index-cleaner feature gates are
  beta. The new index-rotation schema deprecates legacy flags, and storage adds
  `max_trace_duration` for revised time-range handling. Review existing
  rotation, cleaner, and trace-duration settings.
- **Data streams (experimental, 2.20.0):** `datastreamrotation` supplies a
  data-stream-aware span writer as an alternative rotation model.

## Connections, health, and request behavior

- **Compression (2.6.0):** Elasticsearch storage can enable gzip compression.
  The release classifies this option as breaking, so review the setting during
  upgrade.
- **Health checks:** Storage can disable the health check (since 2.7.0) or set a
  startup health-check timeout (since 2.16.0).
- **Replica count (2.7.0):** An explicit `replicas=0` is honored, enabling
  single-node indices without replicas.
- **Custom headers (2.12.0):** Storage requests accept custom HTTP headers.
  In 2.18.0, configured inbound headers can be forwarded to
  Elasticsearch/OpenSearch. In 2.20.0, `custom_headers` are applied to every
  Elasticsearch client and honor the host override.
- **Authentication:** API-key authentication and reloadable bearer tokens were
  added in 2.9.0, with bearer-token handling shared by multiple storage
  backends. AWS SigV4 authentication arrived in 2.12.0; replayable request
  bodies fixed SigV4 writes in 2.18.0. In 2.20.0, administration tools accept
  bearer-token and API-key CLI options, and validation rejects mutually
  exclusive authentication methods.

## Trace IDs, summaries, and metrics

- **Legacy trace IDs:** The span reader can disable legacy-ID handling
  (since 2.5.0). `jaeger.es.disablelegacyid` became stable in 2.8.0; review any
  deployment that still requires legacy identifiers.
- **Native summaries (2.20.0):** Elasticsearch implements a native trace-summary
  reader, avoiding query-service full-trace aggregation for summary searches.
- **Experimental SPM:** In 2.8.0 the Elasticsearch path implemented call-rate
  retrieval and introduced a metric-storage skeleton. Version 2.9.0 added
  error-rate and latency retrieval, time-range optimization, an OpenSearch
  option, and `metrics_storage` in Elasticsearch/OpenSearch configuration.
