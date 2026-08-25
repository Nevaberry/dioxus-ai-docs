---
name: lavaan-cfa-knowledge-patch
description: lavaan / CFA
version: null
license: MIT
metadata:
  author: Nevaberry
---


# lavaan and Confirmatory Factor Analysis Knowledge Patch

Use this skill when writing, reviewing, or updating R code for confirmatory
factor analysis and related structural equation models in lavaan. It is
especially relevant for categorical outcomes, robust estimators, multigroup
constraints, multilevel models, missing data, sampling weights, effects, and
diagnostics.

Before changing a fit:

1. Inspect the installed lavaan version and the variables' continuous,
   ordinal, binary, grouping, cluster, and weight roles.
2. Separate estimation choices from test-statistic and standard-error
   corrections; similarly named robust estimators do not behave identically.
3. Check whether a parameter is fixed, group-constrained, or freely estimated
   before selecting a modification-index or score-test workflow.
4. Preserve explicit parser, optimizer, and weighting choices when migrating
   compatibility-sensitive code.
5. Open the topic reference that matches the task and retain exact option,
   operator, and parameter-table names.

## Reference index

| Reference | Topics |
| --- | --- |
| [model-syntax-and-estimation.md](references/model-syntax-and-estimation.md) | API and parser migration, categorical and robust estimation, instruments, composites, correlations, tuning lists, ESEM targets, and optimization |
| [groups-multilevel-and-weights.md](references/groups-multilevel-and-weights.md) | Multigroup modifiers and equality constraints, sampling weights, two-level least squares, random slopes, missing-data optimization, and level-specific fit |
| [inference-effects-and-diagnostics.md](references/inference-effects-and-diagnostics.md) | Missing-data auxiliaries, residuals, effects, structured-after-measurement inference, corrected tests, fit indices, prediction, modification diagnostics, and parameter inspection |

## Quick reference: compatibility-sensitive changes

### Argument and parser migration

- Prefer `snake_case` for user-facing formal arguments. Dotted argument names
  remain accepted but are deprecated.
- Option names accept snake case or capital letters.
- The `open` syntax parser is now the default. Code that depended on the
  previous parser should choose or test parser behavior explicitly.
- The minimum R version is 3.4, and installing lavaan does not require
  compilation.

```r
fit <- cfa(model, data = dat, sampling_weights = "weight")
```

### Replaced tuning interfaces

- `estimator`, `rotation`, and `bootstrap` may each be a list; use these in
  place of their separate `*.args` arguments.
- `optim_method = "gn"` now means Levenberg-Marquardt damped Fisher scoring,
  and its controls belong in `gn_args`.
- Composite models using `<~` have an analytic gradient. Remove the obsolete
  `optim_gradient = "numerical"` workaround.
- For ESEM, assign a named list of target matrices to
  `rotation_args$target` to provide one target per EFA block.

### Fit-index naming

- `fitMeasures()` reports the Maydeu-Olivares et al. GFI under the usual GFI
  name.
- Request `gfi_lisrel` or `agfi_lisrel` when downstream code intends the
  previously named GFI or AGFI statistics.

## Quick reference: categorical and robust estimation

### Categorical endogenous variables

- lavaan supports binary and ordinal endogenous variables, not nominal ones.
- Pass selected variables with `ordered = c(...)`, or use `ordered = TRUE`
  for all endogenous variables.
- This automatically selects WLSMV: parameter estimation uses DWLS, while
  robust standard errors and the mean-and-variance-adjusted test use the full
  weight matrix.
- ULSMV and PML are alternatives. FIML is not supported for this categorical
  workflow.

```r
fit <- cfa(model, data = dat, ordered = c("item1", "item2"))
```

### Robust continuous-data variants

- `MLM` uses a Satorra-Bentler test, `MLMVS` a Satterthwaite
  mean-and-variance adjustment, and `MLMV` a scale-shifted adjustment. These
  three require complete data.
- `MLF` combines first-derivative standard errors with a conventional test.
- `MLR` combines Huber-White standard errors with an asymptotic Yuan-Bentler
  test. Both `MLF` and `MLR` support complete or incomplete data.
- Less-common choices include distributionally weighted least squares
  (`DLS`) and pairwise maximum likelihood (`PML`).
- Robust DWLS and ULS variants estimate parameters with the diagonal weight
  matrix but use the full matrix for standard-error and test corrections.

```r
fit <- cfa(model, data = dat, estimator = "MLR", missing = "ML")
```

## Quick reference: syntax and structural choices

### External instruments

Use `|~` to declare external instruments and `estimator = "IV"` to select
MIIV-2SLS.

```r
model <- '
  y ~ x
  y |~ z1 + z2
'
fit <- sem(model, data = dat, estimator = "IV")
```

The IV implementation handles multiple groups, categorical data, simple
equality constraints, two-stage missing data, user-specified instruments,
and Sargan/Hansen overidentification tests.

### Model composition and covariance structure

- Pass a character vector directly as `model` to combine reusable or
  conditional syntax fragments.
- A character vector supplied to `correlation` requests a partial-correlation
  structure and can be combined with `fixed_x = TRUE`.
- `auto_cov_x = TRUE` freely estimates covariances between latent and observed
  exogenous variables; its default is `FALSE`.
- Composites support a robust mean structure, higher-order factors,
  multilevel models, and the `composites_cov` option.
- Reduced-bias M-estimation is available as an initial framework for reducing
  finite-sample bias.

## Quick reference: groups, levels, and weights

### Multigroup constraints

- In multigroup syntax, `c(...)` supplies one value or label per group.
- Repeat a label to impose equality. Use `NA` at a group position to leave
  that group's parameter free while another group's value is fixed.
- `group_equal` applies supported classes of equality constraints in bulk;
  `group_partial` names exceptions in model syntax.
- `modindices()` only considers parameters fixed to zero. Use
  `lavTestScore()` to assess release of equality constraints.

```r
fit <- cfa(
  model, data = dat, group = "school",
  group_equal = c("loadings", "intercepts"),
  group_partial = c("visual=~x2", "x7~1")
)
```

### Two-level models

- Two-level models can use DWLS and WLS, including WLSMV for categorical
  data; handle exogenous covariates with `fixed_x` and `conditional_x`.
- `rv()` adds random slopes to continuous two-level models. Supported paths
  include ML through `nlminb` or EM, MLR standard errors, empirical-Bayes
  predictions, and complete data or `missing = "ml"`.
- With ML missing-data handling, EM is the default two-level optimizer. It
  supports SQUAREM or quasi-Newton acceleration and analytic Louis observed
  information.
- Summaries can show level-specific fit based on partially saturated models.
  Request a level through `fitMeasures(fit, level = ...)` and control the
  behavior with `fit_by_level`.

### Sampling weights

- Use `sampling_weights_type` to distinguish design weights from frequency
  weights.
- Weights are normalized within group by default.
- Least-squares estimators use a properly weighted Gamma/NACOV matrix.

## Quick reference: missing data and inference

### Auxiliary and conditional variables

- Supply missing-data auxiliary variables through `aux`.
- For continuous single-level models, FIML, two-stage, and robust-two-stage
  missing-data handling support `conditional_x = TRUE`, including standard
  errors and the corresponding Gamma/NACOV matrix.

### Effects and test statistics

- `lavEffects()` computes total, indirect, and direct effects with
  delta-method, Monte Carlo, or bootstrap standard errors.
- For parameters defined with `:=`, use `se_def = "mc"` for Monte Carlo
  standard errors and confidence intervals; `se_delta_second_order` enables
  the second-order delta option.
- Foldnes-Moss-Gronneberg statistics are available. Select the Hayakawa
  variants with `test = "mean.var.adjusted.corrected"` or
  `test = "scaled.shifted.corrected"`.
- With a robust estimator, `lavTestScore()` and `lavTestWald()` report scaled,
  adjusted, and robust statistics.

### Residuals, prediction, and inspection

- `lavResiduals(output = "text")` can display largest-residual tables and
  supplies elementwise residual standard errors and z-tests. It also supports
  `conditional_x`, multilevel models, and a supplied saturated model via `h1`.
- `lavPredict()` can return standard errors for categorical factor scores and
  accepts `newdata` for two-level models.
- The `mdist` casewise Mahalanobis-distance diagnostics in `lavPredict()` and
  `lavInspect()` support categorical and ordered data.
- With no `what`, `lavInspect()` returns model matrices whose nonzero integers
  identify free parameters. Use `what = "start"` for starting-value matrices
  and `what = "list"` for the full parameter table returned by
  `parTable(fit)`.

Use the references for complete option sets, supported combinations, and
diagnostic distinctions before editing production analyses.
