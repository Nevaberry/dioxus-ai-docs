# Agents, tools, and control loops

## Tool-loop termination

`ToolLoopAgent` defaults to `isStepCount(20)`. It evaluates `stopWhen` after a step
that produced tool results. When `stopWhen` is an array, any matching condition stops
the loop. A typed custom `StopCondition` can inspect all prior steps and their usage.

```ts
const overBudget: StopCondition<typeof tools> = ({ steps }) =>
  steps.reduce(
    (total, step) =>
      total +
      (step.usage.inputTokens ?? 0) +
      (step.usage.outputTokens ?? 0),
    0,
  ) > 20_000;

const agent = new ToolLoopAgent({
  model,
  tools,
  stopWhen: [isStepCount(50), hasToolCall('publish'), overBudget],
});
```

The loop can also end when:

- the model finishes without producing a tool call;
- a called tool has no `execute` function; or
- a tool call requires approval.

`isLoopFinished()` removes the step cap and relies on natural completion. Use it only
when the tools, model behavior, timeout budget, and external side effects make an
unbounded step count acceptable.

## Per-step reconfiguration

`prepareStep` runs before each generation. It receives the current `model`, a
zero-based `stepNumber`, previous `steps`, and outgoing `messages`; runtime context is
also available when configured. It can override the model or messages and narrow
`activeTools` or `toolChoice`. Returning `{}` keeps the initial settings.

```ts
const agent = new ToolLoopAgent({
  model,
  tools: { search, summarize },
  prepareStep: ({ stepNumber }) =>
    stepNumber < 3
      ? { activeTools: ['search'], toolChoice: 'required' }
      : { activeTools: ['summarize'], toolChoice: 'required' },
});
```

## Explicit terminal tools

To force every step through a tool, set `toolChoice: 'required'` and add a terminal
tool without `execute`. Emitting that tool ends the loop, and its inferred payload is
available in `staticToolCalls`:

```ts
const agent = new ToolLoopAgent({
  model,
  toolChoice: 'required',
  tools: {
    search,
    done: tool({
      description: 'Finish and return the answer',
      inputSchema: z.object({ answer: z.string() }),
    }),
  },
});

const result = await agent.generate({ prompt });
const call = result.staticToolCalls[0];
if (call?.toolName === 'done') console.log(call.input.answer);
```

## Structured agent results

Declare output on the agent to make `generate().output` validated and statically
typed. This avoids a separate structured-generation call:

```ts
const agent = new ToolLoopAgent({
  model,
  output: Output.object({
    schema: z.object({ summary: z.string(), score: z.number() }),
  }),
});

const { output } = await agent.generate({ prompt });
```

## Lifecycle callback composition

Constructor callbacks and callbacks passed to `generate()` or `stream()` compose. If
the same lifecycle callback exists in both places, the constructor callback executes
first and the call-level callback executes second. Do not expect the call-level value
to override the constructor value.

The experimental observer hooks `experimental_onStart`,
`experimental_onStepStart`, `experimental_onToolCallStart`, and
`experimental_onToolCallFinish` observe operation, step, and tool boundaries.
Exceptions thrown by these hooks are caught and do not interrupt generation, so they
must not be used for correctness-critical enforcement.

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

## Runtime and tool-scoped context

`runtimeContext` carries typed orchestration state through step preparation,
approvals, callbacks, telemetry, and agent execution. It is shared orchestration state,
not automatically exported telemetry data.

A tool can declare a separate `contextSchema`. Supply its private configuration under
that tool's key in `toolsContext`; only the selected tool receives the validated value
as `context`:

```ts
const agent = new ToolLoopAgent({
  model,
  runtimeContext: { audience: 'developers' },
  prepareStep: ({ runtimeContext }) => ({
    instructions: `Write for ${runtimeContext.audience}.`,
  }),
  tools: {
    weather: tool({
      inputSchema: z.object({ city: z.string() }),
      contextSchema: z.object({ apiKey: z.string() }),
      execute: ({ city }, { context }) => getWeather(city, context.apiKey),
    }),
  },
  toolsContext: {
    weather: { apiKey: process.env.WEATHER_API_KEY! },
  },
});
```

Prefer tool-scoped context for credentials and private integration configuration.

## Tool execution context

Since `4.1.0`, the second argument of a tool's `execute` callback includes
`toolCallId`, the complete conversation `messages`, and the request `abortSignal`.
Use it for call-specific annotations, conversation-aware behavior, and cancellation
propagation:

```ts
const weather = tool({
  parameters: z.object({ location: z.string() }),
  execute: async ({ location }, { toolCallId, messages, abortSignal }) => {
    annotate(toolCallId, messages.length);
    const response = await fetch(`/weather?q=${location}`, {
      signal: abortSignal,
    });
    return response.json();
  },
});
```

## Tool-call repair and typed failures

`experimental_repairToolCall` receives the invalid call and its error. Return a
replacement call to retry with repaired arguments, or `null` to decline repair.

```ts
const result = await generateText({
  model,
  tools,
  prompt,
  experimental_repairToolCall: async ({ toolCall, error }) => {
    if (NoSuchToolError.isInstance(error)) return null;
    const args = await repairArguments(toolCall);
    return { ...toolCall, args: JSON.stringify(args) };
  },
});
```

Handle the failure classes separately where recovery differs:

- `NoSuchToolError`
- `InvalidToolArgumentsError`
- `ToolExecutionError`
- `ToolCallRepairError`

## Approval return and replay

An approval-gated tool does not suspend `generateText` or `streamText`. The first call
ends with `tool-approval-request` content. Preserve its response messages, append
matching `tool-approval-response` parts in a `tool` message, and call generation again.
An approved replay executes the tool; a denial is exposed to the model.

```ts
const approvals: ToolApprovalResponse[] = [];

for (const part of result.content) {
  if (part.type === 'tool-approval-request') {
    approvals.push({
      type: 'tool-approval-response',
      approvalId: part.approvalId,
      approved: true,
    });
  }
}

messages.push(
  ...result.response.messages,
  { role: 'tool', content: approvals },
);

await generateText({ model, tools, messages });
```

At the call or agent level, `toolApproval` can map each tool to user approval,
automatic policy, or a typed decision function. For high-risk or durable flows, use
HMAC-signed approvals and revalidate both tool input and policy during replay.

```ts
await generateText({
  model,
  tools: { deleteFile },
  toolApproval: { deleteFile: 'user-approval' },
  prompt: 'Remove stale temporary files.',
});
```

## Runtime-defined tools

`dynamicTool` represents tools whose input and output types are unavailable at compile
time. Validate or cast their input at runtime. Mixed unions of static and dynamic
calls/results expose a `dynamic` flag, preserving inference for known tools:

```ts
const custom = dynamicTool({
  description: 'Run a runtime-loaded action',
  inputSchema: schemaLoadedAtRuntime,
  execute: async input => runValidated(input),
});

for (const call of result.toolCalls) {
  if (call.dynamic) handleUnknownInput(call.input);
  else handleStaticCall(call);
}
```

## Streaming tool progress

A tool's `execute` can return an `AsyncIterable`, usually via an async generator.
Every yielded value except the last is preliminary; the final yielded value is the
final tool result.

```ts
const report = tool({
  inputSchema,
  async *execute(input) {
    yield { status: 'loading' as const };
    const value = await buildReport(input);
    yield { status: 'complete' as const, value };
  },
});
```

## Tool input hooks

Tools can observe argument construction with:

- `onInputStart`, when streamed argument generation begins;
- `onInputDelta`, for each `inputTextDelta`; and
- `onInputAvailable`, after complete input passes validation.

The start and delta hooks run only with `streamText`. `generateText` invokes only the
complete-input hook.

```ts
const weather = tool({
  inputSchema,
  onInputStart: () => markStarted(),
  onInputDelta: ({ inputTextDelta }) => appendInput(inputTextDelta),
  onInputAvailable: ({ input }) => recordValidated(input),
  execute: getWeather,
});
```

## Model-facing multimedia results

Returning an image or other media object from `execute` is not enough to make it part
of the next model input. Implement `toModelOutput` to serialize the runtime result into
model content. This route is experimental and provider-dependent; inline media data is
safer than assuming a remote media URL is supported.

```ts
const screenshot = tool({
  inputSchema,
  execute: async () => ({ data: await captureScreen() }),
  toModelOutput: ({ output }) => ({
    type: 'content',
    value: [
      { type: 'media', data: output.data, mediaType: 'image/png' },
    ],
  }),
});
```

## Computer-use tools

The Anthropic provider supplies versioned Computer, Text Editor, and Bash tools for
Claude 3.5 Sonnet. The application must implement each tool's `execute`
behavior. Use `experimental_toToolResultContent` to serialize runtime results as text
or image content, and configure `maxSteps` for multi-action runs.

Computer use is a beta, high-risk capability. Isolate it from sensitive data and run
it in a constrained environment, preferably a virtual machine.

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
```

## Timeout budgets and sandbox sessions

Generation and agent calls accept timeout budgets for the whole call, each step, idle
stream chunks, the default tool duration, and individual tools. Timeout aborts are
represented by `TimeoutError`.

```ts
await generateText({
  model,
  timeout: {
    totalMs: 60_000,
    stepMs: 10_000,
    chunkMs: 2_000,
    toolMs: 5_000,
    tools: { runCommandMs: 15_000 },
  },
  prompt,
});
```

A supplied `SandboxSession` reaches tool execution as `experimental_sandbox`. It
supports portable commands, working directories, environment variables, output
streaming, and abort signals:

```ts
await generateText({
  model,
  experimental_sandbox: sandbox,
  tools: {
    runCommand: tool({
      inputSchema: z.object({ command: z.string() }),
      execute: ({ command }, { experimental_sandbox }) =>
        experimental_sandbox!.run({ command }),
    }),
  },
  prompt,
});
```

## Durable workflows

`@ai-sdk/workflow` provides `WorkflowAgent`. It persists execution between steps so a
long-running agent can survive restarts, deployments, interruptions, and delayed
approvals. Streaming, tools, approvals, callbacks, runtime and tool context, and
provider model serialization all work across workflow boundaries.

```ts
import { WorkflowAgent } from '@ai-sdk/workflow';

const agent = new WorkflowAgent({
  model,
  tools,
  runtimeContext: { userId: 'user_123' },
});
```

## External harnesses

Experimental `HarnessAgent` adapts an established agent runtime to the standard
`Agent` interface. Its `generate`, `stream`, UI chat, and workflow integrations return
normal SDK results. Harness runs can receive a sandbox, instructions, skills, and
tools; sessions and interrupted turns can be resumed.

```ts
import { HarnessAgent } from '@ai-sdk/harness/agent';

const agent = new HarnessAgent({
  harness,
  sandbox,
  instructions,
  skills,
  tools,
});
```
