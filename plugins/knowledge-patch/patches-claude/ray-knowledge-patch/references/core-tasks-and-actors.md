# Core Tasks and Actors

## Type-safe actor handles

Keep the original implementation class undecorated. Mark each remote method
with `@ray.method`, wrap the class with `ray.remote()`, and annotate the wrapper
and actor handle with `ActorClass[T]` and `ActorProxy[T]`. This preserves a
method's return type through `.remote()` as `ObjectRef[R]`.

```python
import ray
from ray.actor import ActorClass, ActorProxy

class Counter:
    @ray.method
    def increment(self) -> int:
        return 1

CounterActor: ActorClass[Counter] = ray.remote(Counter)
counter: ActorProxy[Counter] = CounterActor.remote()
result: ray.ObjectRef[int] = counter.increment.remote()
```

## Cooperative actor-task cancellation

`ray.cancel()` is best-effort and its effect depends on task state and actor
execution model:

- A successfully cancelled unscheduled actor task causes `ray.get()` to raise
  `TaskCancelledError`.
- A running regular or threaded actor method is not interrupted. It must poll
  `ray.get_runtime_context().is_canceled()` and return after cleanup.
- An async actor method instead receives `asyncio.Task` cancellation at an
  `await`. Calling `is_canceled()` in that method raises `RuntimeError`.
- `recursive=True` also targets tracked child and actor tasks.

```python
import time
import ray

@ray.remote
class Worker:
    def run(self):
        while not ray.get_runtime_context().is_canceled():
            time.sleep(0.1)
        return "cleaned up"

worker = Worker.remote()
ref = worker.run.remote()
ray.cancel(ref, recursive=True)
```

## Task-event reporting

Set `enable_task_events=False` on remote functions or actors to suppress the
status and profiling events consumed by the Dashboard and State API. Nested
tasks do not inherit their parent's value. A method-level value overrides the
actor-level value.

```python
@ray.remote(enable_task_events=False)
def quiet_task():
    return 1

@ray.remote
class Worker:
    def work(self):
        return 1

worker = Worker.options(enable_task_events=False).remote()
visible = worker.work.options(enable_task_events=True).remote()
```

## Embedded RocksDB for GCS fault tolerance

The changes grouped in `2.56.0-2.57.0` allow the GCS fault-tolerance store to
use embedded RocksDB instead of an external Redis instance. Select the backend
and storage directory with environment variables:

```sh
export RAY_gcs_storage=rocksdb
export RAY_gcs_storage_path=/var/lib/ray/gcs
```

## Topology-aware scheduling

Core scheduling accepts `topology_strategy`. GPU-domain-aware placement groups
can pack bundles across nodes that share the same `ray.io/gpu-domain` label;
packing is not limited to a single node.

## Cluster lifecycle behavior

- Autoscaler v2 has initial Kubernetes in-place Pod-resizing support, allowing
  CPU and memory changes before it adds worker Pods.
- A node started with `ray start --block` drains when it receives `SIGTERM`.
- The memory monitor warns when the system cgroup slice exceeds
  `--system-reserved-memory`.

## Actor execution extensions

`__ray_call__` is a Developer API for executing closures on actors. Async
streaming generators support backpressure through actor-level configuration
and `_num_objects_per_yield`.
