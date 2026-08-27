# Observability, cainjector, and Clients

## Metrics

### Certificate validity timestamps `(1.18)`

Use these metrics for certificate validity monitoring:

- `certmanager_certificate_not_before_timestamp_seconds`
- `certmanager_certificate_not_after_timestamp_seconds`

### ACME request labels `(upgrade-1.19)`

`certmanager_acme_client_request_count` and `certmanager_acme_client_request_duration_seconds` use bounded-cardinality label `action`; label `path` was removed. Update dashboards and alerts that query `path`. Reproducing its high-cardinality semantics requires a Prometheus relabeling or recording rule.

### Challenge status `(1.19)`

`certmanager_certificate_challenge_status` exposes certificate challenge state for monitoring and alerting.

### Stable chart metrics label `(1.20)`

With Prometheus monitoring enabled, the metrics label is always `cert-manager`, independent of namespace and Helm release name.

### Fixed monitor endpoint `(upgrade-1.21)`

ServiceMonitor and PodMonitor path/port overrides were removed. Metrics use `/metrics` and port name `http-metrics`; update custom scrape configuration that used `tcp-prometheus-servicemonitor`.

## Structured logging

### Context changes literal messages `(upgrade-1.17)`

Log messages include more contextual structured data. Tools that match whole lines or literal message strings may need updated rules.

## Cainjector bundle rotation

### Opt-in merging `(1.17)`

The `CAInjectorMerging` feature gate originally made cainjector merge new CA certificates into an injected bundle rather than replacing the existing certificate, preserving trust overlap during issuer rotation.

### Merging enabled by default `(1.19)`

`CAInjectorMerging` became beta and enabled by default. At this stage it could still be explicitly disabled when replacement behavior was required.

### Merging and apply are unconditional `(1.21)`

`CAInjectorMerging` is GA and always enabled, so the feature gate cannot restore replacement semantics. Cainjector also always uses server-side apply; its `ServerSideApply` feature gate is deprecated.

### Ignore selected namespaces `(1.21)`

Use cainjector `--ignore-namespaces` to exclude namespaces while watching Secrets for CA injection.

## Webhook resilience

### Resume after host suspension `(1.21)`

After system suspend or VM live migration, the webhook detects a missed serving-certificate renewal with wall-clock polling and recovers within one minute of resume.

## Client behavior

### Type-safe server-side apply `(1.19)`

Generated apply-configuration types are available for cert-manager resources, allowing typed server-side apply clients rather than unstructured apply payloads.

### Domain-qualified finalizers `(1.17)`

`UseDomainQualifiedFinalizer` is beta and enabled by default, avoiding Kubernetes warnings caused by an unqualified finalizer.
