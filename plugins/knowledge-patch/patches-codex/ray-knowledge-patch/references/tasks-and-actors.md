# Tasks and actors

## Type-safe actor handles

Keep the implementation class undecorated, mark remote methods with
`@ray.method`, and wrap the class with `ray.remote()`. Annotate the remote
class as `ActorClass[T]` and its handle as `ActorProxy[T]`; this preserves a
method return type `R` as `ObjectRef[R]` through `.remote()`.

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

`ray.cancel()` is best-effort:

- Successfully cancelling an unscheduled actor task causes `ray.get()` to
  raise `TaskCancelledError`.
- A running regular or threaded actor method is not interrupted. It must poll
  `ray.get_runtime_context().is_canceled()` and perform its own cleanup.
- An async actor method instead receives `asyncio.Task` cancellation at an
  `await`. Calling `is_canceled()` from an async actor method raises
  `RuntimeError`.
- `recursive=True` also targets tracked child tasks and actor tasks.

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

Set `enable_task_events=False` on a remote function or actor to suppress the
status and profiling events consumed by the Dashboard and State API.

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

Nested tasks do not inherit their parent's setting. An actor method's setting
overrides the setting on the actor.

## Actor execution extensions

For changes in `2.56.0-2.57.0`, `__ray_call__` is a Developer API that runs
closures on actors. Async streaming generators support backpressure through
actor-level configuration and `_num_objects_per_yield`.

## Topology-aware scheduling

The `2.56.0-2.57.0` core scheduling surface includes
`topology_strategy`. GPU-domain-aware placement groups can pack bundles
across nodes carrying the same `ray.io/gpu-domain` label; they are not
restricted to packing on one node.

## Embedded GCS storage

GCS fault tolerance in `2.56.0-2.57.0` can use embedded RocksDB rather than
an external Redis instance. Select the backend and storage path with:

```sh
export RAY_gcs_storage=rocksdb
export RAY_gcs_storage_path=/var/lib/ray/gcs
```

## Cluster lifecycle behavior

In `2.56.0-2.57.0`:

- Autoscaler v2 has initial Kubernetes in-place Pod resizing support. It can
  change CPU and memory before adding worker Pods.
- A node running `ray start --block` drains on `SIGTERM`.
- The memory monitor warns when the system cgroup slice exceeds
  `--system-reserved-memory`.
