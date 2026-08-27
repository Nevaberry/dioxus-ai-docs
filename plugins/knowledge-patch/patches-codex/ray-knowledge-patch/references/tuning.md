# Ray Tune

## Function-trainable results

A function trainable has three result-emission styles:

- call `tune.report()` for intermediate metrics;
- return a dictionary for only the final result; or
- yield dictionaries for successive results.

`tune.report()` is not supported inside a class-based `Trainable`.

```python
def objective(config):
    for score in calculate_scores(config):
        yield {"score": score}
```

## Time-budgeted open-ended sampling

Set `num_samples=-1` together with `time_budget_s` to keep generating
trials until the wall-clock budget expires. A finite `num_samples` caps the
number of trials.

```python
tuner = tune.Tuner(
    objective,
    tune_config=tune.TuneConfig(num_samples=-1, time_budget_s=3600),
)
```

## Scheduler compatibility

| Scheduler | Checkpointing | Search algorithm compatibility |
| --- | --- | --- |
| ASHA | Not required | Compatible |
| Median Stopping | Not required | Compatible |
| HyperBand | Required | Compatible |
| BOHB | Required | Only `TuneBOHB` |
| PBT | Required | Incompatible |
| PB2 | Required | Incompatible |

## Dynamic trial resources

`ResourceChangingScheduler` can wrap any other scheduler and change trial
resource requirements while tuning is running.

## Search integrations

For `2.56.0-2.57.0`, `OptunaSearch` requires `optuna>=3.0.0`, and
`BayesOptSearch` exposes configurable float-hash precision.
