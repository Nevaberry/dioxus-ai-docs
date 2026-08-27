# Raster processing and formats

## Warping, transformation, and resampling

### Transformer and warper capabilities (`3.11.0`)

The transformer supports homographies. Warping adds `MODE_TIES`, bases mode
resampling on source-pixel coverage, and permits a mode value of `-1`.
Transformer options include `ALLOW_BALLPARK=NO`, `ONLY_BEST=AUTO|YES|NO`,
source/destination axis-mapping controls, and `HEIGHT_DEFAULT` for RPC height.
`ogr2ogr -ct_opt` exposes ballpark, best-operation, and differing-operation
warning controls.

### Extents and reprojection

- `gdalwarp -te` plus `-te_srs` uses `TransformBounds()` to obtain the target
  extent (`3.11.1`).
- Reprojection directly to COG works again after an earlier regression
  (`3.11.2`).
- Large rasters, globally extensive WMTS input, and longitude ranges of at
  least 360 degrees no longer trigger affected failures or an inappropriate
  `CENTER_LONG` in Web Mercator (`3.11.4`).
- TPS warping defaults to `SOURCE_EXTRA=5` (`3.11.4`).
- Polar-to-geographic geometry reprojection is corrected in the core and in
  unified vector reprojection (`3.11.5`).
- Homography transformations scale correctly on overviews (`3.12.3`).

### Source windows, nodata, and initialization

The MEM warper handles empty source windows with nonzero nodata (`3.10.3`).
Pansharpening tolerates input extents differing by less than one multispectral
pixel (`3.10.3`).

`UNIFIED_SRC_NODATA=YES` no longer applies an inappropriate destination-nodata
avoidance (`3.12.2`). Multi-threaded interruption is reliable and worker-thread
warps avoid a deadlock (`3.12.4`). Bilinear, cubic, cubic-spline, and Lanczos
correctly process NaN samples when nodata is NaN (`3.12.4`).

Earlier destination-buffer initialization warned and zero-filled for
`INIT_DEST=NO_DATA` without nodata (`3.11.5`). The later command contract makes
that request fail; `RESET_DEST_PIXELS=YES|NO` resets an existing destination to
destination nodata or zero (`3.13.0`).

### Working types and changed samples

`GDALWarpResolveWorkingDataType()` examines band types before defaulting to
`UInt8`; nearest-neighbor has a dedicated `Int8` path (`3.12.3`). RMS overview
normalization is corrected and may change affected values.

RasterIO resampling works in the output buffer type by default
(`3.13-migration`), so Byte-to-Float32 non-nearest output can be fractional.
Set `bOperateInBufType` false for the prior behavior.

Lanczos no longer applies its special validity threshold when fewer than half
the contributing pixels are valid, changing masked/nodata edges (`3.13.1`).
The SSE2 conversion path maps NaN to zero for signed 8-, 16-, and 32-bit
integer targets, matching the scalar path.

For GCP transformers (`3.12.2`), `MAX_GCP_ORDER` is ignored with
`METHOD=GCP_TPS`; negative values are sanitized with
`METHOD=GCP_POLYNOMIAL`.

### Sum, mode, and viewshed correctness

Sum-resampled warps avoid chunk-boundary artifacts (`3.12.1`). Mode resampling
accounts for Float16/CFloat16 NaNs (`3.11.4`). Viewshed DEM and GROUND modes
accept values outside Byte range (`3.12.3`).

## Raster statistics, contours, and masks

### Precision and nodata behavior

`GDALFPolygonize()` preserves Float64 precision. Statistics correct Float64
standard deviation in SSE2/AVX2 paths and use Float64 precision for Float32
mean and deviation (`3.12.1`).

`GDALZonalStats` handles polygons outside the raster, while unified zonal stats
avoids overflow for huge coordinates (`3.12.1`).

`ComputeRasterMinMax()` and `GetHistogram()` require exact equality to exclude
an integer nodata value; a nearby integer is no longer treated as nodata
(`3.13.2`). Constant, non-Byte histograms where `min == max` work correctly
(`3.11.4`).

### Contours and masks

Constant-valued contour generation returns success (`3.10.1`), and all-nodata
contouring succeeds with an empty layer (`3.12.2`). A selected mask in
`gdal_translate -of COG -b 1 -b 2 -b 3 -b mask` becomes a regular alpha-tagged
band and no longer crashes with source overviews (`3.11.5`).

`GDALNoDataMaskBand::IRasterIO()` avoids Byte corruption when line spacing is
larger than buffer width (`3.11.4`). `raster as-features --skip-nodata` no
longer drops non-nodata features (`3.12.4`).

## VRT and processed raster composition

### Embedded and processed VRTs

Processed datasets read source scale and offset (`3.10.1`). A simple or complex
source can embed a `VRTDataset`, and processed VRT adds `OutputBands` for output
count and types (`3.11.0`). VRT source XML accepts a `name` attribute
(`3.12.1`).

Raw-file VRT access is restricted by default (`3.12-migration`). Review the
runtime policy and `GDAL_VRT_ENABLE_RAWRASTERBAND`; the same name is a build
gate (`3.12.0`).

### Derived bands and expressions

VRT functions support arbitrary expressions, reclassification, and `mul` or
`sum` with a band and constant (`3.11.0`). Later functions add nodata-aware
`mean`, `median`, `geometric_mean`, `harmonic_mean`, `mode`, `argmin`, and
`argmax`; `min`/`max` take optional `k`, muparser adds `fmod`, expression
coordinates expose `_CENTER_X_`/`_CENTER_Y_`, and `vrt://` adds `transpose`
(`3.12.0`).

`ComplexSource` calculation and transfer types are corrected (`3.12.1`).
Nearest-neighbor VRT reads use common coordinate rounding; threading is disabled
for neighboring sources not integer-aligned to the output so results are
deterministic (`3.12.1`). Strided derived-band reads zero-initialize output
correctly (`3.12.3`), and implicit derived-band overviews work (`3.12.4`).

Derived functions later add `area`, `quantile`, and `round`; `vrt://` accepts a
`block` option (`3.13.0`).

### Source overviews and pansharpened VRTs

A single-source VRT exposes every source overview, and VRTPansharpen tolerates
sources with different overview counts (`3.11.2`). Pansharpened overview bands
inherit full-resolution nodata (`3.11.5`). Serialization works when panchromatic
and multispectral extents differ, and source vertical orientation is detected
correctly (`3.12.2`).

## COG, GeoTIFF, and TIFF readers

### COG creation and layout

COG supports `INTERLEAVE=BAND` and `TILE`, useful for hyperspectral data
(`3.11.0`), and complex types (`3.11.4`). It later implements random-write
`GDALDriver::Create()` (`3.13.0`). `COGCreate()` always uses BigTIFF for its
temporary file, avoiding classic-TIFF intermediate limits (`3.13.2`).

Multithreaded `BuildOverviews()` works for multiband COG datasets (`3.13.3`).
Overview cleanup exposes layout-break guidance and clean removal preserves the
layout (`3.11.1`).

### GeoTIFF data types, compression, and metadata

GTiff accepts Float16 and DNG 1.7 JPEG XL compression value `52546`
(`3.10.1`). A multithreaded compressed result can be read immediately after
creation (`3.10.3`). Float16 accepts `PREDICTOR=3`, and creation honors
`GDAL_DISABLE_READDIR_ON_OPEN=TRUE` (`3.12.3`).

GTiff and COG warn when `JXL_DISTANCE` or `JXL_ALPHA_DISTANCE` is set without
`JXL_LOSSLESS=NO`; JPEG XL Byte conversion is corrected (`3.11.4`).

GTiff reads ArcGIS `.tif.vat.dbf` raster attribute tables and preserves
premultiplied alpha together with COG and warping (`3.11.0`). It reads and
writes the `GDAL_METADATA` TIFF tag, including supported `json:*` domains
(`3.12.0`). ENVI wavelength, FWHM, and bad-band sidecars are consumed, and
`LAYOUT=COG` is reported for structurally valid COGs even without a GDAL ghost
area (`3.13.0`).

### TIFF reader behavior

LIBERTIFF is a native, thread-safe, read-only GeoTIFF driver (`3.11.0`). It
reads WEBP RGBA where opaque strips omit alpha (`3.11.2`), converts RGB
pixel-interleaved data to RGBA buffers (`3.11.5`), and reads BigTIFF nodata
strings occupying four through eight bytes (`3.13.1`).

## Tiling, mosaics, and GTI

### GTI STAC and source metadata

GTI can use STAC GeoParquet without `assets.image.href` (`3.10.1`). It
recognizes asset `proj:epsg`/`proj:transform`, top-level `proj:code`, `proj:wkt2`
and `proj:projjson`, EO bands under any asset name, all `common_names`, central
wavelength/FWHM, and raster-band scale/offset. It exposes `SRS` and carries a
sample tile color table for one-band datasets.

South-up tiles are accepted and warped north-up (`3.12.1`). STAC GeoParquet
recognizes `stac_extensions`, top-level `bands`, and EO 2.0; URL rewriting is
limited to collection catalogs.

GTI accepts SQL instead of a layer/table for selecting tiles; `s3://` STAC
references map to `/vsis3/` (`3.12.0`). `WARPING_MEMORY_SIZE` controls warp
memory, and unnecessary destination alpha is omitted (`3.12.3`). Relative
paths in XML and `.gti.gpkg` resolve from the main file, and masked overview
reads no longer fail from a missing band map (`3.12.4`).

`SRS_BEHAVIOR=OVERRIDE|REPROJECT` and `INTERLEAVE=BAND|PIXEL` are available;
on-the-fly warp honors the selected interleave (`3.13.0`). Unreadable tile
sources make raster reads fail (`3.11.5`).

### Tiling and raster mosaics

MVT can emit more than one tile at zoom zero (`3.10.2`). Unified raster tiling
supports excluded/nodata thresholds (`3.11.1`), fork or spawn parallelism and
STACTA output (`3.12.0`), and automatic source-overview selection (`3.13.1`).

Raster mosaic requires `--resolution` with target-aligned pixels (`3.12.2`).
Pansharpening can read a small edge window (`3.13.2`).

## JPEG-family, PNG, WEBP, AVIF, and HEIF

### JPEG, JPEG XL, and JP2

JPEG reads FLIR little-endian 16-bit PNG thermal payloads. It keeps
`IRWindowTransmission` separate from temperature and fixes the relative
humidity metadata subdomain (`3.11.1`). JPEGXL reads Float16 as Float32
(`3.11.0`) and converts non-Byte input to Byte correctly (`3.11.4`).

JP2OpenJPEG avoids duplicate type/association entries in the CDEF box for
three-gray-band-plus-alpha output (`3.12.4`). JP2GROK adds Grok-based read/write
under AGPLv3 (`3.13.0`); it handles Float32, Float64, and 16-bit output buffers
and supports genuinely single-threaded decoding (`3.13.2`).

### AVIF and HEIF

AVIF reads images larger than 10 MB (`3.10.3`). HEIF adds tile reads,
`CreateCopy()`, and read-only GeoHEIF with libheif 1.19; AVIF adds read-only
GeoHEIF with the development libavif current at that release (`3.11.0`).

Later, HEIF writes single-band images and AVIF encodes/decodes 16-bit data with
libavif 1.4+ (`3.13.0`). A GeoHEIF without a transform no longer reports one
(`3.13.1`).

### Color maps

`gdal raster color-map` accepts current GMT `.cpt` files (`3.13.1`).

### PNG and WEBP

PNG caches non-band-one reads correctly (`3.11.2`). It reads/writes
`BACKGROUND_COLOR` dataset metadata and supports `ZLEVEL=0` uncompressed
output (`3.12.0`). WEBP supports `.wld` worldfiles (`3.12.0`), and WEBP
MBTiles can be updated (`3.10.3`).

## Specialized imagery and terrain formats

### GRIB, NITF, Sentinel, DIMAP, and Leveller

GRIB2 reads Transverse Mercator with negative false easting/northing and scale
factors other than 0.9996 (`3.10.3`). NITF represents SAR I/Q as one complex
band, Sentinel-2 recognizes `S2C_`, DIMAP reports PNEO FWHM and RPC
`HEIGHT_DEFAULT`, and Leveller accepts document versions through 12 (`3.11.0`).

NITF extended-header TREs are read correctly (`3.12.1`); RPFIMG coverage
latitude/longitude values are corrected (`3.12.2`). All `WAVE_LENGTH_UNIT`
cases in BANDSB are parsed (`3.13.1`). NITF accepts `IC=C4` for CADRG
(`3.13.2`), and creation accepts `NOW` for `NITF_FDT`/`NITF_IDATIM` plus CADRG
writing (`3.13.0`). `gdal driver rpftoc create` builds CADRG A.TOC indexes.

Sentinel-2 geolocation tolerates expected missing granules (`3.12.2`). DIMAP2
reports `CLOUD_COVERAGE` and `SNOW_COVERAGE` (`3.13.2`).

### ENVI, HF2, MRF, and MiraMon

ENVI warns or errors when samples, lines, or bands exceed `INT_MAX`
(`3.11.4`). It later handles multiband BSQ datasets whose band offset exceeds
`INT_MAX`, restoring behavior affected in the previous line (`3.13.3`).

HF2 reads negative elevations (`3.12.2`). MRF decodes masked naked Lerc2 with
liblerc 3+ (`3.13.1`), and caching configuration is renamed from
`MRF_BYPASSCACHING` to `MRF_ENABLE_CACHING` (`3.13.2`).

MiraMonRaster first appears read-only (`3.12.0`), fixes multiband geotransforms
(`3.12.2`), and later gains creation (`3.13.0`).

### RCM, AIVector, E57, and CPHD

RCM and AIVector are new read-only drivers (`3.11.0`). Read-only E57 2D images
and CPHD data are exposed through the multidimensional API (`3.13.0`).

## Georeferencing and metadata correctness

### Raster geotransforms and spatial metadata

- Pansharpening tolerates nearly aligned inputs (`3.10.3`).
- GTiff/COG can create R,G,B,NIR without explicit `PHOTOMETRIC` (`3.11.4`).
- HDF4 skips nodata longitude/latitude while creating GCPs (`3.11.5`).
- Vertical-shift 3D warps do not copy the source unit type to output
  (`3.13.1`).
- `gdalinfo` STAC transform order and floating nodata metadata are correct
  (`3.12.1`).

### Raster read boundaries and buffers

Block RasterIO avoids integer overflow on huge rasters, and sliced
multidimensional `IAdviseRead()` computes parent bounds for non-unit steps
(`3.13.2`). A small edge window can be pansharpened without a window error.

Unix file reads recover from a buffering regression (`3.13.3`).

## MBTiles, MVT, DTED, and miscellaneous formats

- MBTiles updates WEBP-compressed datasets (`3.10.3`) and later accepts
  `ELEVATION_TYPE` (`3.13.0`).
- MVT reads zero-padded files (`3.11.5`) and exposes tile-coordinate fields
  (`3.13.0`).
- `DTED_ASSUME_COMPLIANT` bypasses conversion below -16000 (`3.12.0`).
- RLE4 BMP decoding is corrected (`3.12.2`).
- PDF creation can persist DPI to PAM with `SAVE_DPI_TO_PAM` (`3.13.0`).
- TileDB claims `/vsis3/` paths only when they use `.tdb` or have no extension,
  avoiding unrelated suffixed objects (`3.13.1`).
- S-10x writers and validators use corrected `dataCodingFormat` enumeration
  names (`3.13.3`).
