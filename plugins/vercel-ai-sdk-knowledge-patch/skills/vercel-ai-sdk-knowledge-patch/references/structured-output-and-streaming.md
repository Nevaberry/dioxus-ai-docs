# Structured Output & Server Streaming

## generateObject/streamObject deprecated (v6)

Use `generateText`/`streamText` with `output` instead:

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

## Server-side streaming (v5)

`StreamData` and `createDataStreamResponse` removed. Use `createUIMessageStream`:

```ts
import { createUIMessageStream, createUIMessageStreamResponse, streamText, convertToModelMessages } from 'ai';

// Simple: just return streamText result
const result = streamText({ model, messages: await convertToModelMessages(uiMessages) });
return result.toUIMessageStreamResponse({ originalMessages: uiMessages });

// Custom data streaming
const stream = createUIMessageStream({
  execute({ writer }) {
    writer.write({ type: 'data-status', id: 'status-1', data: { status: 'searching' } });
    const result = streamText({ model, messages });
    writer.merge(result.toUIMessageStream());
  },
});
return createUIMessageStreamResponse({ stream });
```
