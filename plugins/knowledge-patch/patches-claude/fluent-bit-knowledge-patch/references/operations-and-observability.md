# Operations and Observability

## Process supervision and reloads

Supervisor mode introduced in 4.1.0 runs a parent process that watches the
Fluent Bit child process. Use it when parent-managed recovery and a stable
process boundary improve operational reliability, and test graceful recovery
with the service manager that launches the supervisor.

The same version adds a timeout watchdog around hot reload, protecting the
process when a reload does not finish safely. Include stalled and invalid
reloads in operational tests rather than checking only successful
configuration changes.

The `5.0-guide` source batch changes `fluentbit_hot_reloaded_times` from a gauge
to a counter. Prometheus queries should use counter functions such as `rate()`
or `increase()` instead of gauge-oriented functions such as `delta()`. Update
recording rules before comparing reload rates across an upgrade boundary.

## Health endpoints

The built-in HTTP server exposes `/api/v2/health` as JSON in `5.0-guide`. It
returns HTTP `200` for health and `500` for failure. This reports built-in
server health and is distinct from the optional HTTP input readiness endpoint.

Since 5.0.4, an HTTP input can expose `GET /health`. Use that endpoint when a
load balancer or orchestrator needs to know whether HTTP ingestion itself is
ready. Probes should not treat the two endpoint paths as interchangeable.

## Output latency and backpressure

Output monitoring includes a chunk-latency histogram since 4.0.6. The
`5.0-guide` source batch adds the time an output spends waiting on downstream
backpressure. Use the histogram to observe end-to-end chunk delay and the wait
metric to separate downstream pressure from processing time.

Route monitoring added in 4.2.0 reports routing performance and matched,
unmatched, and dropped event counts through `/metrics`. Alert on unexpected
unmatched and dropped outcomes, not just latency.

## Accounting and loss signals

Version 5.0.0 makes S3 output accounting more accurately reflect logical
records. It also clarifies metrics for grouped logs, retries, routed traffic,
worker ownership, and ingress flow. SLOs, delivery validation, and chargeback
queries may change meaning even when delivery behavior is healthy, so compare
the query definitions as part of an upgrade.

Tail's skipped-line counter, also added in 5.0.0, exposes an input-loss mode
that was previously silent. Multiline processing from 4.1.0 separately reports
oversized-buffer truncation through new metrics and diagnostics. Monitor both
signals because a skipped line and a truncated multiline record are different
failures.

## Platform support

Version 4.1.0 adds compatibility with Debian Trixie, Rocky Linux 10,
AlmaLinux 10, and CentOS Stream 10. Validate packaging, service management,
filesystem permissions, and plugin dependencies on the target distribution
instead of treating distribution compatibility as identical deployment
configuration.
