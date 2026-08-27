# Migration and Packaging

## Core API Migration (`llamaindex-v0.11-v0.12-api`)

### Replace `ServiceContext` and `LLMPredictor`

Core 0.11 removes both deprecated abstractions. Use `Settings` for process-wide
defaults, or pass LLM, embedding, and transformation objects directly when
configurations coexist.

```python
from llama_index.core import Settings

Settings.llm = llm
Settings.embed_model = embed_model
```

Core also moves officially to Pydantic v2. Audit custom readers, nodes, output
parsers, tools, models, validators, serialization, and any integration that
depends on Pydantic v1 behavior.

### Coordinate the 0.12 dependency upgrade

Every `llama-index-*` distribution received a version bump for the 0.12
transition. Resolve and test one coherent environment rather than upgrading
core alone or assigning every distribution version `0.12.0`; integrations keep
independent versions and core constraints.

The release drops Python 3.8. Selected newer distributions may set a still
higher floor, so follow package metadata and preserve the resulting lockfile.

```python
from importlib.metadata import version

core_version = version("llama-index-core")
starter_version = version("llama-index")
```

### Migrate agents and workflows deliberately

Current workflow-based agents are asynchronous and imported from
`llama_index.core.agent.workflow`. Current memory guidance uses `Memory`; the
older buffer and vector memory classes are deprecated.

Workflows require a control-flow redesign rather than a `QueryPipeline` rename.
Use typed events, asynchronous steps, event branches and loops, `Context`,
streaming, and checkpointed durable execution. Core applications use
`llama_index.core.workflow`; standalone applications can use the
`llama-index-workflows` distribution and import from `workflows`.

### Move maintained updates into ingestion

Use `IngestionPipeline` when an index needs transformation caching, document
update strategy, or direct vector-store insertion. Rebuild or verify persisted
vector indexes after embedding changes, and test ingestion, retrieval, agents,
and workflows together after migration.

## Integration Releases in 0.14.24

These distributions version independently. Change only the integrations the
application uses and solve their dependency constraints as a set.

### `llama-index-llms-anthropic` 0.11.10

The integration supports the provider's generation-5 balanced model and
allowlists its generation-5 flagship model, including corrected function
calling for the balanced variant. It reports a one-million-token context window
for the provider's flagship 4.6 model.

### `llama-index-llms-bedrock-converse` 0.14.18

The integration supports the provider's generation-5 balanced model, allowlists
its generation-5 flagship model, and accepts thinking type `disabled`.

### `llama-index-llms-google-genai` 0.10.0

The library and its documentation default to the provider's 3.7 fast model.
Pin a model explicitly when the application must preserve earlier behavior.

### `llama-index-llms-openai` 0.7.10

The supported-model set includes the provider's 5.6 family, avoiding
unknown-model validation for those identifiers.

### `llama-index-tools-mcp` 0.5.0

The tooling migrates to MCP 2.x. Treat the release as a dependency and API
compatibility boundary, and test the complete tool integration when upgrading.

### Optional asynchronous AWS dependency

`llama-index-embeddings-bedrock` 0.8.3 and
`llama-index-llms-bedrock-converse` 0.14.18 make `aioboto3` optional. The base
installation no longer needs it when asynchronous AWS access is unused.

### `llama-index-llms-llama-cpp` 0.6.1

The integration reports the loaded model's effective context window. Prompt
budgeting therefore follows the actual loaded model instead of stale or nominal
metadata.
