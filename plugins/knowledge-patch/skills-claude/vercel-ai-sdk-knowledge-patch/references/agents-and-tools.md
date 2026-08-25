# Agents, Tools, and Control Loops

## Stop agent loops deliberately

`ToolLoopAgent` defaults to `isStepCount(20)`. It evaluates `stopWhen` after a step
that produced tool results, and an array of conditions uses OR semantics. A typed
custom condition can inspect every prior step. A loop also ends when the model finishes
without tool calls, a called tool has no `execute`, or a call requires approval.

`isLoopFinished()` removes the step cap and relies on natural completion; use it only
when that is safe.

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

## Reconfigure each step

`prepareStep` runs before each generation. It receives the current `model`, zero-based
`stepNumber`, prior `steps`, outgoing `messages`, and runtime context. It can override
the model, messages, `activeTools`, `toolChoice`, and individual model-call settings;
return `{}` to preserve the initial configuration. (model-call setting overrides
since 2026-08)

`ToolLoopAgent.prepareCall` can also inspect and override the call-level `reasoning`
option. (since 2026-08)

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

## Force explicit completion

Combine `toolChoice: 'required'` with a terminal tool that has no `execute`. Every step
then uses a tool, and the loop ends when the terminal tool is called. Read its typed
payload from `staticToolCalls`.

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

## Type agent outputs and UI messages

An agent can declare `output: Output.object(...)` in its constructor so
`generate().output` is schema-validated and statically inferred. Use
`InferAgentUIMessage<typeof agent>` to carry its tool and output types into UI and
persistence, and `createAgentUIStreamResponse` to adapt UI messages on a server route.

```ts
const agent = new ToolLoopAgent({
  model,
  output: Output.object({
    schema: z.object({ summary: z.string(), score: z.number() }),
  }),
});

export type AgentMessage = InferAgentUIMessage<typeof agent>;
return createAgentUIStreamResponse({ agent, uiMessages: messages });
```

Constructor and call-level lifecycle callbacks compose. If both register the same
callback, the constructor callback runs first.

## Separate orchestration and tool context

`runtimeContext` carries typed orchestration state through step preparation,
approvals, callbacks, telemetry, and agents. A tool can declare `contextSchema`; pass
its private configuration through `toolsContext`, and the validated `context` is
exposed only to that tool. (since 2026-07)

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

## Use tool execution context

The second argument to `execute` contains `toolCallId`, the complete conversation
`messages`, and the request `abortSignal`. Use these for per-call annotations,
conversation-aware execution, and cancellation. (since 4.1.0)

```ts
const weather = tool({
  parameters: z.object({ location: z.string() }),
  execute: async ({ location }, { toolCallId, messages, abortSignal }) => {
    console.log({ toolCallId, messageCount: messages.length });
    const response = await fetch(`/weather?q=${location}`, { signal: abortSignal });
    return response.json();
  },
});
```

## Repair tool calls and distinguish failures

`repairToolCall` can replace an invalid call or return `null` to decline repair. The
earlier `experimental_repairToolCall` spelling was introduced in 4.1.0 and remains a
deprecated alias. Distinguish `NoSuchToolError`, `InvalidToolArgumentsError`,
`ToolExecutionError`, and `ToolCallRepairError` instead of treating all failures as
equivalent. The stable option name applies since 2026-08.

```ts
const result = await generateText({
  model,
  tools,
  prompt,
  repairToolCall: async ({ toolCall, error }) => {
    if (NoSuchToolError.isInstance(error)) return null;
    return { ...toolCall, args: JSON.stringify(await repairArguments(toolCall)) };
  },
});
```

## Replay approvals

An approval-gated call does not suspend generation. The first call returns with
`tool-approval-request` content. Preserve `result.response.messages`, append matching
`tool-approval-response` parts in a `tool` message, and call the model again. A denial
is also replayed so the model can react.

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

At call level, `toolApproval` can require user approval, decide automatically, or run
a typed policy. For higher-risk flows, use HMAC-signed approvals and revalidate tool
input and policy during replay. (since 2026-07)

## Handle runtime-defined tools

`dynamicTool` represents a runtime-defined tool whose input and output types are not
known at compile time. Validate or cast its input at runtime. Mixed static and dynamic
call/result unions expose `dynamic` for narrowing without weakening static tools.

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

## Stream tool progress and input

An `execute` callback may return an `AsyncIterable`, typically from an async generator.
Every yielded value except the last is preliminary; the final value becomes the tool
result.

```ts
const report = tool({
  inputSchema,
  async *execute(input) {
    yield { status: 'loading' as const };
    yield { status: 'complete' as const, value: await buildReport(input) };
  },
});
```

`onInputStart`, `onInputDelta`, and `onInputAvailable` observe argument generation.
`onInputStart` now runs before `onInputAvailable` for non-streaming calls too;
`onInputDelta` remains streaming-only. (ordering since 2026-08)

```ts
const weather = tool({
  inputSchema,
  onInputStart: () => markStarted(),
  onInputDelta: ({ inputTextDelta }) => appendInput(inputTextDelta),
  onInputAvailable: ({ input }) => recordValidated(input),
  execute: getWeather,
});
```

## Serialize multimodal tool results

Returning media from `execute` does not send it back to the model. Define
`toModelOutput` to convert the runtime result into model content. This route remains
experimental and provider-dependent; inline media is safer than assuming remote URLs
are supported.

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

## Bound execution with timeouts and sandboxes

Generation and agent calls support total, per-step, idle-chunk, default-tool, and
per-tool timeout budgets. Streaming calls also support `firstChunkMs`; see the stream
reference for its constraints. Timeout aborts are represented by `TimeoutError`.
(since 2026-07)

A supplied `SandboxSession` reaches tools as `experimental_sandbox` and supports
working directories, environment values, streaming output, and abort signals.

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

## Choose durable workflows or harnesses

`WorkflowAgent` from `@ai-sdk/workflow` persists between steps so execution can survive
restarts, deployments, interruptions, and delayed approvals. It supports streaming,
tools, approvals, callbacks, runtime and tool context, and provider model serialization
across workflow boundaries. (since 2026-07)

```ts
const agent = new WorkflowAgent({
  model,
  tools,
  runtimeContext: { userId: 'user_123' },
});
```

Experimental `HarnessAgent` exposes an external agent runtime through the standard
`Agent` interface. Its runs can receive a sandbox, instructions, skills, and tools;
sessions and interrupted turns can be resumed. (since 2026-07)

## Apply default instructions or code-mode routing

`defaultInstructionsMiddleware` supplies default language-model instructions while
preserving instructions passed by an individual call. (since 2026-08)

Experimental code mode can route `generateText` through `experimental_toolCaller`.
`streamText` and `ToolLoopAgent` also support experimental tool callers, with a
simplified configuration available from 7.0.50. (since 2026-08)
