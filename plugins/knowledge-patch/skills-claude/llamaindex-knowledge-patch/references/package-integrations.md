# Package integrations

## Model-adapter identifiers and defaults

Several independently versioned adapters change supported identifiers or
defaults:

- `llama-index-llms-anthropic` 0.11.10 supports `claude sonnet 5`, allowlists
  `claude opus 5`, corrects function calling for `claude sonnet 5`, and reports
  a one-million-token context window for `claude opus 4.6`.
- `llama-index-llms-bedrock-converse` 0.14.18 supports `claude sonnet 5`,
  allowlists `claude opus 5`, and accepts thinking type `disabled`.
- `llama-index-llms-google-genai` 0.10.0 uses `gemini 3.7 flash` as the library
  and documentation default. Pin the model identifier to retain older
  behavior.
- `llama-index-llms-openai` 0.7.10 recognizes `gpt-5.6` identifiers, so they no
  longer fail unknown-model validation.

## Protocol compatibility boundary

`llama-index-tools-mcp` 0.5.0 moves to MCP 2.x. Treat this as a dependency and
API compatibility boundary when upgrading an MCP tool integration.

## Vector-store client compatibility

- `llama-index-vector-stores-pinecone` 0.8.1 supports client major versions 8
  and 9.
- `llama-index-vector-stores-qdrant` 0.10.3 restores compatibility with
  `qdrant-client` 1.19.0 and preserves falsy shard identifiers such as `0` in
  `aquery()`.
- Azure AI Search indexing retains falsy node-metadata values.
- Weaviate retrieval exposes real collection properties as node metadata even
  for collections created before the integration managed them.
- `llama-index-vector-stores-vertexaivectorsearch` 0.5.0 broadens V2 API
  coverage in `VertexAIVectorStore`.

Test false, zero, and empty metadata explicitly; truthiness-based compatibility
workarounds can hide the corrected behavior.

## Optional async AWS dependency

`llama-index-embeddings-bedrock` 0.8.3 and
`llama-index-llms-bedrock-converse` 0.14.18 no longer require `aioboto3`
unconditionally. Install it only when the selected asynchronous AWS access path
needs it.

## Effective local context window

`llama-index-llms-llama-cpp` 0.6.1 reports the loaded model's effective context
window. Size prompts against that reported value instead of nominal or stale
metadata.
