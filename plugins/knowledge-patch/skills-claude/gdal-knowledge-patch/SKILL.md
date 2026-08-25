---
name: gdal-knowledge-patch
description: GDAL
version: 3.13.2
license: MIT
metadata:
  author: Nevaberry
---


# GDAL Knowledge Patch

Use this skill when upgrading, building, extending, or operating GDAL, its unified
CLI, drivers, VSI handlers, or language bindings. Check project manifests and
runtime behavior first, then use the topic references below for compatibility
details and corrected behavior.

## Reference index

| Reference | Topics |
|---|---|
| [migration-and-api.md](references/migration-and-api.md) | C/C++ API migrations, ABI, RasterIO, algorithms, errors, and binding contracts |
| [commands-and-pipelines.md](references/commands-and-pipelines.md) | Unified CLI, pipelines, raster/vector commands, output defaults, and utility fixes |
| [cloud-vsi-build-and-bindings.md](references/cloud-vsi-build-and-bindings.md) | Build dependencies, CMake, cloud authentication, VSI/HTTP behavior, and language bindings |
| [raster-processing-and-formats.md](references/raster-processing-and-formats.md) | Warping, VRT, overviews, COG/GeoTIFF, imagery formats, and raster correctness |
| [vector-and-database-workflows.md](references/vector-and-database-workflows.md) | OGR formats, Arrow/Parquet, databases, services, geometry, and schema behavior |
| [multidimensional-and-scientific.md](references/multidimensional-and-scientific.md) | Multidimensional APIs, Zarr, netCDF, HDF, planetary, hydrographic, and scientific formats |

## Upgrade-critical changes

### Update public API overrides and call sites

- Use GDAL's declarations from `gcore/gdal_fwd.h`; do not redeclare public
  opaque types.
- Override `OGRLayer::IGetExtent()`/`IGetExtent3D()` and
  `ISetSpatialFilter()`. Public extent and spatial-filter entry points are
  checked, non-virtual methods; spatial-filter setters return `OGRErr`.
- Treat partial coordinate-transform failure as aggregate failure and inspect
  each point's success or error-code array.
- Update const-correct vector overrides and store returned layer definitions,
  spatial references, and metadata in const-qualified pointers or
  `CSLConstList`.
- Update `GDALGeoTransform` references, raster-attribute-table mutation return
  values, geometry point-mutation return values, `CSLConstList` option lists,
  progressive `Close()` overrides, and custom VSI `Read()`/`Write()` signatures.
- Replace `MIN`, `MAX`, and `ABS` with `CPL_MIN`, `CPL_MAX`, and `CPL_ABS`.
  Do not assume GDAL exports `M_PI`.
- Dispatch `GDT_Float16` and `GDT_CFloat16`; `GDT_UInt8` is canonical and
  `GDT_Byte` is its alias.

See [migration-and-api.md](references/migration-and-api.md) for exact signatures,
return semantics, RasterIO changes, and binding behavior.

### Audit ABI and driver availability

- Rebuild binary dependents when consuming the shared-library-major-version
  bump.
- Removed raster drivers include BLX, CTable2, ELAS, FIT, GSBG, JP2Lura,
  Rasterlite v1, and several legacy grid/image formats; removed vector drivers
  include Geoconcept Export, OGDI, SDTS, SVG, Tiger, and UK .NTF. Some were
  restored later: GSBG, GSAG, BT, Tiger, and UK .NTF.
- FileGDB creation/update routes through OpenFileGDB. OGR `Memory` is deprecated
  in favor of `MEM`.
- The OpenCL warper and unofficial `gdalwarpsimple` and `ogrdissolve` programs
  are gone, as are several legacy writers.

### Migrate unified CLI paths and defaults

- Geometry commands moved from `gdal vector geom ...` to `gdal vector ...`;
  `set-type` became `set-geom-type`. The temporary old aliases do not survive
  the next command-family transition.
- Unified options increasingly use `--input` and `--output`; old `--src` and
  `--dst` spellings remain accepted where compatibility is documented.
- CLI progress goes to stdout unless quiet mode is selected. Raster info,
  vector info, and VSI list default to text in the CLI but retain JSON API
  defaults.
- Text-mode vector info requires `--features` to emit features.
- `ogr2ogr` fails when destination field creation fails unless `-skip` is
  supplied, and warns when curve, Z, or M geometry cannot be preserved.

See [commands-and-pipelines.md](references/commands-and-pipelines.md) before
porting scripts.

### Review security and numeric behavior

- Raw VRT bands have restricted file access by default. Account for
  `vrtrawrasterband_restricted_access`, the runtime
  `GDAL_VRT_ENABLE_RAWRASTERBAND` option, and the build-time switch.
- `/vsicurl?header_file=...` accepts only permitted filenames. Redirected
  credentials are not forwarded to S3-like targets.
- RasterIO resampling now operates in the output buffer type by default. Set
  `GDALRasterIOExtraArg::bOperateInBufType` to false only when the old behavior
  is explicitly required.
- Exact integer matching is used when statistics and histograms exclude integer
  nodata. NaN nodata and signed-byte warp paths also have corrected semantics.
- `INIT_DEST=NO_DATA` without a nodata value is an error; use
  `RESET_DEST_PIXELS` when an existing destination must be reset.

## High-value command and pipeline features

### Prefer the unified `gdal` command family

The front end covers raster, vector, multidimensional, VSI, dataset, driver,
and mixed pipeline operations. Notable workflow building blocks include:

- raster calculate, reclassify, tile, mosaic, stack, clip, edit, reproject,
  zonal statistics, blend, index, sample, select, create, and validate;
- vector validation, coverage cleaning, algebra, partitioning, schema export,
  update, sorting, filtering, SQL, and geometry processing;
- nested and composite pipelines, `tee`, `external`, named and anonymous
  `materialize`, multi-input stages, and parameter overrides;
- a dynamically generated Python `gdal.alg` namespace and C/C++ algorithm API.

Pipelines may pass anonymous VRT or COG results into later stages, select a
non-first output with `_`, and mix raster and vector stages. Consult
[commands-and-pipelines.md](references/commands-and-pipelines.md) for stage and
option constraints.

### Use raster algebra and richer VRTs

Raster bands support arithmetic, comparison, conversion, aggregate functions,
and conditional expressions. VRT derived bands add expression evaluation,
reclassification, constants, nodata-aware aggregate functions, `area`,
`quantile`, and `round`; `vrt://` adds transpose and block selection. Embedded
VRT sources and processed-VRT `OutputBands` make fileless composition possible.

### Use current pipeline output semantics

- `--append` creates a missing target.
- `materialize --output name.ext` infers its format; an unnamed materialized
  COG can feed `tile` directly.
- `gdal raster mosaic --target-aligned-pixels` requires `--resolution`.
- A tiled raster pipeline does not print its output filename to stdout.
- Raster tiling automatically selects a source overview and supports spawn or,
  off Windows, fork parallelism.

## High-value data and driver features

### Cloud-native raster access

- Zarr v3, Kerchunk JSON/Parquet reference stores, consolidated metadata,
  sharding, checksums, variable-length UTF-8, datetime/timedelta, multiscales,
  and spatial/proj georeferencing are supported.
- GTI accepts STAC GeoParquet metadata, SQL-selected tile sources, south-up
  tiles, cloud URL translation, SRS override/reprojection, and band/pixel
  interleave.
- STACTA supports Google and Azure URL schemes plus WEBP and JPEG XL tiles.
- COG supports band/tile interleave, complex types, random-write creation,
  reliable BigTIFF intermediates, and multithreaded multiband overviews.

See [raster-processing-and-formats.md](references/raster-processing-and-formats.md)
and [multidimensional-and-scientific.md](references/multidimensional-and-scientific.md).

### Modern vector and columnar workflows

- Arrow and Parquet support explicit close/flush, editable layers, GeoArrow,
  Parquet `GEOMETRY`, `LargeList`, string-view batches, Timestamp With Offset,
  partition metadata, and additional filtering/open controls.
- Unified vector operations propagate domains, relationships, and metadata;
  partitioning can use geometry type and can create Parquet `_metadata`.
- ADBC supports DuckDB, Parquet, and installed BigQuery drivers, with corrected
  missing-database and DuckDB compatibility behavior.
- GeoPackage, SQLite, PostGIS, WFS, OAPIF, ESRIJSON, GML, CSV, DXF, MVT, and
  service-driver changes are cataloged by workflow in the vector reference.

## Operational checklist

1. Identify the exact GDAL runtime and build configuration actually used.
2. Before an upgrade, audit custom drivers, VSI handlers, C/C++ overrides,
   removed drivers, CLI paths, and binary compatibility.
3. Validate raw-VRT policy, redirect/authentication behavior, and cloud cache
   assumptions.
4. Re-run raster golden tests around resampling, nodata, masks, overviews,
   warping, geotransforms, and Float16/Int8 paths.
5. Re-run vector tests around geometry dimensionality, spatial filters,
   Arrow/Parquet field selection, field domains, and transactional counts.
6. Explicitly close output datasets where a driver flushes pending data at
   close time, and inspect returned errors or exceptions.
7. For a detailed fix or option, open the matching topic reference rather than
   inferring behavior from a nearby driver or command.
