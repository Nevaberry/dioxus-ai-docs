# Middleware System (LangChain 1.0)

New extensibility model for the agent loop. Use decorators for simple cases, classes for complex ones.

## Imports

```python
from langchain.agents.middleware import (
    before_model, after_model, wrap_model_call, wrap_tool_call,
    dynamic_prompt, AgentMiddleware, ModelRequest, ModelResponse,
    SummarizationMiddleware, HumanInTheLoopMiddleware,
)
```

## Decorator Style

```python
@before_model
def trim_context(state, runtime):
    # modify state before model call
    return {"messages": state["messages"][-20:]}

@after_model
def log_response(state, runtime):
    print(f"Model responded with {len(state['messages'])} messages")
    return state

@wrap_model_call
def retry_on_error(request, handler):
    try:
        return handler(request)
    except Exception:
        return handler(request)  # simple retry

@wrap_tool_call
def handle_errors(request, handler):
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(content=f"Error: {e}", tool_call_id=request.tool_call["id"])

@dynamic_prompt
def my_prompt(request: ModelRequest) -> str:
    role = request.runtime.context.user_role
    return f"You are helpful. User role: {role}"
```

## Class Style

For complex middleware that needs its own state:

```python
class MyMiddleware(AgentMiddleware):
    state_schema = CustomState  # middleware can define its own state

    def before_model(self, state, runtime): ...
    def after_model(self, state, runtime): ...
    def wrap_model_call(self, request, handler): ...
    def wrap_tool_call(self, request, handler): ...
```

## Built-in Middleware

### SummarizationMiddleware

```python
SummarizationMiddleware(model="claude-sonnet-4-6", trigger={"tokens": 1000})
```

### HumanInTheLoopMiddleware

```python
HumanInTheLoopMiddleware(interrupt_on={
    "send_email": {
        "description": "Review before sending",
        "allowed_decisions": ["approve", "reject"]
    }
})
```

### Usage

```python
agent = create_agent(
    model="claude-sonnet-4-6",
    tools=tools,
    middleware=[
        SummarizationMiddleware(model="claude-sonnet-4-6", trigger={"tokens": 1000}),
        HumanInTheLoopMiddleware(interrupt_on={
            "send_email": {"description": "Review before sending", "allowed_decisions": ["approve", "reject"]}
        }),
    ]
)
```

### Other Built-in Middleware

- `ModelCallLimitMiddleware` — limit number of model calls per invocation
- `ToolCallLimitMiddleware` — limit number of tool calls per invocation
- `ModelFallbackMiddleware` — fall back to another model on failure
- `PIIMiddleware` — redact PII from messages
- `TodoListMiddleware` — planning/task tracking
- `LLMToolSelectorMiddleware` — use LLM to select relevant tools
- `ToolRetryMiddleware` — retry failed tool calls
- `ContextEditingMiddleware` — edit context between steps
