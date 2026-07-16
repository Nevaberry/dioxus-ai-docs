# Agents, Middleware, Tools, State, and Runtime

## `create_agent` loop

`langchain.agents.create_agent` constructs a LangGraph-backed model/tool loop.
It is the current replacement for `langgraph.prebuilt.create_react_agent` and is
the integration point for middleware, state, structured output, and model
profiles.

```python
from langchain.agents import create_agent

agent = create_agent(
    model="openai:gpt-5",
    tools=[get_weather],
    system_prompt="Use tools when they improve the answer.",
)
```

An optional `name` becomes the node identifier when the agent is embedded as a
subgraph. Use only alphanumerics, underscores, and hyphens because some providers
reject spaces or other special characters.

## Middleware lifecycle

Python custom middleware subclasses `AgentMiddleware`; JavaScript custom
middleware is created with `createMiddleware`. The six hook pairs are:

| Phase | Python | JavaScript |
| --- | --- | --- |
| Before the loop | `before_agent` | `beforeAgent` |
| Before a model call | `before_model` | `beforeModel` |
| Around a model call | `wrap_model_call` | `wrapModelCall` |
| Around a tool call | `wrap_tool_call` | `wrapToolCall` |
| After a model call | `after_model` | `afterModel` |
| After the loop | `after_agent` | `afterAgent` |

Wrapper hooks receive a request and handler, making them suitable for routing,
retries, policy checks, request overrides, and short-circuit results.

```python
from langchain.agents.middleware import AgentMiddleware
from langchain_openai import ChatOpenAI

fast_model = ChatOpenAI(model="gpt-5-nano")

class RouteModel(AgentMiddleware):
    def wrap_model_call(self, request, handler):
        return handler(request.override(model=fast_model, tools=[read_email]))
```

### Bundled policy middleware

- `PIIMiddleware` accepts named or regex detectors and a `redact` or `block`
  strategy. It can apply policy to input and other configured boundaries.
- `SummarizationMiddleware` supports token-count triggers and can summarize near
  a context limit.
- `HumanInTheLoopMiddleware` maps tool names to allowed `approve`, `edit`, and
  `reject` decisions.
- Model-retry middleware supplies configurable exponential backoff for transient
  provider endpoint errors.
- Content-moderation middleware can apply one safety policy to user input, model
  responses, and values returned by tools.

```python
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    PIIMiddleware,
    SummarizationMiddleware,
)

middleware = [
    PIIMiddleware("email", strategy="redact", apply_to_input=True),
    SummarizationMiddleware(
        model="claude-sonnet-4-6",
        trigger={"tokens": 500},
    ),
    HumanInTheLoopMiddleware(interrupt_on={
        "send_email": {
            "allowed_decisions": ["approve", "edit", "reject"],
        }
    }),
]
```

JavaScript `dynamicSystemPromptMiddleware` now composes prompts additively.
Returned strings and `SystemMessage` objects extend existing system messages
instead of replacing them.

## Capability profiles

Since `1.1.0`, chat models expose `.profile`, declarative capability data sourced
from the cross-provider models.dev index. Profiles can report structured-output,
function-calling, and JSON-mode support without application-maintained provider
tables.

```python
capabilities = chat_model.profile
```

Summarization middleware consults profiles when choosing when and how to
summarize, allowing provider-sensitive behavior in long sessions.
`ProviderStrategy` can also be inferred from a profile, so an agent can select
native structured output without hard-coded model-name tests.

Profiles are capability hints, not a substitute for handling endpoint errors,
deployment restrictions, or an integration's unsupported options.

## Structured output inside the loop

Structured output participates in the main model/tool loop rather than requiring
an extra model call. Set `response_format` to a schema strategy:

- `ToolStrategy` requests schema output through tool calling.
- `ProviderStrategy` requests provider-native generation and can be inferred
  from a model profile.
- Native strategies can explicitly request strict schema adherence. Python sets
  strict behavior through `response_format` with `ProviderStrategy`; JavaScript
  `providerStrategy` exposes `strict`.

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

`ToolStrategy.handle_errors` in Python and `handleErrors` in JavaScript control
what happens when generated data fails schema parsing or the model emits several
structured-output tool calls.

When middleware dynamically switches models for an agent with structured output,
the replacement models must not be pre-bound with `bind_tools`; that combination
is unsupported.

## Unified `ToolRuntime` injection

A tool can declare a model-hidden `runtime: ToolRuntime` parameter. It exposes:

- short-term `state`;
- immutable typed `context`;
- the long-term `store`;
- `stream_writer`;
- invocation `config`;
- `tool_call_id`.

The names `runtime` and `config` are reserved tool arguments. Declare
`context_schema=Context` on the agent and use `ToolRuntime[Context]` for typed
context.

Return a LangGraph `Command` to mutate state. If the model needs a visible tool
result, include a `ToolMessage` correlated with `runtime.tool_call_id`.

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

State fields written by parallel tools require reducers so concurrent updates
can be combined deterministically.

## Runtime-discovered tools

Filtering the tools already registered with `create_agent` only requires
`wrap_model_call`. A genuinely new runtime tool must also be installed on its
`ToolCallRequest` in `wrap_tool_call`. Showing a definition to the model does not
make that tool executable.

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

Apply authorization and tenancy checks in both hooks when discovery itself may
reveal sensitive tool names.

## Custom agent state

Custom state schemas must extend `AgentState` as a `TypedDict`. Pydantic models
and dataclasses are no longer accepted.

```python
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware

class PreferencesState(AgentState):
    user_preferences: dict

class PreferencesMiddleware(AgentMiddleware):
    state_schema = PreferencesState
```

Prefer middleware-owned `state_schema` when that middleware's hooks or tools use
the fields. `create_agent(state_schema=...)` remains a compatibility shortcut
for state used only by tools.

## Provider-specific tool metadata

Python `BaseTool.extras` carries provider-only definitions and parameters through
the common tool abstraction. It supports cases such as programmatic tool calls,
tool search, provider input examples, and provider built-ins executed by the
client. The metadata stays outside the model-visible input schema.

```python
from langchain.tools import tool

@tool(extras={"defer_loading": True})
def search_catalog(query: str) -> str:
    """Search the catalog."""
    return lookup(query)
```

Use this field instead of discarding provider-only configuration or replacing a
portable tool with an unrelated provider dictionary when the integration knows
how to translate the extras.

## `ToolNode` execution errors

`ToolNode` distinguishes invocation errors from errors raised by the tool body.
It catches invocation errors by default and re-raises execution errors. Set
`handle_tool_errors` to one of the following to expose selected execution
failures to the model:

- `True`;
- a fixed model-visible error string;
- an exception-handling callable;
- a tuple of exception classes.

```python
from langgraph.prebuilt import ToolNode

all_errors = ToolNode(tools, handle_tool_errors=True)
selected = ToolNode(tools, handle_tool_errors=(ValueError, TypeError))
```

Do not convert authorization, process-corruption, cancellation, or other
non-recoverable failures into ordinary model-visible tool results without an
explicit policy.
