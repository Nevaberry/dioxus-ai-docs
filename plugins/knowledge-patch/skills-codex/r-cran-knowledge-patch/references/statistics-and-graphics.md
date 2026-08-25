# Statistics and Graphics

The material is grouped by analysis task and is attributed to `r-4.6.0` and
`r-4.6.1`.

## Model interfaces and residual semantics

- `confint.default()` accepts S4 objects that provide suitable `coef()` and
  `vcov()` methods.
- `binomial(identity)` and `quasibinomial(identity)` work without quoting
  `"identity"`.
- `weighted.residuals()` returns weighted working residuals for `glm`
  objects rather than deviance residuals.
- `influence.glm()` exposes both `wt.res` and `dev.res`.
- Several GLM influence measures use Pearson residuals. For fixed-dispersion
  models, they avoid leave-one-out dispersion estimates.
- `hatvalues()` has an `nls` method.

## Wilcoxon inference

- `wilcox.test()` can perform exact conditional inference when ties are
  present.
- Asymptotic inference can include up to three Edgeworth-series correction
  terms.
- In `wilcox.test(x, exact = FALSE, correct = k)`, the asymptotic p-value
  calculation includes the previously missing `dnorm(z)` factor. The fix
  includes the two-sample case (`r-4.6.1`).

## Distribution-free one-way inference

- `stats::free1way()` provides likelihood- and permutation-based inference
  for distribution-free stratified K-sample layouts.
- `power.free1way.test()` supports power and sample-size planning.
- `rfree1way()` supports simulation.
- `plot()` and `ppplot()` provide diagnostics for these analyses.

## Decomposition and matrix factorization

- `stl()` validates its 3-by-3 tuning parameters at R level
  (`r-4.6.1`).
- `stl(s.window = 0)` no longer crashes, and `s.window = 1` works correctly
  (`r-4.6.1`).
- An `stl()` summary reports robustness weights only when robustness
  iterations actually occurred (`r-4.6.1`).
- When pivoted `chol()` stops early, it zeroes the trailing submatrix. This
  makes positive-semidefinite reconstruction correct when rank is at least
  two below the matrix dimension.

## General plotting controls

- For stacked bars, `barplot(..., orderH = ...)` can sort each stack by size.
- Histograms, bar plots, `bxp()`, and box plots support `panel.first`.
- Bar plots, `bxp()`, and box plots also support `panel.last`.
- `plot.default(lim2 = TRUE)` computes limits from jointly finite x/y pairs.
- `plot.data.frame()` accepts a formula.
- `plot.lm()` no longer draws a smoother in the
  residuals-versus-leverage panel by default. Set
  `panel.raw = panel.smooth` to restore it explicitly.

## Fonts and graphics devices

- The graphics engine is version 17. Reinstall packages that provide
  graphics devices.
- `glyphFont(variations = c(wght = 100))` selects variable-font axes on
  `quartz()` and Cairo-based devices other than `cairo_pdf()`.
