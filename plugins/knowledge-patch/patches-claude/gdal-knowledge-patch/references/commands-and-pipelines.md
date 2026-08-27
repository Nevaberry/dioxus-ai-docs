# Commands, algorithms, and pipelines

## Unified command family

### Core front end and algorithm registry (`3.11.0`)

The `gdal` front end groups raster, vector, multidimensional, VSI, dataset, and
driver work. Initial commands include `gdal raster calc`, `resclassify`, and
`tile`, `gdal vsi list|copy|delete|move|sync`, and `gdal driver DRIVER`.
`gdal raster tile` is a C++ port of `gdal2tiles`. The framework is callable
through C, C++, and Python and installs Bash completion.

The read-only GDALG driver stores a compatible vector command line and replays
it as a streamed, on-the-fly dataset—a streamed-pipeline counterpart to VRT.

### Command path and default migrations (`3.12-migration`)

The geometry operations `buffer`, `explode-collections`, `make-valid`,
`segmentize`, `simplify`, and `swap-xy` move from `gdal vector geom` directly
under `gdal vector`. `geom set-type` becomes `vector set-geom-type`. Old paths
are temporary compatibility aliases and are removed in the next command-family
transition.

Progress is written to stdout unless `--quiet` or `-q` is set. CLI invocations
of raster info, vector info, and VSI list default to text, while API calls keep
their JSON defaults.

### Input and output names (`3.13-migration`)

Unified arguments increasingly use `--input` and `--output` instead of
`--src` and `--dst`. The old spellings remain accepted by CLI and C, C++, and
Python APIs where provided.

## Pipeline composition

### Composite, nested, and reusable pipelines (`3.12.0`)

`gdal pipeline` can mix raster and vector stages. It supports nested pipelines,
`tee`, and running an existing pipeline while overriding or adding parameters.
Raster `mosaic` and `stack` may begin a pipeline; `fill-nodata`, `proximity`,
`sieve`, and `viewshed` may be stages. Vector pipelines add `limit`.

### External and multi-output stages (`3.13.0`)

Use `external` to invoke an external command. The `_` placeholder dataset name
selects a non-first dataset from the preceding stage. Commands using `--append`
create the target if it does not already exist.

Named materialization infers format from its output (`3.13.1`):

```text
... ! materialize --output my.tif ! tile
```

An anonymous COG can be materialized and tiled directly (`3.13.2`):

```text
gdal raster pipeline read byte.tif ! materialize --format COG ! tile
```

### Pipeline corrections and constraints

- Raster `compare`, `info`, and `tile` accept an input passed outside the
  pipeline string; `calc` accepts nested-pipeline inputs (`3.12.1`).
- Nested pipelines accept multi-input stages such as vector concatenation, and
  raster `edit` can follow an anonymous VRT stage (`3.12.4`).
- A selected-layer `read --layer` forwards `ExecuteSQL()` so a following SQL
  stage sees the selected layer (`3.12.4`).
- OSM/PBF read, operate, filter, and write pipelines execute correctly
  (`3.13.2`).
- `gdal vector limit` applies dataset filters before limiting (`3.13.2`).
- A raster pipeline ending in `tile` does not print the output filename to
  stdout (`3.13.1`).

## Raster commands

### Broad raster operation set (`3.12.0`)

Unified raster adds `as-features`, `blend`, `compare`, `neighbors`,
`nodata-to-alpha`, `pansharpen`, `proximity`, `rgb-to-palette`, `update`, and
`zonal-stats`.

`calc` handles nodata, accepts `--flatten`, and selects
`--dialect=muparser|builtin`; the built-in dialect can combine all bands of one
input into one output. `mosaic` accepts `--pixel-function` and its arguments;
`mosaic` and `stack` accept `--absolute-path`.

`clip` accepts `--window column,line,width,height`. `edit` adds `--gcp` and
`--unset-metadata-domain`. `overview add` accepts `--overview-src` and forwards
creation options with `--creation-option`/`--co`. `gdalbuildvrt` adds
`-write_absolute_path`.

`reproject` adds `-j`/`--num-threads` and defaults to `ALL_CPUS`; `resize` adds
`--resolution`. Tiling supports `--parallel-method=fork` off Windows or
`spawn`, emits `stacta.json`, and can terminate a pipeline. Viewshed adds
angular, pitch, and minimum-distance masking.

### Later raster workflow expansion (`3.13.0`)

`blend` adds multiply, screen, overlay, hard-light, darken, lighten,
color-dodge, and color-burn. Raster creation becomes a pipeline stage and
copies `--like` tiling where possible. Editing can set color interpretation,
scale, offset, and color map or remove a color table.

`raster index` adds a `STAC-GeoParquet` profile, `filename`, `md5`, and
`metadata-item` identifiers plus metadata-name and base-URL controls.
`dataset identify --detailed` can write through any writable vector driver.
Text raster/vector info accepts `--crs-format=AUTO|WKT2|PROJJSON`.

`pixel-info` can promote samples to Z, take position datasets/layers, retain
selected fields, write a dataset, and run in a pipeline. Selection accepts
color interpretations such as `red`, `alpha`, and `nir`, plus `--exclude`.
Reprojection adds `--like`.

`rgb-to-palette` adds `--output-nodata`, `--no-dither`, and `--bit-depth`.
Zonal statistics adds `--include-field ALL|NONE`, `--include-geom`, and output
layer selection. Rasterization derives the missing output dimension from the
other dimension and input extent when one requested size is zero.

### Raster utility compatibility and fixes

- `gdal_rasterize -ts` accepts floating-point sizes (`3.10.2`).
- `gdaldem -az` accepts zero and negative azimuths (`3.10.3`). Aspect, TPI, and
  TRI are correct for non-north-up rasters, and hillshade, slope, and roughness
  are correct on rotated sources (`3.11.5`).
- `gdalinfo` again streams to stdout and `gdaltindex -ot` is restored
  (`3.10.1`). `gdalinfo -wkt_format WKT1_ESRI` is restored (`3.12.3`).
- `gdal_translate` and warp reject invalid numeric options; translation nodata
  is copied only when exactly representable (`3.11.0`).
- `gdal_translate -projwin` includes partially covered pixels and transforms
  full bounds (`3.11.0`).
- `gdalbuildvrt` adds `-co` and `-resolution same|compatible`; it later warns
  when `-separate` nodata is outside the target type (`3.11.0`, `3.13.1`).
- `gdaldem` derives scale from the CRS and adds `-xscale`/`-yscale`;
  `gdallocationinfo` can query corners (`3.11.0`). Nodata queries in
  `gdallocationinfo` are restored (`3.11.2`).
- `rgb2pct` accepts `--creation-option`; `gdal2xyz` writes VSI targets;
  `gdalenhance` is installed and documented (`3.11.0`).
- Polygonized contours omit min/max fields, and `gdal2tiles` applies source
  nodata even without reprojection (`3.11.0`).
- `gdal2tiles` computes correct extents for non-square source pixels
  (`3.12.3`).

### Overviews, tiling, and GTI

`gdal raster overview add -r none` is valid. COG cleanup exposes the
`IGNORE_COG_LAYOUT_BREAK` message; `-clean` enables the option automatically
and does not break COG layout (`3.11.1`). Timestamp-based partial refresh works
for GTI as well as VRT.

Raster tile supports excluded-value and nodata-percentage thresholds
(`3.11.1`). Spawn mode no longer stalls on Windows with `CPL_DEBUG=ON`
(`3.12.1`). It later chooses a suitable source overview automatically
(`3.13.1`).

### Output and status contracts

JSON `gdalinfo` emits integer nodata as an integer, includes a `rat` object,
and omits `wgs84Extent`/`extent` for ungeoreferenced images (`3.11.1`). STAC
transform coefficient order and floating nodata output were corrected in
`3.12.1`.

`gdal mdim info` exits zero on success. `gdal_footprint` reports failure when
its only feature cannot be simplified, and `gdal_viewshed` initializes its DEM
lower bound from input (`3.11.4`).

`gdal raster mosaic --target-aligned-pixels` requires `--resolution`
(`3.12.2`). `raster as-features --skip-nodata` retains valid features
(`3.12.4`).

The bundled JSON schemas for `gdalinfo` and `ogrinfo` validate correctly
(`3.12.4`).

Pipeline `raster contour`, `raster polygonize`, and `vector select` expose
`--output-layer`; standalone raster edit exposes `--oo` (`3.12.3`). Raster
calc accepts ungeoreferenced inputs. `dataset copy` and `dataset rename`
support vector datasets and directories.

## Vector commands

### Vector operation set (`3.12.0`)

Unified vector adds `check-coverage`, `check-geometry`, `clean-coverage`,
`index`, `layer-algebra`, `make-point`, `partition`, `set-field-type`, and
`simplify-coverage`. `vector convert` can update an existing destination and
accept output open options. `vector write` and `convert` accept `--upsert`, and
`vector sql --update` changes data in place.

Conversion no longer assumes Shapefile merely because an extensionless output
lacks `.shp`. Text vector info requires `--features` to emit rows and accepts
`--limit`.

### Later vector operation set (`3.13.0`)

Commands add `combine`, `concave-hull`, `convex-hull`, `create`, `dissolve`,
`export-schema`, `update`, `rename-layer`, and `sort`. `dataset check` and
driver-level COG/GeoPackage validators are also available.

Unified vector algorithms preserve field domains, relationships, and metadata.
Filtering can use `--update-extent`, info can select `--fid`, and pipelines can
avoid empty layers with `--no-create-empty-layers`.

Partitioning can group by geometry type, makes `--field` optional, and creates
Parquet `_metadata`; `gdal driver parquet create-metadata-file` builds that
index independently.

### Vector corrections and stricter failures

- Exact non-rectangular `ogr2ogr -clipsrc`/`-clipdst` rejects features that
  intersect only the clip envelope (`3.10.2`).
- `ogr2ogr -upsert` accepts GeoPackage sources (`3.10.3`).
- `ogr2ogr` and unified vector tools accept `@filename` files up to 10 MB
  (`3.11.2`).
- `gdal vector concat` accepts more than 1,000 inputs (`3.11.4`).
- `make-valid` processes 3D geometries; `check-geometry` adds
  `--include-field`; `vector sql --overwrite-layer` performs replacement
  (`3.12.1`).
- `gdaltindex` uses GDALWarp for reprojected extents (`3.12.3`).
- `vector clip` supports curve layer types (`3.13.2`).
- `ogrlineref` accepts a one-part `MULTILINESTRING` and handles invalid input
  geometry safely (`3.13.2`).
- `ogr2ogr` returns nonzero when VRT processing fails (`3.13.2`).
- `ogrmerge.py` accepts input paths beginning with spaces (`3.12.3`).
- Destination field-creation failure is fatal unless `-skip` is used;
  conversion warns when curve, Z, or M cannot be retained (`3.13.0`).

## Multidimensional and dataset commands

`gdal mdim mosaic` and `gdal dataset` replace or expand older management
workflows (`3.12.0`). `gdal mdim convert` accepts repeated `--group`, `--subset`,
and `--scale-axes` values (`3.12.1`). `mdim info --summary` emits abbreviated
output, and `mdim mosaic` accepts dimensions without indexing variables
(`3.13.0`).

## Python command equivalents

The dynamically generated `gdal.alg` namespace mirrors the algorithm registry
(`3.12.0`):

```python
gdal.alg.raster.convert(input="in.tif", output="out.tif")
```

The functions accept a `progress` keyword (`3.12.1`) and visible or hidden
argument aliases (`3.13.0`). Python `gdal.Translate()` adds
`colorInterpretation`, and `gdal.TileIndex()` corrects the same argument
(`3.10.1`).
