# Providers, telemetry, and observability

## Provider capability additions

The `4.0.0` provider updates added:

- Cohere v2 and Cohere tool calling;
- OpenAI predicted outputs and prompt caching;
- Google Generative AI and Google Vertex AI fine-tuned models, schemas, tool choice,
  and frequency penalty;
- Google Vertex AI text embeddings; and
- Amazon Titan embeddings through Amazon Bedrock.

These are provider capabilities, not guarantees of identical behavior across every
model. Keep provider package versions compatible with the core package and pass
provider-specific options when the portable surface does not express a feature.

## Provider integrations

The `4.1.0` line added a dedicated OpenAI-compatible provider and first-party
integrations for:

- Replicate;
- Fireworks;
- Together AI;
- DeepInfra;
- DeepSeek; and
- Cerebras.

Google Vertex AI 2.0 added search grounding, and the OpenAI provider added support for
newer reasoning models. An OpenAI-compatible endpoint can share a protocol shape
without sharing every native OpenAI behavior, so test streaming, tools, structured
output, usage, and error mapping against the actual endpoint.

## Portable reasoning control

`generateText` and `streamText` accept a top-level `reasoning` value that maps to each
provider's native reasoning controls:

```ts
await generateText({
  model,
  prompt,
  reasoning: 'high',
});
```

Use top-level `reasoning` when the application needs portable intent. Keep
`providerOptions` for settings that have no portable equivalent or require exact
provider semantics.

## Global telemetry (`2026-07`)

`registerTelemetry` installs a process-level integration for:

- model calls;
- generation steps;
- tool calls;
- embeddings;
- reranking; and
- agents.

OpenTelemetry support lives in `@ai-sdk/otel`:

```ts
import { OpenTelemetry } from '@ai-sdk/otel';
import { generateText, registerTelemetry } from 'ai';

registerTelemetry(new OpenTelemetry());

await generateText({
  model,
  prompt,
  runtimeContext: {
    userId: 'user_123',
  },
  telemetry: {
    functionId: 'research-agent',
    includeRuntimeContext: {
      userId: true,
    },
  },
  onStepEnd({ stepNumber, usage }) {
    recordStep(stepNumber, usage);
  },
});
```

Runtime context and tool context are excluded from telemetry unless explicitly
selected. This is a data-boundary feature: opt in only the fields that are safe and
useful to export. Never assume that placing secrets in scoped context automatically
makes every custom instrumentation integration safe; audit the integration too.

## Lifecycle callbacks and tracing-channel events

Calls expose consistent `onStart`, `onStepEnd`, and `onEnd` lifecycle hooks for
operation-level and step-level observation. Use these stable hooks for application
metrics, usage recording, and cleanup.

Instrumentation packages can also subscribe to structured events through the Node.js
`ai:telemetry` tracing channel. Prefer that channel for reusable instrumentation that
must observe SDK activity without wrapping each call. Keep observer failure isolated
from application correctness, and redact prompt, context, tool input, and output data
according to the application's privacy policy.
