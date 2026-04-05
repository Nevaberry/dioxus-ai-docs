---
name: vercel-ai-sdk-knowledge-patch
description: >
  Vercel AI SDK v5–v6 features: ToolLoopAgent class, inputSchema/stopWhen/Output
  API replacements, UIMessage parts-based useChat, createUIMessageStream,
  @ai-sdk/mcp tools, dynamicTool, provider changes, Zod 4 requirement.
  Load before writing AI SDK v5+ code.
version: "6.0"
license: MIT
metadata:
  author: Nevaberry
---

# Vercel AI SDK Knowledge Patch (v5–v6)

Claude's baseline knowledge covers the Vercel AI SDK through v4. This skill provides features from v5 (2025) and v6 (2026).

## Reference Index

| Topic | Reference | Key features |
|---|---|---|
| Agents & tools | [references/agents-and-tools.md](references/agents-and-tools.md) | ToolLoopAgent, stopWhen, inputSchema rename, dynamicTool, tool error parts |
| Structured output & streaming | [references/structured-output-and-streaming.md](references/structured-output-and-streaming.md) | Output.object() replaces generateObject, createUIMessageStream, server streaming |
| React useChat | [references/react-useChat.md](references/react-useChat.md) | UIMessage parts, sendMessage, addToolOutput, DefaultChatTransport, tool part states |
| MCP tools | [references/mcp-tools.md](references/mcp-tools.md) | @ai-sdk/mcp, createMCPClient, schema discovery vs definition, transport types |
| Migration v5/v6 | [references/migration-v5-v6.md](references/migration-v5-v6.md) | Key renames, provider changes, Zod 4, codemods, mock class V3 |

---

## Quick Reference — v5/v6 Breaking Changes

| Old (v4) | New (v5+) |
|----------|-----------|
| `parameters` (tool) | `inputSchema` |
| `args` / `result` | `input` / `output` |
| `maxTokens` | `maxOutputTokens` |
| `maxSteps` | `stopWhen: isStepCount(N)` |
| `CoreMessage` | `ModelMessage` |
| `Message` | `UIMessage` (parts-based) |
| `convertToCoreMessages()` | `convertToModelMessages()` (async in v6) |
| `providerMetadata` (input) | `providerOptions` |
| `mimeType` | `mediaType` |
| `ai/react` | `@ai-sdk/react` |
| `ai/rsc` | `@ai-sdk/rsc` |
| `generateObject()` | `generateText({ output: Output.object({schema}) })` (v6) |
| `streamObject()` | `streamText({ output: Output.object({schema}) })` (v6) |
| `StreamData` / `createDataStreamResponse` | `createUIMessageStream` |
| `append({ role, content })` | `sendMessage({ text })` |

Codemods: `npx @ai-sdk/codemod v5` (v4->v5), `npx @ai-sdk/codemod v6` (v5->v6)

---

## ToolLoopAgent (v5)

```ts
import { ToolLoopAgent, tool, isStepCount, hasToolCall } from 'ai';
import { z } from 'zod';

const agent = new ToolLoopAgent({
  model: 'anthropic/claude-sonnet-4-5',
  instructions: 'You are a helpful assistant.',  // not `system`
  tools: {
    weather: tool({
      description: 'Get weather',
      inputSchema: z.object({ city: z.string() }),
      execute: async ({ city }) => ({ temp: 72 }),
    }),
  },
  stopWhen: [isStepCount(50), hasToolCall('done')],
  prepareStep: async ({ stepNumber }) => {
    if (stepNumber > 5) return { activeTools: ['summarize'] };
    return {};
  },
});

const result = await agent.generate({ prompt: 'Weather in SF?' });

// Streaming
const stream = await agent.stream({ prompt: 'Tell me a story' });
for await (const chunk of stream.textStream) { console.log(chunk); }

// API route helper
import { createAgentUIStreamResponse } from 'ai';
return createAgentUIStreamResponse({ agent, uiMessages: messages });
```

## stopWhen (replaces maxSteps)

```ts
import { isStepCount, hasToolCall, isLoopFinished } from 'ai';

const result = await generateText({
  model, messages, tools,
  stopWhen: isStepCount(5),  // or hasToolCall('done'), or isLoopFinished()
});
// result.usage = last step only; result.totalUsage = all steps
```

## Structured Output via Output API (v6)

```ts
import { generateText, streamText, Output } from 'ai';
import { z } from 'zod';

const { output } = await generateText({
  model, prompt: 'Generate a recipe.',
  output: Output.object({
    schema: z.object({ name: z.string(), steps: z.array(z.string()) }),
  }),
});

// Streaming structured data
const { partialOutputStream } = streamText({
  model, prompt: 'Generate a recipe.',
  output: Output.object({ schema }),
});
for await (const partial of partialOutputStream) { console.log(partial); }
```

## useChat — UIMessage parts (v5)

```tsx
import { useChat } from '@ai-sdk/react';
import { DefaultChatTransport, lastAssistantMessageIsCompleteWithToolCalls } from 'ai';
import { useState } from 'react';

const [input, setInput] = useState('');  // no more managed input
const { messages, sendMessage, addToolOutput, status, regenerate } = useChat({
  transport: new DefaultChatTransport({ api: '/api/chat' }),
  sendAutomaticallyWhen: lastAssistantMessageIsCompleteWithToolCalls,
  async onToolCall({ toolCall }) {
    const result = await executeTool(toolCall);
    addToolOutput({ tool: toolCall.toolName, toolCallId: toolCall.toolCallId, output: result });
    // Don't await addToolOutput inside onToolCall — causes deadlocks
  },
});
sendMessage({ text: input });  // was append({ role: 'user', content })
```

### Rendering UIMessage parts

```tsx
message.parts.map(part => {
  switch (part.type) {
    case 'text': return part.text;
    case 'reasoning': return part.text;       // was part.reasoning
    case 'file': return <img src={part.url} />; // was part.data + part.mimeType
    case 'tool-weather':                        // typed tool parts
      switch (part.state) {
        case 'input-streaming': ...   // was partial-call
        case 'input-available': ...   // was call
        case 'output-available': ...  // was result
        case 'output-error': ...      // new
      }
  }
});
```

- **Vue**: `useChat` replaced with `Chat` class + `DefaultChatTransport`
- **Svelte**: `Chat()` now takes factory function, properties readonly, use `setMessages()`

## Server Streaming (v5)

```ts
import { streamText, convertToModelMessages, createUIMessageStreamResponse } from 'ai';

// Simple: return streamText result directly
const result = streamText({ model, messages: await convertToModelMessages(uiMessages) });
return result.toUIMessageStreamResponse({ originalMessages: uiMessages });
```

### Custom data streaming

```ts
import { createUIMessageStream, createUIMessageStreamResponse, streamText } from 'ai';

const stream = createUIMessageStream({
  execute({ writer }) {
    writer.write({ type: 'data-status', id: 'status-1', data: { status: 'searching' } });
    const result = streamText({ model, messages });
    writer.merge(result.toUIMessageStream());
  },
});
return createUIMessageStreamResponse({ stream });
```

## dynamicTool (v5)

For tools with unknown types at compile time (MCP tools without schemas, runtime-defined):

```ts
import { dynamicTool } from 'ai';
const runtimeTool = dynamicTool({
  description: 'A runtime tool',
  inputSchema: z.object({}),
  execute: async (input) => ({ result: 'done' }),  // input/output typed as unknown
});
// Check toolCall.dynamic before type narrowing in onStepFinish
```

## MCP Tools

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
      outputSchema: z.object({ temperature: z.number() }),
    },
  },
});

const result = await generateText({ model, tools, prompt: '...' });
await mcp.close();
```

## Provider Changes (v6)

- **OpenAI**: `strictJsonSchema` defaults to `true`
- **Azure**: `azure()` uses Responses API; use `azure.chat()` for Chat Completions; key `openai` -> `azure`
- **Anthropic**: `structuredOutputMode`: `'auto'` | `'outputFormat'` | `'jsonTool'`
- **Google Vertex**: key `google` -> `vertex`
- **Embedding**: `textEmbeddingModel` -> `embeddingModel`

## Other Notes

- **Zod 4 required** (`zod@^4.1.8` peer dependency)
- Mock classes: V2 -> V3 (`MockLanguageModelV2` -> `MockLanguageModelV3`) in `ai/test`
- `experimental_continueSteps` removed — use models with higher output limits
- Finish reason `unknown` merged into `other` (v6)
- Warning logger: disable with `AI_SDK_LOG_WARNINGS=false`
