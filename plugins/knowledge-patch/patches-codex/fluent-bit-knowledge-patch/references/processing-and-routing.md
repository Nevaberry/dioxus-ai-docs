# Processing and Routing

## Conditional log processors

Log processors can run conditionally (since 4.0.0). Put `condition` on the
processor and compose rules with operators including `and`, `or`, `in`, `gt`,
`lt`, and `regex`. The following inserts `priority=high` only for error logs:

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

Make record-accessor quoting and the chosen context part of tests; a valid rule
against the wrong context will not implement the intended policy.

## Trace sampling

The `sampling` trace processor supports probabilistic head sampling and
conditional tail sampling (since 4.0.0). Tail decisions can inspect:

- status code;
- latency;
- string, numeric, and boolean attributes;
- span count;
- trace state.

Example:

```yaml
pipeline:
  inputs:
    - name: opentelemetry
      port: 4318
      processors:
        traces:
          - name: sampling
            type: tail
            sampling_settings:
              decision_wait: 2s
            conditions:
              - type: boolean_attribute
                key: user.logged
                value: false
```

Tail sampling holds traces until a decision, so align `decision_wait` with trace
duration and capacity. The processor also provides `legacy_reconcile`
(5.0-guide), which lets an upgrade compare the optimized tail-sampling
reconciler with the earlier behavior before migration.

## Metric processors

The cumulative-to-delta processor converts cumulative monotonic metrics, such
as Prometheus-style samples, into deltas for destinations that expect delta
temporality (5.0-guide). Do not apply it indiscriminately to gauges or metrics
already expressed as deltas.

A metrics processor also supports topology-based analysis workflows
(5.0-guide). Treat its output as a processor result that must be routed and
validated like other derived metrics.

## Labels and JSON encoding

The Labels processor accepts record-accessor patterns when selecting label
values (since 4.0.0). Use accessors when labels must come from nested record
content, and test missing or non-scalar values.

`escape_unicode` is honored consistently by all JSON-outputting plugins (since
4.1.0). Existing plugins that previously ignored it can emit different bytes
after an upgrade. Recheck downstream parsing, signatures, snapshots, and any
byte-level comparisons.

## Direct routing

Inputs can route directly to outputs, bypassing traditional routing (since
4.2.0). Direct routes:

- support conditions and context variables;
- can match output labels and plugin names from chunk metadata;
- are configurable in YAML;
- survive restored chunks and reloads.

Test ordinary ingestion, restored chunks, and reloads. The `/metrics` endpoint
reports routing performance and matched, unmatched, and dropped event counts
(since 4.2.0); use those signals to catch overly narrow or unexpectedly broad
conditions.

Route definitions are bound to the exact input section that owns them (since
5.0.4). This prevents accidental cross-routing between multiple instances of
the same input plugin, including instances without aliases. Declare each route
under its intended input and test each instance independently.
