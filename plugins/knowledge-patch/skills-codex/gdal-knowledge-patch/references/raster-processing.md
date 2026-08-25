# Raster Processing

## Warping and coordinate operations

- **Empty source windows (3.10.3).** MEM-backed warping handles an empty
  source window when nodata is nonzero.

- **Transformer and warp controls (3.11.0).** Transformers support Homography.
  The warper adds `MODE_TIES`, uses source-pixel coverage for mode resampling,
  and accepts a mode value of `-1`. Transformer options include
  `ALLOW_BALLPARK=NO`, `ONLY_BEST=AUTO|YES|NO`, source/destination axis mapping,
  and `HEIGHT_DEFAULT` for RPC fallback height. `ogr2ogr -ct_opt` exposes the
  ballpark, best-operation, and differing-operation-warning controls.

- **Bounds transformation (3.11.1).** With both `-te` and `-te_srs`,
  `gdalwarp` obtains the target extent through
  `OGRCoordinateTransformation::TransformBounds()`.

- **Direct COG reprojection (3.11.2).** `gdalwarp` can reproject directly to
  COG output again after the 3.11.0 regression.

- **Global and TPS warps (3.11.4).** Large/global warps, including world-scale
  WMTS input, no longer fail in the affected cases. Longitude spans of at
  least 360 degrees are not assigned an inappropriate `CENTER_LONG` when
  targeting Web Mercator. TPS defaults to `-wo SOURCE_EXTRA=5`.

- **Destination initialization transition.** With `INIT_DEST=NO_DATA` but no
  nodata value, 3.11.5 warns and initializes to zero without returning failure
  (3.11.5). The same request fails in 3.13.0; use
  `RESET_DEST_PIXELS=YES|NO` to reset an existing destination to nodata or zero
  when required (3.13.0).

- **Unified source nodata (3.12.2).** `UNIFIED_SRC_NODATA=YES` no longer
  triggers inappropriate destination-nodata avoidance.

- **Working types (3.12.3).** `GDALWarpResolveWorkingDataType()` considers band
  types before falling back to UInt8. Nearest-neighbor warping has a dedicated
  Int8 path, so signed bytes do not rely on unsigned-byte working behavior.

- **Multithread interruption (3.12.4).** Multithreaded warps detect progress
  cancellation more reliably, and a warp started from a worker thread avoids
  a possible deadlock.

- **Output-buffer calculation (3.13-migration).** RasterIO resampling and VRT
  work in the output buffer type by default. Set `bOperateInBufType=false` to
  opt out.

- **Lanczos validity semantics (3.13.1).** Lanczos no longer uses a special
  case when fewer than half the contributing pixels are valid; output near
  masks and nodata can differ.

- **Vertical-shift metadata (3.13.1).** A 3D-to-3D vertical-shift warp does not
  copy the source unit type to the output.

## Resampling, nodata, masks, and statistics

- **Nodata location queries (3.11.2).** `gdallocationinfo` again handles nodata
  correctly after the 3.10.0 regression.

- **Masks, half-precision NaNs, and constant histograms (3.11.4).**
  `GDALNoDataMaskBand::IRasterIO()` preserves Byte reads when
  `nLineSpace > nBufXSize`. Overview mode resampling accounts for NaN in
  Float16 and CFloat16. `GetDefaultHistogram()` handles constant non-Byte data
  where `min == max`.

- **Float precision in analysis (3.12.1).** `GDALFPolygonize()` processes
  Float64 at native precision. `ComputeStatistics()` corrects Float64 standard
  deviation under SSE2/AVX2 and uses Float64 precision for Float32 mean and
  standard deviation.

- **Zonal statistics bounds (3.12.1).** `GDALZonalStats` handles affected
  polygons outside the raster. `gdal raster zonal-stats` avoids integer
  overflow for extremely large geometry coordinates.

- **Complex source types (3.12.1).** `gdal raster calc` and
  `VRTDerivedRasterBand` use the correct computation and transfer types for a
  `ComplexSource`.

- **Sum resampling (3.12.1).** `gdalwarp -r sum` avoids the former
  chunk-processing artifacts.

- **NaN nodata resampling (3.12.4).** Bilinear, cubic, cubic-spline, and
  Lanczos correctly process NaN when band nodata is also NaN.

- **NaN to signed integers (3.13.1).** SSE2 `GDALCopyWords()` converts
  floating NaN to zero for signed 8-, 16-, and 32-bit integer output, matching
  the scalar path.

- **Exact integer nodata exclusion (3.13.2).** `ComputeRasterMinMax()` and
  `GetHistogram()` require exact integer equality when excluding nodata; cases
  that previously treated a different integer as nodata now produce different
  statistics.

## VRTs and derived raster bands

- **Processed source scale and offset (3.10.1).** A processed VRT reads scale
  and offset from its source dataset.

- **Expression and embedded-source composition (3.11.0).** VRT pixel
  functions support arbitrary expressions, reclassification, and `mul`/`sum`
  with a constant factor on one band. `<SimpleSource>` and `<ComplexSource>`
  can embed a `<VRTDataset>` instead of naming a file. Processed VRTs use
  `OutputBands` to declare output count and types.

- **Complete overview exposure (3.11.2).** A single-source VRT exposes all
  source overviews regardless of size. `VRTPansharpen` accepts source bands
  with differing overview counts when generating virtual overviews.

- **Pansharpened overview nodata (3.11.5).**
  `VRTPansharpenedRasterBand` overviews inherit full-resolution nodata.

- **Derived functions and coordinates (3.12.0).** VRT pixel functions add
  `mean`, `median`, `geometric_mean`, `harmonic_mean`, `mode`, `argmin`, and
  `argmax` with nodata handling. `min` and `max` accept a `k` constant.
  Muparser adds `fmod`; expressions expose `_CENTER_X_` and `_CENTER_Y_`; and
  `vrt://` accepts `transpose`.

- **Source schema and deterministic reads (3.12.1).** VRT source types accept
  a `name` XML attribute. Nearest reads use generic raster-band coordinate
  rounding. Multithreading is disabled for neighboring sources not aligned to
  integer output coordinates so results remain deterministic.

- **Pansharpen serialization and orientation (3.12.2).** Pansharpened VRTs
  serialize correctly when panchromatic and multispectral extents differ; the
  input vertical-orientation test is corrected.

- **Strided derived reads (3.12.3).** `VRTDerivedRasterBand::IRasterIO()`
  zero-initializes output correctly when line spacing differs from pixel
  spacing times buffer width.

- **Implicit derived overviews (3.12.4).** `VRTDerivedRasterBand` creates
  implicit overviews correctly.

- **Additional functions and block selection (3.13.0).** VRT derived bands add
  `area`, `quantile`, and `round`; `vrt://` accepts `block`.

## Pansharpening, contours, terrain, and viewshed

- **Constant contours (3.10.1).** `GDALContourGenerateEx()` returns `CE_None`
  for a constant raster.

- **Nearly aligned pansharpening (3.10.3).** Inputs whose extents differ by
  less than one multispectral resolution no longer cause I/O errors.

- **Terrain azimuth (3.10.3).** `gdaldem` accepts zero and negative `-az`
  values, for example `-az 0`.

- **Terrain scaling and nodata (3.11.0).** `gdaldem` derives scale from the CRS
  and adds `-xscale`/`-yscale`. `gdal2tiles` applies source nodata even without
  reprojection.

- **Non-north-up terrain (3.11.5).** Aspect, TPI, and TRI are corrected for
  non-north-up rasters; hillshade, slope, and roughness are corrected for
  rotated rasters.

- **All-nodata contours (3.12.2).** Contouring succeeds with an empty output
  layer instead of erroring.

- **Homography and viewshed ranges (3.12.3).** Homography overview scaling is
  correct. Viewshed DEM and GROUND modes accept values outside Byte range.

- **Viewshed controls (3.12.0).** Viewshed supports angular, pitch, and
  minimum-distance masks.

- **Current GMT palettes (3.13.1).** `gdal raster color-map` accepts current
  GMT `.cpt` files.

## Raster algebra and composition

- **Band algebra API (3.12.0).** C, C++, and Python support band arithmetic,
  comparisons, `AsType()`, and functions including `abs()`, `sqrt()`, logs,
  `min()`, `max()`, `mean()`, and `IfThenElse()`.

- **Calculation and mosaic controls (3.12.0).** `gdal raster calc` handles
  nodata, `--flatten`, and `--dialect=muparser|builtin`; the built-in dialect
  can create one output band from all bands of one input. Raster mosaic accepts
  `--pixel-function` and `--pixel-function-arg`; mosaic and stack accept
  `--absolute-path`.

- **Inputs without geotransforms (3.12.3).** `gdal raster calc` processes
  sources with no geotransform.

- **Pipeline-supplied raster inputs (3.12.1).** `gdal raster compare`, `info`,
  and `tile` work when their input is supplied outside the pipeline string.
  `calc` accepts nested-pipeline inputs.

- **Blend and edit expansion (3.13.0).** Blend adds multiply, screen, overlay,
  hard-light, darken, lighten, color-dodge, and color-burn. Raster creation can
  be a pipeline step and copies `--like` tiling where possible. Editing can set
  color interpretation, scale, offset, and a color map, or remove a table.

## Raster dimensions, windows, and overview behavior

- **Double target sizes (3.10.2).** `gdal_rasterize -ts` accepts doubles such
  as `-ts 1024.0 512.0`.

- **RMS overview normalization (3.12.3).** RMS resampling uses the corrected
  normalization formula, changing affected overview values.

- **Target-aligned mosaics (3.12.2).** `gdal raster mosaic` requires
  `--resolution` whenever `--target-aligned-pixels` is present.

- **Edge and huge RasterIO reads (3.13.2).** Pansharpening reads small windows
  at raster edges without window errors. Block RasterIO avoids integer
  overflow on huge rasters.

- **Separate-VRT nodata warnings (3.13.1).** `gdalbuildvrt -separate` warns
  when nodata lies outside the target band type.
