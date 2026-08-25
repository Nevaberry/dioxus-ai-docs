---
name: langgraph-knowledge-patch
description: LangGraph
version: null
license: MIT
metadata:
  author: Nevaberry
---


# LangGraph Knowledge Patch

Load this skill when building, migrating, debugging, reviewing, or deploying
LangGraph applications in Python or JavaScript. Check the project's manifests
and lockfiles first because the Python, JavaScript, checkpoint, SDK, and server
packages evolve independently.

## How to use this patch

1. Identify the language, package names, and exact installed versions.
2. Read the reference matching the task before changing graph topology, state,
   persistence, interrupts, streaming, or deployment configuration.
3. Treat graph code, persisted state, and deployment configuration as one
   compatibility surface. A change that is locally valid may still be unsafe
   for interrupted threads or server-managed persistence.
4. Prefer public imports and verify behavior against the repository's tests.
5. For upgrades, audit deprecated APIs, runtime floors, saved-thread
   compatibility, stream consumers, and custom checkpointer conformance.

## Reference index

| Reference | Topics |
| --- | --- |
| [migrations-and-state.md](references/migrations-and-state.md) | Agent migration, runtime floors, state schemas, private and untracked state, reducers, context, routing, recursion |
| [execution-and-reliability.md](references/execution-and-reliability.md) | Caching, replay, retries, timeouts, error handling, execution metadata, draining, fan-in, tracing |
| [persistence-and-subgraphs.md](references/persistence-and-subgraphs.md) | Durability, checkpoint namespaces, delta channels, custom savers, encryption, subgraph lifetimes and inspection |
| [streaming-and-interrupts.md](references/streaming-and-interrupts.md) | Typed interrupts, v3 streams, wire encoding, UI transports, parallel resumes, validation loops |
| [deployment.md](references/deployment.md) | Server graph loading, storage roles, runtime layouts, queues, threadless runs, non-LangGraph agents |

## Breaking changes and deprecations

### Construct agents through LangChain

Use `langchain.agents.create_agent` in Python and `createAgent` from `langchain`
in JavaScript. Rename `prompt` to `system_prompt` in Python or `systemPrompt` in
JavaScript.

```python
from langchain.agents import create_agent

agent = create_agent(model, tools, system_prompt="You are helpful.")
```

```typescript
import { createAgent } from "langchain";

const agent = createAgent({ model, tools, systemPrompt: "You are helpful." });
```

The Python prebuilt compatibility changes are:

- Import `AgentState` from `langchain.agents`.
- Replace Pydantic and structured-response state variants with `AgentState`.
- Rename `HumanInterruptConfig` and `ActionRequest` to `InterruptOnConfig`.
- Rename `HumanInterrupt` to `HITLRequest`.
- Replace `ValidationNode` with `create_agent` tool-input validation.
- Replace `MessageGraph` with `StateGraph` and a `messages` state key.

### Respect runtime and package boundaries

JavaScript packages require Node.js 22 or newer. Python-side LangChain packages
require Python 3.10 or newer. JavaScript packages publish bundled output; remove
private `dist/` imports and import only public modules.

### Do not use removed stream helpers

`toLangGraphEventStream` is removed. Request the wire encoding from
`graph.stream` and return the resulting stream directly.

```typescript
const stream = await graph.stream(input, {
  encoding: "text/event-stream",
  streamMode: ["values", "messages"],
});
return new Response(stream, {
  headers: { "Content-Type": "text/event-stream" },
});
```

## State and routing quick reference

### Prefer `StateSchema` in JavaScript

Use `MessagesValue` for message-aware reduction and `ReducedValue` for a typed
field with a default and custom reducer. `Annotation.Root` and direct Zod v3/v4
state integrations are legacy alternatives.

```typescript
const State = new StateSchema({
  messages: MessagesValue,
  total: new ReducedValue(z.number().default(0), {
    reducer: (current, update) => current + update,
  }),
});
```

Python `BaseModel` state is validated only before the first node. Later updates
and output are not revalidated, and `invoke` returns a dictionary. Prefer
`AnyMessage` for message fields that cross the wire.

### Keep runtime context out of persisted state

Declare `context_schema` in Python and read `Runtime.context`; callers pass
`context=`. In JavaScript, pass the context schema to `StateGraph`, read
`runtime.context`, and invoke with `{ context: ... }`.

For JavaScript runtime-only objects, use `UntrackedValue`. It is omitted from
checkpoints and starts fresh after resume. The default `guard: true` rejects
multiple same-step writes; `guard: false` keeps the last write.

### Treat stream visibility separately from node input

A node's input schema limits reads, not writes. Node schemas can add private
channels, and input/output/private schemas do not redact `values` streams. When
private fields must stay out of v3 events, set `output_keys` in Python or
`outputKeys` in JavaScript.

Use Python `Overwrite(value)` when a single update must bypass the channel's
configured reducer.

### Choose one routing mechanism per node

`Command(goto=...)` adds a route; it does not suppress static outgoing edges.
Using both causes both destinations to run. The same rule applies to commands
returned by tools.

Any `Command` passed to `invoke` or `stream` resumes the latest checkpoint.
Use `Command(resume=...)`, optionally with `update`, for a resume. Start a new
turn on an existing thread with a plain state mapping, not `Command(update=...)`.

## Reliability quick reference

### Make replayed work idempotent

An interrupted or retried node restarts from its beginning. Put non-idempotent
work in checkpointed tasks where completed results can be reused. Do not reorder
tasks or interrupts before a saved resume point.

### Configure both sides of caching

Caching requires a node cache policy and a cache on the compiled graph. An
omitted TTL means no expiry. Python's default key hashes pickled node input;
JavaScript uses `cachePolicy` and `keyFunc`, with `InMemoryCache` imported from
`@langchain/langgraph-checkpoint`.

### Set retries and timeouts deliberately

Default retry filters exclude common programming/runtime failures. Python also
retries HTTP-library errors only for 5xx responses. Use `retry_on` or `retryOn`
when the default exception selection is not appropriate.

For Python async nodes, `timeout=` accepts seconds, `timedelta`, or
`TimeoutPolicy`. A timeout raises `NodeTimeoutError`, discards buffered writes
and child-task scheduling, and retries with a fresh timer. A timeout on a
synchronous node fails compilation.

An `error_handler` runs after retries are exhausted and can return a `Command`
to update state and route recovery. `set_node_defaults()` supplies graph-wide
defaults, but explicit node settings win and defaults do not enter subgraphs.

### Understand recursion budgets

Python defaults to 1000 super-steps and JavaScript to 25. Put
`recursion_limit` or `recursionLimit` at the top invocation-config level, not
under `configurable`. Read `metadata.langgraph_step`; Python can declare
`RemainingSteps` for proactive routing.

## Persistence quick reference

Choose durability per run:

- `exit` writes when execution completes, errors, or interrupts.
- `async` persists while the next step runs and may lose the newest checkpoint
  in a crash.
- `sync` persists before advancing to the next step.

Checkpoint namespaces isolate subgraphs. The root uses `""`; child namespaces
use `node_name:uuid`, and nested namespaces join with `|`. Use a shared Store or
explicit parent-checkpoint writes when data must cross that boundary.

For custom savers, implement exact-ID and latest reads, newest-first history,
complete deletion, serialization of checkpoints/writes/metadata, and reserved
write indexes. Run `langgraph-checkpoint-conformance` in CI.

## Interrupt quick reference

In JavaScript, declare named interrupt types in the `StateGraph` constructor,
call them through `runtime.interrupt`, and use `graph.isInterrupted(result)`.

With parallel interrupts, resume with a mapping from every pending interrupt
`id` to its response. For validation, call `interrupt()` once per node
invocation and route back with a conditional edge; a loop around `interrupt()`
replays earlier iterations on every resume.

In Python v3 event streams, inspect `stream.interrupted` and
`stream.interrupts`, resume in a new stream with `Command(resume=...)`, and
repeat until completion. Message chunks, snapshots, and nested-subgraph chunks
are exposed through their typed projections.

## Deployment quick reference

An exported compiled graph is loaded once and reused by Agent Server; a factory
runs for every invocation. The server injects its checkpointer and Store, so do
not configure those in graph code.

PostgreSQL stores assistants, threads, runs, and cron jobs. Checkpoints and the
long-term Store have configurable backends. Redis is only for ephemeral
signaling, cancellation, and stream pub/sub.

Queue execution allows one active run per thread. `N_JOBS_PER_WORKER` defaults
to 10 and limits worker jobs, not API concurrency. A split deployment must keep
at least one queue worker listening.
