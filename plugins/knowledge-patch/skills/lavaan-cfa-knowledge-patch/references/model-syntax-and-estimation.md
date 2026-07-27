# Model Syntax and Estimation

Use this reference when choosing estimators, migrating lavaan calls, composing
model syntax, or configuring covariance structures and optimizers. Features
identified as “since 0.7-2” are tied to that lavaan release.

## API and parser compatibility

Since 0.7-2, lavaan requires R 3.4 or newer and does not require compilation.
Almost all user-facing formal arguments now use `snake_case`. Dotted argument
names remain accepted but are deprecated, and option names accept snake case
or capital letters.

```r
fit <- cfa(model, data = dat, sampling_weights = "weight")
```

The `open` syntax parser is now the default. When migrating code that relied on
the preceding parser, select parser behavior explicitly where appropriate or
test the parsing result rather than assuming unchanged interpretation.

## Categorical endogenous variables

lavaan supports binary and ordinal endogenous variables, but not nominal
endogenous variables. Declare only the applicable variables with `ordered`, or
declare all endogenous variables ordered:

```r
fit_selected <- cfa(
  model,
  data = dat,
  ordered = c("item1", "item2")
)

fit_all <- cfa(model, data = dat, ordered = TRUE)
```

Declaring ordered outcomes automatically selects WLSMV. Its parameter
estimation uses diagonally weighted least squares, while its robust standard
errors and mean-and-variance-adjusted test use the full weight matrix. ULSMV
and PML are alternative estimators. FIML is not supported for categorical
outcomes in this workflow.

## Continuous-data and least-squares estimators

Less-common continuous-data choices include distributionally weighted least
squares (`DLS`) and pairwise maximum likelihood (`PML`). Do not treat robust
maximum-likelihood names as interchangeable:

| Estimator | Standard-error and test behavior | Missing-data scope |
| --- | --- | --- |
| `MLM` | Satorra-Bentler test | Complete data only |
| `MLMVS` | Satterthwaite mean-and-variance adjustment | Complete data only |
| `MLMV` | Scale-shifted adjustment | Complete data only |
| `MLF` | First-derivative standard errors and a conventional test | Complete or incomplete data |
| `MLR` | Huber-White standard errors and an asymptotic Yuan-Bentler test | Complete or incomplete data |

```r
fit <- cfa(model, data = dat, estimator = "MLR", missing = "ML")
```

The robust DWLS and ULS names are `WLSM`, `WLSMVS`, `WLSMV`, `ULSM`,
`ULSMVS`, and `ULSMV`. In these variants, parameter estimation uses the
diagonal weight matrix; the standard-error and test corrections use the full
matrix.

## Instrumental-variable estimation

Since 0.7-2, the `|~` operator declares external instruments and
`estimator = "IV"` selects MIIV-2SLS:

```r
model <- '
  y ~ x
  y |~ z1 + z2
'

fit <- sem(model, data = dat, estimator = "IV")
```

This IV path supports:

- multiple groups;
- categorical data;
- simple equality constraints;
- two-stage missing-data handling;
- user-specified instruments; and
- Sargan/Hansen overidentification tests.

## Composite and reduced-bias estimation

Composite models expressed with `<~` now have an analytic gradient. The
former `optim_gradient = "numerical"` workaround is obsolete. Composite
support also includes a robust mean structure, higher-order factors,
multilevel models, and the `composites_cov` option.

Initial support is also available for the reduced-bias M-estimation framework,
which targets improved finite-sample bias.

## Partial correlations and exogenous covariances

Pass a vector of variable names to `correlation` to request a
partial-correlation structure. This is compatible with `fixed_x = TRUE`:

```r
fit <- sem(
  model,
  data = dat,
  correlation = c("x1", "x2"),
  fixed_x = TRUE
)
```

Set `auto_cov_x = TRUE` to freely estimate covariances between latent and
observed exogenous variables. Its default is `FALSE`, so request it explicitly
when the model requires those covariances.

## Composing model syntax

A model need not be one joined string. Pass multiple strings directly as a
character vector so reusable or conditional fragments stay separate:

```r
measurement <- '
  f1 =~ y1 + y2 + y3
  f2 =~ y4 + y5 + y6
'
constraint <- 'f1 ~~ 0*f2'

fit <- cfa(model = c(measurement, constraint), data = dat)
```

## Tuning arguments, rotation targets, and optimization

The `estimator`, `rotation`, and `bootstrap` arguments may be lists. These
list-valued arguments replace the separate corresponding `*.args` arguments.
Keep tuning controls with the argument they configure when migrating a call.

For an ESEM model with multiple EFA blocks, assign a named list to
`rotation_args$target`; each named entry supplies the target matrix for its
corresponding block.

Since 0.7-2, `optim_method = "gn"` uses Levenberg-Marquardt damped Fisher
scoring. Supply its controls through the `gn_args` list rather than an older
control location.
