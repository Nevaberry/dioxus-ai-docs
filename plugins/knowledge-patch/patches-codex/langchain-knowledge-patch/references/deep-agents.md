# Deep Agents

## Harness and orchestration tools

`deepagents` is a standalone LangChain package.
`create_deep_agent` builds a LangGraph-backed runnable. In addition to
caller-supplied tools, the harness includes `write_todos` for adaptive plan
tracking and `task` for context-isolated delegation to specialized subagents.

```shell
pip install -U deepagents
```

```python
from deepagents import create_deep_agent

def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"It's always sunny in {city}!"

agent = create_deep_agent(
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)
result = agent.invoke({
    "messages": [{"role": "user", "content": "What is the weather in SF?"}]
})
```

## Filesystem mutation controls

Python v0.7 alpha adds a `delete` tool for files and recursive directory
removal. Backends without deletion support hide it automatically. `write_file`
overwrites existing paths instead of failing, while `edit_file` remains the
targeted-edit tool. `FilesystemMiddleware(tools=...)` allowlists the filesystem
tools exposed to the model.

## Replacing default middleware

A Python `middleware=` instance, including a subagent's instance, replaces a
default middleware in place when its `.name` matches the default. This permits
default customization without the former duplicate-middleware error.

## Binary-capable Python backends

Python `read_file` handles PDFs, audio, and video as well as images. State and
Store backends use a binary-capable stored-file format. Construct
`StateBackend()` and `StoreBackend()` directly; factory forms such as
`backend=lambda rt: StateBackend(rt)` are deprecated.

## JavaScript backend protocol v2

`BackendProtocolV2` returns structured `ReadResult`, `LsResult`, `GrepResult`,
and `GlobResult` objects. Failures are reported through an `error` field rather
than raw return values or exceptions. `read()` returns `ReadResult.content`,
and `readRaw()` returns binary data as `Uint8Array`.

The methods `lsInfo`/`grepRaw`/`globInfo` become `ls`/`grep`/`glob`.
`adaptBackendProtocol` bridges v1 implementations while v1 interfaces remain
deprecated.

## Background subagents

Python and JavaScript Deep Agents can launch non-blocking background subagent
tasks while the user continues interacting with the parent agent. This
requires LangSmith Deployment.

## Code execution and sandbox integrations

Python v0.6 has experimental `CodeInterpreterMiddleware`, providing code
execution and programmatic tool calling in a scoped QuickJS runtime. Pluggable
full-sandbox integrations are separately available from `langchain-modal`,
`langchain-daytona`, and `langchain-runloop`.

## Harness profiles

`HarnessProfile` registers provider- or model-specific bundles that
`create_deep_agent` applies when selecting a model. A profile can alter the
system prompt, tools, middleware, and subagent defaults without changing the
agent construction call site.

## Versioned context storage

`ContextHubBackend` stores skills, memories, and other agent files as
LangSmith Hub commits. Every write gets commit history and durable storage
without provisioning a separate LangGraph store.

## Overflow summarization

Conversation summarization runs inside the model node through
`wrap_model_call`, leaving the complete message history in graph state. It
also triggers automatically after `ContextOverflowError`.
`langchain-anthropic` and `langchain-openai` are the integrations stated to
support that error.

## OpenAI Responses default

Python model strings beginning `"openai:"` use the Responses API by default.
To disable response storage, initialize the model with `store=False` and
include encrypted reasoning content.

```python
agent = create_deep_agent(
    model=init_chat_model(
        "openai:...",
        use_responses_api=True,
        store=False,
        include=["reasoning.encrypted_content"],
    )
)
```

## Composite backends and cross-thread memory

The virtual filesystem can use one custom backend or combine several through
composite routing. Persistent memory across conversation threads uses the
LangGraph Memory Store.

## Headless CLI

The Deep Agents CLI works as an interactive coding agent and as a scriptable
runner. Pass `-n` when piping tasks for non-interactive execution.
