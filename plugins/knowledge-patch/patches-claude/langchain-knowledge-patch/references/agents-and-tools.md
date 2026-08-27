# Agents, Middleware, Tools, State, and Runtime

## Tool runtime and state

### Inject the unified runtime

A tool can declare an automatically injected, model-hidden
`runtime: ToolRuntime` parameter. It exposes short-term `state`, immutable
typed `context`, the long-term `store`, `stream_writer`, `config`, and
`tool_call_id`. The names `config` and `runtime` are reserved. For typed
context, pass `context_schema=Context` and annotate `ToolRuntime[Context]`.

Return `Command` to mutate state. Include a `ToolMessage` correlated with
`runtime.tool_call_id` when the model needs a result. Fields written by
parallel tools need reducers.

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

### Install dynamically discovered tools

Filtering tools already registered with `create_agent` requires only
`wrap_model_call`. A tool discovered at runtime must also be installed on its
`ToolCallRequest` in `wrap_tool_call`; exposing it to the model alone does not
make it executable.

```python
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ToolCallRequest
from langchain.tools import tool

@tool
def runtime_tool(text: str) -> str:
    return text

class DynamicTools(AgentMiddleware):
    def wrap_model_call(self, request: ModelRequest, handler):
        return handler(request.override(tools=[*request.tools, runtime_tool]))

    def wrap_tool_call(self, request: ToolCallRequest, handler):
        if request.tool_call["name"] == runtime_tool.name:
            request = request.override(tool=runtime_tool)
        return handler(request)
```

### Define custom agent state

Custom state schemas must extend `AgentState` as a `TypedDict`. Pydantic models
and dataclasses are not accepted. Prefer middleware-owned `state_schema` when
the middleware's hooks or tools use the fields; `create_agent(state_schema=)`
remains a backwards-compatible shortcut for tool-only state.

```python
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware

class PreferencesState(AgentState):
    user_preferences: dict

class PreferencesMiddleware(AgentMiddleware):
    state_schema = PreferencesState
```

Function-style tool middleware can declare the state it consumes directly.
The `wrap_tool_call` decorator accepts `state_schema` in `1.3.15`.

```python
from langchain.agents.middleware import wrap_tool_call

class TenantState(AgentState):
    tenant_id: str

@wrap_tool_call(state_schema=TenantState)
def tenant_aware_tool_call(request, handler):
    return handler(request)
```

## Tool definitions and execution

### Preserve provider-specific metadata

Python LangChain v1.2 adds `BaseTool.extras` to carry provider-specific
definitions and parameters through `create_agent`. These include Anthropic
programmatic tool calling and tool search, plus provider built-ins executed
client-side. This avoids replacing the common tool abstraction solely to
preserve provider-only configuration.

### Configure `ToolNode` failures

`ToolNode` catches invocation errors by default but re-raises errors from tool
execution. Set `handle_tool_errors` to `True`, a model-visible error string, an
exception-handling callable, or a tuple of exception types to catch execution
failures.

```python
from langgraph.prebuilt import ToolNode

ToolNode(tools, handle_tool_errors=True)
ToolNode(tools, handle_tool_errors=(ValueError, TypeError))
```

### Use provider-native structured output strictly

Agent provider-native structured output can explicitly request strict schema
adherence. Python exposes it through `response_format` with
`ProviderStrategy`; JavaScript lets `providerStrategy` set `strict` manually.

When middleware dynamically switches models for an agent using structured
output, replacement models must not have been pre-bound with `bind_tools`.
Pre-bound models are unsupported in this combination.

## Streaming, prompts, and subgraphs

`stream_mode="messages"` emits `(message_chunk, metadata)` tokens for
LangChain model calls anywhere in a graph, including node code that calls
`model.invoke()` rather than `model.stream()`. Use metadata such as
`langgraph_node` or model `tags` to select one invocation's tokens.

```python
for message, metadata in graph.stream(inputs, stream_mode="messages"):
    if metadata["langgraph_node"] == "writer":
        print(message.content, end="")
```

The optional `name` in
`create_agent(..., name="research_assistant")` becomes the node identifier
when the agent is embedded as a subgraph. Use only alphanumerics, underscores,
and hyphens because some providers reject spaces or special characters.

Values returned by JavaScript `dynamicSystemPromptMiddleware` extend rather
than replace existing system messages. Returned strings and `SystemMessage`
objects therefore compose across multiple prompt-modifying middleware.

## JavaScript provider tools and package movement

`@langchain/openai` supports provider-side file search, web search, code
interpreter, image generation, computer use, shell, and MCP connector tools.
`ChatOpenAI` also has `moderateContent`, and GPT-5.2 Pro prefers the Responses
API. `@langchain/anthropic` adds provider-side text editing, web fetch,
computer use, tool search, and MCP toolsets.

`langchain-google-genai` v4 is rebuilt on Google's consolidated Generative AI
SDK, placing Gemini API and Vertex AI access behind one integration. Upgrades
may require small changes; corresponding packages in
`langchain-google-vertexai` are deprecated.

## Middleware visibility and safety fixes

The following middleware and agent behavior applies in `1.3.15`:

- `AgentMiddleware.trace_policy` is public, so middleware-aware tooling can
  inspect it without an internal attribute.
- Internal model calls made by middleware are filtered out of the `messages`
  projection. Do not rely on that projection to observe internal model work.
- `PIIMatch` is re-exported from `langchain.agents.middleware`.
- If `SummarizationMiddleware` fails while creating a summary, the existing
  conversation history is preserved.
- Failures in human-in-the-loop approval gates no longer silently allow the
  gated action to proceed.
- When `ToolCallLimitMiddleware` ends a run, it no longer leaves orphaned
  `tool_calls` in message history.
- `structured_response` is cleared between checkpointed turns, so a turn with
  no new structured result does not return stale output from an earlier turn.

```python
from langchain.agents.middleware import PIIMatch
```

## Generic model initialization and tracing

In `1.3.15`, `init_chat_model` recognizes LangSmith as a model provider. Core
chat models also expose `reasoning_effort` as a standard parameter, allowing
generic initialization without a provider-specific keyword container.

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("deployment-name", model_provider="langsmith")
model = init_chat_model("provider:model", reasoning_effort="high")
```

In `core-1.5.6`, LangChain Core incorporates gateway metadata into traces, so
tracing consumers receive gateway context without separate propagation.
