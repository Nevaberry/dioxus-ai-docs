# Generation, Structured Output, and Media

## Long and multi-step text generation

Since 4.0.0, `generateText` and `streamText` can automatically continue output that
ended at the length limit. Set `experimental_continueSteps: true` together with
`maxSteps`. The SDK joins the steps and reports combined token usage. Streaming emits
only complete words and may trim trailing tokens at continuation boundaries.

```ts
const result = await generateText({
  model,
  prompt: 'Write a long-form history of Rome.',
  maxSteps: 5,
  experimental_continueSteps: true,
});
```

## Structured output with tools

Since 4.1.0, `generateText` and `streamText` can use tools and finish with one
schema-validated structured result in a multi-step run. In the 4.1 API this combination
was limited to OpenAI models and used `experimental_output`; v7-targeted code uses the
stable `output` name.

```ts
const result = await generateText({
  model: openai('gpt-4o', { structuredOutputs: true }),
  prompt,
  tools,
  maxSteps: 5,
  output: Output.object({
    schema: z.object({ answer: z.string() }),
  }),
});
```

When object parsing or validation fails, `NoObjectGeneratedError` preserves the raw
generated `text`, response metadata, token `usage`, and underlying `cause`. Inspect
these fields before choosing whether to repair, retry, or salvage a partial value.

```ts
try {
  await generateObject({ model, schema, prompt });
} catch (error) {
  if (error instanceof NoObjectGeneratedError) {
    console.log(error.text, error.response, error.usage, error.cause);
  }
}
```

The 2026-07 structured-output behavior uses stricter JSON Schema post-processing for
Zod and Standard Schema inputs. Malformed JSON extraction and repair work for both
structured outputs and tool calls. Array output mode preserves schema transforms,
coercions, defaults, and pipes.

As of 2026-08, `repairText` is the stable repair option on `generateObject` and
`streamObject`; `experimental_repairText` is a deprecated compatibility alias.

## PDF message parts

Since 4.0.0, compatible Anthropic, Google Generative AI, and Google Vertex AI models
accept PDFs as `file` parts. Pass bytes as `data` with
`mimeType: 'application/pdf'`; the same message shape works across these providers.

```ts
const result = await generateText({
  model,
  messages: [{
    role: 'user',
    content: [
      { type: 'text', text: 'Summarize this document.' },
      {
        type: 'file',
        data: readFileSync('./document.pdf'),
        mimeType: 'application/pdf',
      },
    ],
  }],
});
```

## Reusable files and skills

`uploadFile` (2026-07) uploads data once and returns a provider reference that can be
reused as a `file` part instead of resending bytes. `uploadSkill` similarly uploads a
provider-managed skill from `{ path, content }` file entries and returns a reference
for later calls.

```ts
const { providerReference } = await uploadFile({
  api: provider.files(),
  data: await readFile('./brief.pdf'),
  filename: 'brief.pdf',
});

await streamText({
  model,
  messages: [{
    role: 'user',
    content: [
      { type: 'text', text: 'Summarize this brief.' },
      { type: 'file', mediaType: 'application/pdf', data: providerReference },
    ],
  }],
});
```

Canonical `file` parts (2026-07) can contain inline data, URLs, provider references,
or text-backed content. Generated images use stable `generateImage`; the stable media
APIs also include `generateSpeech`, `transcribe`, `SpeechResult`, and
`TranscriptionResult`.

The 2026-08 API deprecates the image-specific `Experimental_GeneratedImage` type in
favor of the general `GeneratedFile` type.

## Transcription and speech

Awaiting any result promise on `experimental_streamTranscribe` (2026-08) consumes the
stream internally, so `await result.text` resolves without separately draining
`fullStream`. The full stream has exactly one consumer and no replay buffer. When both
incremental parts and final values are needed, access and consume `fullStream` before
awaiting a result promise.

`Experimental_SpeechTranslationModelV4` and `experimental_streamTranslate` (2026-08)
add streaming speech-to-speech translation.

Cartesia support (2026-08) includes Sonic 3.5 speech generation, Ink-Whisper batch
transcription, and Ink 2 realtime transcription.

## Video generation

Experimental `generateVideo` (2026-07) provides provider-independent video generation
with abort support and bounded downloads. From 7.0.19, `inputReferences` can include
video references as well as images for reference-to-video generation.

```ts
const result = await experimental_generateVideo({
  model: videoModel,
  prompt: 'A cat walking on a treadmill',
  aspectRatio: '16:9',
});
```

The 2026-08 asynchronous interface lets `VideoModelV4` implement `doStart`,
`doStatus`, and `handleWebhookOption`. `experimental_generateVideo` can orchestrate
completion through `poll` or `webhook`; polling may provide a custom delay function
for durable workflows. Providers that support it can accept
`aspectRatio: 'adaptive'` and derive the ratio from reference media.

```ts
await experimental_generateVideo({
  model,
  prompt,
  aspectRatio: 'adaptive',
});
```

## Batch operations

Batch APIs are available as of 2026-08 across the core, provider, gateway, and
provider-utility layers. Select the layer that owns the model operation and preserve
provider-specific configuration when the shared abstraction does not expose it.
