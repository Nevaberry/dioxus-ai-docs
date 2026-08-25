# Workflows, Activities, and Replay

## Classify Workflow edits by history compatibility

Temporal replays Event History to rebuild Workflow state. Source changes are
safe only when the new code can consume existing histories and produce the
expected Commands.

### Replay-compatible edits

Existing histories can tolerate:

- changes to Activity or Child Workflow inputs and return values;
- changes to Activity or Child Workflow execution timeouts;
- changes to external Signal inputs;
- Timer duration changes, subject to the zero/infinite boundaries below; and
- calls to Workflow APIs that do not emit Commands.

The Activity Type, Child Workflow Type, and their IDs must remain unchanged.
Moving a Timer between `0` and a nonzero duration is nondeterministic in Java,
Python, and Go. .NET has the corresponding boundary between `-1` (infinite)
and another value. Adding a Signal Handler is safe only when a Signal of that
type has not already been received by executions whose histories will replay.

### Command-producing edits

Adding, removing, or reordering the following can make replay nondeterministic:

- Timer scheduling or cancellation;
- Activity scheduling or cancellation;
- Child Workflow scheduling or cancellation;
- external Signals;
- Nexus operations;
- termination calls;
- patch or version calls;
- Search Attribute changes;
- Memo changes;
- Side Effect calls; and
- Mutable Side Effect calls.

Protect these changes with Worker Versioning or patching. Worker Versioning is
the preferred rollout mechanism, and patching can be used alone or with it.
The experimental Worker Versioning method that predates 2025 was scheduled for
removal from Temporal Server in March 2026; use the current deployment-based
model.

## Activity execution and idempotency

A Retry Policy makes Activity completion observable exactly once, but it does
not make the Activity code execute exactly once. For example:

1. An Activity performs an external side effect.
2. Its Worker crashes before reporting completion.
3. Temporal retries the Activity.
4. The code may perform the same side effect again.

Make external operations idempotent. A useful attempt-independent key combines
Workflow Run ID with Activity ID. Do not include an attempt number when the key
must remain stable across retries.

## Heartbeats, recovery, and cancellation

A retried Activity starts from its initial state unless it established
recoverable progress through Heartbeats. Configure at least one timeout,
normally Start-to-Close. Operations longer than a few minutes should Heartbeat
or poll so the Workflow can distinguish ongoing progress from failure.

A running Activity must allow Heartbeating for cancellation to be delivered.
Design Heartbeat details as resumable checkpoints when retrying from the
beginning would be unsafe or expensive.

## Python Workflow initialization

Decorate a Workflow constructor with `@workflow.init` when Signal, Query, or
Update handlers need state initialized from Workflow inputs. The constructor's
parameters and type annotations must match the `@workflow.run` method, which
still receives the same inputs.

```python
from temporalio import workflow

@workflow.defn
class Greeting:
    @workflow.init
    def __init__(self, name: str) -> None:
        self.name = name

    @workflow.run
    async def run(self, name: str) -> str:
        return f"Hello, {self.name}"
```

## Python replay-safe values

Within Workflow code:

- use `workflow.logger` so replay does not duplicate log entries;
- use `workflow.random()` for deterministic randomness;
- use `workflow.uuid4()` for deterministic UUIDs; and
- use `workflow.now()` for the last Workflow Task time.

Standard logging, random, UUID, and wall-clock APIs are not replay-safe.

```python
from temporalio import workflow

@workflow.defn
class ReplaySafeValues:
    @workflow.run
    async def run(self) -> str:
        workflow.logger.info("Generating value")
        value = workflow.random().randint(1, 100)
        identifier = workflow.uuid4()
        current_time = workflow.now()
        return f"{value}:{identifier}:{current_time.isoformat()}"
```

## Replay guards are observability-only

Python's `workflow.unsafe.is_replaying()` and TypeScript's
`workflowInfo().unsafe.isReplaying` can suppress custom interceptor metrics or
notifications while replaying. Do not branch Workflow business logic on these
values; doing so breaks determinism.

For semantics matching built-in logging and tracing, use:

- Python `workflow.unsafe.is_replaying_history_events()`; or
- TypeScript `workflowInfo().unsafe.isReplayingHistoryEvents`.

These history-event variants return false during read-only Queries and Update
validators.

## TypeScript sandbox imports

TypeScript Workflows are bundled with Webpack into a deterministic sandbox.
Imported packages may not reference Node.js or DOM APIs. If a forbidden module
reference is provably unused at runtime, list it in
`BundleOptions.ignoreModules`.

Import Activity types to obtain type-safe calls, but never import Activity
implementations into Workflow code. `WeakRef` and `FinalizationRegistry` are
unavailable because garbage collection timing is nondeterministic.

## TypeScript deterministic globals

The sandbox replaces `Math.random()`, `Date`, and `setTimeout()` with
deterministic implementations. A UUID library backed by `Math.random()` is
safe, while `crypto.randomUUID()` is unavailable.

`Date.now()` and `new Date()` return the last Workflow Task completion time.
That time advances only after the Workflow crosses an `await`.

```typescript
import { sleep } from '@temporalio/workflow';
import { v4 as uuid4 } from 'uuid';

export async function timestampedId() {
  const id = uuid4();
  const before = Date.now();
  await sleep('1 second');
  return { id, before, after: Date.now() };
}
```

## Pre-deployment replay gate

Before a rollout polls its production Task Queue, run one instance of the new
Worker code in verification mode:

1. Select representative recent executions.
2. Convert the result iterator to histories with `map_histories()`.
3. Pass those histories to `Replayer.replay_workflows()`.
4. Fail the deployment on any replay error.
5. Start the remaining Worker instances only after a clean replay.

```python
executions = client.list_workflows(
    f"TaskQueue={task_queue} and StartTime > '{start_time}'",
    limit=100,
)
histories = executions.map_histories()
await Replayer(workflows=my_workflows).replay_workflows(histories)
```

Production histories with encrypted Payloads cannot be used where the replay
environment lacks decryption capability. Histories containing PII must be
scrubbed or excluded from pre-deployment and CI replay paths.
