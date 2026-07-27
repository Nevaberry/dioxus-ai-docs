# Language and Runtime

This reference is organized by runtime task. The changes are attributed to
`r-4.6.0` and, where noted, `r-4.6.1`.

## Files, strings, and DCF data

- `list.files(..., fixed = TRUE)` treats `pattern` literally.
- `substring()` and `substr()` accept an ending index of `NULL`, meaning
  through the end of the string. Their replacement forms accept the same
  open-ended index.
- `read.dcf()` ignores input lines beginning with `#`, so DCF files may
  contain comment lines.
- `abbreviate()` applies wide-character lower- and uppercase handling and
  therefore handles non-ASCII wide characters better (`r-4.6.1`).

## Tables, summaries, and sequences

- `ftable()` and `as.table.ftable()` accept `perm`.
- `as.table.ftable()` now defaults to `named.dim = FALSE`.
- `match.arg()` accepts `several.ok = "all"` as a sentinel for all choices.
- Default `summary()` output is more informative for character vectors.
  Set `character.method = "factor"` to request a factor-style summary.
- Complex-vector summaries select polar or Cartesian coordinates with
  `polar`.
- `sequence()` can jointly recycle `nvec`, `from`, and `by` when
  `recycle = TRUE` or `R_sequence_recycle` is used. The default remains
  backward-compatible for now.

## Session, network, archive, and compression behavior

- The new logical `quiet` option is initialized by `R --quiet` and may be
  changed during a session.
- With the `"libcurl"` download method, basic HTTP authentication can read
  the netrc file selected by `options(netrc = path)`.
- Internal `untar()` accepts `extras = "-P"` to preserve recorded paths
  unchanged.
- `gzcon()` can decompress concatenated streams.
- `extSoftVersion()[["zstd"]]` reports the zstd version when it is available.

## Methods, classes, and object mutation

- `getGenerics()` lists generic-function names in its data portion when more
  than one package defines a generic; it no longer lists package names in
  that case (`r-4.6.1`).
- `as.matrix()` on a `POSIXlt` object again returns a numeric matrix
  (`r-4.6.1`).
- `c()` and subassignment work correctly for more `POSIXlt` cases, including
  objects without a `"tzone"` attribute (`r-4.6.1`).
- `methods::as()` preserves the S4 object when coercing to an S4 superclass
  that extends an old-style class, rather than returning only its S3 portion
  (`r-4.6.1`).
- Assigning attributes to a primitive function is an error.
- Changing a primitive function's environment is ignored with a warning and
  is planned to become an error.
- Values returned from active-binding functions are marked non-mutable. This
  prevents complex assignment from unintentionally changing the returned
  object in place.

## Namespace and deprecated-interface checks

- If `requireNamespace()` receives an unmet `versionCheck`, it reports an
  error and returns `FALSE`.
- Invalid `versionCheck` values error directly.
- Unmatched arguments such as `quiet = TRUE` error even when the namespace
  is already loaded.
- `structure(NULL, name = value)` is defunct.
- The three `tk*.slaves()` functions are deprecated. Use `tk*.child()`,
  which requires Tcl/Tk 8.6 or later.

## Numerical and formatting corrections

- Several math functions experimentally return fully accurate results near
  special values, including `exp(0) == 1` and `log1p(0) == 0`. This reduces
  platform-dependent results.
- When `x` contains `Inf`, `zapsmall(x, digits = Inf)` returns `x` instead of
  converting the result to all `NaN` values (`r-4.6.1`).
