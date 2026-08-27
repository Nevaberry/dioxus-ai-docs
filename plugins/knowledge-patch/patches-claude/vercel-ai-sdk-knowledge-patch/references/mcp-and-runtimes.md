# MCP and Provider-Managed Runtimes

## Choose a transport and own the lifecycle

Create clients with `createMCPClient` from `@ai-sdk/mcp`. It accepts built-in HTTP or
SSE configuration, or a custom `MCPTransport`. Prefer HTTP for deployments and stdio
only for local servers. The lightweight adapter does not provide session management,
resumable streams, or notification reception. Keep the client open throughout
generation and close it afterward.

```ts
const client = await createMCPClient({
  transport: {
    type: 'http',
    url: 'https://example.com/mcp',
    headers: { Authorization: `Bearer ${token}` },
  },
});

try {
  await generateText({ model, tools: await client.tools(), prompt });
} finally {
  await client.close();
}
```

## Select tools and validate output

Calling `tools()` without schemas discovers every server tool without static input
types. Passing `schemas` fetches only named tools and gives them typed inputs. Represent
zero-argument tools with `z.object({})`.

A declared `outputSchema` validates `structuredContent`, then falls back to JSON parsed
from text. It throws when neither produces a valid value. Without an output schema,
tool execution returns the raw `CallToolResult`.

```ts
const tools = await client.tools({
  schemas: {
    search: {
      inputSchema: z.object({ query: z.string() }),
      outputSchema: z.object({ matches: z.array(z.string()) }),
    },
    ping: { inputSchema: z.object({}) },
  },
});
```

## Treat resources and prompts differently

Resources are application-selected context. Use the list, read, and template methods
to decide which resources enter the application. Server prompts are user-selected
templates obtained through the experimental prompt APIs, with optional arguments.

```ts
const resources = await client.listResources();
const resource = await client.readResource({
  uri: 'file:///example/document.txt',
});
const templates = await client.listResourceTemplates();

const prompts = await client.experimental_listPrompts();
const prompt = await client.experimental_getPrompt({
  name: 'code_review',
  arguments: { code: 'function add(a, b) { return a + b; }' },
});
```

## Handle elicitation explicitly

For a server to request user input during tool execution, the client must advertise
elicitation support and register a handler. The handler receives a message and a JSON
Schema, then returns `accept` with content, `decline`, or `cancel`.

```ts
const client = await createMCPClient({
  transport: { type: 'http', url: 'https://example.com/mcp' },
  capabilities: { elicitation: {} },
});

client.onElicitationRequest(ElicitationRequestSchema, async request => ({
  action: 'accept',
  content: await collectInput(
    request.params.message,
    request.params.requestedSchema,
  ),
}));
```

## Render MCP Apps safely

MCP integrations can separate model-visible tools from app-only tools. Render app
resources in sandboxed iframes with `experimental_MCPAppRenderer`. Clients support MCP
protocol version `2025-11-25`, public `listTools()`, `outputSchema`,
`structuredContent`, and `resource_link` content. Treat HTTP and SSE redirects as
errors. (since 2026-07)

```tsx
<MCPAppRenderer
  part={part}
  sandbox={{ url: '/mcp-app-sandbox' }}
  loadResource={app => fetch(`/api/mcp-apps?uri=${app.resourceUri}`)}
  handlers={{ allowedTools: ['refreshDashboard'] }}
/>
```

## Detect remote tool-definition drift

Before exposing remotely described tools, use `fingerprintTools` to record a trusted
baseline of server-controlled string descriptions, input schemas, and titles. Compare
later definitions with `detectToolDrift` before they reach the model. The application
owns baseline storage and the response policy when drift is found. (since 2026-07)
