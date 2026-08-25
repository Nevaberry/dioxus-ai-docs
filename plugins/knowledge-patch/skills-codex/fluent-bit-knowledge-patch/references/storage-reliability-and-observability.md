# Storage, Reliability, and Observability

## Dead-letter queues

Invalid filesystem-backed chunks can be preserved in a dead-letter queue for
inspection instead of being discarded (since 4.2.0). Stored chunks use safe
deletion checks. Monitor quarantine growth and establish an explicit inspect,
replay, and deletion procedure.

`storage_backlog` preserves dead-letter queue data across restarts (since
5.0.0). Test an agent restart with quarantined chunks and verify that retention
does not turn a persistent bad chunk into an unbounded storage problem.

## Emitter backpressure

With filesystem storage active, emitter-backed filters such as `rewrite_tag`
automatically enable `storage.pause_on_chunks_overlimit` when the setting is
otherwise unset (5.0-guide). They pause at `storage.max_chunks_up`. Set
`storage.pause_on_chunks_overlimit off` explicitly on the relevant input only
when the earlier over-limit accumulation behavior is actually required.

Pending emitter bytes count toward `mem_buf_limit`, and records remain queued
while backpressure pauses the emitter (since 5.0.9). The Rewrite Tag filter
also retains the original record when emitter backpressure or an enqueue error
prevents retagging. Size memory limits for queued bytes, and account for the
original record when reasoning about duplicates and route outcomes.

## Output wait and chunk latency

Output monitoring includes a histogram for chunk latency (since 4.0.6).
Output metrics also expose time spent waiting on downstream backpressure
(5.0-guide). Use both to distinguish pipeline processing delay from a slow or
saturated destination.

## Routing and operational accounting

Routing metrics include performance plus matched, unmatched, and dropped event
counts (since 4.2.0). Alert on unexpected unmatched and dropped growth after
condition, input-instance, or output-label changes.

S3 output accounting more accurately describes logical records (since 5.0.0).
Metrics also provide clearer signals for grouped logs, retries, routed traffic,
worker ownership, and ingress flow. Re-evaluate SLO, chargeback, and
delivery-validation queries rather than assuming old counters have identical
meaning.

## Reload metrics

`fluentbit_hot_reloaded_times` is a counter rather than a gauge (5.0-guide).
Prometheus queries and alerts should use counter functions such as `rate()` or
`increase()` instead of gauge-oriented functions such as `delta()`.

## Health endpoints

The built-in HTTP server exposes `/api/v2/health` and returns JSON
(5.0-guide). It signals health with status `200` and failure with status `500`.
Point agent-level health checks at this endpoint and validate the JSON and
status behavior used by the monitor.

The HTTP input can separately expose `GET /health` as an ingestion readiness
probe (since 5.0.4). Use it when a load balancer or orchestrator needs to know
whether that listener is ready. Do not confuse input readiness with the
built-in server's overall health endpoint.

## Output termination thresholds

The Exit output has `time_count` in seconds and `record_count` thresholds
(since 4.0.0). Use them for controlled test and bounded-run pipelines; make the
selected exit condition explicit so production traffic cannot unexpectedly
terminate the process.
