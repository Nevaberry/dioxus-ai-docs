# Workflow Safety and Activity Recovery

## Classify Workflow edits by emitted Commands

Replay compares new Workflow code with recorded Event History. An edit is
compatible only if replay emits the same Commands in the same order.

The following edits can be compatible with existing histories:

- Change Activity or Child Workflow inputs, return values, or execution
  timeouts.
- Change external Signal inputs.
- Change Timer durations, except across the special boundaries below.
- Add calls to Workflow APIs that emit no Commands.
- Add a Signal Handler only when the affected Signal Type has not already
  appeared in those histories.

Do not change Activity or Child Workflow types or IDs. In Java, Python, and Go,
changing a Timer between `0` and a nonzero duration is nondeterministic. In
.NET, the equivalent special boundary is `-1` (infinite) versus another value.

Adding, removing, or reordering any of these operations can break replay:

- scheduling or cancelling Timers;
- scheduling or cancelling Activities;
- starting or cancelling Child Workflows;
- external Signals;
- Nexus operations;
- termination;
- patch or version markers;
- Search Attribute or Memo changes;
- Side Effect or Mutable Side Effect calls.

Protect command-changing edits with current Worker Versioning or a replay-safe
patch, or use both. Temporal recommends current Worker Versioning because it
pins Workers to code revisions and lets old and new Workflow paths coexist.
The pre-2025 experimental Worker Versioning method was scheduled for Server
removal in March 2026 and is not the model to use for current deployments.

## Design Activities for repeated execution

A Retry Policy guarantees that the Workflow observes a completed Activity once.
It does not guarantee that the Activity implementation executes exactly once.
For example, a Worker can perform an external side effect, crash before
reporting completion, and cause another attempt to repeat that side effect.

Make external operations idempotent. For a key that remains stable across
attempts of one Activity, combine Workflow Run ID with Activity ID. Do not use
an attempt number in that key.

Configure at least one Activity timeout, normally Start-to-Close. An Activity
retry starts from its initial state unless it has recorded resumable progress
through Heartbeats. Activities running for more than a few minutes should
heartbeat or poll so the Workflow can distinguish progress from failure.

Cancellation of a running Activity is delivered through heartbeat responses.
An implementation that never heartbeats cannot promptly observe cancellation,
even if the Workflow requested it.

## Add a deployment-time replay gate

Before new code polls the production Task Queue, run one Worker instance in a
verification mode and replay representative recent histories.

```python
executions = client.list_workflows(
    f"TaskQueue={task_queue} and StartTime > '{start_time}'",
    limit=100,
)
histories = executions.map_histories()
await Replayer(workflows=my_workflows).replay_workflows(histories)
```

Treat any replay error as a failed deployment. After a clean replay, start the
remaining Worker instances normally.

Fetched production histories are not automatically safe or usable in CI.
Encrypted Payloads require the matching decryptor, and histories containing
PII must be scrubbed or kept out of pre-deployment and CI replay paths.
