# API migrations

## Configuration after the v0.11 removals

`ServiceContext` and `LLMPredictor` are removed. Use `Settings` for shared
process defaults, or pass LLM, embedding, and transformation objects directly
to the component that owns them. Direct injection is safer when multiple
configurations coexist in one process.

```python
from llama_index.core import Settings

Settings.llm = llm
Settings.embed_model = embed_model
```

Core officially uses Pydantic v2. Audit custom readers, nodes, output parsers,
tools, models, validators, serialization code, and integrations that depend on
v1 behavior instead of assuming a configuration-only migration.

## Coordinated v0.12 dependency upgrade

Every `llama-index-*` package received a release bump for this transition, but
integration distributions retain independent version numbers and core
constraints. Do not upgrade core alone, and do not force every distribution to
`0.12.0`. Resolve a coherent environment, run integration tests, and preserve
the resulting lockfile.

```python
from importlib.metadata import version

core_version = version("llama-index-core")
starter_version = version("llama-index")
```

Python 3.8 is no longer supported by the v0.12 family. Selected newer packages
may set a higher floor, so use their installed or index metadata as the source
of truth.

## Workflow migration boundary

Current workflow agents come from `llama_index.core.agent.workflow` and execute
through asynchronous handlers and events.

```python
from llama_index.core.agent.workflow import (
    AgentWorkflow,
    FunctionAgent,
    ReActAgent,
)
```

Legacy provider-specific agents and runner/worker examples are stale. Current
conversation-memory guidance favors `Memory`; `ChatMemoryBuffer`,
`ChatSummaryMemoryBuffer`, and `VectorMemory` are deprecated.

A workflow is not a mechanical rename of `QueryPipeline`. Redesign the graph
around typed Pydantic events, asynchronous `@step` methods, event branches and
loops, `Context` state, streaming, and checkpointed durable execution. Core
applications use `llama_index.core.workflow`; standalone applications may
install `llama-index-workflows` and import from `workflows`.

## Upgrade test boundary

Treat `IngestionPipeline` as the maintainable update surface when an application
needs transformation caching, document strategies, or direct vector-store
insertion. After an embedding model or configuration change, rebuild or verify
persisted vector indexes. An upgrade test should cross ingestion, retrieval,
agent, and workflow integration paths rather than testing imports alone.

Batch attribution: `llamaindex-v0.11-v0.12-api`.
