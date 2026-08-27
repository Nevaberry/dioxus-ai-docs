# Execution and routing

## Cache activation

Caching requires both a node cache policy and a cache on the compiled graph.
An omitted TTL means no expiration. Python's default cache key hashes the
pickled node input. JavaScript uses `cachePolicy` and `keyFunc`, with
`InMemoryCache` imported from `@langchain/langgraph-checkpoint`.

```python
from langgraph.cache.memory import InMemoryCache
from langgraph.types import CachePolicy

builder.add_node("expensive", expensive, cache_policy=CachePolicy(ttl=30))
graph = builder.compile(cache=InMemoryCache())
```

## Replay happens at node boundaries

After an interrupt or retry, the affected node runs again from the beginning.
Make side effects before the replay point idempotent. Tasks inside a node are
checkpointed and completed task results can be reused, but changing task or
interrupt order before resume can mismatch saved results.

## Additive command routing

`Command(goto=...)` adds a dynamic route without suppressing static outgoing
edges. Both destinations run when both mechanisms exist. Pick commands or
static edges for a node, including nodes returning tool commands.

## Resume commands versus new turns

Passing any `Command` to `invoke` or `stream` resumes from the latest
checkpoint. Use `Command(resume=...)`, optionally with `update`, as resume
input. To start a new turn on an existing thread from `__start__`, pass a plain
state mapping rather than `Command(update=...)`.

```python
graph.invoke({"messages": [follow_up]}, config)
graph.invoke(Command(resume=review_answer), config)
```

## Recursion budgets

Since LangGraph Python 1.0.6, the default recursion limit is 1000 super-steps;
JavaScript defaults to 25. Put `recursion_limit` or `recursionLimit` at the top
level of invocation config, not under `configurable`. A node can read its step
from `metadata.langgraph_step`; Python graphs can expose `RemainingSteps` as a
managed state value for proactive routing.

```python
result = graph.invoke(inputs, config={"recursion_limit": 100})
current_step = config["metadata"]["langgraph_step"]
```

## Retry filtering

Attach `RetryPolicy` with Python `retry_policy=` or JavaScript `retryPolicy`.
Python defaults exclude common programming and runtime failures such as
`ValueError`, `TypeError`, `RuntimeError`, and `OSError`; HTTP-library errors
retry only for 5xx responses. JavaScript excludes `TypeError`, `SyntaxError`,
and `ReferenceError`. Use `retry_on` or `retryOn` to select exceptions
deliberately.

## Per-attempt Python node timeouts

With `langgraph>=1.2`, an async node's `timeout=` accepts seconds, a
`timedelta`, or `TimeoutPolicy(run_timeout=..., idle_timeout=...)`. A timeout
raises `NodeTimeoutError`, discards buffered writes and child-task scheduling,
and starts a new timer if retried. A synchronous-node timeout fails graph
compilation.

```python
from langgraph.types import TimeoutPolicy

builder.add_node(
    "call_model",
    call_model,
    timeout=TimeoutPolicy(run_timeout=120, idle_timeout=30),
)
```

## Post-retry error handling

With `langgraph>=1.2`, Python `add_node(error_handler=...)` runs the handler
only after a node fails and exhausts its retries. It receives current state and
a typed `NodeError`, and may return a `Command` that updates state and routes to
recovery.

```python
from langgraph.errors import NodeError
from langgraph.types import Command

def recover(state: State, error: NodeError) -> Command:
    return Command(update={"status": str(error.error)}, goto="fallback")

builder.add_node("charge", charge, error_handler=recover)
```

## Graph-wide node defaults

Python `langgraph>=1.2` provides `StateGraph.set_node_defaults()` for
compile-time `retry_policy`, `timeout`, `cache_policy`, and `error_handler`
defaults. Explicit node values win, and defaults do not flow into subgraphs.
Retry and timeout defaults apply to handler nodes; cache and error-handler
defaults apply only to regular nodes.

## Execution and server metadata

Python `runtime.execution_info` and JavaScript `runtime.executionInfo` expose
thread, run, checkpoint, task, attempt number, and first-attempt time. Server
deployments additionally expose assistant, graph, and authenticated-user data
through `server_info` or `serverInfo`; these are absent locally. The surfaces
require Python `langgraph>=1.1.5` or JavaScript
`@langchain/langgraph>=1.2.8`.

## Graceful drain awareness

Python `langgraph>=1.2` exposes `runtime.drain_requested` and
`runtime.drain_reason` after a run drain request. Inspect them to skip expensive
work before reaching the next superstep boundary.

```python
def node(state: State, runtime: Runtime):
    if runtime.drain_requested:
        return {"status": "skipped", "reason": runtime.drain_reason}
    return {"status": do_work()}
```

## Deferred fan-in

Python `add_node(..., defer=True)` postpones a node until all pending tasks
finish instead of running when the first incoming branch arrives. Use it as a
final fan-in for parallel branches of different lengths.

## Per-node tracing

In `1.2.11`, Python `StateGraph.add_node()` accepts `trace_policy`, allowing a
trace policy to be assigned while registering an individual node.

```python
builder.add_node("worker", worker, trace_policy=trace_policy)
```
