---
name: ray-knowledge-patch
description: Ray
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Ray Knowledge Patch

Use this skill for implementation, migration, debugging, or operations involving
Ray Core, Ray Data, Ray Train, Ray Tune, Ray Serve, or KubeRay. Inspect the
project's dependency manifests and configuration before applying guidance, and
prefer observed project behavior when it differs.

## Reference index

| Reference | Topics |
| --- | --- |
| [Tasks and actors](references/tasks-and-actors.md) | Typed handles, cancellation, task events, actor execution, scheduling, GCS, and node lifecycle |
| [Data processing](references/data-processing.md) | Streaming, batching, transforms, resource scheduling, expressions, readers, writes, and migrations |
| [Training and API stability](references/training-and-api-stability.md) | Train V2, dataset sharding, subclusters, checkpoint metadata, logging, restore behavior, and API policy |
| [Tuning](references/tuning.md) | Result emission, sampling budgets, scheduler compatibility, dynamic resources, and search integrations |
| [Serving and recovery](references/serving-and-recovery.md) | Deployment handles, failure recovery, management, request routing, ingress, and LLM routing |
| [Kubernetes operations](references/kubernetes-operations.md) | RayCluster, RayJob, submission modes, retries, cleanup, RayService, and endpoints |

Read only the references relevant to the component being changed. For changes
that span Data and Train or Serve and KubeRay, read both corresponding files
because ownership of execution and recovery settings crosses component
boundaries.

## Compatibility priorities

### Data migration hazards

- Expression filters use `compute=`; do not use the deprecated `concurrency=`
  argument.
- Do not build new code on `ConcurrencyCapBackpressurePolicy`,
  `DataIterator.to_torch`, pandas UDF batches, `DataContext.scheduling_strategy`,
  `actor_locality_enabled`, `exclude_resources`, or `local://`.
- `read_tfrecords` no longer supports `tfx-bsl`, and cluster autoscaler v1 has
  been removed.
- DataSource V2 is the default reader path. Account for row-group-aware
  chunking and predicate splitting when comparing plans or performance.
- `read_numpy` disallows pickle by default. `write_lance(mode=CREATE)` fails
  rather than overwriting an existing target.

See [Data processing](references/data-processing.md) before updating readers,
transforms, conversion code, or storage behavior.

### Train and Tune migration hazards

- Train V2 is opt-in through `RAY_TRAIN_V2_ENABLED=1`; verify V2 imports and
  APIs instead of carrying forward legacy helpers by assumption.
- Train v1 `Predictor` is removed. `Result.from_path` is read-only, and
  `ray.train.report(checkpoint=...)` accepts only in-band checkpoints.
- `OptunaSearch` requires `optuna>=3.0.0`.
- `MultiRLModuleSpec.rl_module_specs` must be a dictionary.

Use [Training and API stability](references/training-and-api-stability.md) for
dataset, checkpoint, metadata, and API-transition details. Use
[Tuning](references/tuning.md) for scheduler and search integration constraints.

### Serve ingress hazards

- Replace deprecated `HTTPOptions.location` with `proxy_location`.
- A nonzero `HTTPOptions.num_cpus` is rejected.
- Direct ingress rejects an ingress deployment that also uses a custom request
  router or `serve.multiplexed`.
- HAProxy ingress expects the separately distributed `ray-haproxy` package.

Read [Serving and recovery](references/serving-and-recovery.md) before changing
ingress, routing, controller, or request-lifecycle configuration.

## Core tasks and actors

### Preserve actor method types

Keep the implementation class undecorated, mark methods with `@ray.method`,
wrap the class using `ray.remote()`, and annotate the wrapper and handle with
`ActorClass[T]` and `ActorProxy[T]`. This carries the method's return type
through `.remote()` to `ObjectRef[R]`.

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

### Treat cancellation as cooperative

`ray.cancel()` is best-effort. A queued actor task can surface
`TaskCancelledError`, but running regular or threaded actor methods must poll
`ray.get_runtime_context().is_canceled()`. Async actor methods receive
`asyncio.Task` cancellation at an `await`; do not call `is_canceled()` inside
them. Use `recursive=True` when tracked child and actor tasks should also be
targeted.

### Control task-event overhead explicitly

Set `enable_task_events=False` on remote functions or actors to suppress
Dashboard and State API status and profiling events. Nested tasks do not
inherit the parent's choice. An actor method setting overrides the actor
setting.

See [Tasks and actors](references/tasks-and-actors.md) for actor closures,
streaming-generator backpressure, topology-aware placement, embedded GCS
storage, and node-drain behavior.

## Ray Data

### Know where streaming stops

Dataset transformations are lazy. Non-shuffle operators can overlap as a
streaming pipeline after consumption starts, while `sort()` and `groupby()`
must materialize their shuffle before streaming continues.

### Select the right transform worker model

- Plain functions use tasks and can be capped with
  `TaskPoolStrategy(size=n)`.
- Callable classes use actors, initialize once per worker, and default to an
  autoscaling pool unless configured with `ActorPoolStrategy`.
- Resource arguments affect logical scheduling; they do not enforce physical
  CPU, GPU, or memory limits.
- Async transforms require a callable class with `async def __call__`; async
  function transforms are unsupported.

GPU transforms require an integer `batch_size`; reduce it after worker memory
errors. `batch_size="auto"` is available for non-GPU transforms.

### Preserve order only when required

Transforms do not preserve block order unless the Dataset is sorted or the
current Data context enables `execution_options.preserve_order`. Enabling it
can reduce throughput when workers finish unevenly.

See [Data processing](references/data-processing.md) for replica placement
groups, alpha column expressions, weighted mixing, catalogs, Kafka bounds,
worker isolation, retries, conversions, and backpressure controls.

## Ray Train

### Decide dataset sharding per input

Train normally uses `Dataset.streaming_split()` so every worker receives a
disjoint shard of every Dataset. Set
`DataConfig(datasets_to_split=[...])` to shard only selected inputs. Each
worker sees an unlisted validation Dataset in full; aggregate results across
workers when validation is split.

### Configure both stages of subcluster placement

Apply a copied `DataContext` with an execution label selector while constructing
the Dataset, then repeat the selector in `DataConfig.execution_options` for
ingestion. Train replaces Dataset execution options, so the construction-time
selector alone does not pin worker ingestion.

### Carry preprocessors through checkpoints

Fit and apply preprocessing before Trainer construction. Serialize the fitted
preprocessor, encode its bytes for the JSON-compatible Trainer `metadata`, and
recover it from checkpoint metadata. Use per-Dataset execution resource limits
to backpressure object-store production when consumers lag.

See [Training and API stability](references/training-and-api-stability.md) for
examples and the stability and deprecation rules.

## Ray Tune

### Emit results correctly

A function trainable may call `tune.report()` for intermediate results, return
a dictionary for only its final result, or yield dictionaries for successive
results. Class-based `Trainable` implementations cannot call `tune.report()`.

### Bound open-ended searches

Use `num_samples=-1` with `time_budget_s` to generate trials until the wall
clock budget expires. A finite `num_samples` caps trial count.

### Match schedulers to checkpointing and search

- ASHA and Median Stopping require no checkpointing and support search
  algorithms.
- HyperBand requires checkpointing and supports search algorithms.
- BOHB requires checkpointing and only works with `TuneBOHB`.
- PBT and PB2 require checkpointing and are incompatible with search
  algorithms.

`ResourceChangingScheduler` can wrap another scheduler to change a trial's
resource request while tuning. See [Tuning](references/tuning.md) for the full
matrix and search-library requirements.

## Ray Serve

### Pipeline deployment responses

A deployment method returns `DeploymentResponse` immediately. Await it for a
local value or pass it directly to another `DeploymentHandle` call so composed
deployments do not materialize intermediate values locally.

### Design around recovery boundaries

Application exceptions return HTTP 500 with traceback information without
killing the replica. Serve recreates failed replicas, proxies, and the
controller and restores persisted controller state from GCS. Transient
connections and internal request queues are lost, and whole-cluster recovery
belongs at the KubeRay layer.

HTTP, gRPC, and deployment-handle traffic can continue while the controller is
down, but autoscaling pauses and resumes without the metrics gathered before
failure. Every cluster node exposes a Serve REST management server.

See [Serving and recovery](references/serving-and-recovery.md) for extensible
routers, HAProxy and gRPC ingress, controller runtime environments, request
timeouts, rolling updates, disconnect handling, and LLM routing modes.

## KubeRay

### Choose the RayJob submission model deliberately

A RayJob may embed `rayClusterSpec` to create a cluster or use
`clusterSelector` for an existing one. Submission modes have distinct
constraints: `K8sJobMode` creates a submitter Job, `HTTPMode` submits through
the operator, `InteractiveMode` waits for the user, and `SidecarMode` places
the submitter in the head Pod.

Keep cluster retries separate from submitter Job retries. Configure
pre-running and active deadlines independently, and choose cleanup rules only
after deciding whether the cluster and RayJob custom resource should survive.

See [Kubernetes operations](references/kubernetes-operations.md) for bootstrap
commands, generated services, submission fields, retry defaults, lifecycle
status, cleanup compatibility, suspension, and RayService readiness.
