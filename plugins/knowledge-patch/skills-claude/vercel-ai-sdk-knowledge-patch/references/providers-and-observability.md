# Providers, Telemetry, and Observability

## Provider capabilities added in 4.0

Provider support includes these additions from 4.0.0:

- Cohere v2 and tool calling.
- OpenAI predicted outputs and prompt caching.
- Google Generative AI and Google Vertex AI fine-tuned models, schemas, tool choice,
  and frequency penalty.
- Google Vertex AI text embeddings.
- Amazon Titan embeddings through Bedrock.

## Provider integrations added in 4.1

Version 4.1.0 adds a dedicated OpenAI-compatible provider and first-party integrations
for Replicate, Fireworks, Together AI, DeepInfra, DeepSeek, and Cerebras. Google Vertex
AI 2.0 adds search grounding, and the OpenAI provider supports the then-latest reasoning
models.

## Anthropic computer-use tools

The Anthropic provider supplies versioned Computer, Text Editor, and Bash tools for
Claude 3.5 Sonnet. The application must implement each tool's `execute` behavior.
Convert results to text or image content with `experimental_toToolResultContent`, use
`maxSteps` for multi-action runs, and isolate this beta capability from sensitive data,
preferably in a virtual machine. (since 4.0.0)

```ts
const computer = anthropic.tools.computer_20241022({
  displayWidthPx: 1920,
  displayHeightPx: 1080,
  execute: async ({ action, coordinate, text }) =>
    action === 'screenshot'
      ? { type: 'image', data: getScreenshot() }
      : executeComputerAction(action, coordinate, text),
  experimental_toToolResultContent: result =>
    typeof result === 'string'
      ? [{ type: 'text', text: result }]
      : [{ type: 'image', data: result.data, mimeType: 'image/png' }],
});

await generateText({
  model: anthropic('claude-3-5-sonnet-20241022'),
  prompt: 'Move the cursor to the center and take a screenshot.',
  tools: { computer },
  maxSteps: 10,
});
```

## Portable and provider-native reasoning controls

`generateText` and `streamText` accept top-level `reasoning`, which maps to native
provider reasoning controls. Keep `providerOptions` when the application needs a
provider-specific setting that the portable option does not expose. (since 2026-07)

```ts
await generateText({ model, prompt, reasoning: 'high' });
```

## Global telemetry

Register one global integration with `registerTelemetry` for model calls, steps, tools,
embeddings, reranking, and agents. OpenTelemetry support lives in `@ai-sdk/otel`.
Runtime and tool context is excluded unless explicitly selected; export only safe
fields. (since 2026-07)

```ts
registerTelemetry(new OpenTelemetry());

await generateText({
  model,
  prompt,
  runtimeContext: { userId: 'user_123' },
  telemetry: {
    functionId: 'research-agent',
    includeRuntimeContext: { userId: true },
  },
});
```

## Lifecycle and tracing events

Use portable `onStart`, `onStepEnd`, and `onEnd` hooks for call lifecycle handling.
Instrumentation packages can instead subscribe to structured events on the Node.js
`ai:telemetry` tracing channel. Telemetry covers model, step, tool, embedding,
reranking, and agent operations. (since 2026-07)

Language-model-call end callbacks and their telemetry spans expose provider metadata.
(since 2026-08)

## Cartesia audio models

The Cartesia provider supports Sonic 3.5 speech generation, Ink-Whisper batch
transcription, and Ink 2 realtime transcription. (since 2026-08)

## Batch APIs

Batch APIs are available across the core, provider, gateway, and provider-utility
layers. (since 2026-08)
