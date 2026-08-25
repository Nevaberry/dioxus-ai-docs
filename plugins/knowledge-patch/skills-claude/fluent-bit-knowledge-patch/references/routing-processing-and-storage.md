# Routing, Processing, and Storage

## Conditional log processing

Since 4.0.0, log processors can gate work with a `condition`. Conditions use
operators such as `and`, `or`, `in`, `gt`, `lt`, and `regex`; operator names
may be written in uppercase in YAML. This example inserts a priority only into
error records:

```yaml
pipeline:
  processors:
    logs:
      - name: content_modifier
        match: '*'
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

The Labels processor also accepts record-accessor patterns for selecting label
values (since 4.0.0). Use accessors when labels live in nested record fields
rather than copying those fields solely for label extraction.

The AWS filter sends entity attributes used for telemetry association since
4.0.6. Preserve those attributes through later processors when the receiving
AWS service depends on entity association.

## Trace sampling

The `sampling` trace processor introduced in 4.0.0 supports probabilistic head
sampling and conditional tail sampling. Tail decisions can inspect status
code, latency, string, numeric, or Boolean attributes, span count, and trace
state:

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

The source batch `5.0-guide` adds `legacy_reconcile`. Use it during an upgrade
to compare tail-sampling decisions from the optimized reconciler with the
previous implementation before committing to the new behavior.

## Direct routing

Direct routing introduced in 4.2.0 lets an input bypass the traditional
routing mechanism and target outputs directly. A direct route can:

- apply conditions and context variables;
- match output labels and plugin names obtained from chunk metadata;
- be declared in YAML; and
- survive chunk restoration and configuration reloads.

Routing metrics on `/metrics` report performance plus matched, unmatched, and
dropped event counts. Use all three outcome counters when validating a route;
a healthy output alone does not prove that unmatched or dropped traffic stayed
within expectations.

Since 5.0.4, a route is bound to the exact input section that defines it. This
matters when a pipeline has multiple instances of the same input plugin or
instances without aliases: one instance's route no longer applies accidentally
to the others. Define and test routes per input section instead of relying on a
plugin-name-wide effect.

## Dead-letter queues and restart recovery

Since 4.2.0, invalid filesystem-backed chunks can be retained in a dead-letter
queue for later inspection. Safe deletion checks protect stored chunks. Build
recovery procedures around quarantine and explicit inspection rather than
assuming that invalid chunks disappear.

In 5.0.0, `storage_backlog` gained dead-letter queue persistence across agent
restarts. Recovery tests should therefore include a restart and verify that the
quarantined data remains available without re-entering normal delivery.

## Emitter backpressure

The behavior described by `5.0-guide` applies when filesystem storage is
enabled and `storage.pause_on_chunks_overlimit` is otherwise unset:

- emitter-backed filters such as `rewrite_tag` automatically enable the
  setting;
- emitters pause when storage reaches `storage.max_chunks_up`; and
- setting `storage.pause_on_chunks_overlimit off` explicitly on the relevant
  input restores the previous over-limit accumulation behavior.

Use the explicit `off` value only when accumulation is intentional and the
filesystem and memory risks are understood.

Version 5.0.9 strengthens the retention contract. Pending emitter-queue bytes
count toward `mem_buf_limit`, records remain queued while backpressure pauses
the emitter, and Rewrite Tag keeps the original record when backpressure or an
enqueue error prevents retagging. Capacity estimates must include queued bytes,
and downstream duplicate analysis must account for retained originals.

## Metric processors

The cumulative-to-delta processor in `5.0-guide` converts cumulative monotonic
metrics, including Prometheus-style samples, to delta temporality for backends
that require deltas. Apply it only to cumulative monotonic inputs and make sure
the backend does not perform the same conversion again.

The same source batch introduces a metrics processor for topological data
analysis. Place topology analysis where its derived data will retain the
necessary metric context through the remainder of the pipeline.
