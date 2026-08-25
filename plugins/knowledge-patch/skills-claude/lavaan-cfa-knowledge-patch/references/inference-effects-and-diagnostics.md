# Inference, Effects, and Diagnostics

Use this reference for missing-data auxiliaries, residual analysis, effects,
structured-after-measurement inference, corrected tests, fit measures,
prediction, modification diagnostics, and internal parameter inspection.

## Auxiliary and conditional variables with missing data

Supply auxiliary variables for missing-data estimation with `aux`. In
single-level continuous models, the following missing-data approaches support
`conditional_x = TRUE`:

- full-information maximum likelihood;
- two-stage handling; and
- robust two-stage handling.

That support includes standard errors and the appropriate Gamma/NACOV matrix,
not only parameter estimation. Keep `conditional_x` explicit when conditional
covariate treatment is part of the analysis.

## Residual analysis

`lavResiduals(output = "text")` can display tables of the largest residuals.
Residual output now includes per-element standard errors and z-tests.

```r
residual_report <- lavResiduals(fit, output = "text")
```

Residual analysis also supports:

- `conditional_x`;
- multilevel models; and
- a user-supplied saturated model through `h1`.

Use the elementwise uncertainty when prioritizing residuals instead of ranking
raw magnitudes alone.

## Effects and defined-parameter uncertainty

`lavEffects()` computes total, indirect, and direct effects. Its standard
errors may use the delta method, Monte Carlo simulation, or bootstrap.

For parameters defined with `:=`, set `se_def = "mc"` to request Monte Carlo
standard errors and confidence intervals. Enable `se_delta_second_order` when
the defined parameter requires the second-order delta option.

Keep the effect calculation and its uncertainty method together when
reporting results; the same point estimate can be paired with materially
different uncertainty workflows.

## Structured-after-measurement inference

`sam()` supports several inference paths:

- cluster-robust standard errors for clustered single-level data;
- local standard errors and a corrected structural test for two-level models;
- the Yuan-Chan rescaled test with `sam_method = "global"`;
- `conditional_x = TRUE` with continuous or categorical data;
- experimental `se = "twostep.huber.white"`;
- `se = "local"` with PML; and
- integration with fit measures, residuals, and modification-index tooling.

Select the standard-error and structural-test path from the sampling structure
and SAM method rather than treating all `sam()` output as one inference mode.

## Corrected and robust test statistics

Foldnes-Moss-Gronneberg test statistics are available. Hayakawa statistics are
selected with either of these exact values:

```r
fit_mean_variance <- cfa(
  model,
  data = dat,
  test = "mean.var.adjusted.corrected"
)

fit_scaled_shifted <- cfa(
  model,
  data = dat,
  test = "scaled.shifted.corrected"
)
```

When a robust estimator is active, `lavTestScore()` and `lavTestWald()` report
scaled, adjusted, and robust versions of their statistics.

## Goodness-of-fit index names

`fitMeasures()` now reports the Maydeu-Olivares et al. GFI. The measures that
previously occupied the GFI and AGFI names are now `gfi_lisrel` and
`agfi_lisrel`.

Request the intended name explicitly in downstream extraction code. A script
that asks only for a generic GFI label may otherwise compare different
statistics across lavaan versions.

## Prediction and casewise distance diagnostics

`lavPredict()` can return standard errors for categorical factor scores. It
also accepts `newdata` for two-level models.

The `mdist` casewise Mahalanobis-distance diagnostics exposed through
`lavPredict()` and `lavInspect()` support categorical and ordered data. These
diagnostics therefore need not be restricted to continuous-only fits.

## Modification indices and equality constraints

`modindices()` examines candidate parameters that are currently fixed to
zero. It does not provide the release test for equality constraints. Use
`lavTestScore()` when the proposed change is to release one or more equality
constraints.

```r
mi <- modindices(fit, sort = TRUE, maximum_number = 5)
loading_mi <- mi[mi$op == "=~", ]

score <- lavTestScore(fit)
```

Choose the diagnostic from the current restriction:

| Current restriction | Diagnostic |
| --- | --- |
| Parameter fixed to zero | `modindices()` |
| One or more equality constraints | `lavTestScore()` |

## Inspecting the internal parameterization

With no `what` argument, `lavInspect()` returns model matrices whose nonzero
integers identify free parameters. This makes the default result a free-
parameter map rather than a matrix of fitted estimates.

```r
free_map <- lavInspect(fit)
starts <- lavInspect(fit, what = "start")
parameter_table <- lavInspect(fit, what = "list")
```

`what = "start"` returns starting-value matrices. `what = "list"` returns the
full parameter table and is equivalent to `parTable(fit)`.
