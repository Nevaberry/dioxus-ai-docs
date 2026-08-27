# Ray Train and API Lifecycle

## Enable and migrate to Train V2

Starting with Ray 2.43, set `RAY_TRAIN_V2_ENABLED=1` to enable the overhauled
Train V2 implementation and APIs:

```bash
RAY_TRAIN_V2_ENABLED=1 python train.py
```

The separate V1 reference is deprecated. It contains legacy framework helpers,
trainers, configuration paths, and session utilities. Check the V2 API during a
migration instead of assuming that old imports remain valid.

## Control which Trainer datasets are split

By default, Train uses `Dataset.streaming_split()` to give every worker a
disjoint shard of every Dataset. Set `DataConfig(datasets_to_split=[...])` to
split only selected names. An unlisted validation Dataset is available in full
on every worker. If validation is split, aggregate its results across workers.

```python
trainer = TorchTrainer(
    train_loop_per_worker,
    datasets={"train": train_ds, "val": val_ds},
    dataset_config=ray.train.DataConfig(datasets_to_split=["train"]),
    scaling_config=ScalingConfig(num_workers=2),
)
```

## Pin data work to a labeled subcluster

Pin Dataset construction work such as file listing and schema discovery by
setting a copied `DataContext` while constructing the Dataset. Repeat the label
selector in `DataConfig.execution_options` to pin ingestion. Train replaces the
Dataset context's execution options, so the construction-time selector alone
does not pin per-worker ingest.

```python
from ray.data import ExecutionOptions
from ray.train import DataConfig

ctx = ray.data.DataContext.get_current().copy()
ctx.execution_options.label_selector = {"ray-subcluster": "data"}
with ray.data.DataContext.current(ctx):
    train_ds = ray.data.read_parquet(...)

trainer = TorchTrainer(
    ...,
    datasets={"train": train_ds},
    dataset_config=DataConfig(
        datasets_to_split=["train"],
        execution_options={
            "train": ExecutionOptions(
                label_selector={"ray-subcluster": "data"}
            )
        },
    ),
)
```

## Persist fitted preprocessors

Apply preprocessing before constructing the Trainer, then serialize the fitted
preprocessor into Trainer `metadata`. The metadata is exposed by
`TrainContext.get_metadata()` and attached to Trainer-created checkpoints.
Because serialization returns bytes, encode it for the JSON-compatible metadata
dictionary.

```python
payload = base64.b64encode(scaler.serialize()).decode("ascii")
trainer = TorchTrainer(..., metadata={"preprocessor_pkl": payload})
result = trainer.fit()

payload = result.checkpoint.get_metadata()["preprocessor_pkl"]
restored = StandardScaler.deserialize(base64.b64decode(payload))
```

## Apply per-Dataset object-store backpressure

Limit each Dataset through its execution context. Ray Data slows production at
the limit, preventing training consumers from being overrun by spilled data.

```python
train_ds.context.execution_options.resource_limits = ray.data.ExecutionResources(
    object_store_memory=50 * 1024**3,
)
```

## Configure logging, results, checkpoints, and restore

Changes grouped in `2.56.0-2.57.0` include:

- `LoggingConfig` configures `ray.train` logging on both the controller and
  workers.
- A `DataParallelTrainer` training function may return data.
- `ray.train.get_all_reported_checkpoints` accepts `timeout_s`.
- `ray.train.report(checkpoint=...)` is restricted to in-band checkpoints.
- `Result.from_path` is read-only.
- Train V1 `Predictor` is removed.

## API exposure and deprecation windows

An API without an annotation is a Developer API by default and may change.
Public and deprecated APIs require explicit annotations.

For a Stable API demotion or parameter change, issue warnings, keep the old and
new parameters together during transition, and use a deadline of six months or
25 minor versions. For Beta, use three months or 12 minor versions. Alpha APIs
have no stability guarantee.

## RLlib module-spec validation

`MultiRLModuleSpec.rl_module_specs` must be a dictionary. Inputs that rely on a
different container type fail validation.
