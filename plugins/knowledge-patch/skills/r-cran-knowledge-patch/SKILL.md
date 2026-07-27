---
name: r-cran-knowledge-patch
description: R / CRAN
version: null
license: MIT
metadata:
  author: Nevaberry
---

# R and CRAN Knowledge Patch

Use this skill when writing, reviewing, upgrading, building, or submitting R
code and R packages. Check the project's R requirement, native-code build
settings, package metadata, and target repository before applying a rule.

## Reference index

| Reference | Topics |
| --- | --- |
| [language-and-runtime.md](references/language-and-runtime.md) | Base functions, argument matching, strings, tables, session options, archives, methods, bindings, and corrected edge cases |
| [statistics-and-graphics.md](references/statistics-and-graphics.md) | Statistical inference, GLMs, time-series decomposition, matrix factorization, plotting, and graphics behavior |
| [package-build-and-native-code.md](references/package-build-and-native-code.md) | C++ defaults, native APIs, package formats, integrity and signing, build requirements, checks, and vignette engines |
| [documentation-and-weaving.md](references/documentation-and-weaving.md) | Rd links and equations, generated references, installed README files, LaTeX compatibility, Sweave, and tangling |
| [cran-policy.md](references/cran-policy.md) | Source and licensing, names, dependencies, downloads, Internet resources, compatibility, API coordination, and submission cadence |

## Quick reference: breaking and compatibility-sensitive changes

### Native package builds

- The default C++ dialect is C++20 where available, with C++17 as the
  fallback. A package may explicitly request C++17.
- Existing C++11 or C++14 declarations in `src/Makevars` now select the
  default dialect instead of those removed standards.
- The `R CMD config` variable families `CXX11` and `CXX14` are defunct.
- Remove uses of `Rf_isFrame`, `VECTOR_PTR`, and non-API `DATAPTR`.
- Replace `Rf_isFrame` with `Rf_isDataFrame`.
- Treat the pointers returned by `CHARACTER_DATA` and `CHARACTER_POINTER`
  as `const`.
- Include object-table definitions from `R_ext/ObjectTable.h`, not
  `R_ext/Callbacks.h`.
- Reinstall packages that provide graphics devices because the graphics
  engine is version 17.

See [package-build-and-native-code.md](references/package-build-and-native-code.md)
for supported replacements, new device helpers, and stronger check diagnostics.

### Runtime and method behavior

- `weighted.residuals()` on a `glm` now returns weighted working residuals,
  not deviance residuals.
- `influence.glm()` exposes both `wt.res` and `dev.res`; related influence
  measures use Pearson residuals and handle fixed-dispersion models without
  leave-one-out dispersion estimates.
- `plot.lm()` no longer adds a smoother to the
  residuals-versus-leverage panel unless `panel.raw = panel.smooth` restores
  it explicitly.
- `as.table.ftable()` defaults to `named.dim = FALSE`.
- `structure(NULL, name = value)` is defunct.
- `tk*.slaves()` is deprecated; use `tk*.child()`, which requires Tcl/Tk
  8.6 or later.
- Assigning attributes to a primitive function is an error.
- Changing a primitive function's environment is ignored with a warning and
  is planned to become an error.
- Invalid or unmet `requireNamespace(versionCheck = ...)` requests no longer
  pass quietly; unmatched arguments also error even if the namespace is
  already loaded.
- Values returned by active bindings are marked non-mutable so complex
  assignment cannot modify the returned object in place unintentionally.

### Documentation compatibility

- Cross-package S4 links use `\linkS4class[pkg]{Class}` and require a
  dependency on R 4.6.0 or later.
- Use `\linkS4methods{}` for S4 method documentation and
  `\manual{name}{node}` for a section in an R manual.
- The bundled `jss.cls` works with `hyperref` 7.01q.

### Package distribution

- Binary package tooling must accept custom types named
  `<system>.binary.<build>` and the supported compressed tar extensions.
- Tar-based packages can carry a `SHA256` manifest and detached
  `SHA256.sig`; signing uses GnuPG keyrings under `R_HOME/etc/keyrings`.
- A rebuilt binary can supersede the same package version through the
  timestamp in `Built`.
- `R CMD check` diagnoses `clang -Wkeyword-macro`, including macros that mask
  `bool`, `true`, `false`, or `nullptr`.

## Quick reference: CRAN submission constraints

### Source and licensing

- Supply source, or material readily convertible back to source, for every
  package component. This includes generated `configure` files, PDF
  documentation, and Java bytecode.
- Put Java sources in a top-level `java` directory, or explain there how to
  obtain them.
- Ensure direct and indirect dependencies do not restrict users or usage.
- The package license must permit CRAN to distribute the package in
  perpetuity, and a license change must be highlighted on submission.

### Names and dependencies

- Check a proposed name case-insensitively against current and past CRAN
  packages and current Bioconductor packages.
- Package names persist. A takeover normally needs the former maintainer's
  written agreement unless the package is formally orphaned.
- Strong dependencies in `Depends`, `Imports`, and `LinkingTo` should come
  from CRAN or the Bioconductor software repository.
- Do not make an orphaned CRAN package a direct or indirect strong
  dependency. Conditional use through `Suggests` is allowed but discouraged.
- Document access to nonstandard `Suggests` or `Enhances` dependencies and
  use them conditionally when they are not readily installable on major
  platforms.

### Network, native libraries, and compatibility

- Prefer a suitable installed external library, then bundled source.
- Download only fixed source versions. Precompiled downloads are a last
  resort and require agreement from the CRAN team.
- Windows and macOS builds must use static libraries.
- Make installation and startup downloads secure, and raise the timeout for
  downloads larger than a few megabytes.
- Internet-dependent code must fail informatively when a shared resource is
  unavailable or changes, without causing a check warning or error.
- Minimize shared-resource use and avoid rate-limit responses such as HTTP
  429 and 403.
- Target current released CRAN and Bioconductor dependencies, not
  development versions.

### Coordination and cadence

- Agree on significantly disruptive changes with CRAN maintainers well
  before publicizing them.
- Before changing an API, notify affected reverse-dependency maintainers and
  allow at least two weeks, preferably longer, for updates.
- Use a higher version for every published-package update; increasing it
  after each unsuccessful submission is preferred.
- Established packages should normally update no more often than every one
  to two months, and must not send a replacement while a submission is
  pending.
- After publication, wait for the CRAN check page to finish updating before
  submitting a correction; this can take at least 48 hours.

See [cran-policy.md](references/cran-policy.md) for repository metadata,
archival risk, back-compatibility-package restrictions, and macbuilder
guidance.

## Quick reference: commonly used additions

### Base R

- `list.files(..., fixed = TRUE)` matches `pattern` literally.
- `substring()` and `substr()`, including replacement forms, accept an ending
  index of `NULL` to mean through the end of the string.
- `read.dcf()` ignores lines beginning with `#`.
- `ftable()` and `as.table.ftable()` accept `perm`.
- `match.arg(several.ok = "all")` selects the new all-values sentinel.
- `sequence()` can jointly recycle `nvec`, `from`, and `by` with
  `recycle = TRUE` or `R_sequence_recycle`; its default remains
  backward-compatible for now.
- `options(netrc = path)` selects a netrc file for basic HTTP authentication
  with the `"libcurl"` download method.
- The logical `quiet` option reflects `R --quiet` initially and can be
  changed during the session.

### Statistics and plots

- `wilcox.test()` can perform exact conditional inference with ties and can
  add up to three Edgeworth correction terms to asymptotic inference.
- `stats::free1way()` supports likelihood- and permutation-based inference
  for distribution-free stratified K-sample layouts.
- `barplot(orderH = ...)` can order each stack by size.
- Histograms, bar plots, `bxp()`, and box plots support `panel.first`;
  bar plots, `bxp()`, and box plots also support `panel.last`.
- `plot.default(lim2 = TRUE)` derives limits from jointly finite x/y pairs.
- `plot.data.frame()` accepts a formula, and `hatvalues()` has an `nls`
  method.

### Documentation and packaging

- Rd can generate citations and reference lists from `bibentry` data or
  R/BibTeX bibliographic databases.
- `tools::deparseLatex(math = ...)` can convert `$...$` fields to Rd equation
  markup.
- Package `README.md` files are installed and displayed in HTML help.
- `tools::analyze_license()` computes SPDX license identifiers.
- `R CMD build` installs a package that provides its own vignette engine
  before building the vignettes.

## Quick reference: corrected edge cases

- `stl()` validates its 3-by-3 tuning parameters at R level;
  `s.window = 0` no longer crashes and `s.window = 1` works.
- `zapsmall(x, digits = Inf)` returns `x` when `x` contains `Inf` instead of
  producing all `NaN`.
- Asymptotic `wilcox.test(..., exact = FALSE, correct = k)` includes the
  required `dnorm(z)` factor, including in the two-sample case.
- `as.matrix()` on `POSIXlt` again returns a numeric matrix, while `c()` and
  subassignment handle more objects without a `"tzone"` attribute.
- Pivoted `chol()` zeroes the trailing submatrix after stopping early, so
  positive-semidefinite reconstruction remains correct when rank is at
  least two below dimension.

Use the topic references for the remaining method, formatting, graphics,
archive, weaving, native API, and package-policy details.
