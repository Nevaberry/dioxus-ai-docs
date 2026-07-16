# Generation, structured output, and media

## Stream consumption and error delivery

`streamText` starts generation immediately but honors backpressure. Work progresses
only while a returned stream is consumed, so an unconsumed stream can leave generation
unfinished.

Streaming generation errors are delivered in-band rather than thrown to the original
caller. Observe them through `onError` or `error` parts in the complete event stream.
Tool `execute` failures become `tool-error` parts and are also recorded in
non-streaming `steps`. Schema failures and other `generateText` failures still throw.

```ts
const result = streamText({
  model,
  prompt,
  onError: ({ error }) => log(error),
});

for await (const part of result.fullStream) {
  handle(part);
}
```

The example uses the pre-v7 `fullStream` spelling. For v7-targeted code, the property
is `stream`.

## Stream transforms

`experimental_transform` accepts one transform or an ordered array. Transformed
events are what callbacks observe and what result promises resolve from.

```ts
const result = streamText({
  model,
  prompt,
  experimental_transform: [smoothStream(), redactTransform()],
});
```

A custom transform receives `tools` and `stopStream`. If it stops early, it must emit
synthetic `finish-step` and `finish` events; otherwise callbacks and downstream
consumers may never complete.

## Automatic continuation after a length limit

Introduced in `4.0.0`, `experimental_continueSteps: true` lets `generateText` or
`streamText` continue after a step stops because of the output length limit. Set a
finite `maxSteps`. The SDK joins the generated steps and reports combined token usage.
Streaming emits complete words and may trim trailing tokens at continuation
boundaries.

```ts
const result = await generateText({
  model,
  prompt: 'Write a long-form history of Rome.',
  maxSteps: 5,
  experimental_continueSteps: true,
});
```

## Structured output with tools

Since `4.1.0`, text generation can perform tool calls and return a schema-validated
final value in one multi-step operation. At introduction, the combination used
`experimental_output` and was limited to OpenAI models.

```ts
const result = await generateText({
  model: openai('gpt-4o', { structuredOutputs: true }),
  prompt,
  tools,
  maxSteps: 5,
  experimental_output: Output.object({
    schema: z.object({ answer: z.string() }),
  }),
});
```

On API lines where the prefix has been removed, use `output`. Verify current provider
support instead of carrying forward the introduction-time restriction blindly.

## Diagnosing structured-output failure

`NoObjectGeneratedError` retains enough information for diagnosis or cautious partial
recovery:

- raw generated `text`;
- response metadata;
- token `usage`; and
- the underlying `cause`.

```ts
try {
  await generateObject({ model, schema, prompt });
} catch (error) {
  if (error instanceof NoObjectGeneratedError) {
    console.log(error.text, error.response, error.usage, error.cause);
  }
}
```

Do not retry blindly when the retained response can distinguish malformed JSON,
schema mismatch, truncation, or a provider failure.

## Schema processing and repair

JSON Schema post-processing is stricter for Zod and Standard Schema inputs. Malformed
JSON extraction and repair can be applied to structured output and tool calls. Array
output mode preserves schema transforms, coercions, defaults, and pipes rather than
discarding those effects per element.

Test schema behavior explicitly when upgrading code that depends on coercion,
defaults, transforms, or permissive JSON extraction.

## PDF inputs

Since `4.0.0`, compatible Anthropic, Google Generative AI, and Google Vertex AI models
can receive PDF bytes through the same `file` message-part shape. Set
`mimeType: 'application/pdf'` and put the bytes in `data`:

```ts
import { readFileSync } from 'node:fs';
import { generateText } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';

const result = await generateText({
  model: anthropic('claude-3-5-sonnet-20241022'),
  messages: [
    {
      role: 'user',
      content: [
        { type: 'text', text: 'Summarize this document.' },
        {
          type: 'file',
          data: readFileSync('./document.pdf'),
          mimeType: 'application/pdf',
        },
      ],
    },
  ],
});
```

Use the provider-reference form described below when the same document will be reused
and the provider supports managed uploads.

## Canonical file parts and reusable uploads

Media converges on a canonical `file` shape. Depending on the provider and operation,
a file part can carry inline data, a URL, a provider reference, or text-backed content.

`uploadFile` sends data once and returns `providerReference`, which can be reused as a
`file` part instead of retransmitting the bytes:

```ts
const { providerReference } = await uploadFile({
  api: provider.files(),
  data: await readFile('./brief.pdf'),
  filename: 'brief.pdf',
});

await streamText({
  model,
  messages: [
    {
      role: 'user',
      content: [
        { type: 'text', text: 'Summarize this brief.' },
        {
          type: 'file',
          mediaType: 'application/pdf',
          data: providerReference,
        },
      ],
    },
  ],
});
```

`uploadSkill` similarly accepts skill files as `{ path, content }` entries and returns
a provider-managed skill reference for later calls. Provider references are not
portable raw bytes; retain provider identity and lifecycle information with them.

## Images, speech, and transcription

`generateImage` is stable, as are `generateSpeech`, `transcribe`, `SpeechResult`, and
`TranscriptionResult`.

```ts
const speech = await generateSpeech({
  model: speechModel,
  text,
});

const { text: transcript } = await transcribe({
  model: transcriptionModel,
  audio,
});
```

Generated images use the same stable file-oriented representation as other generated
media. Avoid older experimental image names when the selected API line exposes the
stable API.

## Video generation

Experimental `generateVideo` is provider-agnostic and supports bounded downloads and
abort signals:

```ts
const result = await experimental_generateVideo({
  model: videoModel,
  prompt: 'A cat walking on a treadmill',
  aspectRatio: '16:9',
  abortSignal,
});
```

From 7.0.19, `inputReferences` can contain videos as well as images, enabling both
image-to-video and reference-video generation. Keep experimental naming aligned with
the installed API line and bound remote media downloads.
