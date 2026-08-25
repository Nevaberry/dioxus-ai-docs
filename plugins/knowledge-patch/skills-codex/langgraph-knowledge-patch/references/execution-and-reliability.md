# Execution and Reliability

Relevant source topics: `graph-api-overview`, `graph-api-usage`, and `1.2.11`.

## Cache policy and cache backend

Node caching activates only when the node has a cache policy and the compiled
graph has a cache. Omitting TTL means the entry never expires. Python's default
key function hashes the pickled node input. JavaScript spells the settings
`cachePolicy` and `keyFunc` and imports `InMemoryCache` from
`@langchain/langgraph-checkpoint`.

```python
from langgraph.cache.memory import InMemoryCache
from langgraph.types import CachePolicy

builder.add_node("expensive", expensive, cache_policy=CachePolicy(ttl=30))
graph = builder.compile(cache=InMemoryCache())
```

## Replay begins at node boundaries

After an interrupt or retry, LangGraph runs the affected node again from the
beginning. Make side effects before the pause or failure idempotent. Tasks
inside a node are checkpointed, so completed task results can be reused.
Changing task or interrupt order before a resume point can pair execution with
the wrong saved result.

## Default retry filtering

Attach `RetryPolicy` through `retry_policy=` in Python or `retryPolicy` in
JavaScript. Python defaults exclude common programming and runtime exceptions,
including `ValueError`, `TypeError`, `RuntimeError`, and `OSError`, and retry
HTTP-library errors only for 5xx responses. JavaScript defaults exclude
`TypeError`, `SyntaxError`, and `ReferenceError`. Use `retry_on` or `retryOn`
when an application needs a deliberate exception selection.

## Per-attempt Python node timeouts

With `langgraph>=1.2`, an async node's `timeout=` accepts seconds, a
`timedelta`, or `TimeoutPolicy(run_timeout=..., idle_timeout=...)`. A timeout
raises `NodeTimeoutError`, discards buffered state writes and child-task
scheduling, and may be retried with a fresh timer. Applying a timeout to a
synchronous node fails graph compilation.

```python
from langgraph.types import TimeoutPolicy

builder.add_node(
    "call_model",
    call_model,
    timeout=TimeoutPolicy(run_timeout=120, idle_timeout=30),
)
```

## Post-retry Python error handlers

With `langgraph>=1.2`, `add_node(error_handler=...)` installs a handler that
runs only after the node fails and exhausts its retries. It receives current
state plus a typed `NodeError` and may return a `Command` that updates state and
routes to recovery.

```python
from langgraph.errors import NodeError
from langgraph.types import Command

def recover(state: State, error: NodeError) -> Command:
    return Command(update={"status": str(error.error)}, goto="fallback")

builder.add_node("charge", charge, error_handler=recover)
```

## Graph-wide node defaults

Python `langgraph>=1.2` adds `StateGraph.set_node_defaults()` for compile-time
`retry_policy`, `timeout`, `cache_policy`, and `error_handler` defaults. An
explicit per-node setting wins. Defaults do not flow into subgraphs. Retry and
timeout defaults also apply to handler nodes; cache and error-handler defaults
apply only to regular nodes.

```python
builder.set_node_defaults(
    retry_policy=RetryPolicy(max_attempts=3),
    timeout=TimeoutPolicy(run_timeout=30),
    error_handler=recover,
)
```

## Execution identity and server metadata

Nodes can inspect execution identity and retry state through Python
`runtime.execution_info` or JavaScript `runtime.executionInfo`. These include
thread, run, checkpoint, task, attempt number, and first-attempt time.

Server deployments additionally expose assistant, graph, and authenticated
user data through `server_info` or `serverInfo`; this is absent in local
execution. These surfaces require Python `langgraph>=1.1.5` or JavaScript
`@langchain/langgraph>=1.2.8`.

## Graceful-drain awareness

Python `langgraph>=1.2` exposes `runtime.drain_requested` and
`runtime.drain_reason` after a drain is requested. A node can avoid expensive
work before execution reaches the next super-step boundary.

```python
def node(state: State, runtime: Runtime):
    if runtime.drain_requested:
        return {"status": "skipped", "reason": runtime.drain_reason}
    return {"status": do_work()}
```

## Deferred fan-in nodes

In Python, `add_node(..., defer=True)` waits until every pending task is done
instead of firing when the first incoming branch arrives. Use it as the final
fan-in for parallel branches of different lengths.

```python
builder.add_node("finalize", finalize, defer=True)
```

## Per-node tracing

Python `StateGraph.add_node()` exposes `trace_policy` in 1.2.11. Supply a trace
policy while registering the individual node.

```python
builder.add_node("worker", worker, trace_policy=trace_policy)
```
