# MCP Adapters and Workflows

## Session lifetime

`MultiServerMCPClient` creates and cleans up a fresh MCP `ClientSession` for
each tool invocation, including for a configured stdio server that is itself
stateful. To retain server context across calls, open `client.session()` and
load tools, resources, or prompts against that explicit session.

```python
from langchain_mcp_adapters.tools import load_mcp_tools

async with client.session("orders") as session:
    tools = await load_mcp_tools(session)
```

## Structured and multimodal results

An MCP tool's `structuredContent` is wrapped in `MCPToolArtifact` and exposed
at `ToolMessage.artifact["structured_content"]`. It is not model-visible unless
an interceptor copies it into result content. Multipart MCP results are
normalized into `ToolMessage.content_blocks`, including provider-neutral
`text` and `image` blocks.

```python
for message in result["messages"]:
    if isinstance(message, ToolMessage) and message.artifact:
        data = message.artifact["structured_content"]
        blocks = message.content_blocks
```

## Resources and prompts

`client.get_resources(server_name, uris=...)` converts MCP resources to
text- or binary-capable `Blob` objects. `client.get_prompt(server_name, name,
arguments=...)` converts a server prompt to LangChain messages. With explicit
sessions, use `load_mcp_resources()` and `load_mcp_prompt()`.

```python
blobs = await client.get_resources("docs", uris=["file:///guide.md"])
messages = await client.get_prompt(
    "docs", "review", arguments={"language": "python"}
)
```

## Runtime-aware tool interceptors

Async functions passed through `tool_interceptors=` wrap MCP execution. They
receive `MCPToolCallRequest` plus the next handler. `request.runtime` exposes
context, state, store, config, and tool-call ID. `request.override()` can
replace arguments or headers. An interceptor can short-circuit with a
`ToolMessage` or return a LangGraph `Command` to update state or redirect
execution.

```python
async def inject_tenant(request: MCPToolCallRequest, handler):
    request = request.override(args={
        **request.args,
        "tenant_id": request.runtime.context.tenant_id,
    })
    return await handler(request)

client = MultiServerMCPClient(
    {...}, tool_interceptors=[inject_tenant]
)
```

## Progress and logging callbacks

Pass `Callbacks` to receive server progress and logging notifications.
Progress callbacks receive `progress`, optional `total` and `message`, and a
`CallbackContext`. That context identifies the server and, during a tool call,
the tool name.

```python
callbacks = Callbacks(
    on_progress=on_progress,
    on_logging_message=on_logging_message,
)
client = MultiServerMCPClient({...}, callbacks=callbacks)
```

## Interactive elicitation

An MCP server tool can use `ctx.elicit(message=..., schema=...)` to request
typed input while running. The client handles it through
`Callbacks(on_elicitation=...)` and returns `ElicitResult` with `accept` plus
content, `decline`, or `cancel`.

```python
async def on_elicitation(mcp_context, params, context):
    return ElicitResult(action="decline")

callbacks = Callbacks(on_elicitation=on_elicitation)
```
