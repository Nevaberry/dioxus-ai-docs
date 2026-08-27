# Vector Search and GenAI

## Hi-Fidelity Quantized Vector Search

### Configure HFQ per index (2026.06.0)

Preview Hi-Fidelity Quantized Vector Search expands a search over quantized
vectors, then reranks candidates against full-precision vectors. Enable its
quantization type and default expansion factor in the index configuration:

```cypher
CREATE VECTOR INDEX moviePlots IF NOT EXISTS
FOR (m:Movie)
ON m.embedding
OPTIONS {indexConfig: {
  `vector.quantization.type`: 'binary',
  `vector.default_search_expansion_factor`: 2.0,
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}}
```

An existing index must be rebuilt to use HFQ. Treat the feature as preview and
retain the full-precision vectors required for reranking.

## Cypher vector search

### Filter `SEARCH` with `IN` (2026.06.0)

Cypher 25 vector-search filter predicates accept `IN`:

```cypher
MATCH (movie:Movie)
SEARCH movie IN (
  VECTOR INDEX moviePlots
  FOR $queryVector
  WHERE movie.genre IN ['Horror', 'SciFi']
  LIMIT $topK
)
RETURN movie.title AS title, movie.rating AS rating
```

### Replace vector procedures

In Cypher 25, use the `SEARCH` clause instead of deprecated
`db.index.vector.queryNodes()` and
`db.index.vector.queryRelationships()`.

Two older procedures are removed; use their explicit replacements:

```text
db.index.vector.createNodeIndex() -> CREATE VECTOR INDEX
db.create.setVectorProperty() -> db.create.setNodeVectorProperty()
```

## Vector import

### Keep delimiter roles distinct (2026.06.0)

For `neo4j-admin database import`, the `--vector-delimiter` character must
differ from both `--delimiter` and `--quote`. Validate all three options
together before starting a large import.

### Read native Parquet vectors (2026.06.0)

The importer can read vector values directly from native Parquet list types;
an intermediate delimited-string representation is unnecessary.

## GenAI endpoint configuration

### Override the Azure OpenAI base URL (2026.04.0)

The GenAI plugin recognizes `GENAI_AZURE_OPENAI_BASE_URL` and uses it as the
base URL for `ai.text` calls. Set it when traffic must target a non-default
endpoint.

## Token utilities

### Chunk and estimate input (2026.04.0)

The GenAI plugin provides:

- `ai.text.chunkByTokenLimit` to split input into chunks within a token limit.
- `ai.text.countToken` to estimate an input's token count.

Use the estimator before a call when only sizing is needed, and the chunker
when each output segment must stay under a processing limit.

## File-based embedding batches

### Embed local or remote file content (2026.05.0)

`ai.file.embedBatch` reads text from a local or remote file and generates
embeddings. It can optionally split the input into chunks. The procedure
returns one row per chunk with:

- the chunk index,
- the chunk content,
- the embedding vector.

Preserve the returned index if downstream storage needs to reconstruct source
order.
