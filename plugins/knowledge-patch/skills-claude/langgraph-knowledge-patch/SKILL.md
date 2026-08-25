---
name: langgraph-knowledge-patch
description: LangGraph
version: null
license: MIT
metadata:
  author: Nevaberry
---


# LangGraph Knowledge Patch

Use this skill when implementing, migrating, debugging, or deploying LangGraph
graphs in Python or JavaScript. Start with the quick rules below, then read only
the reference file that matches the work at hand.

## Reference index

| Reference | Read when working on |
| --- | --- |
| [references/migration-and-state.md](references/migration-and-state.md) | Agent migration, runtime requirements, schemas, state, context, and graph migration |
| [references/execution-and-routing.md](references/execution-and-routing.md) | Routing, replay, recursion, caching, retries, timeouts, recovery, fan-in, and tracing |
| [references/persistence-and-subgraphs.md](references/persistence-and-subgraphs.md) | Checkpoints, savers, serialization, delta channels, and subgraph lifetime or inspection |
| [references/streaming-and-interrupts.md](references/streaming-and-interrupts.md) | Event streams, transports, typed interrupts, privacy, and resume flows |
| [references/deployment.md](references/deployment.md) | Agent Server loading, storage, runtime layouts, queues, and remote streaming |

## Migration priorities

### Construct agents through LangChain

Use `create_agent` from `langchain.agents` in Python or `createAgent` from
`langchain` in JavaScript. These factories still run on LangGraph and add
middleware support.

Rename the prompt option while migrating:

- Python: `prompt` becomes `system_prompt`.
- JavaScript: `prompt` becomes `systemPrompt`.

```python
from langchain.agents import create_agent

agent = create_agent(model, tools, system_prompt="Be helpful.")
```

### Replace deprecated Python prebuilt APIs

- Import `AgentState` from `langchain.agents` and use it in place of the
  Pydantic and structured-response state variants.
- Replace `HumanInterruptConfig` and `ActionRequest` with `InterruptOnConfig`.
- Replace `HumanInterrupt` with `HITLRequest`.
- Let `create_agent` validate tool input instead of using `ValidationNode`.
- Replace `MessageGraph` with `StateGraph` and a `messages` channel.

### Respect runtime and package boundaries

Use Node.js 22 or newer for JavaScript packages and Python 3.10 or newer for
Python-side LangChain packages. JavaScript packages ship bundled output; remove
private imports from `dist/` and import only public modules.

## State and schema rules

### Prefer current schema APIs

In JavaScript, prefer `StateSchema` with standard field schemas and LangGraph
value types. Use `MessagesValue` for message-aware reduction and `ReducedValue`
for a schema, default, and custom reducer. Treat `Annotation.Root` and direct
Zod v3/v4 integrations as legacy alternatives.

```typescript
const State = new StateSchema({
  messages: MessagesValue,
  total: new ReducedValue(z.number().default(0), {
    reducer: (current, update) => current + update,
  }),
});
```

Python `BaseModel` state validates only the input to the first node. Later
updates and graph output are not automatically validated, and `invoke` returns
a dictionary. Use `AnyMessage` for message fields that cross the wire.

### Keep runtime context outside state

Declare Python `context_schema`, read values from `Runtime.context`, and pass
them with `context=`. In JavaScript, pass the context schema to `StateGraph`,
read `runtime.context`, and invoke with `{ context: ... }`.

Use `UntrackedValue` for JavaScript objects that must exist only during one
execution and never enter a checkpoint. Its default `guard: true` rejects
multiple same-step writes; `guard: false` accepts them and keeps the last.

### Understand channel visibility and replacement

A node input schema restricts reads, not writes. Node schemas may also add
private channels to the graph-state union. `values` streams do not redact
private channels; apply v3 `output_keys` or `outputKeys` filtering when emitted
snapshots must exclude them.

In Python, wrap a value in `Overwrite` to replace a channel for one update
without invoking its reducer.

## Execution and routing rules

### Choose one routing mechanism per node

`Command(goto=...)` adds a dynamic destination; it does not suppress static
outgoing edges. If both exist, both routes run. Use either commands or static
edges for the node, including nodes that return commands from tools.

To begin a new turn on an existing thread, invoke with a plain state mapping.
Passing any `Command` resumes the latest checkpoint; use
`Command(resume=..., update=...)` only for a resume.

### Design for replay

An interrupted or retried node starts again from its beginning. Make earlier
side effects idempotent. Completed task results inside a node can be reused,
but do not reorder tasks or interrupts before a stored resume point.

### Configure recursion at invocation scope

Set Python `recursion_limit` or JavaScript `recursionLimit` at the top level of
invocation config, never inside `configurable`. Python defaults to 1000
super-steps and JavaScript to 25. Inspect `metadata.langgraph_step`; Python can
also expose `RemainingSteps` in managed state for proactive routing.

### Configure resilience deliberately

Default retry filters exclude several programming and runtime errors. Supply
`retry_on` or `retryOn` when a particular exception is intentionally retryable.

Python async nodes can use `timeout=`. A timeout raises `NodeTimeoutError`,
discards buffered writes and child-task scheduling, and starts a fresh timer on
retry. A timeout on a synchronous node is a compile error.

Use `error_handler=` for recovery only after retries are exhausted. The handler
receives state and `NodeError` and may return a routing `Command`.

Use `set_node_defaults()` for graph-wide Python retry, timeout, cache, and
error-handler defaults. Per-node settings win; defaults do not enter subgraphs,
and cache or error-handler defaults apply only to regular nodes.

## Persistence rules

### Select durability by loss and latency tolerance

- `exit` writes when execution completes, errors, or interrupts.
- `async` writes while the next step runs and can lose the newest checkpoint
  on a crash.
- `sync` persists before execution advances.

Custom savers must support exact-ID and latest reads, newest-first history,
bounded history with `before` and `limit`, complete deletion, and serialization
of checkpoints, writes, and metadata through `self.serde`. Run the checkpointer
conformance package in CI.

Use `pickle_fallback=True` only for values unsupported by msgpack and JSON.
Encrypt saver data with `EncryptedSerializer` when stored state needs
encryption. PostgreSQL saver thread IDs must remain under 255 characters.

### Treat delta channels as chains

`DeltaChannel` stores incremental writes and reconstructs from a prior
`_DeltaSnapshot`. Exact checkpoint lookup is mandatory. Pruning or thread-copy
logic must retain every required ancestor or first materialize a snapshot.

## Interrupt and streaming rules

Use one `interrupt()` call per node invocation. A resume replays the node, so a
loop around `interrupt()` replays prior iterations and grows work rapidly.
Persist the next prompt in state and route back through a conditional edge.

When parallel branches interrupt, map every interrupt ID to its answer and pass
the complete mapping as the resume value.

For Python typed v3 event streams, inspect `stream.interrupted` and
`stream.interrupts`, then create another stream with `Command(resume=...)` until
execution completes. Use `messages`, `values`, and nested subgraph projections
for the corresponding stream data.

For low-level JavaScript SSE, request `encoding: "text/event-stream"` from
`graph.stream` and return the stream directly. Use a custom `transport` with
React `useStream` when the network layer differs from the default.

## Subgraph rules

Choose subgraph checkpoint mode from the required lifetime:

- Default `None`: new state per call, while inheriting the parent saver for
  interrupts and durability during that call.
- `True`: persistent state across calls on one thread.
- `False`: no checkpointing, interrupts, durable execution, or inspection.

The parent needs a checkpointer for either stateful mode. Serialize concurrent
calls to the same `checkpointer=True` child because they share a namespace.
Give persistent children stable, name-based namespaces so call reordering does
not load another child's state.

State inspection discovers only statically visible children. A subgraph hidden
behind a tool or other indirection has no discoverable child snapshot.

## Deployment rules

Export a compiled graph when Agent Server can load and reuse it at startup. Use
a factory only for per-run customization. Do not configure a checkpointer or
Store in graph code when the server owns and injects them.

PostgreSQL persists assistants, threads, runs, and cron jobs. Redis is only for
ephemeral signaling, cancellation, and stream pub/sub. Keep those roles distinct
when designing backups or recovery.

Single-host mode runs the task queue in the API server. Split mode uses
`queue.enabled: true` and separately scaled API and worker pools; keep at least
one worker listening. The queue allows one executing run per thread, while
`N_JOBS_PER_WORKER` controls worker job concurrency rather than API concurrency.

For a deployed threadless stream, pass `None` as the thread identifier and the
deployed graph name as the next argument. JavaScript agents may also implement
the Agent Streaming Protocol on supported web and edge runtimes.

## Implementation workflow

1. Inspect the project's Python and JavaScript package versions and runtime
   versions before choosing APIs.
2. Read the reference that matches the requested change.
3. Separate graph state, runtime context, and untracked execution objects.
4. Decide whether routing is static or command-driven for each node.
5. Make side effects safe under retry and interrupt replay.
6. Choose checkpoint mode, durability, and subgraph lifetime explicitly.
7. Filter stream outputs when graph state contains private channels.
8. Test normal completion, retry exhaustion, interrupt/resume, and checkpoint
   recovery paths that the graph actually uses.
