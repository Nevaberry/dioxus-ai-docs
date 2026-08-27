---
name: langchain-knowledge-patch
description: LangChain
version: "1.1.0"
license: MIT
metadata:
  author: Nevaberry
---


# LangChain Knowledge Patch

Use this skill when implementing or migrating LangChain agents, tools,
provider integrations, MCP clients, Deep Agents, or LangGraph workflows.

## Reference index

Read the reference that matches the code being changed. Several may apply to
an agent that combines provider tools, MCP, and a LangGraph runtime.

| Reference | Topics |
| --- | --- |
| [references/v1-migration.md](references/v1-migration.md) | Package moves, runtime floor, `create_agent`, middleware, structured output, content blocks, and model profiles |
| [references/agents-and-tools.md](references/agents-and-tools.md) | Tool runtime injection, dynamic tools, custom state, middleware, routing, limits, and tracing |
| [references/langgraph-workflows.md](references/langgraph-workflows.md) | Typed streams and results, fault tolerance, draining, state schemas, caching, deferred nodes, and resumable streams |
| [references/mcp.md](references/mcp.md) | Session lifetime, structured results, resources, prompts, interceptors, callbacks, and elicitation |
| [references/deep-agents.md](references/deep-agents.md) | Harness tools, filesystem backends, subagents, sandboxes, profiles, memory, context, and CLI use |
| [references/openai.md](references/openai.md) | `ChatOpenAI`, Responses routing and tools, Azure endpoints, conversation state, compaction, caching, and token counting |
| [references/anthropic.md](references/anthropic.md) | `ChatAnthropic`, schemas, tool streaming and discovery, caching, compaction, code execution, files, and remote MCP |

## Migration essentials

### Build agents with `create_agent`

Use `langchain.agents.create_agent` for the LangGraph-backed model/tool loop.
It supersedes the deprecated `create_react_agent` from `langgraph.prebuilt`.

```python
from langchain.agents import create_agent

agent = create_agent(
    model="openai:gpt-5",
    tools=[get_weather],
    system_prompt="Fetch the weather.",
)
```

The `system_prompt` may also be a `SystemMessage`, including one with advanced
content blocks or cache-control blocks.

### Move legacy APIs to the classic package

The main Python package is limited to core abstractions. Install
`langchain-classic` for legacy APIs. Python 3.9 is unsupported; use Python
3.10 or newer.

```shell
uv pip install --upgrade langchain
uv pip install langchain-classic
```

In JavaScript, legacy chains, retrievers, indexing APIs, and community exports
move to `@langchain/classic`; for example, replace `langchain/chains` with
`@langchain/classic/chains`.

```shell
npm install langchain @langchain/core @langchain/classic
```

### Use middleware at the agent-loop boundary

Python custom middleware subclasses `AgentMiddleware`; JavaScript uses
`createMiddleware`. The lifecycle hook pairs are:

| Python | JavaScript |
| --- | --- |
| `before_agent` | `beforeAgent` |
| `before_model` | `beforeModel` |
| `wrap_model_call` | `wrapModelCall` |
| `wrap_tool_call` | `wrapToolCall` |
| `after_model` | `afterModel` |
| `after_agent` | `afterAgent` |

Bundled policies include PII redaction or blocking, summarization triggers,
human decisions of `approve`, `edit`, or `reject`, model retries with
exponential backoff, and OpenAI content moderation across user, model, and
tool boundaries.

JavaScript `dynamicSystemPromptMiddleware` returns are additive: strings and
`SystemMessage` objects extend existing system messages rather than replacing
them.

## Agent state and tools

### Inject `ToolRuntime`

A tool may declare a model-hidden `runtime: ToolRuntime` parameter. It exposes
short-term `state`, immutable typed `context`, the long-term `store`,
`stream_writer`, `config`, and `tool_call_id`. Both `config` and `runtime` are
reserved argument names.

Return a `Command` to mutate state. When the model needs the result, include a
`ToolMessage` correlated with `runtime.tool_call_id`. State fields written by
parallel tools need reducers.

### Install runtime-discovered tools in both paths

Filtering tools already registered on `create_agent` only requires
`wrap_model_call`. A tool discovered at runtime must also be installed on the
`ToolCallRequest` in `wrap_tool_call`; showing the tool to the model does not
make it executable.

### Define custom state as `TypedDict`

Custom agent state must extend `AgentState` as a `TypedDict`; Pydantic models
and dataclasses are not accepted. Prefer middleware-owned `state_schema` when
the middleware's hooks or tools use the fields. The `create_agent` argument
remains a backwards-compatible shortcut for tool-only state.

### Set the `ToolNode` execution-error boundary explicitly

`ToolNode` catches invocation errors by default but re-raises errors from tool
execution. Set `handle_tool_errors` to `True`, a model-visible error string, an
exception-handling callable, or a tuple of exception types to catch execution
failures.

## Structured output and message content

Structured output participates in the agent's main model/tool loop.
`response_format` selects tool-based or provider-native generation. Wrap a
Pydantic schema in `ToolStrategy` for tool-based generation; use its
`handle_errors` option (`handleErrors` in JavaScript) to control schema-parse
failures and multiple structured-output tool calls.

Provider-native structured output can infer `ProviderStrategy` from the
model's `.profile`. A profile declares capabilities such as structured output,
function calling, and JSON mode; summarization middleware also consults it.

Messages expose provider-neutral `.content_blocks` for typed reasoning,
citations, tool calls, and server-side tool calls. Check the migration
reference before assuming every integration implements content blocks.

When middleware dynamically changes models for an agent using structured
output, replacement models must not be pre-bound with `bind_tools`.

## LangGraph execution

Use `stream_mode="messages"` to receive `(message_chunk, metadata)` tokens for
model calls anywhere in a graph, even when node code calls `model.invoke()`.
Filter by metadata such as `langgraph_node` or model tags.

The opt-in Python `version="v2"` API returns typed stream parts and wraps
invoke results in `GraphOutput`; event streaming `version="v3"` exposes typed
run and chat-model projections. Read the workflow reference before changing a
consumer because older modes remain unchanged.

For async-node limits and recovery, configure `timeout=` and `error_handler=`
on `add_node`. A timeout discards that attempt's writes and enters retry
handling. For cooperative shutdown, `RunControl.request_drain()` saves a
resumable checkpoint after the current superstep and raises `GraphDrained`.

## Provider and protocol boundaries

`ChatOpenAI` follows official API schemas and does not preserve non-standard
fields from compatible third-party endpoints. Use the endpoint-specific
integration when those fields matter.

Anthropic client-side bash, computer-use, text-editor, and memory
specifications describe calls but do not execute them. Supply executors or the
provided middleware implementations and return correlated tool results.

`MultiServerMCPClient` is stateless by default: every tool call gets a fresh
session. Open `client.session()` explicitly when server context must persist
across tools, resources, or prompts.

## Deep Agents essentials

`create_deep_agent` produces a LangGraph-backed runnable with caller-supplied
tools plus `write_todos` for adaptive planning and `task` for context-isolated
subagent delegation.

Filesystem behavior is backend-sensitive. Unsupported deletion hides the
`delete` tool; `write_file` overwrites existing paths; `edit_file` remains the
targeted-edit tool. Use `FilesystemMiddleware(tools=...)` to allowlist exposed
filesystem tools.

Python `StateBackend()` and `StoreBackend()` are directly constructible; the
factory forms are deprecated. In JavaScript, `BackendProtocolV2` returns
structured result objects with an `error` field, and
`adaptBackendProtocol` bridges deprecated v1 implementations.

## Final checks

- Follow moved package and import boundaries before adapting APIs.
- Keep custom state, runtime tool installation, and structured-output routing
  within their documented constraints.
- Preserve provider-returned compaction blocks when the relevant provider
  reference requires them.
- Distinguish server-executed tools from client-side tool specifications that
  require an application executor.
- Check session lifetime before relying on MCP server state.
