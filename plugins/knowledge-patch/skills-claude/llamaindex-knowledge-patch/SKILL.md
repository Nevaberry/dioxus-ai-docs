---
name: llamaindex-knowledge-patch
description: LlamaIndex
version: null
license: MIT
metadata:
  author: Nevaberry
---


# LlamaIndex Knowledge Patch

Use this skill when writing, reviewing, migrating, or debugging LlamaIndex
applications. Inspect the application's installed distributions and lockfile
before applying package-specific advice because core and integration packages
are released independently.

Prefer project code, installed-package metadata, and tests when they disagree
with this guidance. Load only the reference files relevant to the current task.

## Reference index

| Reference | Topics |
| --- | --- |
| [API migrations](references/api-migrations.md) | Configuration, Pydantic v2, coordinated upgrades, and workflow migration |
| [Agents and workflows](references/agents-workflows.md) | Agent selection, handlers, memory, concurrency, state, resources, and validation |
| [Ingestion and storage](references/ingestion-storage.md) | Persistence, caching, upserts, deletion, parsing, and graph extraction |
| [Retrieval and citations](references/retrieval-citations.md) | MMR filters, async reranking, citation identity, and spans |
| [Package integrations](references/package-integrations.md) | Model adapters, protocols, vector stores, client compatibility, and optional dependencies |

## Breaking migrations first

### Replace removed configuration abstractions

Do not build new code around `ServiceContext` or `LLMPredictor`. Use `Settings`
for process-wide defaults, or pass the LLM, embedding model, and transformations
directly when configurations must coexist.

```python
from llama_index.core import Settings

Settings.llm = llm
Settings.embed_model = embed_model
```

Audit custom readers, nodes, output parsers, tools, models, validators,
serialization, and integrations for Pydantic v2 behavior.

### Upgrade the package family coherently

Do not assign one release number to every `llama-index-*` distribution. Resolve
core and integrations together under their actual independent versions and
constraints, test the resulting environment, and preserve its lockfile.

```python
from importlib.metadata import version

core_version = version("llama-index-core")
starter_version = version("llama-index")
```

The v0.12 transition drops Python 3.8. Check each selected distribution's
metadata because newer packages may require a later interpreter.

### Redesign legacy pipelines as workflows

A workflow is not a renamed `QueryPipeline` DAG. Model control flow with typed
events, asynchronous `@step` methods, branches or loops, `Context`, streaming,
and checkpointable execution. Use `llama_index.core.workflow` inside core
applications; standalone workflow applications can use the `workflows` import
surface from `llama-index-workflows`.

### Treat current agent execution as asynchronous

Import current workflow agents from `llama_index.core.agent.workflow`. A call to
`agent.run(...)` or `workflow.run(...)` returns an awaitable handler, not a
finished response. Keep that handler if live events are needed, then await the
same object for the final result.

```python
handler = agent.run("What is 12 times 34?")
async for event in handler.stream_events():
    ...
result = await handler
```

Legacy provider-specific agent, runner, and worker examples do not describe
this execution model.

## Ingestion and persistence quick reference

### Own document updates explicitly

Use `IngestionPipeline` when an application needs transformation caching,
document update strategies, or direct vector-store insertion.
`VectorStoreIndex.from_documents` remains useful for simple construction, but
it does not replace an explicit update lifecycle.

Stable `document.doc_id` and `node.ref_doc_id` values drive duplicate, update,
and deletion decisions. A strategy that deletes records absent from the input
requires a complete authoritative inventory; do not apply it to a partial
crawl.

### Keep pipeline cache and document state distinct

Cache identity includes both a node and its transformation. A custom
transformation whose behavior changes without changing its stable serialized
settings or hash can reuse stale output.

```python
pipeline.persist("./pipeline-state")
pipeline.load("./pipeline-state")
```

This cache is separate from docstore state. Use `pipeline.arun()` for async
execution. Use process-based `num_workers` only when transformations and client
objects are picklable and multiprocessing is actually beneficial.

### Verify both sides of persisted indexes

`StorageContext.persist()` saves local stores; it does not necessarily copy an
external vector collection. The remote collection may likewise lack node text,
mappings, or document state held locally.

```python
from llama_index.core import StorageContext, load_index_from_storage

index.storage_context.persist(persist_dir="./storage")
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)
```

On restore, verify the remote collection, embedding compatibility, and expected
index ID. Rebuild or explicitly validate persisted vector indexes after an
embedding model or embedding configuration change.

## Agents and workflows quick reference

### Select agents by tool interface

Use `FunctionAgent` when the selected LLM provides compatible native tool
calling, `ReActAgent` for text-parsed reasoning and actions, and `CodeActAgent`
for code-action scenarios. Plain synchronous or asynchronous callables can be
tools; type hints and docstrings define their schemas. Use `FunctionTool` when
metadata or adaptation must be explicit.

```python
from llama_index.core.agent.workflow import FunctionAgent

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

agent = FunctionAgent(tools=[multiply], llm=llm)
```

### Separate memory, run state, and resources

Create conversation `Memory` explicitly and pass it to `run`. Keep per-run,
serializable execution state in asynchronous `ctx.store`; inject live clients,
indexes, models, and configuration as workflow resources rather than placing
them in checkpointable state.

```python
from llama_index.core.memory import Memory

memory = Memory.from_defaults(session_id="session-123", token_limit=40000)
response = await agent.run("...", memory=memory)
```

For dynamic fan-out, emit work with `Context.send_event` and join with
`Context.collect_events`; completion order may differ from input order. Call
`workflow.validate()` in tests or at startup to catch invalid typed event
graphs before execution.

## Upgrade verification checklist

After changing core, integrations, embeddings, agents, or workflows:

1. Resolve actual package constraints and retain the lockfile.
2. Run ingestion against representative new, updated, and deleted documents.
3. Reload persistence with the real external vector collection available.
4. Exercise synchronous and asynchronous retrieval and reranking paths.
5. Stream agent or workflow events and await the final handler result.
6. Validate workflow graphs and checkpoint only serializable run state.
7. Recheck node counts, boundaries, citation identities, and metadata values.
8. Pin integration defaults that must not drift with package upgrades.
