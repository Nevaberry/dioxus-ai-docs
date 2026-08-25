# Ray Tune Scheduling

## Emit function-trainable results

A function trainable has three result-emission styles:

- Call `tune.report()` for intermediate metrics.
- Return one dictionary for only the final result.
- Yield dictionaries for successive results.

Do not call `tune.report()` inside a class-based `Trainable`.

```python
def objective(config):
    for score in calculate_scores(config):
        yield {"score": score}
```

## Run time-budgeted open-ended sampling

Set `num_samples=-1` together with `time_budget_s` to generate trials until a
wall-clock budget expires. A finite `num_samples` caps the number of trials.

```python
tuner = tune.Tuner(
    objective,
    tune_config=tune.TuneConfig(num_samples=-1, time_budget_s=3600),
)
```

## Match schedulers to checkpointing and search

| Scheduler | Checkpointing | Search algorithms |
| --- | --- | --- |
| ASHA | Not required | Compatible |
| Median Stopping | Not required | Compatible |
| HyperBand | Required | Compatible |
| BOHB | Required | Only `TuneBOHB` |
| PBT | Required | Incompatible |
| PB2 | Required | Incompatible |

## Change resources during a trial

`ResourceChangingScheduler` can wrap any other scheduler and adjust a trial's
resource requirements while tuning is in progress.

## Search-integration requirements

In the changes grouped as `2.56.0-2.57.0`, `OptunaSearch` requires
`optuna>=3.0.0`, and `BayesOptSearch` exposes configurable float-hash precision.
