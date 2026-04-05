# Migration & Breaking Changes (v5/v6)

## Key renames (v5)

| Old (v4) | New (v5+) |
|----------|-----------|
| `maxTokens` | `maxOutputTokens` |
| `CoreMessage` | `ModelMessage` |
| `Message` | `UIMessage` |
| `convertToCoreMessages()` | `convertToModelMessages()` (async in v6!) |
| `providerMetadata` (input) | `providerOptions` (input only; output still `providerMetadata`) |
| `mimeType` | `mediaType` |
| `rawResponse` | `response` |
| `reasoning` (result property) | `reasoningText` (v5); `reasoning` = details array |
| `ai/react` | `@ai-sdk/react` |
| `ai/rsc` | `@ai-sdk/rsc` |

## Provider changes (v6)

- **OpenAI**: `strictJsonSchema` defaults to `true`; `structuredOutputs` option removed from chat model
- **Azure**: `azure()` now uses Responses API by default; use `azure.chat()` for Chat Completions; providerOptions key `openai` -> `azure`
- **Anthropic**: `structuredOutputMode` option: `'auto'` (default), `'outputFormat'` (native), `'jsonTool'`
- **Google Vertex**: providerOptions/Metadata key `google` -> `vertex`
- **Embedding**: `textEmbeddingModel`/`textEmbedding` -> `embeddingModel`/`embedding`

## Other changes

- **Zod 4 required**: `zod@^4.1.8` peer dependency in AI SDK 5+
- **Codemods**: `npx @ai-sdk/codemod v5` (v4->v5), `npx @ai-sdk/codemod v6` (v5->v6)
- **Mock classes**: V2 -> V3 (`MockLanguageModelV2` -> `MockLanguageModelV3`, etc.) in `ai/test`
- **`experimental_continueSteps` removed** — use models with higher output limits
- **Finish reason `unknown` merged into `other`** (v6)
- **Warning logger**: disable with `AI_SDK_LOG_WARNINGS=false`
