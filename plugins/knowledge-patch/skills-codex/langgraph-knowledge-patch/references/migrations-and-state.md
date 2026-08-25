# Migrations and State

Relevant source topics: `langgraph-v1`, `graph-api-overview`, and
`graph-api-usage`.

## Agent construction and Python prebuilt migration

LangGraph v1 deprecates its React-agent prebuilt in favor of the LangChain
factory. The new factory still runs on LangGraph and supports middleware.

```python
from langchain.agents import create_agent

agent = create_agent(
    model,
    tools,
    system_prompt="You are a helpful assistant.",
)
```

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model,
  tools,
  systemPrompt: "You are a helpful assistant.",
});
```

Apply these Python replacements:

| Old API | Replacement |
| --- | --- |
| LangGraph React-agent prebuilt | `langchain.agents.create_agent` |
| `prompt` | `system_prompt` |
| `AgentState` from LangGraph | `AgentState` from `langchain.agents` |
| Pydantic or structured-response state variants | `AgentState` |
| `HumanInterruptConfig`, `ActionRequest` | `InterruptOnConfig` |
| `HumanInterrupt` | `HITLRequest` |
| `ValidationNode` | Automatic tool-input validation in `create_agent` |
| `MessageGraph` | `StateGraph` with a `messages` key |

In JavaScript, rename `prompt` to `systemPrompt`.

## Runtime floors and public imports

JavaScript LangGraph packages require Node.js 22 or newer. Python-side
LangChain packages require Python 3.10 or newer. JavaScript packages switched
from raw TypeScript output to bundled builds, so private imports below `dist/`
are unsupported; import public package modules instead.

## Modern JavaScript state schemas

`StateSchema` is the recommended state API. It accepts standard field schemas
and LangGraph value types. `MessagesValue` provides the message reducer, while
`ReducedValue` combines a field schema and default with a custom reducer.
`Annotation.Root` and direct Zod v3/v4 integrations are legacy alternatives.

```typescript
import { MessagesValue, ReducedValue, StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  messages: MessagesValue,
  total: new ReducedValue(z.number().default(0), {
    reducer: (current, update) => current + update,
  }),
});
```

## Python Pydantic validation boundary

A `BaseModel` may define graph state, but LangGraph validates it only on input
to the first node. That node receives the model; later node updates and graph
output are not revalidated, and `invoke` returns a dictionary. Use `AnyMessage`
rather than `BaseMessage` when a message field must serialize over the wire.

## Runtime context outside graph state

In Python, declare `context_schema`, type nodes with `Runtime[Context]`, read
`runtime.context`, and pass context using the invocation's `context=` argument.

```python
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from typing_extensions import TypedDict

class State(TypedDict):
    tenant: str

class Context(TypedDict):
    tenant: str

def node(state: State, runtime: Runtime[Context]):
    return {"tenant": runtime.context["tenant"]}

graph = (
    StateGraph(State, context_schema=Context)
    .add_node("node", node)
    .add_edge(START, "node")
    .add_edge("node", END)
    .compile()
)
graph.invoke({}, context={"tenant": "acme"})
```

In JavaScript, supply the context schema as the second `StateGraph` constructor
argument, read `runtime.context`, and invoke with `{ context: ... }`.

## Private channels and value-stream visibility

A node's input schema restricts what the node reads, not which graph channels
it may update. A schema declared by a node can therefore add private channels
to the graph-state union. Input, output, and private schemas do not redact
`values` streams. Filter v3 event streams with `output_keys` in Python or
`outputKeys` in JavaScript whenever private channels must not be emitted.

```python
stream = graph.stream_events(
    {"user_input": "My"},
    version="v3",
    output_keys=["graph_output"],
)
```

## Bypassing reducers with `Overwrite`

A Python node can replace a channel value without invoking its configured
reducer by wrapping that update in `Overwrite`.

```python
from langgraph.types import Overwrite

return {"items": Overwrite(["replacement"])}
```

## Uncheckpointed JavaScript state

`UntrackedValue` holds execution-time values that are excluded from checkpoints
and start fresh after a resume. Use it for connections, temporary caches, and
other runtime-only objects. Its default `guard: true` rejects multiple writes in
one step. With `guard: false`, multiple writes are accepted and the last wins.

```typescript
const State = new StateSchema({
  dbConnection: new UntrackedValue<DatabaseConnection>(),
  tempCache: new UntrackedValue(z.record(z.string(), z.unknown()), {
    guard: false,
  }),
});
```

## Additive `Command` routing

`Command(goto=...)` adds a dynamic route without removing static outgoing
edges. If a node has both, both destinations run. Choose dynamic commands or
static edges for a node, including nodes that can receive tool-returned
commands.

## Resume commands versus new input

Passing any `Command` to `invoke` or `stream` resumes from the latest
checkpoint. Use `Command(resume=...)`, optionally with `update`, as resume
input. To begin a new turn from `__start__` on an existing thread, pass a plain
state mapping instead of `Command(update=...)`.

```python
graph.invoke({"messages": [follow_up]}, config)
graph.invoke(Command(resume=review_answer), config)
```

## Checkpoint-compatible graph migrations

Completed threads tolerate arbitrary topology changes. Interrupted threads do
not safely tolerate renamed or removed nodes because their resume position is
persisted. State keys may be added or removed; renaming a key discards its saved
value, and an incompatible type change can break old thread state.

## Recursion budgets

Since LangGraph Python 1.0.6, the default recursion limit is 1000 super-steps;
JavaScript defaults to 25. Set `recursion_limit` or `recursionLimit` at the top
level of invocation config, not inside `configurable`.

```python
result = graph.invoke(inputs, config={"recursion_limit": 100})
current_step = config["metadata"]["langgraph_step"]
```

Nodes can read the current count from `metadata.langgraph_step`. Python graphs
can declare a `RemainingSteps` managed state value to route before exhausting
the budget.
