---
name: vercel-ai-sdk-knowledge-patch
description: "Vercel AI SDK changes since training cutoff (latest: 4.1.0) — PDF files, computer use tools, continuation, image generation, stream smoothing, createDataStreamResponse, tool call repair. Load before working with Vercel AI SDK."
version: "4.1.0"
license: MIT
metadata:
  author: Nevaberry
---

# Vercel AI SDK Knowledge Patch

Claude Opus 4.6 knows AI SDK through 3.x. It is **unaware** of the features below, which cover AI SDK 4.0 (2024-11-18) through 4.1 (2025-01-20).

## Index

| Topic | Reference | Key features |
|---|---|---|
| 4.0 & 4.1 features | [references/ai-sdk-4-features.md](references/ai-sdk-4-features.md) | PDF files, computer use tools, continuation, image generation, stream smoothing, createDataStreamResponse, tool context/repair, structured outputs with tools, new providers |

---

## PDF Support (4.0)

Send PDFs as `file` type in message content:

```ts
const result = await generateText({
  model: anthropic('claude-3-5-sonnet-20241022'),
  messages: [{
    role: 'user',
    content: [
      { type: 'text', text: 'Summarize this.' },
      { type: 'file', data: fs.readFileSync('./doc.pdf'), mimeType: 'application/pdf' },
    ],
  }],
});
```

Works with Anthropic, Google Generative AI, and Vertex AI.

---

## Computer Use (4.0)

Anthropic tools accessible via `anthropic.tools`:

```ts
const computerTool = anthropic.tools.computer_20241022({
  displayWidthPx: 1920, displayHeightPx: 1080,
  execute: async ({ action, coordinate, text }) => { /* implement actions */ },
  experimental_toToolResultContent: (result) => /* format result */,
});

await generateText({
  model: anthropic('claude-3-5-sonnet-20241022'),
  tools: { computer: computerTool },
  maxSteps: 10,
});
```

Also: `anthropic.tools.textEditor_20241022()`, `anthropic.tools.bash_20241022()`.

---

## Continuation (4.0)

Auto-continue when generation hits length limit:

```ts
await generateText({
  model: openai('gpt-4o'),
  maxSteps: 5,
  experimental_continueSteps: true,
  prompt: 'Write a long essay...',
});
```

---

## Image Generation (4.1)

```ts
import { experimental_generateImage as generateImage } from 'ai';
import { replicate } from '@ai-sdk/replicate';

const { image } = await generateImage({
  model: replicate.image('black-forest-labs/flux-1.1-pro-ultra'),
  prompt: 'A cityscape at sunset',
  size: '16:9',
  n: 3,
});
// image.base64, image.uint8Array
```

Providers: `replicate.image()`, `openai.image()`, `vertex.image()`, `fireworks.image()`.

---

## Stream Smoothing (4.1)

```ts
import { smoothStream, streamText } from 'ai';

const result = streamText({
  model, prompt,
  experimental_transform: smoothStream(),
});
```

---

## Non-blocking Data Streaming (4.1)

Stream custom data before/alongside LLM output:

```ts
import { createDataStreamResponse, streamText } from 'ai';

return createDataStreamResponse({
  execute: async (dataStream) => {
    dataStream.writeData({ type: 'source', url: '...' });
    const result = streamText({ model, messages });
    result.mergeIntoDataStream(dataStream);
  },
});
```

---

## Tool Improvements (4.1)

Execute context: `execute(args, { toolCallId, messages, abortSignal })`.

Tool call repair:

```ts
await generateText({
  model, tools, prompt,
  experimental_repairToolCall: async ({ toolCall, tools, parameterSchema, error }) => {
    if (NoSuchToolError.isInstance(error)) return null;
    const { object } = await generateObject({ model, schema: tools[toolCall.toolName].parameters, prompt: '...' });
    return { ...toolCall, args: JSON.stringify(object) };
  },
});
```

Structured outputs with tools via `experimental_output: Output.object({ schema })` (OpenAI only).

---

## New Providers

| Package | Provider |
|---|---|
| `@ai-sdk/xai` | xAI Grok |
| `@ai-sdk/groq` | Groq |
| `@ai-sdk/replicate` | Replicate (image) |
| `@ai-sdk/fireworks` | Fireworks (language + image) |
| `@ai-sdk/deepinfra` | DeepInfra |
| `@ai-sdk/deepseek` | DeepSeek |
| `@ai-sdk/cerebras` | Cerebras |

---

## Reference Files

| File | Contents |
|---|---|
| [ai-sdk-4-features.md](references/ai-sdk-4-features.md) | Complete API reference for all 4.0 and 4.1 features with full code examples |
