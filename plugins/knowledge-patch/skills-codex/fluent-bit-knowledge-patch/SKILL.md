---
name: fluent-bit-knowledge-patch
description: Fluent Bit
version: 5.0.9
license: MIT
metadata:
  author: Nevaberry
---


# Fluent Bit Knowledge Patch

Use this skill when designing, upgrading, configuring, or troubleshooting
Fluent Bit pipelines. It focuses on behavior that can change routing,
authentication, buffering, delivery, and telemetry interpretation.

## How to use this skill

1. Identify the affected pipeline stage: listener, processor, router, storage,
   or output.
2. Read the breaking-change checks before changing an existing deployment.
3. Open the reference file for the affected stage.
4. Compare every setting against the running configuration format and plugin.
5. Exercise failure paths, backpressure, reloads, and restarts in addition to
   the successful path.
6. Recheck dashboards and alerts when a metric's meaning or type has changed.

## Reference index

| Reference | Topics |
| --- | --- |
| [security-and-configuration.md](references/security-and-configuration.md) | Shared HTTP listener settings, TLS, OAuth 2.0, file-backed environment variables, lifecycle, build and platform notes |
| [processing-and-routing.md](references/processing-and-routing.md) | Conditional processors, trace sampling, metric processors, labels, direct routes, route scoping |
| [inputs-and-enrichment.md](references/inputs-and-enrichment.md) | HTTP, OpenTelemetry, Tail, Syslog, Forward, Windows, Prometheus, Kubernetes, eBPF, and parser behavior |
| [storage-reliability-and-observability.md](references/storage-reliability-and-observability.md) | Dead-letter queues, emitter backpressure, supervisor and reload behavior, health checks, accounting, and metrics |
| [outputs-and-integrations.md](references/outputs-and-integrations.md) | Compression, cloud outputs, Forward, HTTP, Loki, Splunk, InfluxDB, Vivo, and delivery edge cases |

## Breaking-change checks

### Forward metadata interoperability

Forward output metadata retention is enabled by default in the affected
configuration. That extended MessagePack is not accepted by Fluentd receivers.
For a Fluentd destination, set:

```yaml
pipeline:
  outputs:
    - name: forward
      match: "*"
      host: fluentd-host
      port: 24224
      retain_metadata_in_forward_mode: false
```

Do not disable retention blindly for Fluent Bit peers that use event metadata.
Choose the value from the receiving peer's protocol support.

### Hot-reload dashboards

`fluentbit_hot_reloaded_times` is a counter. Query it with counter-aware
functions such as `rate()` or `increase()`. A gauge-oriented `delta()` query
can give misleading reload results.

### JSON escaping

`escape_unicode` is honored by all JSON-producing plugins. An upgrade can
therefore alter JSON bytes emitted by plugins that once ignored this setting.
Test downstream parsers, signatures, snapshots, and byte-sensitive consumers.

### OpenTelemetry identifiers

Log and trace identifier decoding rejects malformed values more strictly.
Validate producer-generated IDs before treating ingest failures as a Fluent Bit
transport problem.

### Route ownership

Routes belong to the exact input section that declares them. This matters when
several instances use the same input plugin or omit aliases. Keep each route
next to its intended input and test that no sibling instance receives it.

### Emitter backpressure

Pending emitter bytes count toward `mem_buf_limit`, and queued records are
retained while the emitter is paused. Rewrite Tag also retains the original
record if retagging cannot enqueue. Capacity plans and duplicate expectations
must account for these semantics.

### Secure Forward peers

Custom peers must satisfy stricter PING, PONG digest, shared-key, credential,
and acknowledgment-token validation. A username or password without a shared
key is rejected, and acknowledgment tokens are base64-encoded 128-bit values.

### Delivery failures

A missing CloudWatch log stream is unrecoverable for the current chunk; stale
stream state is evicted instead of driving retries through that state. Alert on
the lost-chunk path rather than expecting normal retry recovery.

## High-value configuration patterns

### Conditional log mutation

Attach `condition` to a log processor. Conditions can combine rules and inspect
record fields before an action runs:

```yaml
pipeline:
  processors:
    logs:
      - name: content_modifier
        match: "*"
        condition:
          operator: AND
          rules:
            - field: "$log[\"level\"]"
              operator: eq
              value: error
        action: insert
        context: log_body
        key: priority
        value: high
```

Use the processing reference for the complete operator and sampling notes.

### Tail sampling

The `sampling` trace processor supports both probabilistic head sampling and
conditional tail sampling. Tail rules can use status, latency, attributes,
span count, or trace state. Set a decision wait that matches the expected trace
completion window and budget memory for traces held until the decision.

### Direct routes

An input can route directly to selected outputs with conditions and context
variables. Direct routes can target output labels and plugin names, survive
chunk restoration and reload, and bypass the traditional route path. Inspect
matched, unmatched, and dropped routing counters after deployment.

### HTTP listener hardening

HTTP-family inputs share `http_server.*` listener settings. Apply connection,
worker, buffer, and ingress-queue limits at the listener, then layer on:

- `tls.verify_client_cert on` for mutual TLS;
- bearer-token validation through `oauth2.validate`;
- `/api/v2/health` for the built-in server's JSON health status;
- input-specific `/health` where the HTTP input readiness probe is enabled.

Legacy short listener names remain aliases, but new configurations should use
the canonical names.

### File-backed secrets

An environment value may load from `file://`, after which `${...}`
substitution works normally:

```yaml
env:
  TOKEN: file://mysecret.txt
pipeline:
  outputs:
    - name: http
      header: Bearer ${TOKEN}
```

Mount the file with least privilege and verify reload behavior when rotating it.

### Internal diagnostics as records

Use the `fluentbit_logs` input to ingest the agent's own logs as structured
pipeline records. They can be filtered, enriched with local Kubernetes
metadata, and forwarded like other telemetry. Keep a failure-safe diagnostic
destination so a broken primary output does not hide agent failures.

## Reliability checklist

- Decide whether invalid filesystem chunks must enter the dead-letter queue.
- Verify quarantined chunks survive a restart through `storage_backlog`.
- Size emitter `mem_buf_limit` for pending bytes as well as accepted records.
- Check automatic `storage.pause_on_chunks_overlimit` behavior when filesystem
  storage and emitter-backed filters are combined.
- Measure output wait time under downstream backpressure.
- Test multiline truncation and Tail long-line handling with oversized input.
- Confirm HTTP senders interpret busy, ingest-error, authentication, and other
  status codes correctly.
- Test hot reload under the watchdog and process recovery under supervisor mode.
- Compare logical record counts, retries, routes, worker ownership, and ingress
  metrics with existing SLO and chargeback queries.
- Validate load-balancer probes against the intended health endpoint.

## Pipeline review checklist

### Inputs

- Confirm decompression, framing, parser, maximum-message, and Unicode behavior.
- Validate OpenTelemetry JSON, null, ID, profile, and histogram producers.
- Check cursor database journaling and locking for Kubernetes events.
- Treat client-address capture from `X-Forwarded-For` as trusted only behind a
  controlled proxy.
- Enable skipped-line and multiline diagnostics where data loss matters.

### Processing and routing

- Confirm conditions use the intended record context and value types.
- Compare tail-sampling reconcilers before completing a migration.
- Verify cumulative-to-delta conversion is limited to cumulative monotonic
  metrics.
- Exercise restored chunks and reloads through every direct route.
- Watch matched, unmatched, and dropped counts.

### Outputs

- Match compression codecs to the exact output plugin and receiver.
- Revalidate Forward metadata and Secure Forward handshake compatibility.
- Treat S3 accounting as logical-record accounting when checking delivery.
- Confirm AWS authentication and managed-identity settings on their supported
  outputs.
- Exercise HTTP `PUT`, OAuth client credentials, and non-success responses.

## Validation strategy

Run a representative record through each changed input, processor, route,
storage path, and output. Then repeat with malformed data, expired credentials,
oversized records, saturated outputs, a hot reload, and a restart. Compare
payload bytes, response codes, routing counters, queued bytes, skipped records,
dead-letter contents, and downstream acknowledgments.
