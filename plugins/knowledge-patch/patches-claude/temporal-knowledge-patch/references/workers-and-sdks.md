# Workers and SDK Replay APIs

## Know the supported SDK boundary

Temporal officially supports Go, Java, Python, TypeScript, .NET, Ruby, PHP,
and Rust SDKs. Swift, Haskell, Clojure, and Scala integrations are third-party
projects rather than officially supported SDKs.

## Separate Worker Entities from Worker Processes

A Worker Entity polls exactly one Task Queue. It contains a Workflow Worker, an
Activity Worker, or both. A Worker Process can host multiple Worker Entities,
so one process can poll multiple Task Queues.

All user Workflow and Activity code runs in externally operated Worker
Processes. The Temporal Service orchestrates durable execution but never runs
that user code.

SDKs default Worker Identity to `${process.pid}@${os.hostname()}`. That value is
visible in Event History and Task Queue poller lists. In containers it often
collapses to PID `1` plus a random or ephemeral hostname. Set an explicit,
concise, unique identity that maps back to the execution context or log stream,
such as environment and region plus an ECS Task ID.

## Initialize Python Workflow state before handlers

Decorate `__init__` with `@workflow.init` when Signal, Query, or Update handlers
need initialized input-derived state. The initializer's parameters and type
annotations must match `@workflow.run`; the run method still receives those
same inputs.

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

## Use Python's deterministic utilities

Within a Workflow:

- use `workflow.logger` to avoid duplicate replay logs;
- use `workflow.random()` for deterministic randomness;
- use `workflow.uuid4()` for deterministic UUIDs;
- use `workflow.now()` for the time of the last Workflow Task.

Standard logging, randomness, UUID generation, and wall-clock APIs are not
replay-safe replacements.

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

`workflow.unsafe.is_replaying()` can suppress interceptor metrics or external
notifications during replay. Never use it to branch Workflow business logic;
that would make replay behavior differ from live execution.

For the narrower replay semantics used by built-in logging and tracing, use
`workflow.unsafe.is_replaying_history_events()`. It returns false during
read-only Queries and Update validators.

## Respect the TypeScript Workflow sandbox

TypeScript Workflows are Webpack-bundled into a deterministic sandbox. A
Workflow may import a package only when that package does not reference Node.js
or DOM APIs. If forbidden references are provably unused at runtime, list the
module in `BundleOptions.ignoreModules`.

Import Activity types to obtain type-safe proxy calls, but never import
Activity implementations into Workflow code. `WeakRef` and
`FinalizationRegistry` are unavailable because garbage collection timing is
nondeterministic.

The sandbox replaces `Math.random()`, `Date`, and `setTimeout()` with
deterministic implementations. A UUID library backed by `Math.random()` is
safe; `crypto.randomUUID()` is unavailable. `Date.now()` and `new Date()`
return the last Workflow Task completion time and advance only after an
`await`.

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

`workflowInfo().unsafe.isReplaying` is only an observability guard. Do not use
it for business-logic branches. Use
`workflowInfo().unsafe.isReplayingHistoryEvents` when matching built-in
logging and tracing semantics; it is false during read-only Queries and Update
validators.
