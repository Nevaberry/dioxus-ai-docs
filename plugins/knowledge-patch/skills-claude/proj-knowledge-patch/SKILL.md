---
name: proj-knowledge-patch
description: PROJ
version: 9.8.1
license: MIT
metadata:
  author: Nevaberry
---


# PROJ Knowledge Patch

Use this skill when building PROJ, consuming its C or C++ APIs, invoking
`projinfo`, parsing CRS formats, selecting coordinate operations, or diagnosing
changed transformation results.

## Apply the patch

1. Determine the PROJ version from the package metadata, `proj`/`projinfo`
   executable, CMake package, or `proj.h`.
2. Read the quick-reference sections below before changing a build or accepting
   a changed coordinate result.
3. Open only the topic reference needed for the task.
4. Apply notes introduced no later than the installed version.
5. Prefer the installed database, generated build metadata, application tests,
   and observed transformations when they disagree with compatibility guidance.
6. For numerical changes, compare complete pipelines, grids, epochs, axis order,
   and database records before treating a result difference as a regression.

## Reference index

| Reference | Topics |
| --- | --- |
| [build-and-runtime.md](references/build-and-runtime.md) | CMake, C++17, embedded resources, TLS, network grids, WebAssembly, packaging |
| [crs-formats-and-database.md](references/crs-formats-and-database.md) | EPSG/ESRI data, WKT, PROJJSON, identification, aliases, operation methods |
| [operation-selection.md](references/operation-selection.md) | Compound and vertical CRS operations, realization transforms, epochs, extent filtering |
| [projections-and-geodesy.md](references/projections-and-geodesy.md) | Projection additions and numerical changes, geodesic APIs |
| [bounds-cli-and-context.md](references/bounds-cli-and-context.md) | Bounds transforms, `projinfo`, cloning, lookup, library integration |

## Highest-impact compatibility checks

### Account for the EPSG database rollback

Treat the database bundled with 9.8.1 as EPSG 12.029, not 12.049. Records added
with 9.8.0, chiefly `ETRS89-XXX` national datum and CRS definitions, are absent
after the rollback. Do not assume a failure to find those records is an API
failure.

When deployment behavior differs:

1. Record both the PROJ library version and database metadata.
2. Check whether the application relies on an `ETRS89-XXX` national
   realization added with the newer database.
3. Avoid copying a 9.8.0 database into a 9.8.1 installation without validating
   transformation behavior and packaging expectations.
4. Re-run operation discovery for Austria, Belgium, Catalonia, the Netherlands,
   Romania, and Serbia; the rollback specifically avoids ETRS89 regressions
   affecting those areas.

See [crs-formats-and-database.md](references/crs-formats-and-database.md).

### Expect corrected transformation choices

Do not pin a pipeline merely because an older release selected it. Operation
selection now handles more vertical, compound, realization, and epoch cases.
Changed results may reflect a corrected pipeline rather than numerical drift.

Check these inputs:

- Source and target CRS dimensionality.
- Vertical datum identity and units.
- Coordinate epoch for time-dependent transformations.
- Required grids and their actual download location.
- `CRS_EXTENT_USE`, visualization normalization, and desired longitude
  overrange behavior.
- Whether a cloned `PJ` retains all source flags.

See [operation-selection.md](references/operation-selection.md).

### Revalidate corrected projection numerics

Update golden values when they encoded earlier defects. In particular, verify:

- Wagner VI results after its parameter correction.
- Inverse authalic-latitude results for equal-area projections.
- Antimeridian and global bounds calculations.
- Spherical Transverse Mercator values at the latitude of origin.
- Projected CRS identification when input and candidate ellipsoids differ.

Use tolerances appropriate to the operation, but do not widen tolerances before
confirming that the selected pipeline and database are equivalent.

See [projections-and-geodesy.md](references/projections-and-geodesy.md) and
[bounds-cli-and-context.md](references/bounds-cli-and-context.md).

## Build and deployment quick reference

### Require a C++17-capable toolchain

Compile PROJ and downstream C++ integration with C++17 support. If a build
environment previously relied on an older language mode, update the compiler,
standard-library configuration, and consumer target features together.

### Choose an embedded-resource mode deliberately

Use the CMake switches as a coordinated set:

```sh
cmake -S . -B build \
  -DEMBED_RESOURCE_FILES=ON \
  -DUSE_ONLY_EMBEDDED_RESOURCE_FILES=ON \
  -DEMBED_RESOURCE_DIRECTORY=/path/to/resources
```

`EMBED_RESOURCE_FILES` embeds `proj.db` and `proj.ini`.
`USE_ONLY_EMBEDDED_RESOURCE_FILES` restricts use to embedded resources.
`EMBED_RESOURCE_DIRECTORY` adds `.tif` and `.json` resources to `libproj`.

Test the exact compiler and platform combination. Older compilers must not be
treated as supporting C23 `#embed`, and Windows supports enabling both resource
switches together.

### Configure native trust stores explicitly

Set `native_ca` in `proj.ini` or its `PROJ_NATIVE_CA` environment equivalent
when curl should use the operating-system CA store. Include SSL connection
timeouts in network-failure tests because PROJ retries that failure mode.

### Treat WebAssembly fetching as platform-specific

Expect Emscripten builds to retrieve remote resources through Emscripten Fetch.
Exercise browser policy, URL reachability, caching, and error behavior in the
actual WebAssembly deployment rather than assuming native curl behavior.

See [build-and-runtime.md](references/build-and-runtime.md).

## CRS parsing and serialization quick reference

### Accept the Projected CRS `base_crs.type`

When validating PROJJSON for a Projected CRS, allow an explicit `type` member in
`base_crs`. Its value is `GeographicCRS` or `GeodeticCRS`. Update strict schemas
and structural equality fixtures accordingly.

### Handle `DEFININGTRANSFORMATION` conservatively

The WKT2 parser accepts `DEFININGTRANSFORMATION`, but does not apply its
contents. Parsing success therefore does not prove that the defining
transformation affected the resulting object or coordinate operation.

### Permit empty datum ensembles

Allow WKT and PROJJSON datum ensembles with no members. Do not reject them in a
wrapper solely because earlier PROJ versions did.

### Expect legacy-name recognition to improve

Name lookup and identification accept more historical EPSG and ESRI spellings,
direction abbreviations, missing zones or heights, and `_IntlFeet` names.
Preserve authority identifiers when available; use fuzzy names as an import
compatibility path, not as a canonical serialization format.

See [crs-formats-and-database.md](references/crs-formats-and-database.md).

## Bounds and API quick reference

### Use the bounds API that matches dimensionality

Use `proj_trans_bounds()` for ordinary bounds, including a CompoundCRS target.
Use `proj_trans_bounds_3D()` when the bounds themselves are three-dimensional.
Retest extrema rather than transforming only corners: bounds processing samples
the source grid to capture transformed extrema.

For antimeridian-crossing geographic input, use a release containing the
regression fix and keep a focused test. A `PJ*` created directly from a PROJ
pipeline is also valid in cases that previously errored.

### Use new library entry points without reproducing CLI code

Use `proj_geod_direct()` for a direct geodesic calculation with a `PJ`
transformation object. For embedded `projinfo` behavior, include
`projapps_lib.h` and use the exposed library functionality instead of scraping
command output.

### Preserve context and clone semantics

Expect `proj_clone()` to carry configuration flags, including
`errorIfBestTransformationNotAvailable` and `FORCE_OVER=YES`. After
`proj_download_file()` succeeds, expect caches associated with that file to be
invalidated in the current context.

See [bounds-cli-and-context.md](references/bounds-cli-and-context.md).

## Validation checklist

- Confirm the actual library and database pair.
- Rebuild with a C++17-capable toolchain.
- Verify resource mode, grid availability, CA configuration, and fetch backend.
- Parse and serialize representative WKT, PROJJSON, and legacy ESRI inputs.
- Compare operation pipelines before comparing final coordinates.
- Supply coordinate epochs for time-dependent cases.
- Exercise compound and vertical CRS transformations in both directions.
- Test antimeridian, global, 3D, and pipeline-created bounds objects.
- Refresh numerical fixtures only after identifying the relevant correction.
- Consult every linked topic that affects the changed behavior.
