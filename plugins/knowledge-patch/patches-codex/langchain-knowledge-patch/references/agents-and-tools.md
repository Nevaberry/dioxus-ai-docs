# Agents, Middleware, Tools, State, and Runtime

## Agent construction and structured output

### Structured output in the loop

Structured output participates in the main model/tool loop instead of needing
an extra model call. `response_format` chooses tool-based or provider-native
generation. Wrap a Pydantic schema in `ToolStrategy` to request tool calling.

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
    response_format=ToolStrategy(WeatherReport),
    system_prompt="Fetch the weather and return a report.",
)
```

`ToolStrategy` exposes `handle_errors` in Python and `handleErrors` in
JavaScript. These control handling when generated data fails schema parsing or
the model emits multiple structured-output tool calls.

Provider-native output can explicitly request strict schema adherence. Python
uses `response_format` with `ProviderStrategy`; JavaScript `providerStrategy`
can set `strict` manually.

When middleware dynamically switches models for an agent using structured
output, replacement models must not be pre-bound with `bind_tools`; pre-bound
models are unsupported in this combination.

### Agent names as subgraph identifiers

The optional `create_agent(..., name="research_assistant")` name becomes the
node identifier when the agent is embedded as a subgraph. Keep names to
alphanumerics, underscores, and hyphens because some providers reject spaces
or special characters.

## Middleware policy and lifecycle

Prebuilt policies support named or regex PII detectors with `redact` or
`block`, token-count summarization triggers, and tool-keyed human decisions of
`approve`, `edit`, or `reject`. Python custom middleware subclasses
`AgentMiddleware`; JavaScript uses `createMiddleware`.

The six hook pairs are `before_agent`/`beforeAgent`,
`before_model`/`beforeModel`, `wrap_model_call`/`wrapModelCall`,
`wrap_tool_call`/`wrapToolCall`, `after_model`/`afterModel`, and
`after_agent`/`afterAgent`.

```python
from langchain.agents.middleware import (
    AgentMiddleware,
    HumanInTheLoopMiddleware,
    PIIMiddleware,
    SummarizationMiddleware,
)
from langchain_openai import ChatOpenAI

fast_model = ChatOpenAI(model="gpt-5-nano")

class RouteModel(AgentMiddleware):
    def wrap_model_call(self, request, handler):
        return handler(request.override(model=fast_model, tools=[read_email]))

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[read_email, send_email],
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        SummarizationMiddleware(
            model="claude-sonnet-4-6", trigger={"tokens": 500}
        ),
        HumanInTheLoopMiddleware(interrupt_on={
            "send_email": {
                "allowed_decisions": ["approve", "edit", "reject"]
            }
        }),
        RouteModel(),
    ],
)
```

Values returned by JavaScript `dynamicSystemPromptMiddleware` extend rather
than replace existing system messages. Strings and `SystemMessage` objects can
therefore compose across multiple prompt-modifying middleware.

## Runtime injection and state

### Unified `ToolRuntime`

A tool can declare a model-hidden `runtime: ToolRuntime` parameter. It exposes
short-term `state`, immutable typed `context`, long-term `store`,
`stream_writer`, `config`, and `tool_call_id`. `config` and `runtime` are
reserved argument names. Typed context uses `context_schema=Context` and
`ToolRuntime[Context]`.

Return `Command` to mutate state. Include a `ToolMessage` correlated with
`runtime.tool_call_id` when the model needs a result. State fields written by
parallel tools need reducers.

```python
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command

@tool
def set_language(language: str, runtime: ToolRuntime) -> Command:
    """Set the preferred response language."""
    return Command(update={
        "preferred_language": language,
        "messages": [ToolMessage(
            content=f"Language set to {language}.",
            tool_call_id=runtime.tool_call_id,
        )],
    })
```

### Custom agent state

Custom schemas must extend `AgentState` as `TypedDict`; Pydantic models and
dataclasses are not accepted. Prefer middleware-owned `state_schema` when its
hooks or tools use the fields. `create_agent(state_schema=...)` remains a
backward-compatible shortcut for tool-only state.

```python
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware

class PreferencesState(AgentState):
    user_preferences: dict

class PreferencesMiddleware(AgentMiddleware):
    state_schema = PreferencesState
```

## Runtime-discovered tools

Filtering tools already registered with `create_agent` requires only
`wrap_model_call`. A runtime-discovered tool must additionally be installed on
its `ToolCallRequest` in `wrap_tool_call`; exposing it to the model does not
make it executable.

```python
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ToolCallRequest
from langchain.tools import tool

@tool
def runtime_tool(text: str) -> str:
    """Echo text through a dynamically registered tool."""
    return text

class DynamicTools(AgentMiddleware):
    def wrap_model_call(self, request: ModelRequest, handler):
        return handler(request.override(tools=[*request.tools, runtime_tool]))

    def wrap_tool_call(self, request: ToolCallRequest, handler):
        if request.tool_call["name"] == runtime_tool.name:
            request = request.override(tool=runtime_tool)
        return handler(request)
```

## Tool execution and metadata

### `ToolNode` error boundary

By default, `ToolNode` catches invocation errors and re-raises errors from tool
execution. Set `handle_tool_errors` to `True`, a model-visible error string, an
exception-handling callable, or a tuple of exception types to catch execution
failures.

```python
from langgraph.prebuilt import ToolNode

ToolNode(tools, handle_tool_errors=True)
ToolNode(tools, handle_tool_errors=(ValueError, TypeError))
```

### Provider-specific metadata

Python LangChain v1.2 adds `BaseTool.extras`, which lets `create_agent` carry
provider-specific tool definitions and parameters. This includes Anthropic
programmatic tool calling and tool search, plus provider built-ins executed
client-side, without replacing the common tool abstraction.

JavaScript `@langchain/openai` supports provider-side file search, web search,
code interpreter, image generation, computer use, shell, and MCP connector
tools. `ChatOpenAI` also provides `moderateContent`, and GPT-5.2 Pro prefers the
Responses API. `@langchain/anthropic` supports provider-side text editing, web
fetch, computer use, tool search, and MCP toolsets.

## Streaming ordinary model invocations

`stream_mode="messages"` emits `(message_chunk, metadata)` tokens for
LangChain model calls anywhere in a graph, even when node code uses
`model.invoke()` instead of `model.stream()`. Select an invocation through
metadata such as `langgraph_node` or model tags.

```python
for message, metadata in graph.stream(inputs, stream_mode="messages"):
    if metadata["langgraph_node"] == "writer":
        print(message.content, end="")
```

## Middleware and agent correctness fixes (`1.3.15`)

### Public policy and state schema APIs

`AgentMiddleware.trace_policy` is public, so middleware-aware tooling can
inspect the policy directly instead of relying on an internal attribute.

The function-style `wrap_tool_call` decorator accepts `state_schema`, allowing
middleware to declare the custom agent-state fields it consumes.

```python
from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call

class TenantState(AgentState):
    tenant_id: str

@wrap_tool_call(state_schema=TenantState)
def tenant_aware_tool_call(request, handler):
    return handler(request)
```

`PIIMatch` is re-exported publicly:

```python
from langchain.agents.middleware import PIIMatch
```

### Message projections and failure behavior

Internal model calls made by middleware are filtered from the `messages`
projection. Consumers should not rely on that projection to observe
middleware-internal model work.

If `SummarizationMiddleware` fails while creating a summary, it preserves the
existing conversation history. Failures in human-in-the-loop approval gates no
longer silently allow the gated action. When `ToolCallLimitMiddleware` ends a
run, it no longer leaves orphaned `tool_calls` in message history.

The checkpointed `structured_response` value is cleared between turns, so a
turn with no new structured result does not return stale output.

### Generic model initialization

`init_chat_model` recognizes LangSmith as a model provider.

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("deployment-name", model_provider="langsmith")
```

Core chat models expose `reasoning_effort` as a standard parameter, so generic
initialization can pass it without a provider-specific keyword container.

```python
model = init_chat_model("provider:model", reasoning_effort="high")
```
