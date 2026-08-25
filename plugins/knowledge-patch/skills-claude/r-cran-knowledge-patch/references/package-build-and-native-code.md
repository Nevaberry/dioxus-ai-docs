# Package Builds and Native Code

This topic reference is attributed to `r-4.6.0`.

## C++ standards

- R uses C++20 by default where it is available and falls back to C++17.
- Packages may request C++17 when needed.
- C++11 and C++14 declarations in `src/Makevars` now select the default C++
  standard instead of selecting those removed standards.
- The `R CMD config` `CXX11` and `CXX14` variable families are defunct.

## Supported C object and attribute APIs

- Supported helpers include `R_class()`, `Rf_isScalarString`, `R_mapAttrib`,
  `R_getAttributes`, `R_getAttribCount`, `R_getAttribNames`, `R_hasAttrib`,
  `R_nrow`, and `R_ncol`.
- ALTREP implementations receive `DATAPTR_RW()` for `Dataptr` methods.
- Use `R_altrep_class_name()` and `R_altrep_class_package()` instead of
  `ALTREP_CLASS`.

## Binding inspection

- The experimental binding API can identify binding types without forcing
  them.
- It can create delayed, forced, or missing bindings and inspect expressions
  and environments, including `...` bindings.
- `R_envSymbols()` lists bound symbols.
- `R_getVar()` and `R_getVarEx()` replace many uses of the non-API
  `Rf_findVar*` functions.

## Removed and tightened interfaces

- `Rf_isFrame` is removed; use `Rf_isDataFrame`.
- `VECTOR_PTR` is removed.
- Non-API `DATAPTR` is no longer declared.
- `CHARACTER_DATA` and `CHARACTER_POINTER` return `const` pointers.
- Object-table definitions moved from `R_ext/Callbacks.h` to
  `R_ext/ObjectTable.h`.
- Numerous non-API accessors are hidden from installed headers or produce
  stronger `R CMD check` diagnostics.

## Graphics-device C API

- Device packages can allocate and free `DevDesc` structures with
  `GEcreateDD()` and `GEfreeDD()`.
- On-screen devices should use `R_eval_with_gd()` when evaluating code in a
  drawing routine so that the device is not closed during evaluation.
- The graphics engine is version 17, so packages that provide graphics
  devices must be reinstalled.

## Building R on Unix-like systems

- Building the manuals requires Texinfo 6.8.
- `make docs` no longer ignores failures while building base documentation.
- `LIBR_LDFLAGS`, which defaults to `LDFLAGS`, separately controls linking
  for libR.
- Failure to create `libR.pc` is no longer ignored.

## Custom binary package types

- Binary distributors can name package types
  `<system>.binary.<build>`.
- Set the native package type with `R_PLATFORM_PKGTYPE`.
- Repositories use `bin/<system>/<build>/contrib/<x.y>`.
- Built filenames include `_R_<system>-<build>`.
- Binary tooling must accept `.tar.bz2`, `.tar.xz`, `.tar.zst`, and
  `.tar.zstd`.

## Integrity, signing, and rebuilds

- Tar-based source and binary packages can include a `SHA256` manifest and a
  detached `SHA256.sig` GnuPG signature.
- `R CMD INSTALL --build` creates the manifest by default.
- `R CMD build --sha256` requests the manifest explicitly.
- `R CMD INSTALL --sign` signs binaries.
- System keyrings are `.gpg` files under `R_HOME/etc/keyrings`.
- Binary installation considers the timestamp in `Built` even if the package
  version has not changed, allowing repositories to replace a binary without
  increasing its version.
- `installed.packages()` and `old.packages()` return the full `Built` value.
- `--built-timestamp` normalizes RFC-2822 timestamps to ISO UTC.

## Package analysis, checks, and build preparation

- `tools::analyze_license()` computes SPDX license identifiers.
- `R CMD check` reports `clang -Wkeyword-macro`, notably for macros that mask
  `bool`, `true`, `false`, or `nullptr`.
- `R CMD check` determines the package name from the tarball contents rather
  than its filename.
- `R CMD build` installs a package that provides its own vignette engine
  before building that package's vignettes.
