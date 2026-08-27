---
name: gdal-knowledge-patch
description: GDAL
version: "3.13.2"
license: MIT
metadata:
  author: Nevaberry
---


# GDAL Knowledge Patch

Use this skill when changing GDAL applications, bindings, out-of-tree drivers,
builds, command lines, pipelines, or data-access configuration. Inspect the
project's manifest and linked GDAL at runtime before applying version-sensitive
advice. Prefer the project's headers, generated API documentation, tests, and
observed driver metadata when they disagree with assumptions.

## Reference index

| Reference | Topics |
| --- | --- |
| [Bindings, Build, and Packaging](references/bindings-build-and-packaging.md) | Dependency compatibility, CMake, installed headers, Python, Java, C#, and SWIG |
| [CLI and Pipelines](references/cli-and-pipelines.md) | Unified commands, pipeline composition, utility options, output, and failure semantics |
| [Migrations and Core API](references/migrations-and-core-api.md) | C/C++ source migrations, ABI changes, CPL, dataset, geometry, CRS, and algorithm APIs |
| [Multidimensional Data and Georeferencing](references/multidimensional-and-georeferencing.md) | Multidimensional arrays, HDF, netCDF, transforms, geolocation, and slicing |
| [Raster Formats](references/raster-formats.md) | GeoTIFF/COG, imagery, scientific, hydrographic, and tiled raster drivers |
| [Raster Processing](references/raster-processing.md) | Warp, resampling, nodata, VRT, overviews, statistics, contours, and pansharpening |
| [Vector Formats and Databases](references/vector-formats-and-databases.md) | OGR formats, SQL databases, Arrow/Parquet, schemas, services, and vector geometry |
| [Virtual Filesystems and Cloud](references/virtual-filesystems-and-cloud.md) | VSI paths, cloud authentication, HTTP, caching, redirects, sync, and archives |

## Upgrade checks first

### Update out-of-tree driver signatures

For the 3.11 API transition:

- Include `gcore/gdal_fwd.h` instead of redeclaring public opaque types.
- Override protected `IGetExtent()`/`IGetExtent3D()` hooks rather than the
  checked public extent methods.
- Override `ISetSpatialFilter()` and return/check `OGRErr` from spatial-filter
  calls.
- Handle `GDT_Float16` and `GDT_CFloat16`; request `GDT_Float32` conversion
  when native half precision is unsuitable.
- Treat partial coordinate-transform failure as aggregate failure and inspect
  the per-point success or error-code arrays.

For the 3.12 API transition:

- Make dataset and layer inspection overrides const-correct and store returned
  layer definitions and spatial references through const pointers.
- Handle `GFT_Boolean`, `GFT_DateTime`, and `GFT_WKBGeometry`; check the
  `CPLErr` returned by raster-attribute-table mutation.
- Change geotransform overrides from six-double pointers to
  `GDALGeoTransform` references.
- Do not assume raw-file VRT bands have unrestricted access; honor the runtime
  policy and the build-time raw-band gate.

For the 3.13 API transition:

- Check `OGRErr` from C point-setting and point-adding functions.
- Replace `MIN`, `MAX`, and `ABS` from GDAL headers with `CPL_MIN`, `CPL_MAX`,
  and `CPL_ABS`; arrange your own `M_PI` declaration.
- Update `GDALDataset::Close()` overrides for progress arguments and option
  lists to `CSLConstList` where required.
- Treat metadata lists as const and update custom VSI `Read()`/`Write()`
  overrides to the single-count form.
- Account for RasterIO resampling operating in the output buffer type unless
  `bOperateInBufType` is false.

### Audit removals, restorations, and binary compatibility

The 3.11 line removed many legacy raster and vector drivers, several writers,
the OpenCL warper, and unofficial utilities. It also redirected FileGDB writes
to OpenFileGDB, deprecated OGR `Memory` in favor of `MEM`, removed PDF
`GEO_ENCODING=OGC_BP`, and bumped the shared-library major version. GSBG,
GSAG, and BT were restored in later 3.11 maintenance releases; Tiger and UK
.NTF returned later as future-removal candidates. Never infer availability from
the initial removal list alone. Rebuild binary dependents whenever the shared
library major changes.

### Migrate unified command paths

The unified `gdal` front end covers raster, vector, multidimensional, dataset,
driver, and VSI work. In 3.12, several `gdal vector geom ...` operations moved
directly beneath `gdal vector`, and `geom set-type` became `set-geom-type`.
Update scripts to the direct paths. CLI info commands default to text while API
calls retain JSON defaults, and progress goes to standard output unless quiet.

The 3.13 command argument spelling favors `--input` and `--output`; older
`--src`/`--dst` aliases remain accepted. Avoid parsing incidental standard
output from tiling pipelines, and request JSON explicitly when automation
depends on it.

### Treat failure status as part of the API

- Check algorithm argument validation, cancellation, close-time progress,
  field-domain operations, raster-attribute mutations, and geometry mutations.
- `ogr2ogr` now fails by default when destination field creation fails; use
  `-skip` only when dropping fields is intentional.
- `ogr2ogr` also returns a nonzero status for VRT-processing errors.
- `INIT_DEST=NO_DATA` without a nodata value warns and zero-fills in 3.11.5,
  but fails in 3.13.0. Gate behavior when supporting both.
- GTI reads fail when a source is unreadable, missing Kerchunk and ADBC targets
  are errors, and contouring an all-nodata raster succeeds with empty output.

## High-value current workflows

### Compose algorithms and pipelines

Use the algorithm registry rather than shelling out when an in-process API is
needed. Python exposes dynamically generated `gdal.alg.*()` calls and accepts a
`progress` callback. Pipelines can mix raster and vector stages, nest other
pipelines, branch with `tee`, invoke `external`, override saved parameters, and
use `_` to select a non-first dataset emitted by a preceding stage.

Materialize intermediate data when a following stage requires a concrete
dataset. Named outputs infer their format, while an anonymous COG can flow
directly into `tile`. Keep filters before `gdal vector limit`; current behavior
applies the filtered stream.

### Use raster algebra and VRT expressions

Raster bands support arithmetic, comparisons, `AsType()`, common math and
aggregation functions, and `IfThenElse()`. VRT derived bands provide richer
aggregates, expressions, reclassification, constants, coordinate variables,
transpose and block controls. Ensure muparser is present for C++ VRT
expressions; exprtk is optional and increases library size.

For calculations, choose `--dialect=muparser|builtin` deliberately, account for
nodata, and use `--flatten` where required. The built-in dialect can reduce all
bands of one input to one output band. Inputs without geotransforms and nested
pipeline inputs are supported.

### Select correct warp and resampling semantics

Check per-point transform results, output-buffer data type, exact integer
nodata comparisons, and NaN nodata handling. Lanczos no longer has its old
half-valid-pixel threshold, RMS overview normalization changed, and sum
resampling no longer carries the earlier chunking artifacts. Use
`TransformBounds()` semantics for `-te` with `-te_srs`.

When `--target-aligned-pixels` is used for a raster mosaic, also provide
`--resolution`. Reprojection can use all CPUs by default, so set thread counts
explicitly when resource limits matter. For global or TPS warps, retain the
corrected longitude and `SOURCE_EXTRA=5` behavior.

### Handle modern raster types and COG creation

Treat `GDT_UInt8` as the canonical unsigned eight-bit type; `GDT_Byte` is an
alias. Support Float16/CFloat16 in dispatch, prediction, statistics, and nodata
paths. COG supports band/tile interleave, complex data, random-write creation,
and BigTIFF temporary files; multiband overview creation works through its
multithreaded path.

When translating a selected mask to COG, the mask becomes a regular alpha-tagged
band. Creation options for lossy JPEG XL require `JXL_LOSSLESS=NO`; otherwise
GTiff and COG warn. Do not assume a structurally valid COG needs GDAL's ghost
area for `LAYOUT=COG` reporting.

### Work safely with cloud and curl-backed paths

Authentication changes invalidate relevant cloud caches. Keep redirect
authorization scoped, especially for S3-like redirects, and use path-specific
controls for query strings, headers, connection limits, cache behavior, and
verbatim path handling. `/vsis3/` supports IAM Identity Center,
`credential_process`, directory buckets, and endpoint URLs with schemes.

Use permitted `header_file` names, expect `/vsicurl/` to fall back to a bounded
GET when size is absent from HEAD, and remember that multithreaded cloud sync
includes empty files. For Azure/ADLS, token and SAS settings are exposed in
handler option metadata.

### Preserve vector schemas and geometry fidelity

Unified vector algorithms propagate field domains, relationships, and metadata.
Conversion warns when curves, Z, or M cannot be preserved. Parquet supports
editable layers, geometry logical types, list variants, Timestamp With Offset,
Hive filtering, covering bounding boxes, partition metadata, and ignored-field
name collisions.

Expect geometry-producing operations to return richer types: edge-built
polygons may be multipolygons, polar reprojection closes polygon rings, and
GeoJSON export has explicit curve, measure, and coordinate-order controls.
PostGIS can use full-geometry intersection; select local or server-side spatial
filtering deliberately.

## Verification checklist

Before shipping a change:

1. Confirm the loaded GDAL version and shared-library ABI.
2. Query driver metadata for create, update, append, upsert, subdataset,
   reopen, close-visibility, and directory-oriented capabilities.
3. Exercise failure paths, progress interruption, and explicit `Close()` for
   buffered Arrow/Parquet or other long-running output.
4. Test representative nodata, mask, alpha, Float16, complex, and very large
   raster cases.
5. Test CRS axis mapping, partial failures, polar/global bounds, and
   geotransform consistency.
6. Run command automation with explicit output format and inspect exit status.
7. Test cloud paths with the intended credentials, redirects, cache policy,
   empty objects, and path normalization.
8. For bindings, test ownership, repeated closure, no-GIL execution where
   applicable, NumPy dtypes/strides, and option-list parsing.
