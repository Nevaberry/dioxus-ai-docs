---
name: vercel-ai-sdk-knowledge-patch
description: Vercel AI SDK 6.0 compatibility. Use for Vercel AI SDK work.
license: MIT
version: "6.0"
metadata:
  author: Nevaberry
---

# Vercel AI SDK Knowledge Patch

Use this skill when implementing or reviewing TypeScript applications built with the
`ai` package, AI SDK UI, provider packages, agents, workflows, or `@ai-sdk/mcp`.
Start with the breaking-change notes, then load the topic reference that matches the
work. Preserve provider-specific options when a top-level abstraction does not expose
the required capability.

## Reference index

| Reference | Topics |
| --- | --- |
| [migrations.md](references/migrations.md) | Runtime requirements, codemods, renamed APIs, deprecations, and result semantics |
| [agents-and-tools.md](references/agents-and-tools.md) | Agent loops, step control, tools, approvals, timeouts, workflows, and harnesses |
| [generation-and-media.md](references/generation-and-media.md) | Text streams, structured output, PDFs, files, images, speech, transcription, and video |
| [mcp-and-runtimes.md](references/mcp-and-runtimes.md) | MCP transports, schemas, resources, prompts, elicitation, apps, drift, and managed assets |
| [providers-and-observability.md](references/providers-and-observability.md) | Provider capabilities, integrations, reasoning controls, telemetry, and lifecycle events |
| [ui-and-streams.md](references/ui-and-streams.md) | `useChat`, persistence, data streams, direct agent transport, approvals, and realtime UI |

## Breaking changes first

### Runtime and modules

When targeting the v7 API line:

- Require Node.js 22 or newer.
- Use ESM imports; CommonJS `require()` is unsupported.
- Upgrade `ai` and every provider package together.
- Run `npx @ai-sdk/codemod v7`, then review semantic changes manually.

The earlier 4.0 migration also removed deprecated APIs. Its codemods cover much of the
mechanical work, but they do not eliminate the need to follow the migration guide.

### Renamed APIs

For v7-targeted code, use the current names:

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

System messages placed directly in `prompt` or `messages` require
`allowSystemInMessages: true`. Tool-level `needsApproval`, result-instance response
methods, and Vue's `Chat` class are deprecated; prefer call-level `toolApproval`,
top-level response helpers, and `useChat`.

### Multi-step result scope

Top-level multi-step results accumulate `content`, tool calls and results, files,
sources, warnings, and usage across the whole run. Use `finalStep` when only the last
step is relevant. Request and response bodies are no longer retained unless explicitly
requested.

```ts
const totalUsage = await result.usage;
const finalStep = await result.finalStep;
console.log(totalUsage, finalStep.usage);
```

## Agent control quick reference

### Stop conditions

`ToolLoopAgent` defaults to `isStepCount(20)`. `stopWhen` is evaluated after a step
that produced tool results; arrays use OR semantics. A loop also stops on a normal
finish without tool calls, a tool without `execute`, or an approval-required call.
Use `isLoopFinished()` only when natural completion is safe without a step cap.

```ts
const agent = new ToolLoopAgent({
  model,
  tools,
  stopWhen: [isStepCount(50), hasToolCall('publish')],
});
```

### Reconfigure each step

`prepareStep` receives the current model, zero-based `stepNumber`, prior `steps`,
outgoing `messages`, and runtime context. It can replace the model or messages and
restrict `activeTools` or `toolChoice`; return `{}` to keep constructor settings.

For explicit completion, combine `toolChoice: 'required'` with a terminal tool that
has no `execute`. The terminal payload remains available through `staticToolCalls`.

### Typed outputs and UI

Declare `output: Output.object(...)` on the agent for a validated, inferred
`generate().output`. Derive persisted and rendered chat types with
`InferAgentUIMessage<typeof agent>`, and serve them with
`createAgentUIStreamResponse`.

Constructor-level and call-level lifecycle callbacks compose. If both define the same
callback, the constructor callback runs first; the call callback does not replace it.

### Context boundaries

Use `runtimeContext` for typed orchestration state shared across step preparation,
approvals, callbacks, telemetry, and agents. Use a tool's `contextSchema` plus
`toolsContext` for private, tool-scoped configuration; only that tool receives its
validated `context`.

### Approvals are return and replay

An approval request ends the current generation. Preserve `result.response.messages`,
append matching `tool-approval-response` parts in a `tool` message, and invoke the
model again. Call-level `toolApproval` can require a user decision, decide
automatically, or use a typed policy. Use signed approvals and revalidate input and
policy when replay crosses a trust boundary.

## Tool execution quick reference

- `execute(input, context)` can read `toolCallId`, conversation `messages`, and the
  request `abortSignal`.
- `dynamicTool` keeps static inference for known tools while exposing `dynamic: true`
  for runtime-defined calls that need validation or casting.
- An async-generator `execute` streams preliminary values; its last value is the final
  tool result.
- `onInputStart` and `onInputDelta` observe streamed argument construction;
  `onInputAvailable` receives validated complete input in both streaming and
  non-streaming generation.
- Media returned by `execute` does not automatically reach the model. Implement
  `toModelOutput`, preferably with inline media bytes where provider URL support is
  uncertain.
- Use `experimental_repairToolCall` to replace malformed calls or return `null` to
  decline repair. Distinguish `NoSuchToolError`, `InvalidToolArgumentsError`,
  `ToolExecutionError`, and `ToolCallRepairError`.

Generation and agents accept total, step, idle-chunk, default-tool, and per-tool
timeouts. Timeout aborts surface as `TimeoutError`. A supplied `SandboxSession` reaches
tools as `experimental_sandbox` and supports working directories, environment values,
streaming output, and abort signals.

Use `WorkflowAgent` when execution must survive restarts, deployments, interruptions,
or delayed approvals. Use `HarnessAgent` to expose an external agent runtime through
the standard `Agent` interface, including resumable sessions and interrupted turns.

## Streaming and structured output quick reference

`streamText` starts immediately but progresses under consumer backpressure: always
consume a returned stream. Streaming generation failures arrive through `onError` or
an in-band `error` part; tool failures become `tool-error` parts. Non-streaming schema
and generation failures still throw.

Stream transforms run in order before callbacks and result promises. A transform that
calls `stopStream` must emit synthetic `finish-step` and `finish` events so downstream
consumers complete. Exceptions in experimental lifecycle observer hooks are swallowed
and do not fail generation.

For structured output:

- Agents can own an `Output.object` schema directly.
- Text generation can combine tools with a final validated output in a multi-step run.
- `NoObjectGeneratedError` retains raw text, response metadata, usage, and cause.
- Array mode preserves transforms, coercions, defaults, and pipes.
- JSON extraction and repair can recover malformed structured output and tool calls.

## UI and transport quick reference

`useChat` supports client-to-server chat IDs, server-assigned response message IDs,
and `appendResponseMessages` for persistence. `createDataStreamResponse` can emit
custom data and message annotations before or alongside generation; merge a
`streamText` result with `mergeIntoDataStream`.

`DirectChatTransport` connects `useChat` directly to an `Agent` without a separate
route transport. UI flows can submit approval responses automatically, use async
`sendAutomaticallyWhen` conditions, and preserve provider metadata across streams and
turns. Experimental realtime hooks normalize browser WebSocket sessions, ephemeral
tokens, audio transcription, client tools, and `UIMessage[]` state.

## MCP quick reference

Create MCP clients from `@ai-sdk/mcp`. Prefer HTTP for deployments and stdio only for
local servers. Keep the client open through generation and close it afterward. The
lightweight adapter does not provide session management, resumable streams, or
notification reception.

Passing `schemas` to `client.tools()` limits discovery to named tools and adds typed
inputs. An `outputSchema` validates `structuredContent`, falls back to JSON parsed from
text, and throws when neither yields a valid value. Without one, execution returns the
raw `CallToolResult`.

Treat resources as application-selected context and prompts as user-selected server
templates. Elicitation requires both an advertised capability and a registered handler
that returns `accept`, `decline`, or `cancel`.

Before exposing remotely described tools, persist a trusted `fingerprintTools`
snapshot and compare later definitions with `detectToolDrift`. The application owns
snapshot storage and the policy for detected drift.

## Media and provider quick reference

- Compatible providers accept PDF bytes as a `file` message part with
  `mimeType: 'application/pdf'`.
- `uploadFile` and `uploadSkill` create reusable provider references instead of
  resending bytes or skill files.
- `generateSpeech`, `transcribe`, `SpeechResult`, `TranscriptionResult`, and
  `generateImage` are stable APIs.
- Canonical `file` parts may contain inline data, URLs, provider references, or
  text-backed content.
- Experimental video generation supports aborts and bounded downloads; reference
  inputs can include images and video.
- Top-level `reasoning` provides portable reasoning effort while `providerOptions`
  remains available for provider-specific controls.

Register one global telemetry integration with `registerTelemetry`. OpenTelemetry lives
in `@ai-sdk/otel`. Runtime and tool context is excluded unless explicitly selected;
include only fields safe to export. Use `onStart`, `onStepEnd`, and `onEnd` for portable
lifecycle handling, or subscribe instrumentation to the Node.js `ai:telemetry` tracing
channel for structured events.

## Implementation checklist

1. Confirm the target API line before choosing renamed or experimental symbols.
2. Bound every agent loop and long-running tool with stop rules, timeouts, and aborts.
3. Consume streams and handle their in-band error parts.
4. Persist complete response messages before replaying approvals.
5. Validate runtime-defined tools, MCP outputs, and remotely supplied tool definitions.
6. Keep secrets in tool-scoped context and opt telemetry fields in deliberately.
7. Use durable workflows for operations that must survive process boundaries.
