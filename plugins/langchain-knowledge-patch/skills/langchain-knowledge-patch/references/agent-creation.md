# Agent Creation (LangChain 1.0)

## create_agent replaces create_react_agent

`langgraph.prebuilt.create_react_agent` is deprecated. Use `langchain.agents.create_agent`:

```python
from langchain.agents import create_agent

agent = create_agent(
    model="anthropic:claude-sonnet-4-6",  # or model instance
    tools=[my_tool],
    system_prompt="You are a helpful assistant",  # was "prompt"
    middleware=[...],           # new: replaces pre/post hooks
    response_format=...,       # ToolStrategy or ProviderStrategy
    state_schema=CustomState,  # must be TypedDict, not Pydantic
    context_schema=Context,    # new: typed runtime context
    name="my_agent",           # snake_case preferred
)
```

## Invocation

```python
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Hello"}]},
    context=Context(user_id="123")  # new: replaces config["configurable"]
)
```

## Migration Summary

| Old (0.2.x / LangGraph 0.1) | New (1.0) |
|------------------------------|-----------|
| `from langgraph.prebuilt import create_react_agent` | `from langchain.agents import create_agent` |
| `prompt=` parameter | `system_prompt=` |
| `config={"configurable": {...}}` | `context=Context(...)` with `context_schema` |
| Pydantic or dataclass for `state_schema` | `TypedDict` only |
| Streaming node named `"agent"` | Node named `"model"` |
| Pre-bound model via `model.bind_tools(tools)` | Pass unbound model + `tools=` parameter |
| Pre/post processing hooks | `middleware=[...]` parameter |
