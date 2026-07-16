# Migration and compatibility

## Upgrade procedure

### Removed deprecated APIs (`4.0.0`)

The 4.0 line removes previously deprecated APIs. Automated codemods perform most
mechanical updates, but some changes require the manual steps in the migration guide.
Run tests after the codemod and audit any provider-specific configuration it could not
rewrite.

### Runtime and package migration (`2026-07`)

The v7 API line requires Node.js 22 or newer and ESM imports. CommonJS `require()` is
unsupported. Upgrade the core `ai` package and all `@ai-sdk/*` provider packages
together, run the codemod, then review semantic changes:

```sh
npx @ai-sdk/codemod v7
```

Do not treat a successful codemod as proof that behavior is unchanged. In particular,
review system instructions, callbacks, stream iteration, approvals, multi-step result
reads, and any code that inspects raw request or response bodies.

## Core option and property renames

Use these mappings when targeting v7:

| Earlier API | v7 API | Notes |
| --- | --- | --- |
| `system` | `instructions` | Top-level generation/agent instruction option |
| `onFinish` | `onEnd` | End-of-run lifecycle callback |
| `StreamTextResult.fullStream` | `StreamTextResult.stream` | Full event stream |
| `experimental_customProvider` | `customProvider` | Stable name |
| `experimental_generateImage` | `generateImage` | Stable name |
| `experimental_output` | `output` | Stable name |
| `experimental_prepareStep` | `prepareStep` | Stable name |
| `experimental_telemetry` | `telemetry` | Stable name |

These names are target-sensitive. Existing code on an earlier API line can still use
the earlier spelling; do not mix spellings from different package generations.

## System messages

Prefer the top-level `instructions` option in v7 code. If the application intentionally
places system-role messages inside `prompt` or `messages`, it must opt in:

```ts
const result = streamText({
  model,
  instructions: 'Be concise.',
  allowSystemInMessages: true,
  messages,
  onEnd({ usage }) {
    recordUsage(usage);
  },
});
```

Without `allowSystemInMessages: true`, do not assume embedded system messages are
accepted.

## Deprecated interaction APIs

- Tool-level `needsApproval` is deprecated. Configure approval at call or agent level
  with `toolApproval`.
- Response conversion methods attached to result objects are deprecated. Use the
  corresponding top-level response helpers.
- Vue's `Chat` class is deprecated. Use `useChat`.

Approval behavior is also semantic rather than merely a rename: an approval-gated
generation returns an approval request and must be replayed with an approval response.
See [agents-and-tools.md](agents-and-tools.md#approval-return-and-replay).

## Multi-step result semantics

Top-level result fields now represent the complete run rather than only the last step.
This applies to:

- `content`
- tool calls and tool results
- files and sources
- warnings
- usage

Read `finalStep` for last-step-only values:

```ts
const totalUsage = await result.usage;
const finalStep = await result.finalStep;

console.log({
  totalUsage,
  finalStepUsage: finalStep.usage,
  finalStepContent: finalStep.content,
});
```

Code that previously interpreted top-level tool calls, content, or usage as the last
step must be updated deliberately. Request and response bodies are not retained by
default; ask for them explicitly when diagnostics require them rather than relying on
implicit retention.

## Compatibility notes for features introduced in earlier lines

The `4.1.0` line added combinations that older integrations may not account for:

- `generateText` and `streamText` can combine tool use with a final schema-validated
  result through the then-experimental output option. At introduction this combination
  was limited to OpenAI models.
- Tool execution receives a second context argument with call metadata, messages, and
  cancellation.
- Invalid tool calls can be repaired and tool failure classes can be distinguished.
- Chat persistence carries identifiers in both directions and custom data can be
  interleaved with an LLM stream.

When modernizing such code, migrate the symbol names independently from reviewing
these behaviors; a rename does not imply identical provider support.

## Migration review checklist

1. Verify Node and module format for the selected API line.
2. Keep core and provider package versions compatible.
3. Run the codemod and inspect its diff.
4. Replace renamed options, callbacks, and stream properties consistently.
5. Decide whether embedded system messages should be allowed.
6. Replace deprecated approvals, response methods, and Vue chat state.
7. Audit multi-step reads for whole-run versus final-step intent.
8. Request raw bodies only where their storage is necessary and safe.
9. Re-run streaming, approval replay, structured output, and provider integration tests.
