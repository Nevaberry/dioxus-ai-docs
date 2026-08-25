# Ray Data processing

## Streaming and shuffle boundaries

Dataset transformations are lazy. Once a Dataset is consumed, non-shuffle
operators can run concurrently as a streaming pipeline. `sort()` and
`groupby()` must materialize data and stop streaming until their shuffle
completes.

## Batch sizing

`map_batches()` accepts `batch_size="auto"` for automatic sizing. GPU
transforms require an explicit integer batch size; reduce it if the worker runs
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
`TaskPoolStrategy(size=n)`. Callable-class transforms use actors, run
`__init__` once per worker, and default to an autoscaling actor pool unless
given a fixed `ActorPoolStrategy`.

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

Arguments such as `memory`, `num_cpus`, and `num_gpus` affect logical
scheduling. They do not enforce physical resource limits.

## Row ordering

Transforms do not preserve block order by default. A sorted Dataset preserves
order, or order can be enabled globally for the current Data context:

```python
ctx = ray.data.DataContext().get_current()
ctx.execution_options.preserve_order = True
```

Preserving order can reduce performance when workers finish unevenly.

## Placement groups for class-based replicas

Pass `ray_remote_args_fn` to create a separate placement group and scheduling
strategy for every class-based model replica. Capturing child tasks places the
replica's internally launched tasks or actors in the same group.

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

An asynchronous transform must be a callable class with
`async def __call__`. Function transforms are not supported. This feature
requires `uvloop==0.21.0`.

```python
class AsyncTransform:
    async def __call__(self, batch):
        return batch

ds = ds.map_batches(AsyncTransform)
```

## Column expressions

Column expressions are an alpha API. Use `col()` and `lit()` with
`with_column()` so the optimizer can reason about and reorder column
operations. A custom expression UDF is vectorized over PyArrow arrays and must
declare `return_dtype`.

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

## Weighted dataset mixing

`Dataset.mix()` is public in `2.56.0-2.57.0`. Use it to combine Datasets
with weighted sampling instead of manually interleaving iterators.

## Reader and catalog behavior

In Ray 2.57, from the `2.56.0-2.57.0` batch,
`DataContext.use_datasource_v2` defaults to enabled. Readers such as
`read_parquet` use the DataSource V2 listing and scanning path, including
row-group-aware chunking and predicate splitting.

The same batch adds the `Catalog` abstraction and a `UnityCatalog`
implementation accepted by `read_*` APIs. Unity Catalog also supports
Parquet and Iceberg writes.

`read_kafka` accepts per-partition `start_offset` and `end_offset` so a
Dataset can read explicit Kafka ranges.

## Execution controls

The `2.56.0-2.57.0` execution controls can:

- move read tasks into isolated worker processes with
  `isolate_read_workers`;
- retry transient exceptions from UDFs; and
- provide default logical memory for map operators with
  `default_map_logical_memory_enabled`.

## Conversion and write safety

For `2.56.0-2.57.0`:

- Arrow-backed `to_pandas` conversion can be disabled with
  `RAY_DATA_ENABLE_ARROW_BACKED_PANDAS_CONVERSION` or
  `DataContext.enable_arrow_backed_pandas_conversion`.
- `read_numpy` defaults to `allow_pickle=False`.
- `write_lance(mode=CREATE)` raises an error rather than silently
  overwriting existing data.

## Migration checklist

The `2.56.0-2.57.0` migration surface includes:

- For expression filters, replace deprecated `concurrency=` with
  `compute=`.
- Do not adopt deprecated `ConcurrencyCapBackpressurePolicy`,
  `DataIterator.to_torch`, pandas UDF batches,
  `DataContext.scheduling_strategy`, `actor_locality_enabled`,
  `exclude_resources`, or `local://`.
- `read_tfrecords` no longer supports `tfx-bsl`.
- Cluster autoscaler v1 is removed.
