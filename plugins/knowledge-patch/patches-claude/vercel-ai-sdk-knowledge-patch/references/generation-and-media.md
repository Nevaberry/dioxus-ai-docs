# Generation, Structured Output, and Media

## Send PDFs as file parts

Anthropic, Google Generative AI, and Google Vertex AI models accept PDF bytes as a
`file` part with `mimeType: 'application/pdf'`. The same message shape works across
those providers. (since 4.0.0)

```ts
const result = await generateText({
  model: anthropic('claude-3-5-sonnet-20241022'),
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

## Continue length-limited text

Set `experimental_continueSteps: true` together with `maxSteps` on `generateText` or
`streamText`. When a step reaches the length limit, the SDK continues, joins the steps,
and reports combined token usage. Streaming emits only complete words and may trim
trailing tokens at step boundaries. (since 4.0.0)

```ts
const result = await generateText({
  model,
  prompt: 'Write a long-form history of Rome.',
  maxSteps: 5,
  experimental_continueSteps: true,
});
```

## Combine tools with structured output

`generateText` and `streamText` can execute tools and finish with a schema-validated
output in one multi-step call. The capability was introduced as `experimental_output`
in 4.1.0 and was then limited to OpenAI models; the current v7 option is `output`.

```ts
const result = await generateText({
  model,
  prompt,
  tools,
  output: Output.object({
    schema: z.object({ answer: z.string() }),
  }),
});
```

## Diagnose structured-output failures

`NoObjectGeneratedError` retains the raw generated `text`, response metadata, token
`usage`, and underlying `cause`. Inspect these before retrying or salvage a partial
result when appropriate. (since 4.1.0)

```ts
try {
  await generateObject({ model, schema, prompt });
} catch (error) {
  if (error instanceof NoObjectGeneratedError) {
    console.log(error.text, error.response, error.usage, error.cause);
  }
}
```

JSON Schema post-processing is stricter for Zod and Standard Schema inputs. Malformed
JSON extraction and repair apply to structured outputs and tool calls. Array output
mode preserves schema transforms, coercions, defaults, and pipes. (since 2026-07)

Use the stable `repairText` option on `generateObject` and `streamObject` rather than
the deprecated `experimental_repairText` alias. (since 2026-08)

## Reuse provider-managed files and skills

`uploadFile` sends data once and returns a provider reference that can be reused in a
`file` part. `uploadSkill` does the same for provider-managed skills, accepts files as
`{ path, content }` entries, and returns a reference for later calls. (since 2026-07)

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

Canonical `file` parts can hold inline data, URLs, provider references, or text-backed
content. (since 2026-07)

## Generate speech and transcribe audio

`generateSpeech`, `transcribe`, `SpeechResult`, and `TranscriptionResult` are stable
APIs. (since 2026-07)

```ts
const speech = await generateSpeech({ model: speechModel, text });
const { text: transcript } = await transcribe({
  model: transcriptionModel,
  audio,
});
```

Awaiting any result promise from `experimental_streamTranscribe` now consumes its
stream internally, so `await result.text` does not require separately draining
`fullStream`. There is one consumer and no replay buffer: access `fullStream` before a
result promise when both incremental parts and final values are needed. (since 2026-08)

`Experimental_SpeechTranslationModelV4` and `experimental_streamTranslate` provide
experimental streaming speech-to-speech translation. (since 2026-08)

## Use the general generated-file type

`Experimental_GeneratedImage` is deprecated. Use the more general `GeneratedFile`
type. (since 2026-08)

## Generate video asynchronously

Experimental `generateVideo` provides provider-agnostic video generation with abort
support and bounded downloads. Video reference inputs are supported in addition to
images from 7.0.19. (since 2026-07)

`VideoModelV4` can implement `doStart`, `doStatus`, and `handleWebhookOption`.
`experimental_generateVideo` can wait through `poll` or `webhook`; polling may inject
a custom delay implementation for durable workflows. Provider-specific calls may use
`aspectRatio: 'adaptive'` when the model derives the ratio from reference media.
(since 2026-08)

```ts
await experimental_generateVideo({
  model,
  prompt: 'A cat walking on a treadmill',
  aspectRatio: 'adaptive',
});
```
