# Providers, Reasoning, and Observability

## Provider capabilities

The 4.0.0 provider line added:

- Cohere v2 and Cohere tool calling.
- OpenAI predicted outputs and prompt caching.
- Google Generative AI and Google Vertex AI fine-tuned models, schemas, tool choice,
  and frequency penalty.
- Google Vertex AI text embeddings.
- Amazon Titan embeddings through Bedrock.

The 4.1.0 line added a dedicated OpenAI-compatible provider and first-party
integrations for Replicate, Fireworks, Together AI, DeepInfra, DeepSeek, and Cerebras.
Google Vertex AI 2.0 added search grounding, and the OpenAI provider added the then
latest reasoning models.

Preserve provider-specific options whenever the shared API does not expose a required
capability.

## Portable reasoning control

`generateText` and `streamText` accept top-level `reasoning` (2026-07), which maps a
portable reasoning setting to provider-native controls. Continue using
`providerOptions` for capabilities that cannot be expressed portably.

```ts
await generateText({
  model,
  prompt,
  reasoning: 'high',
});
```

A `ToolLoopAgent.prepareCall` callback can read and override the top-level reasoning
setting for an individual model call as of 2026-08.

## Global telemetry

`registerTelemetry` (2026-07) installs one integration for model calls, steps, tools,
embeddings, reranking, and agents. OpenTelemetry support lives in `@ai-sdk/otel`.
Runtime and tool context is excluded by default; include only selected fields that are
safe to export.

```ts
import { OpenTelemetry } from '@ai-sdk/otel';
import { generateText, registerTelemetry } from 'ai';

registerTelemetry(new OpenTelemetry());

await generateText({
  model,
  prompt,
  runtimeContext: { userId: 'user_123' },
  telemetry: {
    functionId: 'research-agent',
    includeRuntimeContext: { userId: true },
  },
  onStepEnd({ stepNumber, usage }) {
    recordStep(stepNumber, usage);
  },
});
```

Portable lifecycle callbacks include `onStart`, `onStepEnd`, and `onEnd`.
Instrumentation packages can also subscribe to structured events through the Node.js
`ai:telemetry` tracing channel.

## Observer hooks and failures

Experimental `experimental_onStart`, `experimental_onStepStart`,
`experimental_onToolCallStart`, and `experimental_onToolCallFinish` observe operation,
step, and tool execution boundaries. Exceptions thrown from these observer hooks are
caught and do not interrupt generation; report hook failures through a separate
monitoring path when they matter.

```ts
await generateText({
  model,
  prompt,
  tools,
  experimental_onToolCallFinish({ toolName, durationMs, error }) {
    recordToolRun({ toolName, durationMs, error });
  },
});
```

## Provider metadata

As of 2026-08, language-model-call end callbacks and their telemetry spans expose
provider metadata. Treat that metadata as provider-defined, validate before depending
on its shape, and apply the same redaction policy used for other telemetry fields.
