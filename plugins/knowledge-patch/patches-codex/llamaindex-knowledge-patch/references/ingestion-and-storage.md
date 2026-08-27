# Ingestion and Storage

## Use Explicit Ingestion for Maintained Indexes

`VectorStoreIndex.from_documents` remains convenient, but
`IngestionPipeline` is the maintainable surface for transformation caching,
document update strategy, and direct vector-store insertion.

Persisted vector indexes must be rebuilt or explicitly verified when the
embedding model or its configuration changes. Exercise ingestion, retrieval,
agent, and workflow integration paths after upgrades.

## Understand the Storage Boundary

`index.storage_context.persist()` saves local stores, but an external vector
store generally remains remote and may leave only auxiliary state in the
persist directory. Conversely, remote vectors alone can omit node text,
mappings, or document state.

Reloading local state does not prove that the remote collection still exists or
that it uses a compatible embedding model. When a persistence directory is
shared by multiple indexes, load the expected index ID.

```python
from llama_index.core import StorageContext, load_index_from_storage

index.storage_context.persist(persist_dir="./storage")
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)
```

Back up or reconstruct each side of this boundary deliberately.

## Keep Cache Identity Stable

Ingestion cache reuse is keyed by each node-plus-transformation combination.
Custom behavior changes that do not alter stable serialized settings or hashes
can silently reuse stale output.

Pipeline cache state can be saved and restored with `persist()` and `load()`,
but it is separate from docstore state, which manages duplicate, updated, and
deleted documents.

```python
pipeline.persist("./pipeline-state")
pipeline.load("./pipeline-state")
```

## Select Async or Process Execution Deliberately

Use `pipeline.arun()` for asynchronous execution. `num_workers` enables
process-based parallelism for suitable synchronous transformations. Provider
clients and non-picklable transformations can make process execution invalid or
slower than the single-process path.

```python
nodes = await pipeline.arun(documents=documents, num_workers=4)
```

## Require Authoritative Inputs for Deletion

When both docstore and vector store are attached, hashes keyed by stable
`document.doc_id` or `node.ref_doc_id` drive duplicate and update detection.
Any `DocstoreStrategy` mode that deletes documents absent from a run assumes the
run is a complete inventory. Applying it to a partial crawl can delete unrelated
documents.

## Ingestion and Retrieval Corrections in 0.14.24

### Preserve every upserted document node

`IngestionPipeline` upserts preserve all nodes associated with each document
instead of dropping siblings from a transformation that returns multiple nodes.
Re-ingesting a document can replace its complete derived-node set. Tests should
assert all sibling nodes, not merely one representative node.

### Honor zero thresholds and default conjunctions

MMR embedding search respects an explicit `mmr_threshold=0`.
`MetadataFilters(condition=None)` defaults to AND. Remove truthiness workarounds
for zero and avoid supplying an explicit conjunction solely to obtain AND.

## Query and Extraction Corrections in 0.14.24

### Propagate property-graph extraction errors

LLM-based property-graph path extractors accept `raise_on_error`. Enable it when
extraction failures must fail the operation rather than be silently tolerated.

### Use asynchronous reranking

`LLMRerank` implements asynchronous reranking. Async query pipelines no longer
need to force this postprocessor through its synchronous path.

### Track citation fragments independently

`CitationQueryEngine` assigns every citation node its own ID and offsets.
Consumers can distinguish and locate individual citation fragments rather than
treating all derived citations as sharing the source node's identity.

## Parser Boundary Corrections in 0.14.24

Parser output can change at edge cases:

- `CodeSplitter` preserves oversized leaf nodes.
- `HTMLNodeParser` omits empty nodes.
- `SemanticDoubleMergingSplitterNodeParser` removes stopwords using word
  tokenization.

Rebaseline any tests or downstream assumptions that depend on node counts and
boundaries after upgrading.

## Vector-Store Compatibility in 0.14.24

### Pinecone and Qdrant clients

`llama-index-vector-stores-pinecone` 0.8.1 supports client versions 8 and 9.
`llama-index-vector-stores-qdrant` 0.10.3 restores compatibility with
`qdrant-client` 1.19.0 and preserves falsy shard identifiers such as `0` in
`aquery()`.

### Falsy and pre-existing metadata

Azure AI Search indexing retains falsy node metadata values. Weaviate retrieval
exposes actual collection properties as node metadata, including for collections
that predate the LlamaIndex integration.

### Vertex AI Vector Search V2

`llama-index-vector-stores-vertexaivectorsearch` 0.5.0 broadens coverage of the
V2 API. Recheck any adapter code that previously filled gaps in V2 operations.
