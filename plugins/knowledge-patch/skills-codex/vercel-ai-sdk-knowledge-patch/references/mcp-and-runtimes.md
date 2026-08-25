# MCP and Provider-Managed Runtimes

## Client transports and lifecycle

Create clients with `createMCPClient` from `@ai-sdk/mcp`. It accepts built-in HTTP or
SSE configuration, or a custom `MCPTransport`. Prefer HTTP for deployments; reserve
stdio for local servers. Keep the client open for the entire generation and close it
afterward.

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
  await generateText({ model, tools: await client.tools(), prompt });
} finally {
  await client.close();
}
```

The lightweight adapter does not implement session management, resumable streams, or
notification reception. If an application needs those capabilities, provide the
corresponding lifecycle outside the adapter.

## Selective tools and output schemas

Calling `client.tools()` with no schemas discovers every server tool but cannot give
their inputs static types. Supplying `schemas` fetches only the named tools and adds
typed inputs. Represent a zero-argument tool with `z.object({})`.

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

When a tool has an `outputSchema`, execution first validates `structuredContent`, then
falls back to parsing JSON from text content. It throws when neither produces a valid
value. Without an output schema, execution returns the raw `CallToolResult`.

## Resources and prompts

Treat resources as application-selected context. Clients can list and read resources
and list URI templates. Treat server prompts as user-selected templates; retrieve
them through the experimental prompt APIs and pass optional arguments explicitly.

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

## Elicitation

An MCP server may ask for more user input during tool execution only when the client
advertises elicitation support and registers a handler. The handler receives a
message and requested JSON Schema and must return one of `accept` with content,
`decline`, or `cancel`.

```ts
import { ElicitationRequestSchema } from '@ai-sdk/mcp';

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

## MCP Apps and richer content

The 2026-07 integration can distinguish model-visible tools from app-only tools and
render app resources in sandboxed iframes with experimental `MCPAppRenderer`. Limit
the app's callable tools and load its resource through an application-controlled
endpoint.

```tsx
<MCPAppRenderer
  part={part}
  sandbox={{ url: '/mcp-app-sandbox' }}
  loadResource={app => fetch(`/api/mcp-apps?uri=${app.resourceUri}`)}
  handlers={{ allowedTools: ['refreshDashboard'] }}
/>
```

Clients also support protocol version `2025-11-25`, public `listTools()`, tool
`outputSchema` and `structuredContent`, and `resource_link` content. HTTP and SSE
redirects are treated as errors rather than followed.

## Tool-definition drift

Before remotely described tools reach the model, use `fingerprintTools` (2026-07) to
record a trusted baseline of server-controlled string descriptions, input schemas,
and titles. Compare later discovery results with `detectToolDrift`. The application is
responsible for durable baseline storage and for the allow, block, or review policy
when drift is detected.
