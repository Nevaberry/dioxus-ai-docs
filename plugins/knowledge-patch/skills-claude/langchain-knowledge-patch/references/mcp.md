# MCP Adapters and Workflows

## Session lifetime

`MultiServerMCPClient` creates and cleans up a fresh MCP `ClientSession` for
every tool invocation, including when a configured stdio server is itself
stateful. To retain server context across calls, open `client.session()`
explicitly and load tools, resources, or prompts against that session.

```python
from langchain_mcp_adapters.tools import load_mcp_tools

async with client.session("orders") as session:
    tools = await load_mcp_tools(session)
```

## Tool results

An MCP tool's `structuredContent` is wrapped in `MCPToolArtifact` and exposed
as `ToolMessage.artifact["structured_content"]`. It is not model-visible
unless an interceptor copies it into result content.

Multipart MCP results are normalized into `ToolMessage.content_blocks`,
including provider-neutral `text` and `image` blocks.

```python
for message in result["messages"]:
    if isinstance(message, ToolMessage) and message.artifact:
        data = message.artifact["structured_content"]
        blocks = message.content_blocks
```

## Resources and prompts

`client.get_resources(server_name, uris=...)` converts MCP resources into
text- or binary-capable `Blob` objects. `client.get_prompt(server_name, name,
arguments=...)` converts a server prompt into LangChain messages. With an
explicit session, use `load_mcp_resources()` and `load_mcp_prompt()` instead.

```python
blobs = await client.get_resources("docs", uris=["file:///guide.md"])
messages = await client.get_prompt(
    "docs", "review", arguments={"language": "python"}
)
```

## Runtime-aware tool interceptors

Async functions supplied through `tool_interceptors=` wrap MCP execution. An
interceptor receives an `MCPToolCallRequest` and the next handler.
`request.runtime` exposes context, state, store, config, and the tool-call ID.

Use `request.override()` to replace arguments or headers. An interceptor may
short-circuit with a `ToolMessage` or return a LangGraph `Command` to update
state or redirect execution.

```python
async def inject_tenant(request: MCPToolCallRequest, handler):
    request = request.override(args={
        **request.args,
        "tenant_id": request.runtime.context.tenant_id,
    })
    return await handler(request)

client = MultiServerMCPClient(
    {...},
    tool_interceptors=[inject_tenant],
)
```

## Progress and logging callbacks

Pass `Callbacks` to the client to receive server progress and logging
notifications. A progress callback receives `progress`, optional `total` and
`message`, and a `CallbackContext`. The context identifies the server and,
during tool calls, the tool name.

```python
callbacks = Callbacks(
    on_progress=on_progress,
    on_logging_message=on_logging_message,
)
client = MultiServerMCPClient({...}, callbacks=callbacks)
```

## Interactive elicitation

An MCP server tool can call `ctx.elicit(message=..., schema=...)` to request
typed input while it runs. The client handles the request through
`Callbacks(on_elicitation=...)` and returns `ElicitResult` with `accept` plus
content, `decline`, or `cancel`.

```python
async def on_elicitation(mcp_context, params, context):
    return ElicitResult(action="decline")

callbacks = Callbacks(on_elicitation=on_elicitation)
```
