# Agents, Tools, and Control Loops

## Stop and completion rules

`ToolLoopAgent` defaults to `isStepCount(20)`. A `stopWhen` condition is evaluated
after a step that produced tool results; an array of conditions uses OR semantics. A
typed condition can inspect every prior step, including cumulative usage.

```ts
const overBudget: StopCondition<typeof tools> = ({ steps }) =>
  steps.reduce(
    (sum, step) =>
      sum + (step.usage.inputTokens ?? 0) + (step.usage.outputTokens ?? 0),
    0,
  ) > 20_000;

const agent = new ToolLoopAgent({
  model,
  tools,
  stopWhen: [isStepCount(50), hasToolCall('publish'), overBudget],
});
```

The loop can also stop when the model finishes without a tool call, a selected tool
has no `execute`, or a call requires approval. `isLoopFinished()` removes the step cap
and relies on natural completion, so use it only when that behavior is safe.

To require an explicit terminal payload, combine `toolChoice: 'required'` with a tool
that has no `execute`. The unexecuted call ends the loop and remains available through
the typed `staticToolCalls` collection.

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

## Per-step configuration

`prepareStep` runs before every generation. It receives the current `model`, a
zero-based `stepNumber`, prior `steps`, outgoing `messages`, and runtime context. It
can replace the model or messages, restrict `activeTools`, select a `toolChoice`, or
override model-call settings. Returning `{}` keeps constructor settings.

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

In 2026-08 behavior, each `prepareStep` invocation can override model-call settings,
and a `ToolLoopAgent.prepareCall` callback can inspect and replace the top-level
`reasoning` option.

`defaultInstructionsMiddleware` (2026-08) supplies default language-model
instructions without overwriting instructions provided by an individual call.

## Typed agent output and UI adaptation

An agent can declare `output: Output.object(...)` in its constructor. Its
`generate().output` is then schema-validated and statically inferred without a
separate structured-generation call.

```ts
const agent = new ToolLoopAgent({
  model,
  output: Output.object({
    schema: z.object({ summary: z.string(), score: z.number() }),
  }),
});

const { output } = await agent.generate({ prompt });
```

Use `InferAgentUIMessage<typeof agent>` to carry agent tool and output types into UI
components and persistence. Server routes can adapt UI messages with
`createAgentUIStreamResponse`.

```ts
export type AgentMessage = InferAgentUIMessage<typeof agent>;

return createAgentUIStreamResponse({ agent, uiMessages: messages });
```

Constructor and invocation lifecycle callbacks compose. If the same callback is
defined on an agent and on `generate()` or `stream()`, both run and the constructor
callback runs first.

## Runtime and tool-scoped context

`runtimeContext` (2026-07) carries typed orchestration state through step preparation,
approvals, callbacks, telemetry, and agents. For private tool configuration, declare
the tool's `contextSchema`, supply its value through `toolsContext`, and read the
validated `context` from the execution callback. Other tools do not receive it.

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
  toolsContext: { weather: { apiKey: process.env.WEATHER_API_KEY! } },
});
```

Since 4.1.0, a normal tool `execute` callback also receives the `toolCallId`, full
conversation `messages`, and request `abortSignal` as its second argument. Use them
for per-call annotations, conversation-aware behavior, and cancellation propagation.

## Approvals

Call-level `toolApproval` (2026-07) on `generateText`, `streamText`, or
`ToolLoopAgent` can require a user decision, approve automatically, or delegate to a
typed policy. For high-risk actions, use HMAC-signed approvals and revalidate both the
tool input and current policy during replay.

```ts
await generateText({
  model,
  tools: { deleteFile },
  toolApproval: { deleteFile: 'user-approval' },
  prompt: 'Remove stale temporary files.',
});
```

Approval is a return-and-replay protocol, not a suspended call. The first generation
ends with `tool-approval-request` content. Preserve `result.response.messages`, append
matching `tool-approval-response` parts in a `tool` message, and call the model again.
An approved response permits execution; a denial is exposed to the model.

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

messages.push(...result.response.messages, { role: 'tool', content: approvals });
await generateText({ model, tools, messages });
```

## Tool repair and typed failures

Since 4.1.0, invalid tool calls can be replaced by a repair callback or declined by
returning `null`. Distinguish `NoSuchToolError`, `InvalidToolArgumentsError`,
`ToolExecutionError`, and `ToolCallRepairError` instead of treating all failures as a
retry signal.

```ts
const result = await generateText({
  model,
  tools,
  prompt,
  repairToolCall: async ({ toolCall, error }) => {
    if (NoSuchToolError.isInstance(error)) return null;
    const args = await repairArguments(toolCall);
    return { ...toolCall, args: JSON.stringify(args) };
  },
});
```

The stable option name is `repairToolCall` as of 2026-08. Older code can still use
the deprecated `experimental_repairToolCall` compatibility alias.

## Dynamic, streaming, and multimodal tools

`dynamicTool` represents a runtime-loaded tool whose input and output are unknown at
compile time. Validate or cast its values at runtime. Mixed static and dynamic call or
result unions expose `dynamic` for narrowing while retaining inference for static
tools.

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

A tool `execute` function may be an async generator. Every yielded value is a
preliminary result except the last, which becomes the final result.

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

Tools expose `onInputStart`, streaming `onInputDelta`, and validated
`onInputAvailable` hooks. Earlier behavior called start and delta only under
`streamText`; since 2026-08, `onInputStart` also runs before `onInputAvailable` for
non-streaming calls. `onInputDelta` remains the per-chunk streaming observer.

Returning an image or other media from `execute` does not send it back to the model.
Define `toModelOutput` to serialize the runtime value into model content. This path is
experimental and provider-dependent, so inline bytes are safer than assuming a remote
URL can be fetched.

```ts
const screenshot = tool({
  inputSchema,
  execute: async () => ({ data: await captureScreen() }),
  toModelOutput: ({ output }) => ({
    type: 'content',
    value: [{ type: 'media', data: output.data, mediaType: 'image/png' }],
  }),
});
```

## Timeouts and sandboxes

Generation and agent calls (2026-07) support total, per-step, idle-chunk,
default-tool, and per-tool timeout budgets. Timeout aborts are represented by
`TimeoutError`. A provided `SandboxSession` is delivered to tools as
`experimental_sandbox` and supports a working directory, environment values,
streaming command output, and abort signals.

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

## Durable and external execution

`WorkflowAgent` from `@ai-sdk/workflow` (2026-07) persists execution between steps so
long-running agents can survive restarts, deployments, interruptions, and delayed
approvals. It supports streaming, tools, approvals, callbacks, runtime and tool
context, and serialization of provider models across workflow boundaries.

Experimental `HarnessAgent` (2026-07) wraps an existing agent runtime with the normal
`Agent` interface, allowing standard `generate`, `stream`, UI chat, and workflow
integration. Harness runs can receive a sandbox, instructions, skills, and tools, and
can resume sessions or interrupted turns.

## Provider computer-use tools

Since 4.0.0, the Anthropic provider offers versioned Computer, Text Editor, and Bash
tools for Claude 3.5 Sonnet. The application must implement each `execute` operation,
serialize text or image results with `experimental_toToolResultContent`, bound the
multi-action run with `maxSteps`, and isolate this beta capability from sensitive data,
preferably inside a virtual machine.

## Experimental code-mode routing

As of 2026-08, `generateText` can route code mode through
`experimental_toolCaller`. `streamText` and `ToolLoopAgent` also accept experimental
tool callers, with simplified configuration available from 7.0.50.
