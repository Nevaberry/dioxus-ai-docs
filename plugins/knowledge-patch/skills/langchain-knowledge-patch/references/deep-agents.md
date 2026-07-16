# Deep Agents

## Harness and orchestration tools

`deepagents` is a standalone LangChain package. `create_deep_agent` builds a
LangGraph-backed runnable and adds orchestration tools alongside caller-supplied
tools:

- `write_todos` tracks and revises an adaptive plan.
- `task` delegates context-isolated work to specialized subagents.

```sh
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
    "messages": [{
        "role": "user",
        "content": "What is the weather in SF?",
    }]
})
```

Design delegated tasks so the subagent receives all required context but does not
inherit unrelated conversation state.

## Filesystem mutation policy

The Python v0.7 alpha adds a `delete` tool for files and recursive directory
removal. A backend that cannot delete hides the tool automatically.

`write_file` now overwrites an existing path instead of failing. Use `edit_file`
for a targeted change where wholesale replacement is not intended.

Configure `FilesystemMiddleware(tools=...)` with an allowlist to limit which
filesystem operations the agent can see. Treat write, overwrite, and recursive
delete as separate authorities even if one backend supports all three.

## Replacing default middleware

Passing a Python `middleware=` instance whose `.name` matches a default
middleware now replaces that default in place. The rule also applies to
middleware configured on a subagent.

Use the same name when customizing a default; a differently named instance is
additional middleware. This avoids the former duplicate-middleware error while
preserving deterministic placement in the stack.

## Binary-capable backends

Python `read_file` handles PDFs, audio, video, and images. State and Store
backends use a binary-capable stored-file representation.

Construct these backends directly:

```python
state_backend = StateBackend()
store_backend = StoreBackend()
```

Factory forms such as `backend=lambda rt: StateBackend(rt)` are deprecated.
Update custom composition code to pass direct instances and preserve binary data
instead of assuming every stored file is UTF-8 text.

## JavaScript backend protocol v2

`BackendProtocolV2` returns structured result objects:

- `ReadResult`
- `LsResult`
- `GrepResult`
- `GlobResult`

Failures are reported in each result's `error` field rather than as raw values or
exceptions. `read()` returns `ReadResult.content`; `readRaw()` returns binary data
as `Uint8Array`.

Rename protocol methods as follows:

| v1 | v2 |
| --- | --- |
| `lsInfo` | `ls` |
| `grepRaw` | `grep` |
| `globInfo` | `glob` |

Use `adaptBackendProtocol` to bridge an existing v1 implementation. The v1
interfaces remain available only as deprecated migration surfaces.

## Background subagents

Python and JavaScript can launch non-blocking subagent tasks while the user keeps
interacting with the parent agent. This facility requires LangSmith Deployment.

Account for the fact that parent state may advance before a background result
arrives. Define how late results are correlated, merged, displayed, or discarded
instead of treating background delegation like a blocking `task` call.

## Code execution and sandboxes

Python v0.6 adds experimental `CodeInterpreterMiddleware`. It provides code
execution and programmatic tool calling in a scoped QuickJS runtime.

Full-sandbox integrations are separate packages:

- `langchain-modal`
- `langchain-daytona`
- `langchain-runloop`

Choose the QuickJS middleware for scoped in-process language execution and a
pluggable sandbox when the task needs a fuller operating-system environment.
Neither choice removes the need for tool authorization, resource limits, and
output validation.

## Harness profiles

`HarnessProfile` registers a provider- or model-specific bundle applied by
`create_deep_agent` during model selection. A profile can modify:

- the system prompt;
- tools;
- middleware;
- subagent defaults.

This keeps provider tuning outside the agent-construction call site. Audit the
effective profile when a model change unexpectedly alters available tools or
delegation behavior.

## Versioned context storage

`ContextHubBackend` stores skills, memories, and other agent files as LangSmith
Hub commits. Every write gains commit history and durable storage without a
separate LangGraph store.

Use commit history for rollback and provenance, but still define naming,
retention, and access policy for memories and skills shared across runs.

## Overflow summarization

Conversation summarization runs inside the model node through `wrap_model_call`.
The graph state retains the full message history; the summarized view is prepared
for the model call instead of destructively replacing state.

Summarization also triggers automatically after `ContextOverflowError`.
`langchain-anthropic` and `langchain-openai` are the integrations stated to
support that error signal.

This behavior matters to checkpoint size and replay: full history remains in
state even when the model sees a compacted view.

## OpenAI Responses defaults

In Python, model strings beginning with `"openai:"` use the Responses API by
default. To disable response storage while retaining reasoning continuity,
initialize the model explicitly with `store=False` and request encrypted
reasoning content.

```python
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

agent = create_deep_agent(
    model=init_chat_model(
        "openai:...",
        use_responses_api=True,
        store=False,
        include=["reasoning.encrypted_content"],
    )
)
```

Keep encrypted reasoning blocks in the protocol state needed for continuation;
do not display or transform them as ordinary text.

## Composite backends and memory

The virtual filesystem can use one custom backend or route different paths to
multiple backends through composite routing. Make routing rules unambiguous so a
read, write, edit, or delete reaches the intended persistence boundary.

For memory that persists across conversation threads, use LangGraph's Memory
Store. Do not confuse checkpointed per-thread graph state with cross-thread
memory.

## Headless CLI

The Deep Agents CLI supports both an interactive coding-agent mode and a
scriptable runner. Pass `-n` when piping tasks for non-interactive execution so
automation does not wait for an interactive prompt.
