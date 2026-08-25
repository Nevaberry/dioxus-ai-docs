# Persistence and subgraphs

## Checkpoint namespaces

Each checkpoint has `checkpoint_ns`. The root uses `""`; a subgraph uses
`"node_name:uuid"`; nested namespaces join with `|`. Subgraph updates may not
be immediately visible to the parent. Use a shared Store or arrange a write to
the parent checkpoint when data must cross the boundary.

```python
def node(state, config):
    namespace = config["configurable"]["checkpoint_ns"]
```

## Per-run durability

Execution methods accept three durability modes:

| Mode | Persistence behavior |
| --- | --- |
| `exit` | Write only when execution completes, errors, or interrupts |
| `async` | Write while the next step runs; a crash can lose the newest checkpoint |
| `sync` | Persist before advancing to the next step |

```python
graph.stream({"input": "test"}, durability="sync")
```

## Delta-backed checkpoint storage

Python `langgraph>=1.2` adds beta `DeltaChannel` for append-heavy state. It
stores incremental writes rather than the full accumulated channel and
reconstructs from the nearest `_DeltaSnapshot` plus ancestor writes.

A custom saver must support exact `(thread_id, checkpoint_ns, checkpoint_id)`
lookup. Pruning must preserve the write chain or first materialize a snapshot.
Thread copying must include ancestors back to a snapshot for every delta
channel.

## Custom saver contract

A `BaseCheckpointSaver` implements `put`, `put_writes`, `get_tuple`, `list`,
and `delete_thread`, or the async equivalents. It must support exact-ID and
latest-checkpoint reads; return newest-first history with `before` and `limit`;
delete checkpoint and write rows; and send checkpoints, writes, and complete
metadata through `self.serde`. Use `WRITES_IDX_MAP` for reserved channels such
as `__error__` and `__interrupt__`.

The `langgraph-checkpoint-conformance` package tests base methods and detected
extensions, including delta history. Run it against custom backends in CI.

```python
import asyncio
from langgraph.checkpoint.conformance import checkpointer_test, validate

@checkpointer_test(name="MyCheckpointer")
async def my_checkpointer():
    async with MyCheckpointer.create() as saver:
        yield saver

async def main():
    report = await validate(my_checkpointer)
    if not report.passed_all_base():
        raise RuntimeError("checkpointer failed conformance")

asyncio.run(main())
```

## Serialization and encryption

`JsonPlusSerializer` normally uses msgpack and JSON. Enable
`pickle_fallback=True` only for unsupported values such as dataframes. Encrypt
persisted state with `EncryptedSerializer.from_pycryptodome_aes()`; it reads
`LANGGRAPH_AES_KEY` unless given a key directly.

```python
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer
from langgraph.checkpoint.postgres import PostgresSaver

serde = EncryptedSerializer.from_pycryptodome_aes()
saver = PostgresSaver.from_conn_string("postgresql://...", serde=serde)
saver.setup()
```

## PostgreSQL thread identifiers

`PostgresSaver` and `AsyncPostgresSaver` require `thread_id` values shorter
than 255 characters. Use a UUID or hash rather than an oversized deterministic
identifier.

## Plain-value delta seeds

In `1.2.11`, delta-channel history collects writes at a plain-value seed.
Checkpoint-history consumers must expect those writes rather than assuming they
are absent at the seed boundary.

## Subgraph checkpoint modes

The value used when compiling a subgraph sets its state lifetime:

| Checkpointer value | Behavior |
| --- | --- |
| Default `None` | Fresh state per call; inherits the parent's saver for interrupts and durable execution within the call |
| `True` | Retains state across calls on the same thread |
| `False` | Disables checkpointing, interrupts, durable execution, and state inspection |

The parent must have a checkpointer for either stateful mode.

```python
per_call = builder.compile()
per_thread = builder.compile(checkpointer=True)
stateless = builder.compile(checkpointer=False)
graph = parent_builder.compile(checkpointer=MemorySaver())
```

## Persistent-subgraph concurrency

Concurrent calls to the same `checkpointer=True` subgraph collide because they
write the same checkpoint namespace. Serialize access. For a tool-wrapped
agent, a run limit is one option. Use per-invocation persistence when calls must
be independent.

```python
middleware = [
    ToolCallLimitMiddleware(tool_name="ask_expert", run_limit=1),
]
```

## Stable namespaces for child graphs

Persistent children invoked inside a node receive namespaces by call order.
Reordering children can therefore make one load another's stored state. Wrap
each child in a uniquely named `StateGraph` node. Subgraphs passed directly to
`add_node` already receive name-based namespaces.

```python
def named_child(agent, name):
    return (
        StateGraph(MessagesState)
        .add_node(name, agent)
        .add_edge("__start__", name)
        .compile()
    )
```

## State-inspection discovery boundary

`get_state(..., subgraphs=True)` exposes child snapshots only for statically
discoverable subgraphs: children added as nodes or invoked directly inside a
node. A child behind a tool or other indirection is not discoverable.
Per-invocation state is inspectable only for the current interrupted call;
per-thread state accumulates; stateless children have no snapshot.

```python
snapshot = graph.get_state(config, subgraphs=True)
child_state = snapshot.tasks[0].state
```
