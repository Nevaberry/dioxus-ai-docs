# MCP Tools (`@ai-sdk/mcp`)

```ts
import { createMCPClient } from '@ai-sdk/mcp';

const mcp = await createMCPClient({
  transport: { type: 'http', url: 'https://server.com/mcp', headers: { Authorization: 'Bearer key' } },
  // or: { type: 'sse', url }, or: new StdioClientTransport({ command: 'node', args: [...] })
});

// Schema discovery (all tools, no type safety)
const tools = await mcp.tools();

// Schema definition (selected tools, full type safety)
const tools = await mcp.tools({
  schemas: {
    'get-weather': {
      inputSchema: z.object({ location: z.string() }),
      outputSchema: z.object({ temperature: z.number() }),  // typed output from structuredContent
    },
  },
});

const result = await generateText({ model, tools, prompt: '...' });
await mcp.close();  // close when done
```
