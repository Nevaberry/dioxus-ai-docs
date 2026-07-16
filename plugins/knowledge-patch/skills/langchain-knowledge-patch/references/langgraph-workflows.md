# LangGraph State, Execution, and Streaming

## Typed v2 stream and invoke results

Python LangGraph accepts opt-in `version="v2"` execution results.

- `stream()` and `astream()` yield `StreamPart` records with `type`, `ns`, and
  `data`.
- `invoke()` and `ainvoke()` return `GraphOutput` with `.value` and
  `.interrupts`.
- Output values are coerced to the graph's declared Pydantic model or dataclass.
- Dict-style access on `GraphOutput` remains only as a deprecated migration
  surface.

```python
result = graph.invoke(inputs, version="v2")
value = result.value
interrupts = result.interrupts
```

Update consumers together with the call site. Code that adds `version="v2"` but
still indexes the result as a dict is intentionally relying on deprecated
behavior.

## Content-block event streaming v3

Python LangChain agents, Deep Agents, and LangGraph accept `version="v3"` in
`stream_events()` and `astream_events()`.

LangGraph v3 provides typed projections:

- `run.values`
- `run.messages`
- `run.lifecycle`
- `run.subgraphs`

Each LLM call produces a `ChatModelStream` divided into text, reasoning,
tool-call, and usage projections.

```python
async for event in graph.astream_events(inputs, version="v3"):
    handle(event)
```

The v1 and v2 event contracts remain unchanged. Select a version explicitly at
an API boundary rather than writing one consumer that guesses several shapes.

## Token streaming from ordinary invocation

`stream_mode="messages"` emits `(message_chunk, metadata)` tokens for LangChain
model calls anywhere in a graph, even when node code calls `model.invoke()`
rather than `model.stream()`.

```python
for message, metadata in graph.stream(
    inputs,
    stream_mode="messages",
):
    if metadata["langgraph_node"] == "writer":
        print(message.content, end="")
```

Use metadata such as `langgraph_node` or model `tags` to select tokens from one
invocation when several nodes or models run in the same graph.

## Delta-only checkpoint channels

The beta `DeltaChannel` stores each step's incremental change instead of
serializing the complete accumulated channel value. It fits append-heavy state
such as message histories and agent files.

Set `snapshot_frequency=K` to store a full snapshot periodically. Lower values
use more checkpoint storage; higher values increase worst-case reconstruction
work. Ensure each delta can be applied deterministically in order.

## Node timeouts and recovery

Python `add_node` accepts `timeout=` for asynchronous node limits and
`error_handler=` for recovery after retries are exhausted.

`TimeoutPolicy` provides:

- `run_timeout`, a hard total limit;
- `idle_timeout`, which resets when the node makes progress.

```python
graph.add_node(
    "work",
    work,
    timeout=TimeoutPolicy(
        run_timeout=30,
        idle_timeout=10,
    ),
    error_handler=recover,
)
```

A timeout raises `NodeTimeoutError`, discards writes from that attempt, and then
enters the retry policy. Do not expect partial state updates from a timed-out
attempt to survive.

After retries are exhausted, the error handler receives `NodeError`. It may
return a `Command` that updates state and redirects execution. Keep recovery
idempotent because the failed node may already have produced external side
effects even though its graph writes were discarded.

## Graceful draining

`RunControl.request_drain()` asks an in-flight run to stop cooperatively after
its current superstep. LangGraph saves a resumable checkpoint and the run raises
`GraphDrained`.

Resume later with the same configuration. Draining is not immediate cancellation:
work in the active superstep is allowed to finish, so external operations in that
step still require their normal idempotency and timeout controls.

## JavaScript `StateSchema`

`StateSchema` defines graph state with any Standard Schema-compatible validator,
including Zod 4, Valibot, and ArkType.

```typescript
import {
  StateGraph,
  StateSchema,
  ReducedValue,
  MessagesValue,
} from "@langchain/langgraph";
import { z } from "zod";

const AgentState = new StateSchema({
  messages: MessagesValue,
  count: z.number().default(0),
  history: new ReducedValue(
    z.array(z.string()).default(() => []),
    {
      inputSchema: z.string(),
      reducer: (current, next) => [...current, next],
    },
  ),
});

const graph = new StateGraph(AgentState);
```

Related state helpers have distinct persistence and reduction behavior:

- `ReducedValue` gives reducer inputs their own type.
- `UntrackedValue` stores runtime-only state that is never checkpointed.
- `MessagesValue` supplies the standard message reducer.
- `GraphNode` and `ConditionalEdgeRouter` type standalone nodes and conditional
  routers.

Do not place values needed for resume or replay in `UntrackedValue`.

## Node result caching

Python and JavaScript workflows can cache individual node results so later runs
skip redundant node execution. Cache only nodes whose result is valid for the
configured key and policy; model calls, time-sensitive queries, and tools with
external side effects need deliberate invalidation or should remain uncached.

## Deferred nodes as fan-in points

A deferred node waits until every upstream path completes before running. Use it
as a built-in fan-in point for map-reduce, consensus, aggregation, and other
multi-branch workflows.

Account for interrupted or failed upstream branches. Deferral defines scheduling
after upstream completion; it does not by itself define how missing or failed
branch results should be represented.

## Resumable LangGraph.js streams

LangGraph.js streams can set `reconnectOnMount` to resume after a page reload or
connection drop. Use a durable run/thread identity and ensure the frontend can
deduplicate content already rendered before disconnection.

## LangGraph.js builder and result changes

JavaScript adds object forms for `.addNode({ ... })` and `.addSequence({ ... })`.
`.stream()` is fully type-safe, and interrupts are returned directly from
`.invoke()` and from `"values"` stream mode.

Prefer the typed object forms in reusable builders, and update result consumers
to inspect direct interrupts instead of relying on older nested or side-channel
shapes.
