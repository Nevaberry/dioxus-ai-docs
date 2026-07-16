# MCP Adapters and Workflows

## Session lifetime is stateless by default

`MultiServerMCPClient` creates and cleans up a fresh MCP `ClientSession` for every
tool invocation. This remains true when the configured stdio server process is
itself stateful.

Open an explicit session when server context must survive across calls, then load
tools, resources, or prompts against that session.

```python
from langchain_mcp_adapters.tools import load_mcp_tools

async with client.session("orders") as session:
    tools = await load_mcp_tools(session)
    # Invoke tools while this session remains open.
```

Do not store protocol state in a server session unless the application also owns
the session lifetime. A tool loaded through the default client path may run in a
different fresh session on its next invocation.

## Structured and multimodal tool results

An MCP tool's `structuredContent` is wrapped in `MCPToolArtifact` and exposed at
`ToolMessage.artifact["structured_content"]`. Artifact data is not model-visible
unless an interceptor deliberately copies or summarizes it into result content.

Multipart MCP results are normalized into `ToolMessage.content_blocks`, including
provider-neutral `text` and `image` blocks.

```python
from langchain_core.messages import ToolMessage

for message in result["messages"]:
    if isinstance(message, ToolMessage) and message.artifact:
        data = message.artifact["structured_content"]
        blocks = message.content_blocks
```

Use artifacts for application data and content blocks for model-visible or UI
content. Copy only the fields the model is authorized to see.

## Resources and prompts

`client.get_resources(server_name, uris=...)` converts MCP resources to `Blob`
objects capable of holding text or binary data.

`client.get_prompt(server_name, name, arguments=...)` converts a server prompt to
LangChain messages.

```python
blobs = await client.get_resources(
    "docs",
    uris=["file:///guide.md"],
)
messages = await client.get_prompt(
    "docs",
    "review",
    arguments={"language": "python"},
)
```

Within an explicit session, use `load_mcp_resources()` and `load_mcp_prompt()` so
all reads participate in that session's context.

Treat resource URIs and prompt arguments as untrusted server inputs. Enforce the
same server allowlist and tenancy policy used for tools.

## Runtime-aware tool interceptors

Install async interceptor functions through `tool_interceptors=`. Each receives
an `MCPToolCallRequest` and the next handler.

`request.runtime` exposes:

- typed context;
- graph state;
- the long-term store;
- invocation config;
- the tool-call ID.

Use `request.override()` to replace arguments or headers. An interceptor may
short-circuit with a `ToolMessage`, or return a LangGraph `Command` to update
state or redirect graph execution.

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

Use interceptors for authorization, tenant injection, audit metadata, result
filtering, and policy routing. Do not trust a model-supplied tenant or identity
argument when an authenticated runtime value is available.

## Progress and logging callbacks

Pass `Callbacks` to receive MCP progress and server logging notifications.
Progress callbacks receive `progress`, optional `total` and `message`, and a
`CallbackContext`.

The callback context identifies the server. During a tool invocation it also
identifies the tool name.

```python
callbacks = Callbacks(
    on_progress=on_progress,
    on_logging_message=on_logging_message,
)
client = MultiServerMCPClient(
    {...},
    callbacks=callbacks,
)
```

Correlate notifications with server and tool identity before displaying them or
attaching them to traces; several MCP calls can make progress concurrently.

## Interactive elicitation

An MCP server tool can call `ctx.elicit(message=..., schema=...)` to request typed
input while it runs. The client handles the request with
`Callbacks(on_elicitation=...)`.

The handler returns `ElicitResult` with one of these outcomes:

- `accept` plus typed content;
- `decline`;
- `cancel`.

```python
async def on_elicitation(mcp_context, params, context):
    return ElicitResult(action="decline")

callbacks = Callbacks(on_elicitation=on_elicitation)
```

Validate the elicitation schema and identify the requesting server and tool
before presenting it to a user. Keep decline and cancel semantically distinct so
the server can decide whether to continue or terminate the operation.
