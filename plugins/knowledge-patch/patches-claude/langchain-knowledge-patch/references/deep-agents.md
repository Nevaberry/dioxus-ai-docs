# Deep Agents

## Harness and orchestration

`deepagents` is a standalone LangChain package. `create_deep_agent` builds a
LangGraph-backed runnable and adds `write_todos` for adaptive plan tracking and
`task` for context-isolated delegation to specialized subagents alongside
caller-supplied tools.

```shell
pip install -U deepagents
```

```python
from deepagents import create_deep_agent

def get_weather(city: str) -> str:
    return f"It's always sunny in {city}!"

agent = create_deep_agent(
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)
result = agent.invoke({
    "messages": [{"role": "user", "content": "What is the weather in SF?"}]
})
```

## Filesystem mutation and backends

### Control exposed filesystem operations

The Python v0.7 alpha adds `delete` for files and recursive directory removal.
Backends without deletion support hide it automatically. `write_file` now
overwrites existing paths rather than failing, while `edit_file` remains the
targeted-edit tool. `FilesystemMiddleware(tools=...)` allowlists the filesystem
tools exposed to the model.

### Handle binary files and direct backend construction

Python `read_file` handles PDFs, audio, and video as well as images. State and
Store backends use a binary-capable stored-file format. Construct
`StateBackend()` and `StoreBackend()` directly; factory forms such as
`backend=lambda rt: StateBackend(rt)` are deprecated.

### Migrate JavaScript backends to protocol v2

`BackendProtocolV2` returns structured `ReadResult`, `LsResult`, `GrepResult`,
and `GlobResult` objects. Failures appear in an `error` field rather than raw
return values or exceptions. `read()` returns `ReadResult.content`; `readRaw()`
returns binary data as `Uint8Array`. Rename `lsInfo`, `grepRaw`, and `globInfo`
to `ls`, `grep`, and `glob`. `adaptBackendProtocol` bridges v1 implementations
while v1 interfaces remain deprecated.

### Compose storage and memory

The virtual filesystem can use a custom backend or combine backends with
composite routing. Persistent memory across conversation threads uses the
LangGraph Memory Store.

`ContextHubBackend` stores skills, memories, and other agent files as
LangSmith Hub commits. Each write receives commit history and durable storage
without provisioning a separate LangGraph store.

## Middleware replacement and profiles

A Python `middleware=` instance, including one attached to a subagent,
replaces a default middleware in place when its `.name` matches the default.
This customizes defaults without the former duplicate-middleware error.

`HarnessProfile` registers provider- or model-specific bundles that
`create_deep_agent` applies when selecting a model. A profile can alter the
system prompt, tools, middleware, and subagent defaults without changing the
agent-construction call site.

## Background subagents

Python and JavaScript Deep Agents can launch non-blocking background subagent
tasks while the user continues interacting with the parent. This facility
requires LangSmith Deployment.

## Code execution and sandboxes

Python v0.6 adds experimental `CodeInterpreterMiddleware`. It provides code
execution and programmatic tool calling in a scoped QuickJS runtime. Separate
pluggable full-sandbox integrations are available through `langchain-modal`,
`langchain-daytona`, and `langchain-runloop`.

## Context overflow and provider state

Conversation summarization runs inside the model node through
`wrap_model_call`, leaving full message history in graph state. It also
triggers automatically after `ContextOverflowError`; `langchain-anthropic`
and `langchain-openai` are the integrations stated to support that error.

Model strings beginning with `"openai:"` use the Responses API by default.
To disable response storage, initialize the model explicitly with
`store=False` and include encrypted reasoning content.

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

## CLI automation

The Deep Agents CLI is both an interactive coding agent and a scriptable
runner. Pass `-n` when piping tasks for non-interactive execution.
