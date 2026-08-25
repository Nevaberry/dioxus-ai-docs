# Persistence and Subgraphs

Relevant source topics: `persistence-and-checkpointing`, `subgraphs`, and
`1.2.11`.

## Checkpoint namespaces

Each checkpoint has a `checkpoint_ns`. The root graph uses `""`; a subgraph
uses `"node_name:uuid"`; nested subgraph namespaces join with `|`.

```python
def node(state, config):
    namespace = config["configurable"]["checkpoint_ns"]
```

Subgraph writes may not be immediately visible to the parent because the two
graphs have separate namespaces. Use a shared Store or arrange for the child to
write the parent checkpoint when data must cross the boundary.

## Per-run durability modes

Execution methods accept `durability="exit"`, `"async"`, or `"sync"`:

- `exit` writes only when execution completes, errors, or interrupts.
- `async` writes while the next step runs and may lose the latest checkpoint
  if the process crashes.
- `sync` persists before execution advances to the next step.

```python
graph.stream({"input": "test"}, durability="sync")
```

## Delta-backed checkpoint storage

Python `langgraph>=1.2` adds the beta `DeltaChannel` for append-heavy state.
Instead of embedding the full accumulated value in every checkpoint, it stores
incremental writes and reconstructs the channel from the nearest
`_DeltaSnapshot` plus its ancestor writes.

A custom saver used with delta channels must support exact
`(thread_id, checkpoint_ns, checkpoint_id)` lookup. Pruning must retain the
write chain back to a snapshot or first materialize a snapshot. Copying a
thread must copy ancestors back to a snapshot for every delta channel.

In 1.2.11, delta-channel history also collects writes at a plain-value seed.
History consumers must expect those boundary writes rather than assuming they
are omitted.

## Custom saver contract

A Python `BaseCheckpointSaver` implementation must provide `put`, `put_writes`,
`get_tuple`, `list`, and `delete_thread`, or the async equivalents. It must:

- support both exact checkpoint-ID reads and latest-checkpoint reads;
- return history newest-first with `before` and `limit` handling;
- delete checkpoint rows and their write rows;
- pass persisted checkpoints, writes, and complete metadata through
  `self.serde`;
- use `WRITES_IDX_MAP` for reserved channels such as `__error__` and
  `__interrupt__`.

The `langgraph-checkpoint-conformance` package tests all base methods and
detected extensions, including delta history. Run it in CI for custom backends.

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
`pickle_fallback=True` only for unsupported values such as dataframes. Any saver
can encrypt persisted state with
`EncryptedSerializer.from_pycryptodome_aes()`, which reads
`LANGGRAPH_AES_KEY` unless the key is passed explicitly.

```python
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer
from langgraph.checkpoint.postgres import PostgresSaver

serde = EncryptedSerializer.from_pycryptodome_aes()
saver = PostgresSaver.from_conn_string("postgresql://...", serde=serde)
saver.setup()
```

## PostgreSQL thread identifiers

`PostgresSaver` and `AsyncPostgresSaver` require `thread_id` values shorter
than 255 characters. Use a UUID or hash rather than a large deterministic ID.

```python
import uuid

config = {"configurable": {"thread_id": str(uuid.uuid4())}}
```

## Subgraph checkpointer modes

The value used to compile a subgraph defines its state lifetime:

| Value | Behavior |
| --- | --- |
| `None` (default) | Fresh state on every call; inherits the parent saver for interrupts and durable execution during that call |
| `True` | Retains state across calls on the same thread |
| `False` | Disables checkpointing, interrupts, durable execution, and state inspection |

The parent graph needs a checkpointer for either stateful mode to work.

```python
per_call = builder.compile()
per_thread = builder.compile(checkpointer=True)
stateless = builder.compile(checkpointer=False)

graph = parent_builder.compile(checkpointer=MemorySaver())
```

## Serializing persistent child calls

Two concurrent calls to the same `checkpointer=True` subgraph target the same
checkpoint namespace and conflict. Serialize access. A tool-wrapped child can,
for example, use a per-run tool-call limit. Prefer per-invocation persistence
when calls should be independent.

```python
middleware = [
    ToolCallLimitMiddleware(tool_name="ask_expert", run_limit=1),
]
```

## Stable namespaces for persistent children

Persistent subgraphs called inside a node receive namespaces according to call
order. Reordering multiple children can make one child load another child's
saved state. Wrap each child in a `StateGraph` node with a unique name to give
it a stable namespace. A subgraph passed directly to `add_node` already gets a
name-based namespace.

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

`get_state(..., subgraphs=True)` exposes child snapshots only when the child is
statically discoverable: it was added as a node or invoked directly inside a
node. A child hidden behind a tool or other indirection is not discoverable.

Per-invocation state can be inspected only for the current interrupted call;
per-thread state accumulates; stateless children have no snapshot.

```python
snapshot = graph.get_state(config, subgraphs=True)
child_state = snapshot.tasks[0].state
```
