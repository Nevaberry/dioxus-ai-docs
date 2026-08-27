# Agents and workflows

## Choose an agent from the tool interface

`FunctionAgent` requires an LLM with compatible native function or tool calls.
Use `ReActAgent` when reasoning and actions must be parsed from text, and
`CodeActAgent` for code-action scenarios.

Current agents accept ordinary synchronous or asynchronous callables as tools.
Type hints and docstrings become their schemas; use `FunctionTool` when schema
metadata or adaptation must be explicit.

```python
from llama_index.core.agent.workflow import FunctionAgent

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

agent = FunctionAgent(tools=[multiply], llm=llm)
```

## Run handlers are streamable awaitables

`agent.run(...)` and `workflow.run(...)` return workflow handlers, not completed
results. Retain the handler, consume live events when needed, and await that
same handler for the result.

```python
handler = agent.run("What is 12 times 34?")
async for event in handler.stream_events():
    ...
result = await handler
```

## Create conversation memory explicitly

Use `Memory.from_defaults` and pass the resulting object to `run`.

```python
from llama_index.core.memory import Memory

memory = Memory.from_defaults(session_id="session-123", token_limit=40000)
response = await agent.run("...", memory=memory)
```

Conversation history and memory blocks are distinct from workflow `Context`,
which carries execution state and events for a run.

## Fan out and collect dynamic work

A finite fan-out step can return a list of events. For dynamically discovered
work, emit events with `Context.send_event`; at fan-in, use
`Context.collect_events` to wait for the expected event types. Do not assume
that results arrive in input order.

## Separate checkpointable state from resources

Put per-run serializable state in the asynchronous `ctx.store` get, set, and
edit interface. Supply clients, indexes, models, and configuration through
workflow resources. Resource factories and validation support dependency
injection without pretending that live external objects are checkpointable.

## Validate the typed event graph

Call `workflow.validate()` in tests or during startup. It checks start and stop
paths, events produced without consumers, events consumed without producers,
and dead ends.

```python
workflow = RagFlow(timeout=60)
workflow.validate()
```

## Tool schema and structured-output corrections

In `0.14.24`, generated tool schemas no longer mark `*args` or `**kwargs` as
required. `AgentWorkflow` also honors agent-level `structured_output_fn` and
`output_cls`; remove workarounds that duplicated those settings elsewhere.

## Async and streaming memory corrections

`Memory` accepts any `AsyncDBChatStore`. Streaming writes preserve multiblock
histories and populate response text, while `SimpleChatStore` persists
non-ASCII content without escaping it. Test both streamed and non-streamed
history round trips when removing earlier workarounds.

## Protocol-driven runs

`llama-index-protocols-ag-ui` 0.4.0 accepts images, audio, video, and documents
from users and persists frontend tool messages. Invalid missing tool-call
identity now raises `ValueError` instead of fabricating an identifier, and
initial-state copies are isolated between runs.
