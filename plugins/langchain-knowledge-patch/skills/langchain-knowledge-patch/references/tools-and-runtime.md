# Tools & ToolRuntime (LangChain 1.0)

## ToolRuntime

Tools access agent state, context, and store via `ToolRuntime`:

```python
from langchain.tools import tool, ToolRuntime

@tool
def greet(runtime: ToolRuntime[Context, CustomState]) -> str:
    """Greet the user."""
    name = runtime.state.get("user_name", "Unknown")
    user_id = runtime.context.user_id
    return f"Hello {name} (id: {user_id})!"
```

`ToolRuntime` is generic over context and state types: `ToolRuntime[ContextType, StateType]`.

## Reserved Parameter Names

`config` and `runtime` cannot be used as tool argument names — they are reserved for framework injection.
