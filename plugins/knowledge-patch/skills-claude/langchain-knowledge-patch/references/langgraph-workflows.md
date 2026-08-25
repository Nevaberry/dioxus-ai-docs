# LangGraph State, Execution, and Streaming

## Typed Python results

Python LangGraph has an opt-in `version="v2"` mode. `stream()` and `astream()`
yield typed `StreamPart` records with `type`, `ns`, and `data`. `invoke()` and
`ainvoke()` return `GraphOutput` with `.value` and `.interrupts`.

Values are coerced to a declared Pydantic model or dataclass. Deprecated
dict-style `GraphOutput` access remains available for migration.

```python
result = graph.invoke(inputs, version="v2")
value = result.value
interrupts = result.interrupts
```

## Content-block event streaming

Python LangChain agents, Deep Agents, and LangGraph accept `version="v3"` in
`stream_events()` and `astream_events()`. LangGraph v3 exposes typed
`run.values`, `run.messages`, `run.lifecycle`, and `run.subgraphs`
projections. Each LLM call produces a `ChatModelStream` split into text,
reasoning, tool-call, and usage projections. Event-stream versions v1 and v2
remain unchanged.

```python
async for event in graph.astream_events(inputs, version="v3"):
    handle(event)
```

## Checkpoint storage

The beta `DeltaChannel` stores each step's incremental change rather than the
full accumulated channel value. It is suitable for growing message histories
and agent files. Set `snapshot_frequency=K` to store periodic full snapshots
and bound reconstruction latency.

## Fault tolerance and draining

### Configure node timeouts and exhausted-retry recovery

Python `add_node` accepts `timeout=` for async-node limits and
`error_handler=` for recovery after retries are exhausted. `TimeoutPolicy`
supports hard `run_timeout` and progress-resetting `idle_timeout`.

A timeout raises `NodeTimeoutError`, discards that attempt's writes, and
enters the retry policy. An error handler receives `NodeError` and may return
a `Command` that updates state and reroutes execution.

```python
graph.add_node(
    "work",
    work,
    timeout=TimeoutPolicy(run_timeout=30, idle_timeout=10),
    error_handler=recover,
)
```

### Drain cooperatively

`RunControl.request_drain()` stops an in-flight run after its current
superstep and saves a resumable checkpoint. The run raises `GraphDrained` and
can later resume with the same configuration.

## JavaScript state schemas

`StateSchema` defines graph state with any Standard Schema-compatible
validator, including Zod 4, Valibot, and ArkType. `ReducedValue` supplies typed
reducer inputs, `UntrackedValue` holds runtime-only state that is never
checkpointed, and `MessagesValue` supplies the standard message reducer.
`GraphNode` and `ConditionalEdgeRouter` type standalone nodes and routers.

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
  history: new ReducedValue(z.array(z.string()).default(() => []), {
    inputSchema: z.string(),
    reducer: (current, next) => [...current, next],
  }),
});

const graph = new StateGraph(AgentState);
```

## Workflow construction and delivery

LangGraph Python and JavaScript workflows can cache individual node results,
allowing later runs to skip redundant node execution.

A deferred node waits until every upstream path has completed before it runs.
It provides a built-in fan-in point for map-reduce, consensus, and other
multi-branch workflows.

LangGraph.js streams can set `reconnectOnMount` to resume automatically after
a page reload or connection drop.

LangGraph.js also adds object-form `.addNode({ ... })` and
`.addSequence({ ... })`, makes `.stream()` fully type-safe, and returns
interrupts directly from `.invoke()` and from `"values"` stream mode.
