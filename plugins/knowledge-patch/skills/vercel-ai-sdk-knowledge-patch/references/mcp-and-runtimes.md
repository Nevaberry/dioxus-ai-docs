# MCP and provider-managed runtimes

## Client transports and lifecycle

Create the lightweight MCP client with `createMCPClient` from `@ai-sdk/mcp`. It accepts
built-in HTTP or SSE transport configuration, or a custom `MCPTransport`. Prefer HTTP
for deployments; use stdio only for local servers.

```ts
import { createMCPClient } from '@ai-sdk/mcp';
import { generateText } from 'ai';

const client = await createMCPClient({
  transport: {
    type: 'http',
    url: 'https://example.com/mcp',
    headers: { Authorization: `Bearer ${token}` },
  },
});

try {
  await generateText({
    model,
    tools: await client.tools(),
    prompt,
  });
} finally {
  await client.close();
}
```

Keep the client open until generation and any tool calls are complete. The lightweight
adapter does not provide session management, resumable streams, or notification
reception. Choose a fuller MCP client when those features are required.

## Selective and typed tool discovery

Calling `client.tools()` without schemas discovers all tools exposed by the server,
but their inputs are not statically typed. Passing `schemas` requests only the named
tools and provides typed input. Represent a zero-argument tool with `z.object({})`.

```ts
const tools = await client.tools({
  schemas: {
    search: {
      inputSchema: z.object({ query: z.string() }),
      outputSchema: z.object({ matches: z.array(z.string()) }),
    },
    ping: {
      inputSchema: z.object({}),
    },
  },
});
```

When an `outputSchema` is present, the adapter validates `structuredContent`. If that
is unavailable or unsuitable, it attempts to parse JSON from text content. It throws
if neither path produces a valid value. Without `outputSchema`, execution returns the
raw `CallToolResult`.

Schema validation does not make an untrusted server definition safe. Restrict exposed
tools, validate outputs, and apply drift checks where server-controlled definitions can
change.

## Resources

Resources are application-selected context. The application lists them, chooses what
to read, and decides what enters a prompt. Resource templates describe parameterized
resource URIs.

```ts
const resources = await client.listResources();
const resource = await client.readResource({
  uri: 'file:///example/document.txt',
});
const templates = await client.listResourceTemplates();
```

Do not confuse server availability with authorization to disclose a resource to a
generation call.

## Server prompts

MCP prompts are user-controlled server templates, retrieved through experimental
APIs. Arguments are optional and template-specific:

```ts
const prompts = await client.experimental_listPrompts();
const prompt = await client.experimental_getPrompt({
  name: 'code_review',
  arguments: {
    code: 'function add(a, b) { return a + b; }',
  },
});
```

Keep the resource and prompt trust models distinct: applications select resource
context, while users select prompts and their arguments.

## Elicitation

An MCP server can request additional user input while a tool executes. The client must
advertise the elicitation capability and register a handler. The handler receives the
server message and requested JSON Schema, then returns one of:

- `accept`, with validated content;
- `decline`; or
- `cancel`.

```ts
import { ElicitationRequestSchema } from '@ai-sdk/mcp';

const client = await createMCPClient({
  transport: {
    type: 'http',
    url: 'https://example.com/mcp',
  },
  capabilities: {
    elicitation: {},
  },
});

client.onElicitationRequest(
  ElicitationRequestSchema,
  async request => ({
    action: 'accept',
    content: await collectInput(
      request.params.message,
      request.params.requestedSchema,
    ),
  }),
);
```

Validate the collected input against the requested schema and present enough server
identity and purpose for an informed user decision.

## MCP Apps (`2026-07`)

MCP Apps can separate tools visible to the language model from app-only tools used by
an interactive resource. `experimental_MCPAppRenderer` renders app resources inside a
sandboxed iframe. Supply a sandbox URL, a resource loader, and an explicit tool allow
list:

```tsx
<MCPAppRenderer
  part={part}
  sandbox={{ url: '/mcp-app-sandbox' }}
  loadResource={app =>
    fetch(`/api/mcp-apps?uri=${app.resourceUri}`)
  }
  handlers={{
    allowedTools: ['refreshDashboard'],
  }}
/>
```

The integration also supports:

- MCP protocol version `2025-11-25`;
- public `listTools()`;
- tool `outputSchema` and `structuredContent`; and
- `resource_link` content.

HTTP and SSE redirects are treated as errors. Configure the final endpoint directly;
do not rely on redirect following for authentication or transport setup.

## Tool-definition drift

Remote MCP servers control descriptive strings and schemas that can alter tool
selection and arguments. `fingerprintTools` captures the trusted tool set's
server-controlled descriptions, input schemas, and titles. `detectToolDrift` compares a
later fetch to that snapshot before tools are exposed to generation.

The application is responsible for:

1. storing and versioning the trusted fingerprint;
2. deciding when a new trusted snapshot may be approved;
3. blocking, warning, or constraining tools when drift is detected; and
4. keeping the check before any changed definition reaches the model.

Do not silently accept a changed fingerprint, because that converts detection into a
no-op.
