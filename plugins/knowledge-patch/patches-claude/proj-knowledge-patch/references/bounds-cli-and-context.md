# Bounds, Command-Line Tools, Contexts, and Library APIs

## Bounds transformations

### Compound and 3D bounds

`proj_trans_bounds()` accepts a CompoundCRS target (since 9.6.0).
`proj_trans_bounds_3D()` provides a three-dimensional bounds API (since 9.6.0).
Choose based on the dimensionality of the bounds contract, not merely because a
compound CRS includes a vertical component.

Operation creation uses a 2D Helmert transformation when either source or
target CRS is compound. Account for that operation when explaining changed
horizontal extents.

### Extrema sampling

`proj_trans_bounds()` samples within the source grid to avoid missing
transformed extrema (since 9.6.2). This includes world-wide EPSG:4326 bounds
transformed to ESRI:54099. Do not replace the call with a four-corner transform;
curved edges and projection topology can move extrema away from corners.

### Pipeline-created objects

A `PJ*` constructed directly from a PROJ pipeline works in bounds cases that
previously errored (since 9.6.2). Preserve a focused test if a wrapper accepts
both CRS-to-CRS and explicit-pipeline objects.

### Antimeridian

Geographic bounds crossing the antimeridian transform correctly to a projected
CRS again (since 9.7.0), fixing a regression introduced in 9.6.2. Include east
less than west or equivalent wrapped input in regression tests, and verify the
chosen output convention.

## `projinfo`

- Output reports whether an operation is time-dependent (since 9.6.0). Use that
  signal to require epoch-aware application paths.
- A Bash completion script is shipped (since 9.6.0). Package it in the
  distribution-specific completion location if command-line tooling is
  included.
- `projinfo -k crs` restricts results to CRS objects as requested (since
  9.7.1). Remove client-side filtering added solely because the option used to
  be ignored.

## Embedding `projinfo` functionality

`projinfo` behavior is exposed through the library and installations provide
`projapps_lib.h` (since 9.8.0). Prefer the library interface when an application
needs structured integration. Do not scrape CLI text when a linked interface
is suitable; CLI output remains intended for human and shell use.

Verify that build and packaging rules install both the header and the library
providing the symbols expected by the consumer.

## Name lookup

`createObjectsFromName()` tolerates:

- `N` or `S` where a stored name uses `North` or `South`, and vice versa.
- A missing zone.
- A missing height.

These forms are accepted since 9.6.0. Treat multiple returned candidates as an
ambiguity to resolve with authority, type, or area information rather than
choosing solely by list position.

## Cloning

`proj_clone()` copies context-sensitive flags from the source object, including
`errorIfBestTransformationNotAvailable` and other configuration (since 9.6.0).
It also preserves `FORCE_OVER=YES` (since 9.7.1), so longitude-overrange
behavior no longer silently disappears from a cloned transformation.

When clone behavior matters:

1. Set options on the source object.
2. Clone it into the intended context.
3. Exercise a coordinate that distinguishes the option, such as longitude
   outside the conventional range for `FORCE_OVER`.
4. Assert both error behavior and numeric output where relevant.

## Downloads and current-context caches

After `proj_download_file()` downloads a file, caches associated with that file
are invalidated in the current context (since 9.6.0). Code may retry operation
creation with the same context after a successful download. If another context
was created earlier, verify its behavior independently rather than assuming
cross-context invalidation.
