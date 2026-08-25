# Agents and Workflows

## Choose an Agent for the Tool Interface

`FunctionAgent` requires an LLM with compatible native function or tool calling.
`ReActAgent` uses text-based reasoning and action parsing when native calls are
unavailable. Use `CodeActAgent` for code-action scenarios.

Current agents accept ordinary synchronous or asynchronous callables as tools.
They derive tool schemas from type hints and docstrings; use `FunctionTool` when
explicit metadata or adaptation is required.

```python
from llama_index.core.agent.workflow import FunctionAgent

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

agent = FunctionAgent(tools=[multiply], llm=llm)
```

## Treat Runs as Streamable Awaitables

`agent.run(...)` and `workflow.run(...)` return workflow handlers, not completed
results. Retain the handler to consume live events and then await that same
handler for its final result.

```python
handler = agent.run("What is 12 times 34?")
async for event in handler.stream_events():
    ...
result = await handler
```

## Create Agent Memory Explicitly

Create current `Memory` instances with `Memory.from_defaults` and pass them to
`run`. Conversation history and memory blocks are distinct from workflow
`Context`, which contains per-run execution state and events.

```python
from llama_index.core.memory import Memory

memory = Memory.from_defaults(session_id="session-123", token_limit=40000)
response = await agent.run("...", memory=memory)
```

`ChatMemoryBuffer`, `ChatSummaryMemoryBuffer`, and `VectorMemory` are deprecated.

## Use Workflow-Based Agent Imports

The current agents are asynchronous workflow components imported from
`llama_index.core.agent.workflow`. Older agent, runner, and worker examples do
not match this execution model.

```python
from llama_index.core.agent.workflow import (
    AgentWorkflow,
    FunctionAgent,
    ReActAgent,
)
```

## Redesign Query Pipelines as Workflows

Workflows are not a mechanical rename of `QueryPipeline`. They express control
flow through typed Pydantic events, asynchronous `@step` methods, event branches
and loops, `Context` state, streaming, and checkpointed durable execution.

Core applications use `llama_index.core.workflow`. Standalone applications can
install `llama-index-workflows` and import from `workflows`.

## Build Dynamic Concurrency with Context Events

A finite fan-out may return a list of events. For dynamic fan-out, emit work
with `Context.send_event`; use `Context.collect_events` for fan-in and wait for
the expected event set. Results do not necessarily arrive in input order.

## Keep State and External Resources Distinct

Put serializable per-run state in the asynchronous `ctx.store` get/set/edit
interface. Put clients, indexes, models, and configuration in workflow
resources. Resource factories and validation provide dependency injection
without treating live objects as checkpointable state.

## Validate the Typed Event Graph

`workflow.validate()` checks start and stop paths, produced events with no
consumers, consumed events with no producers, and dead ends. Run it in tests or
as a startup check.

```python
workflow = RagFlow(timeout=60)
workflow.validate()
```

## Agent, Memory, and Protocol Corrections in 0.14.24

### Tool schemas and structured outputs

Tool-schema generation no longer marks `*args` or `**kwargs` as required.
Within `AgentWorkflow`, agent-level `structured_output_fn` and `output_cls` are
now honored. Remove workarounds that patched these schemas or bypassed the
configured structured output.

### Asynchronous stores and streaming memory

`Memory` accepts any `AsyncDBChatStore`. Streaming chat writes preserve
multiblock histories and populate response text. `SimpleChatStore` persists
non-ASCII content without escaping it.

Test custom asynchronous stores against the same history and streaming paths
used in production.

### Multimodal AG-UI input and safer state

`llama-index-protocols-ag-ui` 0.4.0 accepts user-supplied images, audio, video,
and documents, and persists frontend tool messages. Missing tool call identity
now raises `ValueError` instead of fabricating a `tool_call_id`; callers must
handle the invalid input. Initial state copies are isolated between runs.
