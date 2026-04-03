---
name: langchain-knowledge-patch
description: LangChain 1.0 / LangGraph 1.0 changes — create_agent replaces create_react_agent, middleware system, ToolRuntime, content_blocks, structured output strategies, simplified namespace, Deep Agents SDK, breaking changes (Python 3.10+, .text property). Load before working with LangChain.
license: MIT
metadata:
  author: Nevaberry
  version: "1.0.0"
---

# LangChain 1.0 Knowledge Patch

Claude's baseline knowledge covers LangChain 0.2.x and LangGraph 0.1.x. This skill provides changes from the LangChain 1.0 / LangGraph 1.0 release (2025-10-22).

## Quick Reference

### Agent Creation

| Old API | New API | Notes |
|---------|---------|-------|
| `langgraph.prebuilt.create_react_agent` | `langchain.agents.create_agent` | Full replacement |
| `prompt=` | `system_prompt=` | Parameter renamed |
| `config["configurable"]` | `context=Context(...)` | Typed runtime context |
| Pydantic/dataclass state | `TypedDict` only | `state_schema` constraint |
| Streaming node `"agent"` | `"model"` | Node name changed |
| `model.bind_tools(...)` then pass | Pass unbound model + `tools=` | Pre-bound models rejected |

### create_agent — Essential Pattern

```python
from langchain.agents import create_agent

agent = create_agent(
    model="anthropic:claude-sonnet-4-6",  # or model instance
    tools=[my_tool],
    system_prompt="You are a helpful assistant",
    middleware=[...],           # replaces pre/post hooks
    response_format=...,       # ToolStrategy or ProviderStrategy
    state_schema=CustomState,  # must be TypedDict, not Pydantic
    context_schema=Context,    # typed runtime context
    name="my_agent",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Hello"}]},
    context=Context(user_id="123")  # replaces config["configurable"]
)
```

See `references/agent-creation.md` for full migration guide.

### Middleware System

| Decorator | Purpose |
|-----------|---------|
| `@before_model` | Modify state before model call |
| `@after_model` | Modify state after model response |
| `@wrap_model_call` | Wrap entire model call (try/except, retries) |
| `@wrap_tool_call` | Wrap tool execution |
| `@dynamic_prompt` | Generate system prompt dynamically |

Built-in: `SummarizationMiddleware`, `HumanInTheLoopMiddleware`, `ModelCallLimitMiddleware`, `ToolCallLimitMiddleware`, `ModelFallbackMiddleware`, `PIIMiddleware`, `TodoListMiddleware`, `LLMToolSelectorMiddleware`, `ToolRetryMiddleware`, `ContextEditingMiddleware`.

All middleware imports from `langchain.agents.middleware`. See `references/middleware.md` for decorator and class patterns.

### Middleware — Quick Example

```python
from langchain.agents.middleware import before_model, wrap_tool_call

@before_model
def trim_context(state, runtime):
    return {"messages": state["messages"][-20:]}

@wrap_tool_call
def handle_errors(request, handler):
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(content=f"Error: {e}", tool_call_id=request.tool_call["id"])

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=tools,
    middleware=[trim_context, handle_errors],
)
```

### Tools & Runtime

`ToolRuntime` gives tools access to agent state, context, and store:

```python
from langchain.tools import tool, ToolRuntime

@tool
def greet(runtime: ToolRuntime[Context, CustomState]) -> str:
    """Greet the user."""
    name = runtime.state.get("user_name", "Unknown")
    return f"Hello {name} (id: {runtime.context.user_id})!"
```

Reserved parameter names: `config`, `runtime` cannot be used as tool argument names.

See `references/tools-and-runtime.md`.

### Content Blocks & Structured Output

| Feature | API |
|---------|-----|
| Provider-agnostic content | `response.content_blocks` (list of typed dicts) |
| Multimodal input | `HumanMessage(content_blocks=[...])` |
| Serialization opt-in | `LC_OUTPUT_VERSION=v1` or `output_version="v1"` |
| Tool-based structured output | `ToolStrategy(MySchema)` |
| Native structured output | `ProviderStrategy(MySchema)` |
| Auto-fallback | Pass schema directly to `response_format=` |

### Structured Output — Quick Example

```python
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy

# ToolStrategy: works with any model supporting tool calling
agent = create_agent(model="gpt-4.1", tools=tools, response_format=ToolStrategy(MySchema))

# ProviderStrategy: uses native structured output (more reliable, fewer providers)
agent = create_agent(model="gpt-4.1", response_format=ProviderStrategy(MySchema))

# Passing schema directly defaults to ProviderStrategy with ToolStrategy fallback
agent = create_agent(model="gpt-4.1", response_format=MySchema)

result["structured_response"]  # access the typed output
```

Prompted output is removed. Structured output now happens in the main agent loop (no extra LLM call).

See `references/content-and-output.md` for content blocks and multimodal messages.

### Namespace Changes

| New location | Old location |
|-------------|-------------|
| `langchain.agents` | `langgraph.prebuilt` |
| `langchain.messages` | `langchain_core.messages` |
| `langchain.tools` | `langchain_core.tools` |
| `langchain.chat_models` | `langchain_community.chat_models` |
| `langchain.embeddings` | `langchain_community.embeddings` |
| `langchain_classic.*` | Legacy chains, retrievers, hub, indexing |

### langchain-classic

Legacy chains, retrievers, indexing, hub, and community re-exports:

```python
# pip install langchain-classic
from langchain_classic.chains import LLMChain
from langchain_classic.retrievers import ...
from langchain_classic import hub
```

See `references/namespace-and-migration.md` for full details.

## Breaking Changes (1.0)

- **Python 3.10+** required (3.9 dropped)
- `message.text` is now a **property** — use `response.text` not `response.text()`
- `example` parameter removed from `AIMessage`
- `langchain-anthropic` `max_tokens` default increased (was 1024)
- Chat model return type fixed to `AIMessage` (was `BaseMessage`)
- OpenAI Responses API now defaults to storing response items in message `content`

## Deep Agents SDK

New `deepagents` package for complex multi-step tasks:

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    tools=[my_tool],
    system_prompt="You are a helpful assistant",
)
```

Built-in capabilities: `write_todos` (planning), `ls`/`read_file`/`write_file`/`edit_file` (context management), `task` (subagent spawning). Pluggable filesystem backends (in-memory, local disk, LangGraph store, sandboxes).

See `references/namespace-and-migration.md` for package details.

## Reference Files

| File | Contents |
|------|----------|
| `agent-creation.md` | `create_agent` API, migration from `create_react_agent`, parameters, invocation |
| `middleware.md` | Decorator and class middleware patterns, built-in middleware, `SummarizationMiddleware`, `HumanInTheLoopMiddleware` |
| `tools-and-runtime.md` | `ToolRuntime` typed access to state/context/store, reserved parameter names |
| `content-and-output.md` | `content_blocks` property, multimodal messages, `ToolStrategy`, `ProviderStrategy`, structured output in agent loop |
| `namespace-and-migration.md` | Simplified namespace, `langchain-classic` package, Deep Agents SDK |
