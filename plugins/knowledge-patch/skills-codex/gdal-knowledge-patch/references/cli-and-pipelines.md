# CLI and Pipelines

## Unified command structure and output contracts

- **Unified front end (3.11.0).** The `gdal` command groups operations into
  subcommands. Initial additions include `gdal raster calc`,
  `raster resclassify`, `raster tile` (a C++ port of `gdal2tiles`),
  `gdal vsi list/copy/delete/move/sync`, and `gdal driver {driver_name}`. The
  algorithm framework is also available through C, C++, and Python, and Bash
  completion is installed.

- **Moved vector subcommands (3.12-migration).** `buffer`,
  `explode-collections`, `make-valid`, `segmentize`, `simplify`, and `swap-xy`
  moved from `gdal vector geom` directly under `gdal vector`.
  `gdal vector geom set-type` became `gdal vector set-geom-type`. The old paths
  are 3.12-only compatibility paths and are removed in 3.13.

- **Progress and default output (3.12-migration).** CLI progress goes to
  standard output unless `--quiet`/`-q` is used. `gdal raster info`,
  `gdal vector info`, and `gdal vsi list` default to text at the command line;
  API calls keep JSON defaults.

- **Input/output argument names (3.13-migration).** Unified commands prefer
  `--input` and `--output` over `--src` and `--dst`. The older names remain
  accepted by the command line and C, C++, and Python APIs.

- **Expanded unified CLI (3.13.0).** New vector commands include `combine`,
  `concave-hull`, `convex-hull`, `create`, `dissolve`, `export-schema`,
  `update`, `rename-layer`, and `sort`. `gdal dataset check` is new, and COG
  and GeoPackage validation live under `gdal driver`.

- **Multidimensional summaries (3.13.0).** `gdal mdim info --summary` emits
  abbreviated output; `gdal mdim mosaic` accepts dimensions without indexing
  variables.

## Pipeline composition and materialization

- **Streamed vector datasets (3.11.0).** The read-only GDALG driver represents
  an on-the-fly vector dataset by replaying compatible `gdal` command lines,
  acting as a VRT-like format for streamed algorithm pipelines.

- **Composite pipelines (3.12.0).** `gdal pipeline` can mix raster and vector
  stages, nest pipelines, and branch with `tee`. A stored pipeline can be run
  while overriding or adding parameters.

- **Pipeline source and terminal stages (3.12.0).** `fill-nodata`, `proximity`,
  `sieve`, and `viewshed` can be steps. `mosaic` and `stack` can start a raster
  pipeline. Raster tiling can terminate one.

- **Pipeline-supplied inputs (3.12.1).** Raster `compare`, `info`, and `tile`
  accept a dataset supplied outside the pipeline string. `calc` accepts files
  represented by nested pipelines.

- **Nested multi-input stages (3.12.4).** Nested pipeline definitions work
  when a stage such as vector concatenation accepts several datasets. A raster
  `edit` stage can follow an anonymous VRT-producing stage.

- **Selected-layer SQL (3.12.4).** In a vector pipeline, `read --layer`
  forwards `ExecuteSQL()` to the source, allowing a selected-layer read to feed
  a later `sql` step.

- **External and multi-output stages (3.13.0).** Pipelines add `external` for
  executing an external command. `_` can select a non-first dataset emitted by
  the previous stage. Unified `--append` creates the target if it is absent.

- **Named materialization (3.13.1).** A named `materialize` output infers its
  format, so `... ! materialize --output my.tif ! tile` is valid.

- **Anonymous COG materialization (3.13.2).** An unnamed COG can flow directly
  to tiling:

  ```text
  gdal raster pipeline read byte.tif ! materialize --format COG ! tile
  ```

- **OSM/PBF pipelines (3.13.2).** Pipelines can read OSM or PBF, perform an
  operation and filter, and write the result correctly.

- **Filtered limits (3.13.2).** `gdal vector limit` applies dataset filters
  before limiting the stream.

## Raster command families

- **Initial raster utility expansion (3.11.0).** `gdalbuildvrt` adds `-co` and
  `-resolution same|compatible`; `gdaldem` derives scale from the CRS and adds
  `-xscale`/`-yscale`; `gdallocationinfo` can query corners;
  `rgb2pct` adds `--creation-option`; `gdal2xyz` writes VSI paths; and
  `gdalenhance` is installed and documented.

- **Stricter raster utility behavior (3.11.0).** `gdal_translate -projwin`
  transforms full bounds and includes partly covered pixels. Translation and
  warping reject invalid numeric options. Nodata copies only when exactly
  representable. Polygonized contours omit min/max fields, and `gdal2tiles`
  applies source nodata without reprojection.

- **Overview controls (3.11.1).** `gdal raster overview add` accepts `-r none`.
  COG cleanup through `gdaladdo` or unified overview commands reports
  `IGNORE_COG_LAYOUT_BREAK`; `-clean` automatically enables it and does not
  break the layout.

- **Tiling exclusions (3.11.1).** `gdal raster tile` supports
  `--excluded-values`, `--excluded-values-pct-threshold`, and
  `--nodata-values-pct-threshold`.

- **Raster JSON output (3.11.1).** `gdalinfo` JSON renders integer-band nodata
  as an integer, attaches the raster attribute table as `rat`, and omits
  `wgs84Extent` and `extent` for ungeoreferenced images.

- **Expanded raster operations (3.12.0).** Unified commands add
  `as-features`, `blend`, `compare`, `neighbors`, `nodata-to-alpha`,
  `pansharpen`, `proximity`, `rgb-to-palette`, `update`, and `zonal-stats`.

- **Calculation and composition options (3.12.0).** `raster calc` handles
  nodata, adds `--flatten`, and supports `--dialect=muparser|builtin`.
  `mosaic` accepts `--pixel-function` and `--pixel-function-arg`; `mosaic` and
  `stack` accept `--absolute-path`.

- **Edit, clip, and overview inputs (3.12.0).** `raster clip` accepts
  `--window <column>,<line>,<width>,<height>`. `raster edit` accepts `--gcp` and
  `--unset-metadata-domain`. `raster overview add` can use `--overview-src` and
  forwards `--creation-option`/`--co`; `gdalbuildvrt` adds
  `-write_absolute_path`.

- **Reprojection, resize, tile, and viewshed (3.12.0).** `raster reproject`
  adds `-j`/`--num-threads` and defaults to `ALL_CPUS`; `resize` adds
  `--resolution`. Tiling supports `--parallel-method=fork` on non-Windows and
  `spawn`, and emits `stacta.json`. Viewshed adds angular, pitch, and
  minimum-distance masking.

- **Windows spawn tiling (3.12.1).** `gdal raster tile
  --parallel-mode=spawn` no longer stalls on Windows when `CPL_DEBUG=ON`.

- **Correct STAC JSON (3.12.1).** `gdalinfo -json` writes
  `stac:transform` coefficients in the correct order and sets
  `[stac][raster:bands][0][nodata]` for floating-point datasets.

- **Target alignment requires resolution (3.12.2).** Raster mosaic rejects
  `--target-aligned-pixels` unless `--resolution` is supplied.

- **Option parity (3.12.3).** Pipeline `raster contour`, `raster polygonize`,
  and `vector select` expose `--output-layer`. Standalone `raster edit` exposes
  input open options through `--oo`.

- **Nodata feature filtering (3.12.4).** `gdal raster as-features
  --skip-nodata` keeps features that were incorrectly omitted before.

- **Bundled JSON schemas (3.12.4).** The supplied `gdalinfo` and `ogrinfo`
  JSON schemas validate correctly after fixes to their schema definitions.

- **Raster creation and editing (3.13.0).** Raster creation is a pipeline step
  and copies `--like` tiling when possible. Editing can set color
  interpretation, scale, offset, and a color map, or remove a color table.

- **Index and identify workflows (3.13.0).** `gdal raster index` supports a
  `STAC-GeoParquet` profile and `filename`, `md5`, or `metadata-item` ID
  methods, plus metadata-name and base-URL controls. `gdal dataset identify
  --detailed` can write through any writable vector driver. Text raster/vector
  info accepts `--crs-format=AUTO|WKT2|PROJJSON`.

- **Sampling, selection, and reprojection (3.13.0).** `raster pixel-info` can
  promote values to Z, take position datasets/layers, carry selected fields,
  write output, and run in a pipeline. Raster selection accepts color names
  such as `red`, `alpha`, and `nir` plus `--exclude`; reproject adds `--like`.

- **Palette, zonal, and rasterize controls (3.13.0).** `rgb-to-palette` adds
  `--output-nodata`, `--no-dither`, and `--bit-depth`. Zonal statistics accepts
  `--include-field ALL|NONE`, `--include-geom`, and an output layer.
  Rasterization derives one output dimension from the other and input extent
  when one requested size is zero.

- **Automatic tiling overview (3.13.1).** `gdal raster tile` selects a suitable
  source overview automatically.

- **Tiling pipeline stdout (3.13.1).** A `gdal raster pipeline ... ! tile`
  sequence does not print the output filename to standard output.

## Vector and dataset command families

- **Expanded vector/dataset operations (3.12.0).** New commands include
  `gdal vector check-coverage`, `check-geometry`, `clean-coverage`, `index`,
  `layer-algebra`, `make-point`, `partition`, `set-field-type`, and
  `simplify-coverage`; pipelines add `limit`. `gdal mdim mosaic` is new, and
  `gdal dataset` replaces `gdal manage` functionality.

- **Update and inspection (3.12.0).** `gdal vector convert` can update existing
  output and accepts output open options. `vector write` and `convert` add
  `--upsert`; `vector sql --update` modifies data in place. Extensionless
  output no longer defaults to Shapefile. Text `vector info` requires
  `--features` to emit features and accepts `--limit`.

- **Three-dimensional validation (3.12.1).** `gdal vector make-valid` processes
  3D geometries instead of skipping them.

- **Geometry-check fields (3.12.1).** `gdal vector check-geometry` accepts
  `--include-field`.

- **SQL layer overwrite (3.12.1).** `gdal vector sql --overwrite-layer`
  performs the requested replacement.

- **Dataset copy and rename (3.12.3).** `gdal dataset copy` and `rename` work
  with vector datasets and directories.

- **Restored ESRI WKT output (3.12.3).** `gdalinfo -wkt_format WKT1_ESRI`
  works again.

- **Reprojected index extents (3.12.3).** `gdaltindex` uses GDALWarp for
  reprojected extents; `gdal2tiles` computes correct extents for non-square
  source pixels.

- **Vector workflow preservation (3.13.0).** Unified algorithms propagate
  field domains, relationships, and metadata. Filtering adds
  `--update-extent`, info adds `--fid`, and pipelines support
  `--no-create-empty-layers`.

- **Partition workflows (3.13.0).** `gdal vector partition` can partition by
  geometry type, makes `--field` optional, and creates a Parquet `_metadata`
  index. `gdal driver parquet create-metadata-file` builds the same index
  separately.

- **Conversion failures (3.13.0).** `ogr2ogr` fails by default if destination
  field creation fails unless `-skip` is used. It and `gdal vector convert`
  warn when output cannot preserve curve, Z, or M geometry.

- **Curve clipping (3.13.2).** `gdal vector clip` works with curve-typed
  layers.

## Legacy utility compatibility and status

- **Restored standard output and option (3.10.1).** `gdalinfo` streams to
  standard output again, and `gdaltindex -ot` is restored.

- **Large argument files (3.11.2).** `ogrinfo`, `ogr2ogr`, `gdal vector sql`,
  and related vector tools accept `@filename` files up to 10 MB.

- **Utility result status (3.11.4).** `gdal mdim info` returns zero on success.
  `gdal_footprint` reports failure when its only input feature cannot be
  simplified. `gdal_viewshed` sets the DEM lower bound from input.

- **Large concatenations (3.11.4).** `gdal vector concat` accepts more than
  1,000 input files.

- **Leading-space merge paths (3.12.3).** `ogrmerge.py` accepts input names
  beginning with spaces.

- **VRT error status (3.13.2).** `ogr2ogr` returns nonzero when VRT processing
  reports an error.

- **Removed unofficial applications (3.11.0).** `gdalwarpsimple` and
  `ogrdissolve` were removed along with the OpenCL warper.
