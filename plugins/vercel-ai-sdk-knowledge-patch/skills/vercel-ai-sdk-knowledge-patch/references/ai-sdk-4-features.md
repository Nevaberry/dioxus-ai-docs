# AI SDK 4.0 & 4.1 Features Reference

## PDF Support (4.0)

Send PDF files as `file` type in message content. Works with Anthropic, Google Generative AI, and Google Vertex AI.

```ts
import { generateText } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';

const result = await generateText({
  model: anthropic('claude-3-5-sonnet-20241022'),
  messages: [{
    role: 'user',
    content: [
      { type: 'text', text: 'Summarize this document.' },
      {
        type: 'file',
        data: fs.readFileSync('./doc.pdf'),
        mimeType: 'application/pdf',
      },
    ],
  }],
});
```

## Computer Use — Anthropic (4.0)

Three predefined tools via `anthropic.tools`:

```ts
// Computer tool — mouse, keyboard, screenshots
const computerTool = anthropic.tools.computer_20241022({
  displayWidthPx: 1920,
  displayHeightPx: 1080,
  execute: async ({ action, coordinate, text }) => {
    switch (action) {
      case 'screenshot':
        return { type: 'image', data: getScreenshot() };
      default:
        return executeComputerAction(action, coordinate, text);
    }
  },
  experimental_toToolResultContent: (result) =>
    typeof result === 'string'
      ? [{ type: 'text', text: result }]
      : [{ type: 'image', data: result.data, mimeType: 'image/png' }],
});

// Text editor tool
const textEditorTool = anthropic.tools.textEditor_20241022({
  execute: async ({ command, path, old_str, new_str }) => { /* ... */ },
});

// Bash tool
const bashTool = anthropic.tools.bash_20241022({
  execute: async ({ command }) => { /* ... */ },
});

// Combine with maxSteps for multi-step automation
const result = await generateText({
  model: anthropic('claude-3-5-sonnet-20241022'),
  prompt: 'Open the browser and search for...',
  tools: { computer: computerTool, textEditor: textEditorTool, bash: bashTool },
  maxSteps: 10,
});
```

## Continuation Support (4.0)

Auto-continues when generation hits length limit. Combines into single output.

```ts
const result = await generateText({
  model: openai('gpt-4o'),
  maxSteps: 5,
  experimental_continueSteps: true,
  prompt: 'Write a very long essay...',
});
// Works with streamText too — streams complete words at boundaries
```

## Image Generation (4.1)

```ts
import { experimental_generateImage as generateImage } from 'ai';
import { replicate } from '@ai-sdk/replicate';

const { image } = await generateImage({
  model: replicate.image('black-forest-labs/flux-1.1-pro-ultra'),
  prompt: 'A futuristic cityscape at sunset',
  size: '16:9',       // or width x height
  aspectRatio: '16:9', // alternative to size
  n: 3,               // generate multiple
  seed: 0,            // reproducibility
  providerOptions: {
    replicate: { style: 'realistic_image' },
  },
});

// Access results
image.base64;     // base64 string
image.uint8Array; // binary data
```

Provider image model constructors:
- `replicate.image('model-name')`
- `openai.image('dall-e-3')`
- `vertex.image('imagegeneration@006')`
- `fireworks.image('accounts/fireworks/models/SSD-1B')`

## Stream Smoothing & Transformation (4.1)

```ts
import { smoothStream, streamText } from 'ai';

const result = streamText({
  model,
  prompt,
  // Single transform
  experimental_transform: smoothStream(),
  // Or multiple transforms
  experimental_transform: [smoothStream(), customFilter],
});
```

`smoothStream()` smooths chunky provider responses into consistent flow. Options include chunking by character, word, or line.

## Non-blocking Data Streaming (4.1)

`createDataStreamResponse` enables streaming custom data before/alongside LLM output.

```ts
import { createDataStreamResponse, streamText } from 'ai';

export async function POST(req: Request) {
  const { messages } = await req.json();

  return createDataStreamResponse({
    execute: async (dataStream) => {
      // Stream custom data (e.g., RAG sources) BEFORE LLM response
      dataStream.writeData({ type: 'source', url: '...', title: '...' });

      // Then stream LLM output
      const result = streamText({ model, messages });
      result.mergeIntoDataStream(dataStream);

      // Add annotations after completion
      // onFinish: () => dataStream.writeMessageAnnotation({ ... })
    },
  });
}
```

Client receives both via `useChat`:
```ts
const { messages, data } = useChat();
// data contains streamed custom data
// messages[i].annotations contains message annotations
```

## Tool Calling Improvements (4.1)

### Execute context

```ts
execute: async (args, { toolCallId, messages, abortSignal }) => {
  // toolCallId — unique ID for this call
  // messages — full conversation history
  // abortSignal — forward to fetch calls
  const res = await fetch(url, { signal: abortSignal });
  return res.json();
}
```

### Tool call repair

```ts
const result = await generateText({
  model, tools, prompt,
  experimental_repairToolCall: async ({ toolCall, tools, parameterSchema, error }) => {
    if (NoSuchToolError.isInstance(error)) return null; // don't fix bad tool names

    const { object: repairedArgs } = await generateObject({
      model: openai('gpt-4o', { structuredOutputs: true }),
      schema: tools[toolCall.toolName].parameters,
      prompt: `Fix: ${JSON.stringify(toolCall.args)}`,
    });
    return { ...toolCall, args: JSON.stringify(repairedArgs) };
  },
});
```

### Error types

- `NoSuchToolError` — model called undefined tool
- `InvalidToolArgumentsError` — schema validation failure
- `ToolExecutionError` — runtime error during execution
- `ToolCallRepairError` — repair attempt failed

## Structured Outputs with Tools (4.1)

Combine tool calling with structured output in a single call:

```ts
import { generateText, Output } from 'ai';

const result = await generateText({
  model: openai('gpt-4o', { structuredOutputs: true }),
  prompt: "What's the weather in London and NYC?",
  maxSteps: 5,
  tools: { getWeather: weatherTool },
  experimental_output: Output.object({
    schema: z.object({
      cities: z.array(z.object({
        name: z.string(),
        temperature: z.number(),
        conditions: z.string(),
      })),
    }),
  }),
});
```

Currently only available with OpenAI models.

### NoObjectGeneratedError

```ts
try {
  const result = await generateObject({ model, schema, prompt });
} catch (error) {
  if (error instanceof NoObjectGeneratedError) {
    console.log(error.text);     // raw model output
    console.log(error.response); // response metadata
    console.log(error.usage);    // token usage
    console.log(error.cause);    // underlying error
  }
}
```

## Provider Ecosystem

### New in 4.0
| Package | Provider |
|---|---|
| `@ai-sdk/xai` | xAI Grok |
| `@ai-sdk/groq` | Groq |

### New in 4.1
| Package | Provider | Models |
|---|---|---|
| `@ai-sdk/replicate` | Replicate | Image models |
| `@ai-sdk/fireworks` | Fireworks | Language + image |
| `@ai-sdk/deepinfra` | DeepInfra | Language |
| `@ai-sdk/deepseek` | DeepSeek | Language |
| `@ai-sdk/cerebras` | Cerebras | Language |
| `@ai-sdk/openai-compatible` | Generic OpenAI-compatible | Language |
