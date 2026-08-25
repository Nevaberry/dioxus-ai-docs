# Migration and state

## Agent construction and prebuilt replacements

The `langgraph-v1` migration moves React-agent construction to LangChain while
retaining LangGraph as the execution layer and adding middleware support.

Python:

```python
from langchain.agents import create_agent

agent = create_agent(
    model,
    tools,
    system_prompt="You are a helpful assistant.",
)
```

JavaScript:

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model,
  tools,
  systemPrompt: "You are a helpful assistant.",
});
```

The import moves to `langchain`; rename Python `prompt` to `system_prompt` and
JavaScript `prompt` to `systemPrompt`.

Replace these Python prebuilt surfaces:

| Previous API | Replacement |
| --- | --- |
| LangGraph `AgentState` and its Pydantic or structured-response variants | `AgentState` from `langchain.agents` |
| `HumanInterruptConfig` or `ActionRequest` | `InterruptOnConfig` |
| `HumanInterrupt` | `HITLRequest` |
| `ValidationNode` | Automatic tool-input validation in `create_agent` |
| `MessageGraph` | `StateGraph` with a `messages` key |

## Runtime and package output

JavaScript LangGraph packages require Node.js 22 or newer. Python-side
LangChain packages require Python 3.10 or newer. JavaScript packages now ship
bundled builds rather than raw TypeScript output, so replace private `dist/`
imports with public package modules.

## Modern JavaScript state schemas

Use `StateSchema` with standard field schemas and LangGraph value types.
`MessagesValue` supplies message-aware reduction. `ReducedValue` combines a
field schema and default with a reducer. `Annotation.Root` and direct Zod v3/v4
integrations remain legacy alternatives.

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

A `BaseModel` may define graph state, but validation occurs only on input to the
first node. That node receives the validated model; later updates and graph
output are not automatically validated, and `invoke` returns a dictionary.
Use `AnyMessage`, not `BaseMessage`, for message fields that must serialize over
the wire.

## Runtime context outside graph state

Python graphs declare `context_schema`, nodes read `Runtime.context`, and
callers pass `context=`:

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

JavaScript passes a context schema as the second `StateGraph` constructor
argument, reads `runtime.context`, and supplies `{ context: ... }` in invocation
options.

## Uncheckpointed JavaScript values

`UntrackedValue` holds connections, temporary caches, or other execution-only
objects. It is excluded from checkpoints and starts fresh after resume. Its
default `guard: true` rejects multiple writes in one step; `guard: false`
permits them and retains the last value.

```typescript
const State = new StateSchema({
  dbConnection: new UntrackedValue<DatabaseConnection>(),
  tempCache: new UntrackedValue(z.record(z.string(), z.unknown()), {
    guard: false,
  }),
});
```

## Reducer bypass with `Overwrite`

A Python node can bypass a channel's reducer for one update by wrapping the
replacement value:

```python
from langgraph.types import Overwrite

return {"items": Overwrite(["replacement"])}
```

## Checkpoint-compatible graph changes

Completed threads tolerate arbitrary topology changes. Interrupted threads
cannot safely rename or remove nodes. Adding or removing state keys is
compatible, but renaming a key loses its saved value, and incompatible type
changes may break state stored by older threads.
