# Ray Data Execution

## Streaming and materialization

Dataset transformations are lazy. Once consumption begins, non-shuffle
operators can execute concurrently as a streaming pipeline. `sort()` and
`groupby()` must materialize data, stopping streaming until their shuffle
finishes.

## Batch sizing

`map_batches()` accepts `batch_size="auto"` for automatic sizing. A GPU
transform requires an explicit integer batch size; reduce it if the worker runs
out of memory.

```python
ds = ds.map_batches(
    GpuPredictor,
    num_gpus=1,
    batch_size=64,
)
```

## Transformation pools and logical resources

Function transforms use tasks and can be capped with
`TaskPoolStrategy(size=n)`. Callable-class transforms use actors, execute
`__init__` once per worker, and default to an autoscaling actor pool unless a
fixed `ActorPoolStrategy` is supplied.

`memory`, `num_cpus`, and `num_gpus` influence scheduling; they do not enforce
physical resource limits.

```python
tasks = ds.map_batches(
    transform,
    compute=ray.data.TaskPoolStrategy(size=4),
    memory=1024 * 1024 * 1024,
)
actors = ds.map_batches(
    Predictor,
    compute=ray.data.ActorPoolStrategy(size=2),
)
```

## Row ordering

Transforms do not preserve block order unless the Dataset is sorted or order
preservation is enabled on the current Data context. Preserving order can reduce
performance when workers complete unevenly.

```python
ctx = ray.data.DataContext().get_current()
ctx.execution_options.preserve_order = True
```

## Placement groups for model replicas

For a class-based distributed transform, pass `ray_remote_args_fn` to create a
separate placement group and scheduling strategy for each model replica. Enable
child-task capture to place tasks or actors launched by that replica in the
same group.

```python
from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy

def remote_args():
    pg = ray.util.placement_group([{"CPU": 1}, {"CPU": 1}])
    return {
        "scheduling_strategy": PlacementGroupSchedulingStrategy(
            placement_group=pg,
            placement_group_capture_child_tasks=True,
        )
    }

ds = ds.map_batches(DistributedModel, ray_remote_args_fn=remote_args)
```

## Async transforms

An async transform must be a callable class with `async def __call__`;
function transforms are unsupported. This feature requires
`uvloop==0.21.0`.

```python
class AsyncTransform:
    async def __call__(self, batch):
        return batch

ds = ds.map_batches(AsyncTransform)
```

## Column expressions

Column expressions are an alpha API. Use `col()` and `lit()` with
`with_column()` so the optimizer can understand and reorder column operations.
Custom expression UDFs are vectorized over PyArrow arrays and must declare a
`return_dtype`.

```python
import pyarrow as pa
import pyarrow.compute as pc
from ray.data.datatype import DataType
from ray.data.expressions import col, udf

@udf(return_dtype=DataType.int32())
def add_one(values: pa.Array) -> pa.Array:
    return pc.add(values, 1)

ds = ds.with_column("value_plus_one", add_one(col("value")))
```

## Dataset mixing and data-source behavior

The following data-access changes are grouped in `2.56.0-2.57.0`:

- `Dataset.mix()` is public and combines datasets using weighted sampling,
  replacing manual iterator interleaving.
- Ray 2.57 enables `DataContext.use_datasource_v2` by default. Readers such as
  `read_parquet` use V2 listing and scanning with row-group-aware chunking and
  predicate splitting.
- A `Catalog` abstraction can be passed to `read_*` APIs. Its `UnityCatalog`
  implementation also supports Parquet and Iceberg writes.
- `read_kafka` accepts per-partition `start_offset` and `end_offset` to bound
  explicit Kafka ranges.

## Execution controls

- `isolate_read_workers` moves read tasks to isolated worker processes.
- UDFs can retry transient exceptions.
- `default_map_logical_memory_enabled` supplies default logical memory for map
  operators.

These controls affect task placement and retry behavior; retain explicit
physical capacity planning.

## Safer conversions and writes

- Arrow-backed `to_pandas` conversion can be disabled with
  `RAY_DATA_ENABLE_ARROW_BACKED_PANDAS_CONVERSION` or
  `DataContext.enable_arrow_backed_pandas_conversion`.
- `read_numpy` defaults to `allow_pickle=False`.
- `write_lance(mode=CREATE)` raises an error instead of silently overwriting an
  existing target.

## Migration checklist

- For expression filters, use `compute=` instead of deprecated `concurrency=`.
- `ConcurrencyCapBackpressurePolicy`, `DataIterator.to_torch`, pandas UDF
  batches, `DataContext.scheduling_strategy`, `actor_locality_enabled`,
  `exclude_resources`, and `local://` are deprecated.
- `read_tfrecords` no longer supports `tfx-bsl`.
- Cluster autoscaler v1 is removed.
