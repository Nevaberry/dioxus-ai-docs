# Groups, Multilevel Models, and Weights

Use this reference when parameters differ across groups or levels, when data
carry sampling weights, or when a two-level model needs categorical outcomes,
random slopes, missing-data optimization, or level-specific fit.

## Group-specific parameter modifiers

In a multigroup model, a `c(...)` modifier supplies one value or label for
each group. Repeating a label imposes equality. An `NA` at one group position
leaves that parameter free even when another group's position fixes it.

```r
model <- '
  f =~ item1 + c(v2, v2)*item2 + c(1, NA)*item3
'

fit <- cfa(model, data = dat, group = "site")
```

Here the `item2` loading shares label `v2` across groups. The `item3` loading
is fixed to `1` in the first group and freely estimated in the second.

## Bulk equality constraints and exceptions

Use `group_equal` to constrain whole parameter classes across groups. The
supported class names are:

- `"loadings"`
- `"intercepts"`
- `"means"`
- `"residuals"`
- `"residual.covariances"`
- `"lv.variances"`
- `"lv.covariances"`
- `"regressions"`

Use `group_partial` with model-syntax parameter names to exempt selected
parameters from those bulk constraints:

```r
fit <- cfa(
  model,
  data = dat,
  group = "school",
  group_equal = c("loadings", "intercepts"),
  group_partial = c("visual=~x2", "x7~1")
)
```

Before diagnosing a constrained multigroup fit, distinguish equality
constraints from parameters fixed to zero. `modindices()` considers only the
latter. Use `lavTestScore()` when the proposed change releases one or more
equality constraints.

## Sampling-weight semantics

Since lavaan 0.7-2, `sampling_weights_type` distinguishes design weights from
frequency weights. Weights are normalized within group by default. For
least-squares estimators, the Gamma/NACOV matrix is properly weighted as well;
do not assume weights alter only the point estimates.

Choose the weight type from the data-generating design rather than relying on
the normalization default to make design and frequency weights equivalent.

## Two-level least-squares estimation

Two-level models can use DWLS and WLS. This includes WLSMV for categorical
data. Exogenous covariates in these models are handled through `fixed_x` and
`conditional_x`, so preserve those choices when switching estimators.

## Random slopes in continuous two-level models

The `rv()` modifier adds random slopes to continuous two-level models. The
supported fitting and inference combinations include:

- ML optimization with `nlminb` or EM;
- MLR standard errors;
- empirical-Bayes predictions;
- complete data; and
- ML missing-data handling through `missing = "ml"`.

Treat `rv()` as a model-syntax modifier, not merely an optimizer request; the
model must identify the intended random slope before selecting the fitting
path.

## ML missing-data optimization

For two-level models using ML missing-data handling, EM is now the default
optimizer. EM can use SQUAREM or quasi-Newton acceleration and provides
analytic Louis observed information.

If old code assumed a different optimizer, preserve that choice explicitly or
revalidate convergence and inference under the EM default. `nlminb` remains
one of the fitting paths for continuous two-level random-slope models.

## Level-specific fit

Multilevel summaries can report level-specific fit measures derived from
partially saturated models. Request a particular level with
`fitMeasures(fit, level = ...)`.

Use `fit_by_level` to control whether and how this behavior is applied. Do not
interpret an overall fit measure as though it were automatically the fit of a
specific level.
