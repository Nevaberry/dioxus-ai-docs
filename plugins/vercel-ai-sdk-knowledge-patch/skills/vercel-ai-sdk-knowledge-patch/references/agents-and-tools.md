# Agents & Tool System

## ToolLoopAgent class (v5, replaces manual agent loops)

Reusable agent class encapsulating model, tools, instructions, and loop control. Uses `instructions` (not `system`). Default stop: `isStepCount(20)`.

```ts
import { ToolLoopAgent, tool, isStepCount, hasToolCall, isLoopFinished } from 'ai';
import { z } from 'zod';

const agent = new ToolLoopAgent({
  model: 'anthropic/claude-sonnet-4-5',
  instructions: 'You are a helpful assistant.',
  tools: {
    weather: tool({
      description: 'Get weather',
      inputSchema: z.object({ city: z.string() }),  // was `parameters`
      execute: async ({ city }) => ({ temp: 72 }),
    }),
  },
  stopWhen: [isStepCount(50), hasToolCall('done')],  // replaces maxSteps
  prepareStep: async ({ stepNumber, messages, steps }) => {
    // Dynamic per-step config: model, tools, activeTools, toolChoice, messages
    if (stepNumber > 5) return { activeTools: ['summarize'] };
    return {};
  },
});

const result = await agent.generate({ prompt: 'Weather in SF?' });
console.log(result.text, result.steps);

// Streaming
const stream = await agent.stream({ prompt: 'Tell me a story' });
for await (const chunk of stream.textStream) { console.log(chunk); }

// API route helper
import { createAgentUIStreamResponse } from 'ai';
return createAgentUIStreamResponse({ agent, uiMessages: messages });
```

## stopWhen replaces maxSteps (v5)

```ts
import { isStepCount, hasToolCall, isLoopFinished } from 'ai';

// Works with generateText/streamText too
const result = await generateText({
  model, messages, tools,
  stopWhen: isStepCount(5),  // or hasToolCall('done'), or isLoopFinished()
});
// result.usage = last step only; result.totalUsage = all steps
```

## Tool definition renames (v5 breaking)

- `parameters` -> `inputSchema`
- `args` -> `input`, `result` -> `output` (in tool calls/results and stream parts)
- `experimental_toToolResultContent` -> `toModelOutput` (returns `{ type: 'content', value: [...] }`)
- `toModelOutput` signature in v6: `({ output }) => ...` (destructured)
- `ToolCallOptions` -> `ToolExecutionOptions`
- Per-tool `strict: true` (v6) replaces global `strictJsonSchema` in providerOptions
- Tool execution errors now appear as `tool-error` content parts in steps (no more `ToolExecutionError` class)
- Tool call streaming always enabled (no `toolCallStreaming` option)

## dynamicTool helper (v5)

For tools with unknown types at compile time (MCP tools without schemas, runtime-defined tools):

```ts
import { dynamicTool } from 'ai';
const runtimeTool = dynamicTool({
  description: 'A runtime tool',
  inputSchema: z.object({}),
  execute: async (input) => ({ result: 'done' }),  // input/output typed as unknown
});
// Check toolCall.dynamic before type narrowing in onStepFinish
```
