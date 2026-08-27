# Migration and Compatibility

## Runtime and module migration

For the v7 API line (2026-07), require Node.js 22 or newer and ESM imports;
CommonJS `require()` is unsupported. Upgrade the core `ai` package and all provider
packages together, then run the codemod and inspect semantic changes manually:

```sh
npx @ai-sdk/codemod v7
```

Version 4.0.0 removed deprecated APIs and supplied codemods for most mechanical
changes. Codemods do not replace the manual steps in the migration guide.

## Core API names

For v7-targeted code (2026-07), apply these renames:

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

System messages inside `prompt` or `messages` require
`allowSystemInMessages: true`. Tool-level `needsApproval`, result-instance response
methods, and Vue's `Chat` class are deprecated; use call-level `toolApproval`,
top-level response helpers, and `useChat`.

The 2026-08 API stabilizes `repairToolCall` for `generateText` and `streamText`, and
`repairText` for `generateObject` and `streamObject`. The corresponding
`experimental_repairToolCall` and `experimental_repairText` options remain as
deprecated compatibility aliases. `Experimental_GeneratedImage` is also deprecated;
use the general `GeneratedFile` type.

## Multi-step result semantics

For multi-step calls (2026-07), top-level `content`, tool calls, tool results, files,
sources, warnings, and usage accumulate across the whole run. Use `finalStep` when
only the last step matters. Request and response bodies are not retained unless the
caller requests them explicitly.

```ts
const totalUsage = await result.usage;
const finalStep = await result.finalStep;

console.log({
  totalUsage,
  finalStepUsage: finalStep.usage,
});
```

Audit code that assumed top-level tool calls or usage represented only the terminal
step, and explicitly opt in wherever retained HTTP bodies are required for debugging
or compliance.
