---
name: vercel-ai-sdk-knowledge-patch
description: Vercel AI SDK
version: "6.0"
license: MIT
metadata:
  author: Nevaberry
---


# Vercel AI SDK Knowledge Patch

Use this skill for TypeScript applications built with the `ai` package, AI SDK UI,
provider packages, agents, workflows, generated media, or `@ai-sdk/mcp`. Confirm the
application's installed core and provider versions before applying version-dependent
names. Start with migrations and breaking changes, then load the topic reference for
the work at hand.

## Reference index

| Reference | Topics |
| --- | --- |
| [migrations.md](references/migrations.md) | Runtime requirements, migration, renamed APIs, deprecations, and result semantics |
| [agents-and-tools.md](references/agents-and-tools.md) | Agent loops, tools, approvals, timeouts, workflows, harnesses, and code-mode routing |
| [generation-and-media.md](references/generation-and-media.md) | Text and object generation, files, images, speech, transcription, video, and batches |
| [mcp-and-runtimes.md](references/mcp-and-runtimes.md) | MCP clients, schemas, resources, prompts, apps, elicitation, and drift detection |
| [providers-and-observability.md](references/providers-and-observability.md) | Provider capabilities, integrations, reasoning controls, telemetry, and lifecycle data |
| [ui-and-streams.md](references/ui-and-streams.md) | `useChat`, persistence, data streams, direct transport, approvals, realtime, and stream errors |

## Breaking changes first

### Runtime and packages

For the v7 API line, require Node.js 22 or newer and ESM imports. CommonJS
`require()` is unsupported. Upgrade `ai` and every provider package together, run the
codemod, and manually review semantic changes:

```sh
npx @ai-sdk/codemod v7
```

Version 4.0 also removed deprecated APIs. Its codemods handle much of the mechanical
migration, but consult the migration guide for manual work.

### Current names and deprecations

Use these names in v7-targeted code:

| Earlier name | Current name |
| --- | --- |
| `system` option | `instructions` |
| `onFinish` | `onEnd` |
| `StreamTextResult.fullStream` | `StreamTextResult.stream` |
| `experimental_customProvider` | `customProvider` |
| `experimental_generateImage` | `generateImage` |
| `experimental_output` | `output` |
| `experimental_prepareStep` | `prepareStep` |
| `experimental_telemetry` | `telemetry` |
| `experimental_repairToolCall` | `repairToolCall` |
| `experimental_repairText` | `repairText` |
| `Experimental_GeneratedImage` | `GeneratedFile` |

The repair options retain deprecated experimental aliases. System messages embedded
in `prompt` or `messages` require `allowSystemInMessages: true`. Tool-level
`needsApproval`, result-instance response methods, and Vue's `Chat` class are
deprecated; use call-level `toolApproval`, top-level response helpers, and `useChat`.

### Multi-step result scope

Top-level multi-step results accumulate `content`, tool calls and results, files,
sources, warnings, and usage for the whole run. Use `finalStep` for last-step-only
values. Request and response bodies are retained only when explicitly requested.

```ts
const totalUsage = await result.usage;
const finalStep = await result.finalStep;
console.log(totalUsage, finalStep.usage);
```

## Agent control quick reference

### Bound every loop

`ToolLoopAgent` defaults to `isStepCount(20)`. `stopWhen` runs after a step that
produced tool results, and arrays have OR semantics. A loop also stops after normal
completion without tool calls, a tool call with no `execute`, or an approval request.
Use `isLoopFinished()` only when uncapped natural completion is intentional.

```ts
const agent = new ToolLoopAgent({
  model,
  tools,
  stopWhen: [isStepCount(50), hasToolCall('publish')],
});
```

### Reconfigure steps and calls

`prepareStep` sees the current model, zero-based `stepNumber`, previous `steps`,
outgoing `messages`, and runtime context. It may replace the model or messages,
restrict `activeTools`, choose tools, and override per-call settings; return `{}` to
retain constructor settings. `ToolLoopAgent.prepareCall` can inspect and override the
top-level `reasoning` setting.

For explicit completion, combine `toolChoice: 'required'` with a terminal tool that
has no `execute`. Read its typed payload from `staticToolCalls`.

### Typed state and output

Declare `output: Output.object(...)` on an agent for validated, inferred
`generate().output`. Derive UI and persistence types with
`InferAgentUIMessage<typeof agent>` and serve them with
`createAgentUIStreamResponse`.

Use `runtimeContext` for typed orchestration state shared across preparation,
approvals, callbacks, telemetry, and agents. Use a tool's `contextSchema` with
`toolsContext` for private, tool-scoped values; only that tool receives validated
`context`.

Constructor-level and call-level lifecycle callbacks compose. When both define the
same callback, the constructor callback runs first.

### Approvals return, then replay

Approval does not suspend generation. Preserve `result.response.messages`, append
matching `tool-approval-response` parts in a `tool` message, then invoke generation
again. Call-level `toolApproval` can request user review, decide automatically, or use
a typed policy. Sign approvals and revalidate input and policy when replay crosses a
trust boundary.

## Tool execution quick reference

- `execute(input, context)` can read `toolCallId`, conversation `messages`, the
  request `abortSignal`, scoped `context`, and an optional sandbox session.
- `dynamicTool` retains static inference for known tools while marking runtime-loaded
  calls and results with `dynamic: true`; validate or cast their unknown values.
- An async-generator `execute` streams preliminary values; its last value is final.
- `onInputStart` runs before validated `onInputAvailable` in streaming and
  non-streaming calls; `onInputDelta` observes streaming argument chunks.
- Media returned from `execute` does not automatically reach the model. Implement
  `toModelOutput`, favoring inline bytes when provider URL support is uncertain.
- Use `repairToolCall` to replace malformed calls or return `null`; distinguish
  `NoSuchToolError`, `InvalidToolArgumentsError`, `ToolExecutionError`, and
  `ToolCallRepairError`.

Generation and agents accept total, step, first-content, idle-chunk, default-tool, and
per-tool timeouts. Timeouts surface as `TimeoutError`; first-content and idle-chunk
budgets apply only to streaming. A supplied `SandboxSession` reaches tools as
`experimental_sandbox` and supports working directories, environment values,
streaming output, and abort signals.

Use `WorkflowAgent` when execution must survive restarts, deployments,
interruptions, or delayed approvals. Use experimental `HarnessAgent` to adapt an
external runtime to the standard `Agent` interface and resume sessions or interrupted
turns.

## Streaming and structured output quick reference

`streamText` begins immediately but advances under consumer backpressure. Always
consume a returned stream. Generation errors arrive through `onError` or in-band
`error` parts; tool failures become `tool-error` parts. Non-streaming schema and
generation failures still throw. Await response-piping helpers to catch both stream
read and write errors.

Transforms run in order before callbacks and result promises. A transform that calls
`stopStream` must emit synthetic `finish-step` and `finish` events. Exceptions in
experimental lifecycle observer hooks are swallowed and do not fail generation.

For structured results:

- Agents can own an `Output.object` schema.
- Text generation can combine tools with a final validated output in a multi-step run.
- `NoObjectGeneratedError` preserves raw text, response metadata, usage, and cause.
- Array mode preserves transforms, coercions, defaults, and pipes.
- JSON extraction and repair can recover malformed structured output and tool calls.

## UI and MCP quick reference

`useChat` can send client chat IDs, receive server-assigned response message IDs, and
persist with `appendResponseMessages`. `createDataStreamResponse` emits custom data
and annotations before or beside generation; merge `streamText` with
`mergeIntoDataStream`. `DirectChatTransport` connects `useChat` directly to an agent.

Create MCP clients with `@ai-sdk/mcp`. Prefer HTTP in deployments and stdio locally.
Keep the client open through generation and close it afterward. Passing `schemas` to
`client.tools()` limits discovery and types inputs. An `outputSchema` validates
`structuredContent`, falls back to JSON parsed from text, and throws if neither is
valid; without it the tool returns raw `CallToolResult`.

Treat MCP resources as application-selected context and prompts as user-selected
templates. Elicitation requires an advertised capability and a handler returning
`accept`, `decline`, or `cancel`. Before exposing remotely described tools, persist a
trusted `fingerprintTools` snapshot and compare later definitions with
`detectToolDrift`.

## Media, providers, and telemetry quick reference

- Compatible providers accept PDFs as `file` message parts with
  `mimeType: 'application/pdf'`.
- `uploadFile` and `uploadSkill` create reusable provider references.
- `generateSpeech`, `transcribe`, `SpeechResult`, `TranscriptionResult`, and
  `generateImage` are stable; canonical `file` parts support bytes, URLs, provider
  references, or text content.
- Streaming transcription has one consumer: read `fullStream` before awaiting result
  promises when both incremental and final values are required.
- Experimental video supports aborts, bounded downloads, image and video references,
  polling or webhooks, durable polling delays, and provider-specific adaptive ratios.
- Top-level `reasoning` supplies portable effort control; keep `providerOptions` for
  provider-specific settings.

Register one telemetry integration with `registerTelemetry`; OpenTelemetry is in
`@ai-sdk/otel`. Runtime and tool context is excluded unless explicitly selected.
Portable lifecycle hooks are `onStart`, `onStepEnd`, and `onEnd`; Node.js
instrumentation can subscribe to the `ai:telemetry` tracing channel. Include only
context fields safe to export.

## Implementation checklist

1. Confirm the installed API line before selecting stable, deprecated, or
   experimental names.
2. Bound loops and long-running tools with stop rules, timeouts, and abort signals.
3. Consume streams, await piping helpers, and handle in-band failures.
4. Persist complete response messages before replaying approvals.
5. Validate runtime-defined tools, MCP outputs, and remotely supplied definitions.
6. Keep secrets in tool-scoped context and opt telemetry fields in deliberately.
7. Use durable workflows for operations that must survive process boundaries.
