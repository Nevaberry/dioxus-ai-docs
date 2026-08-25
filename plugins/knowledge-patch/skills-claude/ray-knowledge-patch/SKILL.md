---
name: ray-knowledge-patch
description: Ray
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Ray Compatibility Guide

Use this skill when implementing, migrating, or reviewing Ray Core, Data, Train,
Tune, Serve, RLlib, or KubeRay code. Ray's components evolve independently, so
inspect the project's package, image, chart, and custom-resource versions before
applying guidance. Prefer the project's manifests, code, tests, and observed
runtime behavior when they disagree with general compatibility advice.

## Reference index

| Reference | Topics |
| --- | --- |
| [Core tasks and actors](references/core-tasks-and-actors.md) | Typed actor handles, cancellation, task events, GCS storage, topology scheduling, lifecycle, actor extensions |
| [Data execution](references/data-execution.md) | Streaming boundaries, batches, worker pools, ordering, placement groups, expressions, data sources, conversions, migrations |
| [Train and API lifecycle](references/train-and-api-lifecycle.md) | Train V2, dataset sharding, labeled subclusters, checkpoint metadata, backpressure, logging, restore behavior, API stability, RLlib validation |
| [Tune scheduling](references/tune-scheduling.md) | Result emission, open-ended sampling, scheduler constraints, changing resources, search integrations |
| [Serve runtime and recovery](references/serve-runtime-and-recovery.md) | Deployment-response pipelining, recovery, controller outages, REST management, custom routing, direct ingress, LLM routing |
| [KubeRay jobs and services](references/kuberay-jobs-and-services.md) | RayCluster bootstrap, RayJob modes, retries, deadlines, cleanup, RayService endpoints |

## Compatibility hazards first

### Migrate Train deliberately

- Train V2 is opt-in from Ray 2.43 with
  `RAY_TRAIN_V2_ENABLED=1`; do not assume V1 imports or helpers have direct V2
  equivalents.
- The separate V1 reference is deprecated, and V1 `Predictor` is removed in
  newer Ray releases.
- `ray.train.report(checkpoint=...)` accepts only in-band checkpoints, and
  `Result.from_path` is read-only.
- A `DataParallelTrainer` function may return data; use `LoggingConfig` for
  controller and worker `ray.train` logging.

### Update Ray Data migrations

- Ray 2.57 enables DataSource V2 by default for readers such as
  `read_parquet`, changing listing and scanning to the V2 path.
- Expression filters use `compute=`; `concurrency=` is deprecated.
- Deprecated surfaces include `ConcurrencyCapBackpressurePolicy`,
  `DataIterator.to_torch`, pandas UDF batches,
  `DataContext.scheduling_strategy`, `actor_locality_enabled`,
  `exclude_resources`, and `local://`.
- `read_tfrecords` no longer supports `tfx-bsl`, and autoscaler v1 is removed.
- `read_numpy` defaults to `allow_pickle=False`; `write_lance(mode=CREATE)`
  now errors rather than overwriting.

### Check Serve ingress compatibility

- Use `HTTPOptions.proxy_location` instead of deprecated `location`.
- A nonzero `HTTPOptions.num_cpus` is an error.
- Direct ingress rejects an ingress deployment that also uses a custom request
  router or `serve.multiplexed`.
- HAProxy ingress uses the separately distributed `ray-haproxy` package as its
  default binary in Ray 2.57.
- Full KV-cache-aware routing is deferred beyond Ray 2.57 even though
  `KVAwareRouter` and `KVRouterActor` interfaces are present experimentally.

### Validate strict integrations

- `OptunaSearch` requires `optuna>=3.0.0`.
- `MultiRLModuleSpec.rl_module_specs` must be a dictionary.
- KubeRay rules-based cleanup cannot be combined with
  `shutdownAfterJobFinishes` or the global `ttlSecondsAfterFinished`; the older
  `onSuccess` and `onFailure` cleanup style is deprecated.

## Core tasks and actors

### Preserve actor method types

Keep the implementation class undecorated, mark its remote methods with
`@ray.method`, wrap the class with `ray.remote()`, and annotate the wrapper and
handle as `ActorClass[T]` and `ActorProxy[T]`. A typed method returning `R`
then exposes `.remote()` as `ObjectRef[R]`.

### Cancel according to execution model

- `ray.cancel()` is best-effort. Cancelling an unscheduled actor task causes
  `ray.get()` to raise `TaskCancelledError`.
- Running regular and threaded actor methods are not interrupted; they must
  poll `ray.get_runtime_context().is_canceled()` and clean up cooperatively.
- Async actor methods receive `asyncio.Task` cancellation at an `await`.
  Calling `is_canceled()` inside one raises `RuntimeError`.
- `recursive=True` also targets tracked child and actor tasks.

### Control task-event visibility

Set `enable_task_events=False` on a remote function or actor to suppress
Dashboard and State API status and profiling events. Nested tasks do not inherit
the parent's setting. A method-level setting overrides its actor's setting.

## Ray Data execution

### Know the streaming boundary

Lazy non-shuffle operators can overlap as a streaming pipeline after
consumption begins. `sort()` and `groupby()` materialize their inputs, so
streaming stops until the shuffle completes.

### Select batches and worker pools

- `map_batches(batch_size="auto")` enables automatic sizing, but a GPU
  transform needs an explicit integer. Reduce it on worker out-of-memory errors.
- Functions execute as tasks and can use `TaskPoolStrategy(size=n)`.
- Callable classes execute as actors, run `__init__` once per worker, and use
  an autoscaling actor pool unless a fixed `ActorPoolStrategy` is supplied.
- `memory`, `num_cpus`, and `num_gpus` are logical scheduling resources, not
  enforced physical limits.

### Preserve order only when required

Transforms do not preserve block order by default. Sorting or setting
`DataContext.get_current().execution_options.preserve_order = True` preserves
order but can reduce throughput when workers finish unevenly.

### Treat advanced transform APIs carefully

- Give every class-based distributed-model replica its own placement group via
  `ray_remote_args_fn`; enable child-task capture to keep internally launched
  tasks and actors in that group.
- Async transforms must be callable classes with `async def __call__`; function
  transforms are unsupported, and the feature requires `uvloop==0.21.0`.
- Column expressions are alpha. Build them with `col()`, `lit()`, and
  `with_column()`; vectorized expression UDFs operate on PyArrow arrays and must
  declare `return_dtype`.

## Ray Train data flow

### Choose which datasets to shard

Train normally calls `Dataset.streaming_split()` for every dataset. Set
`DataConfig(datasets_to_split=[...])` to shard only selected datasets. Each
worker sees a full unlisted validation dataset; aggregate validation results
across workers when that dataset is split.

### Pin construction and ingestion separately

To target a labeled subcluster, construct the Dataset under a copied
`DataContext` with `execution_options.label_selector`, then repeat the selector
in `DataConfig.execution_options`. Train replaces Dataset execution options for
ingestion, so the construction-time selector alone is insufficient.

### Keep preprocessors with checkpoints

Fit preprocessing before constructing the Trainer. Serialize the fitted
preprocessor, encode the bytes for JSON-compatible Trainer `metadata`, and read
it through `TrainContext.get_metadata()` or checkpoint metadata when restoring.

Set per-Dataset `ExecutionResources(object_store_memory=...)` limits to apply
object-store backpressure when producers could outrun training consumers.

## Tune trials and schedulers

### Emit results correctly

A function trainable may call `tune.report()` for intermediate metrics, return
one final dictionary, or yield successive dictionaries. Do not call
`tune.report()` from a class-based `Trainable`.

For wall-clock-bounded open-ended sampling, combine `num_samples=-1` with
`time_budget_s`; a finite sample count remains a hard trial cap.

### Match scheduler requirements

| Scheduler | Checkpointing | Search algorithm compatibility |
| --- | --- | --- |
| ASHA, Median Stopping | Not required | Compatible |
| HyperBand | Required | Compatible |
| BOHB | Required | `TuneBOHB` only |
| PBT, PB2 | Required | Incompatible |

Wrap another scheduler with `ResourceChangingScheduler` when trial resource
requirements must change during tuning.

## Serve composition and recovery

Pass a `DeploymentResponse` directly into another deployment-handle call to
pipeline composed deployments without materializing intermediate values. Await
the response only where the local value is needed.

- Application exceptions return HTTP 500 with traceback information but do not
  kill the replica.
- Serve replaces failed replicas, proxies, and the controller, restoring routing
  and deployment state from the GCS. Transient connections and internal request
  queues are not restored.
- HTTP, gRPC, and handle traffic can continue while the controller is down, but
  autoscaling pauses and resumes without outage-period metrics.
- Entire-cluster recovery is a KubeRay concern.

## KubeRay operations

- A `RayJob` can embed `rayClusterSpec` or select an existing cluster with
  `clusterSelector`; its entrypoint is submitted after readiness.
- `K8sJobMode` is the default. `HTTPMode`, alpha `InteractiveMode`, and
  `SidecarMode` have distinct submitter behavior and constraints.
- Top-level `backoffLimit` retries with a new RayCluster; the separately scoped
  `submitterConfig.backoffLimit` retries the submitter Job.
- `preRunningDeadlineSeconds` bounds reaching `Running`;
  `activeDeadlineSeconds` bounds reaching a terminal job state.
- `shutdownAfterJobFinishes` defaults to false, and
  `ttlSecondsAfterFinished` applies only when shutdown is enabled.
- A ready `RayService` exposes Dashboard access through its head service on
  port 8265 and Serve HTTP traffic through its Serve service on port 8000.

Use the linked references for exact examples, option interactions, lifecycle
semantics, and the remaining component-specific guidance.
