# Operations, Deployment, and Development

## Pipeline and endpoint operations

- **Kafka components (2.0.0):** V2 includes Kafka receiver/exporter
  configuration and accepts environment variables in Kafka settings.
- **All-in-one UDP (2.2.0):** UDP ports are enabled; expose and allow them only
  where UDP ingestion is required.
- **Kafka metrics port (2.3.0):** The shipped ingester configuration moves its
  metrics port to avoid the collector. Recheck scrape targets and exposure.
- **Kafka authentication (2.9.0):** TLS works together with plaintext
  authentication.
- **Storage exporter resilience:** Queueing arrived with the reorganized v2
  storage exporter in 2.0.0; retry configuration was added in 2.7.0.
- **Environment overrides (2.7.0):** Storage-cleaner configuration and the gRPC
  remote-storage endpoint can be overridden by environment variables.

## Commands and operational endpoints

- **Feature discovery transition:** `jaeger features` was introduced in 2.3.0
  and reverted in 2.4.0. Current runbooks must not depend on this command.
- **Trace quality (2.4.0):** `/quality-metrics` exposes trace-quality data.
- **Dependencies (2.9.0):** `/deep-dependencies` handles deep-dependency
  requests.

## Deployment assets

- **Compose registry (2.8.0):** Shipped Compose files use
  `cr.jaegertracing.io`; allow that registry in image policy and network rules.
- **Elasticsearch Compose (2.7.0):**
  `docker-compose-elasticsearch.yml` is the shipped Elasticsearch starting
  point.
- **Kubernetes demo (experimental, 2.8.0):** The repository contains a Jaeger
  Kubernetes demo.
- **Operational assets (2.9.0):** Jaeger 2.x includes alerts. The experimental
  demo has ingress, TLS certificate automation, readiness/liveness probe paths,
  monitoring, and a trace load generator.
- **Demo controls (experimental, 2.12.0):** The Jaeger/OpenSearch/OpenTelemetry
  demo supports a global image registry and clean, deploy, and port-forward
  scripts and values; image references are fully qualified.
- **Metrics dashboard (2.15.0):** A Grafana dashboard is included for the
  metrics exporter.
- **SPM assets (2.17.0):** The SPM Compose example includes Grafana, and the
  monitoring assets include a generated Go SDK dashboard.

## Platforms and exposure

- **RISC-V (2.12.0):** Distribution binaries support 64-bit RISC-V
  (`riscv64`).
- Bind OTLP and query endpoints deliberately, especially when upgrading from
  configurations whose receiver listen behavior changed. Keep health checks,
  scrape ports, readiness/liveness paths, and proxy routes aligned with the
  actual role configuration.
