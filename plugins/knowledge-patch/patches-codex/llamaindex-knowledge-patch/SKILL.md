---
name: llamaindex-knowledge-patch
description: LlamaIndex
version: null
license: MIT
metadata:
  author: Nevaberry
---


# LlamaIndex Knowledge Patch

Use this skill when writing, reviewing, migrating, or debugging Python code that
uses LlamaIndex core, ingestion, storage, retrieval, agents, workflows, or its
separately versioned integrations.

Inspect the application's installed distributions and lockfile before applying
package-specific advice. The umbrella package, core, workflows, and integrations
do not necessarily share a distribution version.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Agents and workflows](references/agents-and-workflows.md) | Agent selection, handlers, memory, events, concurrency, state, resources, validation, AG-UI |
| [Ingestion and storage](references/ingestion-and-storage.md) | Pipelines, caches, document updates, persistence, retrieval, parsers, graph extraction, vector stores |
| [Migration and packaging](references/migration-and-packaging.md) | Core API migration, dependency coordination, Python and Pydantic changes, model and tool integrations |

## First Checks

Before changing code:

1. Inspect the versions of `llama-index`, `llama-index-core`, and every
   `llama-index-*` integration actually imported by the application.
2. Preserve and review the resolved lockfile; never infer integration versions
   from the core version.
3. Identify whether persistence includes local stores, a remote vector store,
   or both.
4. Determine whether each ingestion run is a complete source inventory or only
   a partial crawl before enabling deletion behavior.
5. Treat agent and workflow runs as asynchronous, streamable executions.
6. Re-run ingestion, retrieval, agent, and workflow integration tests after an
   upgrade.

## Breaking Migration Priorities

### Replace removed configuration abstractions

Do not construct `ServiceContext` or `LLMPredictor`. Set process-wide defaults
through `Settings`, or pass LLMs, embedding models, and transformations directly
when multiple configurations must coexist.

```python
from llama_index.core import Settings

Settings.llm = llm
Settings.embed_model = embed_model
```

Audit custom readers, nodes, parsers, tools, models, validators, serialization,
and integrations for Pydantic v2 behavior.

### Coordinate package upgrades

Upgrade a coherent dependency set rather than changing core alone or forcing
every distribution to the same version. Respect each distribution's metadata,
including its Python floor, and preserve the resolved environment.

```python
from importlib.metadata import version

core_version = version("llama-index-core")
starter_version = version("llama-index")
```

### Redesign obsolete agent code

Use the workflow-based agent imports. Older agent, runner, and worker examples
do not describe the current execution model.

```python
from llama_index.core.agent.workflow import (
    AgentWorkflow,
    FunctionAgent,
    ReActAgent,
)
```

Choose `FunctionAgent` only when the configured LLM provides compatible native
tool calling. Use `ReActAgent` for text-based reasoning and action parsing, or
`CodeActAgent` for code-action scenarios.

### Redesign pipelines as workflows

A workflow is not a renamed `QueryPipeline`. Model the control flow with typed
events, asynchronous `@step` methods, branches, loops, `Context`, streaming, and
checkpoint-aware execution.

Use `llama_index.core.workflow` inside core applications. Standalone workflow
applications may use the `llama-index-workflows` distribution and import from
`workflows`.

## Agent and Workflow Quick Reference

### Keep and await the handler

`agent.run(...)` and `workflow.run(...)` return awaitable handlers. Keep the
handler, consume its event stream if needed, and await that same object for the
final result.

```python
handler = agent.run("What is 12 times 34?")
async for event in handler.stream_events():
    ...
result = await handler
```

### Create memory explicitly

Create `Memory` with `Memory.from_defaults` and pass it to `run`. Conversation
history and memory blocks are distinct from workflow `Context`, which carries
per-run execution state and events.

```python
from llama_index.core.memory import Memory

memory = Memory.from_defaults(session_id="session-123", token_limit=40000)
response = await agent.run("...", memory=memory)
```

### Separate state from resources

Store serializable per-run state through the asynchronous `ctx.store`
get/set/edit interface. Supply clients, indexes, models, and configuration as
workflow resources so dependency injection and validation do not mistake live
objects for checkpointable state.

### Validate event graphs

Call `workflow.validate()` in tests or during startup to detect missing
start/stop paths, events without consumers or producers, and dead ends.

```python
workflow = RagFlow(timeout=60)
workflow.validate()
```

For dynamic fan-out, emit work with `Context.send_event` and join it with
`Context.collect_events`. Do not assume results arrive in input order.

## Ingestion and Persistence Quick Reference

### Own updates through an ingestion pipeline

`VectorStoreIndex.from_documents` is convenient, but use `IngestionPipeline`
when the application needs transformation caching, document update strategy,
or direct vector-store insertion.

Stable `document.doc_id` and `node.ref_doc_id` values drive hash-based duplicate,
update, and deletion detection. A deletion strategy that removes absent
documents is safe only when the run is an authoritative inventory.

### Treat caches and document state separately

An ingestion cache keys reuse by the node-plus-transformation combination.
Persisted cache state is separate from docstore state; saving one does not save
the other.

```python
pipeline.persist("./pipeline-state")
pipeline.load("./pipeline-state")
```

Ensure custom transformations expose stable serialized settings or hashes so a
behavior change cannot silently reuse stale output.

### Choose the correct execution path

Use `pipeline.arun()` in asynchronous code. `num_workers` enables process-based
parallelism for suitable synchronous transformations; provider clients and
non-picklable transformations may make it invalid or slower.

```python
nodes = await pipeline.arun(documents=documents, num_workers=4)
```

### Verify the whole persistence boundary

`index.storage_context.persist()` saves local stores, not necessarily the
external vector collection. A remote collection alone can also omit node text,
mappings, or document state. Confirm that both sides exist, use a compatible
embedding configuration, and select the expected index ID when a directory
contains multiple indexes.

```python
from llama_index.core import StorageContext, load_index_from_storage

index.storage_context.persist(persist_dir="./storage")
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)
```

Rebuild or explicitly verify persisted vector indexes whenever the embedding
model or its configuration changes.

## Upgrade Regression Checklist

After changing packages or configuration, verify:

- all derived nodes for a re-ingested document are present;
- zero-valued retrieval thresholds remain effective;
- omitted metadata-filter conjunctions behave as AND;
- tool schemas exclude variadic parameters from required fields;
- structured agent outputs honor the configured callback and output class;
- streaming memory writes retain every block and populate response text;
- citation fragments have distinct identities and usable offsets;
- parser node counts and boundaries match the application's expectations;
- remote metadata retains falsy values and pre-existing properties;
- asynchronous reranking, graph extraction errors, and multimodal input follow
  the application's chosen behavior.

Consult the topic references for the exact package releases and edge cases
behind these checks.
