---
name: langchain-knowledge-patch
description: LangChain 1.1.0 compatibility. Use for LangChain work.
license: MIT
version: "1.1.0"
metadata:
  author: Nevaberry
---

# LangChain Knowledge Patch

Use this guide when choosing current LangChain, LangGraph, provider-integration,
MCP-adapter, or Deep Agents APIs. Read the topic reference before changing an
agent loop, middleware policy, graph state, streaming contract, or provider tool.

## Reference index

| Reference | Topics |
| --- | --- |
| [Agents and tools](references/agents-and-tools.md) | `create_agent`, middleware hooks and policies, structured output, model profiles, tool runtime injection, dynamic tools, custom state, and `ToolNode` errors |
| [Anthropic integration](references/anthropic.md) | Native schemas, tool metadata and streaming, effort, citations, caching, context management, provider tools, code execution, remote MCP, and tool search |
| [Deep Agents](references/deep-agents.md) | Harness tools, filesystem and binary backends, protocol v2, background subagents, sandboxes, profiles, context storage, summarization, memory, and CLI use |
| [LangGraph workflows](references/langgraph-workflows.md) | Typed stream and invoke results, event projections, delta checkpoints, timeouts and recovery, draining, JavaScript state schemas, node caching, fan-in, and reconnectable streams |
| [MCP adapters](references/mcp.md) | Session lifetime, structured and multimodal results, resources, prompts, runtime-aware interceptors, callbacks, progress, logging, and elicitation |
| [OpenAI integration](references/openai.md) | Official and Azure endpoints, custom and built-in tools, Responses routing and continuation, approvals, compaction, reasoning, PDF input, and prompt caching |
| [v1 migration](references/v1-migration.md) | Package split, runtime floor, classic imports, agent migration, provider-neutral content blocks, rollout limits, and Google GenAI v4 |

## Start with breaking changes

### Replace legacy package imports

The main Python and JavaScript packages now focus on core agent abstractions.
Install the classic package only where migration cannot happen immediately:

```sh
uv pip install --upgrade langchain langgraph
uv pip install langchain-classic

npm install langchain @langchain/core @langchain/langgraph
npm install @langchain/classic
```

- Python requires 3.10 or newer.
- Move legacy Python APIs to `langchain-classic`.
- Move JavaScript chains, retrievers, indexing APIs, and community exports to
  `@langchain/classic`; for example, replace `langchain/chains` with
  `@langchain/classic/chains`.
- Replace `langgraph.prebuilt.create_react_agent` with
  `langchain.agents.create_agent`.

### Use TypedDict agent state

Custom agent state must extend `AgentState` as a `TypedDict`. Pydantic models and
dataclasses are not accepted for this purpose. Put a schema on the middleware
that owns the fields; reserve `create_agent(state_schema=...)` for compatibility
with tool-only state.

```python
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware

class PreferencesState(AgentState):
    user_preferences: dict

class PreferencesMiddleware(AgentMiddleware):
    state_schema = PreferencesState
```

### Update Deep Agents backends

- Construct `StateBackend()` and `StoreBackend()` directly; runtime factories
  such as `lambda rt: StateBackend(rt)` are deprecated.
- In JavaScript, implement `BackendProtocolV2` structured results and report
  failures in `error`. Use `readRaw()` for binary bytes and rename
  `lsInfo`/`grepRaw`/`globInfo` to `ls`/`grep`/`glob`.
- Use `adaptBackendProtocol` while migrating a v1 backend.

### Migrate Google GenAI packages

`langchain-google-genai` v4 uses Google's consolidated SDK for both Gemini API
and Vertex AI. Expect small upgrade changes and migrate away from the
corresponding deprecated `langchain-google-vertexai` packages.

## Build agents with `create_agent`

`create_agent` builds a LangGraph-backed model/tool loop. It accepts provider
model strings, tools, a system prompt, middleware, state, and structured output.

```python
from langchain.agents import create_agent

agent = create_agent(
    model="openai:gpt-5",
    tools=[get_weather],
    system_prompt="Fetch weather when needed and answer concisely.",
    name="weather_assistant",
)
```

Names become node identifiers when agents are embedded as subgraphs. Restrict
them to letters, digits, underscores, and hyphens.

## Compose middleware deliberately

Python middleware subclasses `AgentMiddleware`; JavaScript uses
`createMiddleware`. The lifecycle consists of these hook pairs:

| Python | JavaScript |
| --- | --- |
| `before_agent` | `beforeAgent` |
| `before_model` | `beforeModel` |
| `wrap_model_call` | `wrapModelCall` |
| `wrap_tool_call` | `wrapToolCall` |
| `after_model` | `afterModel` |
| `after_agent` | `afterAgent` |

Use bundled middleware for common policies:

- `PIIMiddleware` supports named or regex detectors and `redact` or `block`.
- `SummarizationMiddleware` supports token triggers and profile-aware behavior.
- `HumanInTheLoopMiddleware` configures per-tool `approve`, `edit`, and `reject`.
- Model-retry middleware provides configurable exponential backoff.
- Content-moderation middleware can check user input, model output, and tool
  results at one policy boundary.

JavaScript `dynamicSystemPromptMiddleware` results are additive: returned strings
and `SystemMessage` objects extend existing system messages rather than replacing
them.

## Choose structured output strategy

Structured output runs inside the agent loop. Use `ToolStrategy` when the model
should emit a schema through tool calling; use `ProviderStrategy` for native
schema generation. A model profile can infer native support.

```python
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from pydantic import BaseModel

class WeatherReport(BaseModel):
    temperature: float
    condition: str

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[weather_tool],
    response_format=ToolStrategy(WeatherReport, handle_errors=True),
)
```

Python `handle_errors` and JavaScript `handleErrors` control schema-parse and
multiple-output failures. Provider strategies can request strict schema
adherence explicitly. If middleware switches models, replacement models must not
already be bound with `bind_tools` when structured output is enabled.

## Use the unified tool runtime

Declare `runtime: ToolRuntime` on a tool to receive model-hidden state, immutable
typed context, store, stream writer, config, and tool-call ID. The argument names
`runtime` and `config` are reserved. Return `Command` to update state, and include
a correlated `ToolMessage` when the model needs the result.

```python
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command

@tool
def set_language(language: str, runtime: ToolRuntime) -> Command:
    return Command(update={
        "preferred_language": language,
        "messages": [ToolMessage(
            content=f"Language set to {language}.",
            tool_call_id=runtime.tool_call_id,
        )],
    })
```

Fields written by parallel tools need reducers. A tool discovered at runtime
must be added in both `wrap_model_call` and `wrap_tool_call`; advertising it to
the model does not install an executable implementation.

## Consume messages and streams through typed surfaces

- Use `message.content_blocks` to normalize text, reasoning, citations, tool
  calls, server-side tool calls, and multimodal content across integrations.
- Use `stream_mode="messages"` to receive token chunks from ordinary
  `model.invoke()` calls inside graph nodes; select calls with metadata such as
  `langgraph_node` or model tags.
- With LangGraph `version="v2"`, stream methods emit `StreamPart`, while invoke
  methods return `GraphOutput.value` and `GraphOutput.interrupts`.
- With event streaming `version="v3"`, consume typed run and model-call
  projections instead of reconstructing events from provider-specific payloads.

## Respect tool error boundaries

`ToolNode` catches invocation errors by default but re-raises failures raised by
tool execution. Set `handle_tool_errors` to `True`, a model-visible string, an
exception handler, or a tuple of exception types when execution failures should
return to the model.

```python
from langgraph.prebuilt import ToolNode

node = ToolNode(tools, handle_tool_errors=(ValueError, TypeError))
```

## Keep provider behavior explicit

Provider-native tools, response continuation, caching, context compaction, and
approval loops have integration-specific contracts. Do not infer one provider's
wire shape from another. Read the provider reference before binding server-side
tools or retaining provider content blocks in message history.

For MCP tools, decide whether each invocation may use a fresh session. Open an
explicit session for server-side state, and use runtime-aware interceptors for
tenant headers, policy checks, state updates, or rerouting.

For Deep Agents, choose filesystem mutation policy, backend protocol, sandbox,
subagent behavior, and persistence explicitly. Background subagents require a
LangSmith Deployment.
