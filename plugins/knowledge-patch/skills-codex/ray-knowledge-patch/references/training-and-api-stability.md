# Training and API stability

## Train V2 opt-in and legacy APIs

Starting in Ray 2.43, set `RAY_TRAIN_V2_ENABLED=1` to enable the overhauled
Train V2 implementation and APIs:

```sh
RAY_TRAIN_V2_ENABLED=1 python train.py
```

The separate V1 reference is deprecated and contains legacy framework helpers,
Trainers, configuration paths, and session utilities. Check the V2 API during
migration rather than assuming old imports remain valid.

## Selecting Trainer datasets to shard

By default, Train calls `Dataset.streaming_split()` so every worker gets a
disjoint shard of every Dataset. Set
`DataConfig(datasets_to_split=[...])` to split only selected inputs. An
unlisted validation Dataset is available in full on every worker. Results from
a split validation Dataset must be aggregated across workers.

```python
trainer = TorchTrainer(
    train_loop_per_worker,
    datasets={"train": train_ds, "val": val_ds},
    dataset_config=ray.train.DataConfig(datasets_to_split=["train"]),
    scaling_config=ScalingConfig(num_workers=2),
)
```

## Pinning data work to a labeled subcluster

Pin Dataset construction work and ingestion separately. Copy the current
`DataContext`, set its label selector while constructing the Dataset, and
repeat that selector in `DataConfig.execution_options`. Train replaces the
Dataset context's execution options, so the construction selector alone does
not pin per-worker ingestion.

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

## Persisting fitted preprocessors

Apply preprocessing before constructing the Trainer. Serialize the fitted
preprocessor into Trainer `metadata`, which is available through
`TrainContext.get_metadata()` and is attached to checkpoints saved by the
Trainer. Encode the serialized bytes for the JSON-compatible metadata
dictionary.

```python
payload = base64.b64encode(scaler.serialize()).decode("ascii")
trainer = TorchTrainer(..., metadata={"preprocessor_pkl": payload})
result = trainer.fit()

payload = result.checkpoint.get_metadata()["preprocessor_pkl"]
restored = StandardScaler.deserialize(base64.b64decode(payload))
```

## Dataset object-store backpressure

Set an execution resource limit on each Dataset. Ray Data slows production at
the limit so a training consumer is not overrun by spilled data.

```python
train_ds.context.execution_options.resource_limits = ray.data.ExecutionResources(
    object_store_memory=50 * 1024**3,
)
```

## API exposure and deprecation policy

An unannotated API is a Developer API by default and may change. Public and
deprecated APIs require explicit annotations.

- A Stable API demotion or parameter change requires warnings, coexistence of
  old and new parameters during transition, and a deadline of six months or
  25 minor versions.
- Beta uses three months or 12 minor versions.
- Alpha has no stability guarantee.

## Logging and training-function results

In `2.56.0-2.57.0`, `LoggingConfig` configures `ray.train` logging on the
controller and workers. A `DataParallelTrainer` training function may return
data.

## Checkpoint and restore behavior

For `2.56.0-2.57.0`:

- `ray.train.get_all_reported_checkpoints` accepts `timeout_s`.
- `ray.train.report(checkpoint=...)` is restricted to in-band checkpoints.
- `Result.from_path` is read-only.
- Train v1 `Predictor` is removed.

## RLlib module specifications

`MultiRLModuleSpec.rl_module_specs` must be a dictionary in
`2.56.0-2.57.0`. Other container types fail validation.
