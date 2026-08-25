# Ingestion and storage

## Understand what persistence contains

`index.storage_context.persist()` writes local stores. When the index uses an
external vector store, the persist directory may hold only auxiliary state;
the vectors generally remain remote. Conversely, the remote collection may
not contain node text, mappings, or document state held locally.

```python
from llama_index.core import StorageContext, load_index_from_storage

index.storage_context.persist(persist_dir="./storage")
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)
```

Loading local state does not prove that the external collection still exists
or that its vectors use a compatible embedding model. When a directory stores
multiple indexes, select and verify the expected index ID.

## Treat cache and docstore state separately

Ingestion cache reuse is keyed by the node-plus-transformation combination. A
custom transformation can therefore reuse stale output when its behavior
changes without a corresponding change to stable serialized settings or
hashes.

```python
pipeline.persist("./pipeline-state")
pipeline.load("./pipeline-state")
```

Persisted pipeline cache state is separate from docstore state used to detect
duplicate, updated, and deleted documents.

## Choose the appropriate execution path

Use `pipeline.arun()` for asynchronous ingestion. Setting `num_workers` enables
process-based parallelism for suitable synchronous transformations.

```python
nodes = await pipeline.arun(documents=documents, num_workers=4)
```

Provider clients and non-picklable transformations may make process workers
invalid or slower than the non-worker path.

## Apply deletion strategies only to complete inventories

When a docstore and vector store are attached, stable `document.doc_id` or
`node.ref_doc_id` values and their hashes drive duplicate and update detection.
A `DocstoreStrategy` mode that deletes documents missing from a run assumes the
run is authoritative and complete. On a partial crawl, it can delete unrelated
documents as though they were removed.

## Preserve all derived nodes during upserts

In `0.14.24`, `IngestionPipeline` upserts retain every node associated with a
document rather than dropping siblings from a multi-node transformation.
Re-ingestion can replace the document's complete derived-node set; test and
remove any compensating duplication logic.

## Propagate property-graph extraction failures

LLM-based property-graph path extractors accept `raise_on_error`. Enable it
when an extraction failure must abort processing instead of being silently
tolerated.

## Rebaseline parser edge cases

Parser corrections can change node counts and boundaries:

- `CodeSplitter` preserves oversized leaf nodes.
- `HTMLNodeParser` omits empty nodes.
- `SemanticDoubleMergingSplitterNodeParser` removes stopwords using word
  tokenization.

Re-run ingestion and retrieval checks against documents that exercise these
edge cases before accepting a stored-index migration.
