# Ingestion and Operations

## OTLP receiver behavior

- Since **2.0.0**, Jaeger sanitizes invalid UTF-8 and empty service names in
  OTLP input.
- Since **2.0.0**, the OTLP receiver again listens on all interfaces by
  default. Bind endpoints deliberately and account for them in network policy,
  host firewall, and service exposure.
- Since **2.3.0**, invalid OTLP payloads return HTTP 400 rather than 500.
  Classify them as client/request failures in retries, alerts, and SLOs.
- Since **2.7.0**, spans with negative durations are sanitized.
- Since **2.9.0**, array-valued tags are accepted rather than rejected as an
  invalid string type.
- Since **2.16.0**, empty span names are sanitized, so malformed input may be
  stored and returned with a normalized name.

## Receivers, processors, and exporters

- Since **2.2.0**, all-in-one enables UDP ports. Expose or deny those active
  endpoints explicitly even if OTLP is the primary ingestion path.
- Since **2.6.0**, the Jaeger distribution contains the OpenTelemetry
  `filterprocessor`, so filtering does not require a custom distribution.
- Since **2.0.0**, the storage exporter supports queueing.
- Since **2.7.0**, the storage exporter supports retry configuration. Tune
  queue capacity, retry timing, and backend timeouts as one failure policy.
- Since **2.0.0**, v2 configurations include the `remotesampling` extension and
  tail-based sampling processor. Sampling-specific behavior is in
  [query-sampling-metrics.md](query-sampling-metrics.md).

## Kafka pipelines

- Since **2.0.0**, v2 provides Kafka receiver and exporter configuration, with
  environment-variable support for Kafka settings.
- Since **2.3.0**, the shipped Kafka ingester configuration uses a metrics port
  that does not conflict with the collector. Recheck scrape targets and exposed
  ports when adopting it.
- Since **2.9.0**, Kafka TLS works together with plaintext authentication.
- Since **2.16.0**, the Kafka receiver uses list-valued `traces.topics` rather
  than singular `traces.topic`:

```yaml
traces:
  topics:
    - jaeger-spans
```

## Health, profiling, and internal telemetry

- Since **2.0.0**, v2 configurations include the health-check extension. A
  temporary `expvar` extension is also available, and the Collector can observe
  its own internal telemetry.
- Since **2.1.0**, environment variables are honored when Jaeger constructs its
  internal tracer.
- Since **2.6.0**, the distribution includes the `pprof` extension. Bind and
  protect profiling endpoints as administrative surfaces.
- Since **2.10.0**, Jaeger no longer appends an extra `_total` to metric names.
  Update dashboards and alerts that used the incorrect double suffix.
- Since **2.13.0**, the component factory registers `basicauth`, so a
  configuration that instantiates the extension can load successfully.
- Since **2.17.0**, duration-valued timer bucket settings are parsed during
  metrics initialization.

## Deployment and monitoring assets

- Since **2.8.0**, the repository includes an experimental Kubernetes demo.
- Since **2.9.0**, Jaeger 2.x includes alert definitions. The experimental demo
  adds ingress, automated TLS certificates, readiness and liveness paths,
  monitoring, and a trace-data load generator.
- Since **2.12.0**, the Jaeger/OpenSearch/OpenTelemetry demo supports a global
  image-registry value and includes clean, deploy, and port-forward scripts and
  values. Its image names are fully qualified.
- Since **2.15.0**, a Grafana dashboard for the metrics exporter ships with
  Jaeger.
- Since **2.17.0**, the SPM Compose example includes Grafana again, and a
  generated Go SDK dashboard is available.

These are example and monitoring inputs, not production security defaults.
Review credentials, persistence, ingress, resource limits, TLS issuance,
network exposure, and load-generator behavior before deployment.

## Operational validation

1. Enumerate every configured receiver endpoint, including OTLP and UDP.
2. Send valid, malformed, and oversized payloads and verify response classes.
3. Confirm normalization of empty names, invalid UTF-8, and negative durations
   is acceptable to downstream consumers.
4. Interrupt storage temporarily and observe queue saturation and retry
   behavior.
5. Verify health, telemetry, profiling, and scrape ports are reachable only
   from intended networks.
6. Exercise Kafka with the deployed TLS/authentication combination and every
   configured trace topic.
7. Compare emitted metric names with dashboard and alert selectors.
