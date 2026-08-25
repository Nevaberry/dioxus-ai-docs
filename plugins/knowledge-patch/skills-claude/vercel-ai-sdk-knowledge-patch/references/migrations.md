# Migration and Compatibility

## AI SDK 4.0 migration

Version 4.0 removes deprecated APIs. Use its codemods for the mechanical changes, then
follow the migration guide for changes that require manual review. (since 4.0.0)

## AI SDK 7 runtime and modules

AI SDK 7 requires Node.js 22 or newer and ESM imports. CommonJS `require()` is not
supported. Upgrade `ai` and all provider packages together, run the codemod, and then
review semantic changes manually. (since 2026-07)

```sh
npx @ai-sdk/codemod v7
```

## Current v7 names

Use these names in v7-targeted code. (since 2026-07)

| Earlier API | Current API |
| --- | --- |
| `system` option | `instructions` |
| `onFinish` | `onEnd` |
| `StreamTextResult.fullStream` | `StreamTextResult.stream` |
| `experimental_customProvider` | `customProvider` |
| `experimental_generateImage` | `generateImage` |
| `experimental_output` | `output` |
| `experimental_prepareStep` | `prepareStep` |
| `experimental_telemetry` | `telemetry` |

System messages included in `prompt` or `messages` require
`allowSystemInMessages: true`. The following patterns are deprecated:

- Tool-level `needsApproval`; use call-level `toolApproval`.
- Response methods on result instances; use top-level response helpers.
- Vue's `Chat` class; use `useChat`.

```ts
const result = streamText({
  model,
  instructions: 'Be concise.',
  allowSystemInMessages: true,
  onEnd({ usage }) {
    recordUsage(usage);
  },
});

for await (const part of result.stream) consume(part);
```

## Stable repair option names

Use `repairToolCall` with `generateText` and `streamText`, and `repairText` with
`generateObject` and `streamObject`. `experimental_repairToolCall` and
`experimental_repairText` remain deprecated compatibility aliases. (since 2026-08)

## Whole-run and final-step values

In a multi-step call, top-level `content`, tool calls, tool results, files, sources,
warnings, and usage accumulate across every step. Use `finalStep` for the last step's
values. Request and response bodies are not retained unless explicitly requested.
(since 2026-07)

```ts
const totalUsage = await result.usage;
const finalStep = await result.finalStep;
console.log({ totalUsage, finalStepUsage: finalStep.usage });
```
