---
name: langchain-knowledge-patch
description: LangChain
version: 1.1.0
license: MIT
metadata:
  author: Nevaberry
---


# LangChain Knowledge Patch

Use this skill for LangChain, LangGraph, Deep Agents, provider integrations,
and MCP adapter work. Start with the quick reference, then read the topic file
that matches the task before changing code.

## Topic index

| Reference | Topics |
| --- | --- |
| [references/v1-migration.md](references/v1-migration.md) | Package split, runtime floor, JavaScript imports, content blocks, model profiles, and migration boundaries |
| [references/agents-and-tools.md](references/agents-and-tools.md) | Agent construction, middleware, structured output, tools, runtime injection, state, and model routing |
| [references/langgraph-workflows.md](references/langgraph-workflows.md) | State schemas, streaming, checkpoints, fault tolerance, draining, caching, and workflow results |
| [references/deep-agents.md](references/deep-agents.md) | Deep-agent harness, filesystem and backends, subagents, sandboxes, context storage, and CLI |
| [references/openai.md](references/openai.md) | OpenAI and Azure models, Responses API tools, continuation, compaction, reasoning, files, and caching |
| [references/anthropic.md](references/anthropic.md) | Anthropic schemas, tool execution and discovery, caching, compaction, code execution, files, and MCP |
| [references/mcp.md](references/mcp.md) | Sessions, structured results, resources, prompts, interceptors, callbacks, and elicitation |

## Breaking changes and deprecations

### Use the v1 agent entry point

`langchain.agents.create_agent` is the LangGraph-backed model/tool loop. It
supersedes deprecated `create_react_agent` from `langgraph.prebuilt`.
LangGraph otherwise preserves backward compatibility, but
`langgraph.prebuilt` is deprecated as enhanced agent functionality moves into
`langchain.agents`.

```python
from langchain.agents import create_agent

agent = create_agent(
    model="openai:gpt-5",
    tools=[get_weather],
    system_prompt="Help the user by fetching the weather in their city.",
)
```

### Account for the package split

The Python main package is limited to core abstractions. Install
`langchain-classic` for legacy APIs. Python 3.9 is unsupported; use Python
3.10 or newer.

```shell
uv pip install --upgrade langchain
uv pip install langchain-classic
```

In JavaScript, use the unscoped `langchain` package with `@langchain/core`.
Legacy chains, retrievers, indexing APIs, and community exports are in
`@langchain/classic`; for example, replace `langchain/chains` with
`@langchain/classic/chains`.

```shell
npm install langchain @langchain/core
npm install @langchain/classic
```

### Use supported custom state

Custom agent state schemas must be `TypedDict` classes extending `AgentState`.
Pydantic models and dataclasses are not accepted. Prefer middleware-owned
`state_schema` when middleware hooks or tools use the fields;
`create_agent(state_schema=...)` remains a shortcut for tool-only state.

```python
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware

class PreferencesState(AgentState):
    user_preferences: dict

class PreferencesMiddleware(AgentMiddleware):
    state_schema = PreferencesState
```

### Migrate Deep Agents backends deliberately

JavaScript `BackendProtocolV2` returns structured results with an `error`
field. `read()` returns `ReadResult.content`; `readRaw()` returns binary data
as `Uint8Array`; and `lsInfo`/`grepRaw`/`globInfo` become
`ls`/`grep`/`glob`. `adaptBackendProtocol` bridges v1 backends while the v1
interfaces remain deprecated.

In Python, construct `StateBackend()` and `StoreBackend()` directly. Factory
forms such as `backend=lambda rt: StateBackend(rt)` are deprecated.

## Agent and middleware essentials

### Select structured-output strategy inside the loop

Structured output participates in the main model/tool loop. `response_format`
can select provider-native or tool-based generation. Wrap a Pydantic schema in
`ToolStrategy` to request tool calling.

```python
from langchain.agents.structured_output import ToolStrategy

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[weather_tool],
    response_format=ToolStrategy(WeatherReport),
)
```

Use `ToolStrategy.handle_errors` in Python or `handleErrors` in JavaScript to
control schema-parse failures and multiple structured-output tool calls.
Provider-native output can explicitly request strict schema adherence with
Python `ProviderStrategy` or JavaScript `providerStrategy`.

### Know the six middleware hook pairs

Python custom middleware subclasses `AgentMiddleware`; JavaScript uses
`createMiddleware`. The hook pairs are:

| Python | JavaScript |
| --- | --- |
| `before_agent` | `beforeAgent` |
| `before_model` | `beforeModel` |
| `wrap_model_call` | `wrapModelCall` |
| `wrap_tool_call` | `wrapToolCall` |
| `after_model` | `afterModel` |
| `after_agent` | `afterAgent` |

Bundled policies include human approval, context-limit summarization, PII
handling, model retry with exponential backoff, and OpenAI moderation across
user input, model output, and tool results.

### Install runtime-discovered tools in both places

Filtering tools already registered with `create_agent` needs only
`wrap_model_call`. A tool discovered at runtime must also be installed on its
`ToolCallRequest` in `wrap_tool_call`; showing the definition to the model does
not make the tool executable.

### Inject runtime instead of exposing it to the model

A tool may declare a model-hidden `runtime: ToolRuntime` argument. It exposes
`state`, typed immutable `context`, `store`, `stream_writer`, `config`, and
`tool_call_id`. The names `config` and `runtime` are reserved. Return `Command`
to mutate state, and include a correlated `ToolMessage` when the model needs a
result. Fields written by parallel tools need reducers.

### Keep structured-output routing models unbound

When middleware dynamically switches models for an agent using structured
output, replacement models must not be pre-bound with `bind_tools`.

## Messages and content

Use `.content_blocks` for a backward-compatible typed representation of
reasoning, citations, tool calls, and server-side tool calls across providers.
This lets streams, frontends, and memory stores avoid provider-specific
response shapes. Read [references/v1-migration.md](references/v1-migration.md)
for the integration rollout limits.

`system_prompt` on `create_agent` accepts a `SystemMessage`, including advanced
content blocks, cache-control blocks, structured orchestration hints, and
richer instructions.

## Workflow essentials

### Stream tokens from ordinary invocations

In LangGraph, `stream_mode="messages"` emits `(message_chunk, metadata)` for
model calls anywhere in a graph even when a node calls `model.invoke()`.
Filter by metadata such as `langgraph_node` or model tags.

### Choose the needed stream/result contract

Python LangGraph opt-in `version="v2"` returns typed `StreamPart` values from
stream methods and `GraphOutput` from invoke methods. Event streaming
`version="v3"` provides typed run and chat-model projections while earlier
event versions remain unchanged. Read the workflow reference before changing
result access or checkpoint behavior.

### Make tool errors explicit

`ToolNode` catches invocation errors by default but re-raises tool-execution
errors. Set `handle_tool_errors` to `True`, a model-visible string, a callable,
or a tuple of exception types when execution failures should be caught.

## Provider routing

### OpenAI

`ChatOpenAI` targets official API schemas only; it does not preserve
non-standard fields from compatible third-party endpoints. Use the endpoint's
provider-specific integration when those fields matter.

`ChatOpenAI` selects the Responses API automatically when built-in tools,
conversation-state IDs, or reasoning summaries require it. It can also be
selected with `use_responses_api=True`. Read
[references/openai.md](references/openai.md) for tool loops, continuation,
compaction, reasoning, file inputs, and caching.

### Anthropic

Anthropic client-side bash, computer-use, text-editor, and memory tool
specifications only describe calls; the application must execute them and
return correlated results. Use a tool carrying
`extras["provider_tool_definition"]` or the supplied middleware implementations
when `create_agent` should run that loop. Read
[references/anthropic.md](references/anthropic.md) for schema enforcement,
server tools, caching, files, discovery, and remote MCP.

### MCP

`MultiServerMCPClient` is stateless by default: each tool invocation gets a
fresh `ClientSession`. Open `client.session()` explicitly when server context
must persist across calls. Structured MCP content is an artifact and is not
model-visible unless an interceptor copies it into result content.

## Deep Agents

`deepagents.create_deep_agent` builds a LangGraph-backed runnable and adds
`write_todos` for adaptive plan tracking plus `task` for context-isolated
delegation. Its virtual filesystem can route across composite backends, and
persistent cross-thread memory uses the LangGraph Memory Store.

Read [references/deep-agents.md](references/deep-agents.md) before working with
filesystem mutation, binary files, background subagents, code execution,
harness profiles, durable context, overflow summarization, or headless CLI use.
