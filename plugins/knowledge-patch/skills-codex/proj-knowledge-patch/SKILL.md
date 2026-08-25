---
name: proj-knowledge-patch
description: PROJ
version: 9.8.1
license: MIT
metadata:
  author: Nevaberry
---


# PROJ Knowledge Patch

Use this skill when building PROJ, embedding its resources, consuming its C or
C++ APIs, invoking `projinfo`, importing or exporting CRS definitions, or
debugging coordinate-operation selection and numerical results.

## Working Method

1. Determine the exact PROJ version used by the application or package.
2. Inspect whether the runtime uses the bundled `proj.db`, a system database,
   or an embedded database before reasoning about available objects.
3. Record source and target CRS dimensionality, datum realization, coordinate
   epoch, vertical units, area of interest, and network/resource settings.
4. Treat authority-database content and transformation grids as runtime inputs,
   not merely build-time details.
5. Compare pipelines and numeric output when moving across releases; several
   fixes intentionally change selected operations or computed coordinates.
6. Use the topic references below for the complete behavior details.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Build, packaging, and network resources](references/build-network.md) | CMake, C++17, embedded files, PDBs, pkg-config, CA stores, downloads, Emscripten |
| [Database, CRS identification, and serialization](references/database-crs-io.md) | EPSG and ESRI data, aliases, lookup, WKT, PROJJSON, CRS identification |
| [Coordinate-operation selection](references/operation-selection.md) | Compound and vertical CRS handling, datum realizations, epochs, extent filtering |
| [Bounds, projections, and geodesy](references/bounds-projections-geodesy.md) | Bounds APIs, projection methods, numerical fixes, direct geodesics |
| [Command-line and library interfaces](references/tools-api.md) | `projinfo`, cloning, public headers, context state |

## Compatibility-Critical Changes

### Confirm authority-database content

PROJ 9.8.1 deliberately restores EPSG 12.029 after the EPSG 12.049 database in
9.8.0 caused ETRS89 regressions. Do not assume that a numerically newer PROJ
contains every CRS or datum record shipped by its immediate predecessor.

If an ETRS89 national realization disappears or operation selection changes:

- inspect the PROJ patch release and database metadata together;
- avoid copying identifiers from a different database revision;
- verify transformations for Austria, Belgium, Catalonia, the Netherlands,
  Romania, and Serbia against the application’s actual data directory; and
- distinguish a missing database record from a parser or factory failure.

### Expect intentional numeric changes

Rebaseline affected tests when the old result depended on behavior that was
corrected:

- Wagner VI parameters changed;
- inverse authalic latitude became exact for several projections;
- bounds sampling now looks inside the source grid;
- antimeridian handling was repaired after a regression;
- spherical Transverse Mercator is stable at `lat=lat_0`;
- prolate-ellipsoid meridional inverses are supported; and
- time-dependent transformations receive epochs in more scenarios.

Do not relax tolerances until the selected pipeline, authority database,
resource grids, axis order, and coordinate epoch have been compared.

### Recheck operation selection

Factory fixes can remove implausible candidates or select a more appropriate
vertical or realization-specific operation. This is especially relevant for:

- compound-to-geographic and compound-to-compound transformations;
- NAD83(CSRS), ETRF, WGS 84, ETRS89 national, and Czechia operations;
- source and target interpolation CRSs that are both three-dimensional;
- equivalent but non-identical vertical CRS definitions;
- vertical CRSs that use different units; and
- chains through an intermediate same-datum vertical CRS.

Compare the operation name, steps, grids, accuracy, and extent—not only the
final coordinates.

### Audit parsers and serializers

Consumers must accept the explicit `type` in a Projected CRS PROJJSON
`base_crs`. WKT2 `DEFININGTRANSFORMATION` is accepted but its contents are
ignored, so successful parsing does not mean that the defining transformation
was applied.

Import and identification fixes cover legacy ESRI names, South Orientated
Transverse Mercator, NTF (Paris), empty datum ensembles, old EPSG WKT, and
specific vertical WKT1 forms. Keep parser success separate from semantic
operation availability.

### Update build assumptions

PROJ requires a C++17-capable toolchain. Embedded-resource configuration,
Windows support, C23 `#embed` detection, CMake 4.3 SQLite targets, PDB
packaging, and `proj.pc` output all have release-sensitive behavior.

Run a clean configure when changing any embedding option; cached feature
detection can hide the effective resource strategy.

## High-Value Features

### Build a self-contained library

Use the embedding switches when deployment cannot rely on a writable or
discoverable PROJ data directory:

```sh
cmake -S . -B build \
  -DEMBED_RESOURCE_FILES=ON \
  -DUSE_ONLY_EMBEDDED_RESOURCE_FILES=ON \
  -DEMBED_RESOURCE_DIRECTORY=/path/to/resources
```

`proj.db` and `proj.ini` can be embedded, while the resource directory adds
`.tif` and `.json` files to `libproj`. Confirm that all required grids are
present before enabling embedded-only mode.

### Transform robust bounds

Use `proj_trans_bounds()` for two-dimensional envelopes and
`proj_trans_bounds_3D()` when the vertical dimension matters. Current behavior
supports compound targets and directly constructed pipeline objects, samples
the source grid to find transformed extrema, and handles geographic bounds
crossing the antimeridian.

Bounds output is not a substitute for a coordinate-operation suitability
check. Validate the operation and the densification strategy for the area of
interest.

### Diagnose vertical transformations

For an unexpected or missing vertical operation:

1. Resolve both horizontal and vertical CRS components.
2. Compare datum identity separately from object identity.
3. Check vertical units and interpolation CRS dimensionality.
4. Inspect installed grids and `grid_alternatives`.
5. Confirm coordinate epochs for dynamic transformations.
6. Review whether an intermediate same-datum vertical CRS can bridge the pair.
7. Check whether CRS extent filtering has been disabled.

### Use new callable interfaces

`proj_geod_direct()` performs a direct geodesic calculation with an existing
`PJ` object. `projinfo` functionality is also available through the library,
with declarations installed in `projapps_lib.h`.

Prefer these public interfaces over subprocess parsing or private headers.
Keep ownership, context, and error handling consistent with the rest of the
application’s PROJ calls.

### Configure network trust explicitly

Set `native_ca` in `proj.ini` or `PROJ_NATIVE_CA` in the environment when curl
should use the operating system CA store. Known alternative grid URLs are not
restricted to `cdn.proj.org`, and Emscripten builds fetch resources through
Emscripten Fetch.

After `proj_download_file()` succeeds, the current context invalidates caches
for that file. Other contexts or processes may still need their own lifecycle
handling.

## Diagnostic Playbooks

### A transformation changed after upgrade

1. Capture the old and new operation pipelines.
2. Compare bundled authority-database revisions.
3. Confirm that both executions discover the same resource files.
4. Check dimensionality, axis order, area of interest, and coordinate epoch.
5. Look for a relevant numerical correction or factory-selection fix.
6. Verify accuracy metadata and grid direction before accepting the result.

### A CRS cannot be found or identified

1. Query by authority code before trying a name.
2. Confirm whether the record exists in the installed `proj.db`.
3. Retry with the corrected legacy-name behavior where appropriate.
4. Check ellipsoid compatibility for projected CRS identification.
5. Separate a deprecated record filtered by the caller from a missing record.
6. Inspect the original WKT or PROJJSON rather than a lossy reserialization.

### A grid cannot be opened

1. Determine whether the build is embedded-only.
2. Inspect `EMBED_RESOURCE_DIRECTORY` contents.
3. Check local search paths and the database’s grid name.
4. Inspect `grid_alternatives` for known download URLs.
5. Verify CA-store configuration and network enablement.
6. In WebAssembly, verify Emscripten Fetch integration.
7. Retry after context cache invalidation or context recreation as appropriate.

### A cloned transformation behaves differently

Use `proj_clone()` from a release that preserves behavioral flags. In
particular, verify `FORCE_OVER=YES` and
`errorIfBestTransformationNotAvailable`; both must remain effective on the
clone.

## Verification Checklist

- Pin and report the library version and authority-database revision.
- Confirm the data-directory or embedded-resource strategy at runtime.
- Exercise representative horizontal, vertical, compound, and 3D cases.
- Include an antimeridian bounds case when bounds APIs are used.
- Include a coordinate at `lat=lat_0` when spherical `tmerc` is used.
- Include legacy WKT and PROJJSON fixtures when formats cross system boundaries.
- Compare cloned and original `PJ` behavior when cloning is part of the design.
- Test CA trust and alternate grid download URLs in the deployment environment.
- Verify pkg-config output and public installed headers for downstream builds.
- Read every relevant topic reference before changing compatibility logic.
