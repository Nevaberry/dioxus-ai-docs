# Raster Formats

## GeoTIFF, COG, and JPEG XL

- **DNG JPEG XL and half precision (3.10.1).** GTiff supports `Float16` and
  TIFF compression value `52546`, the JPEG XL encoding from DNG 1.7.

- **Immediate multithreaded reads (3.10.3).** A compressed GeoTIFF created in
  multithreaded mode can be read immediately after creation.

- **COG interleave and alpha metadata (3.11.0).** COG creation accepts
  `INTERLEAVE=BAND` and `INTERLEAVE=TILE`, including hyperspectral use cases.
  GTiff reads ArcGIS-style `.tif.vat.dbf` attribute tables. GTiff, COG, and
  warping preserve premultiplied-alpha information from source TIFFs.

- **Complex COG and RGB-NIR TIFF (3.11.4).** COG can create complex-valued
  datasets. GTiff can create R, G, B, NIR data without an explicit
  `PHOTOMETRIC` creation option.

- **JPEG XL conversion and diagnostics (3.11.4).** Translating non-Byte JPEG
  XL to Byte converts values correctly. GTiff and COG warn when `JXL_DISTANCE`
  or `JXL_ALPHA_DISTANCE` is used without `JXL_LOSSLESS=NO`.

- **Selected mask to COG (3.11.5).** A command such as
  `gdal_translate -of COG -b 1 -b 2 -b 3 -b mask ...` works with RGB input
  that has overviews. The selected mask becomes a normal output band tagged as
  alpha.

- **GeoTIFF metadata tag (3.12.0).** GTiff reads and writes the
  `GDAL_METADATA` TIFF tag, including supported `json:*` metadata domains.

- **Float16 predictor (3.12.3).** GTiff accepts `Float16` with `PREDICTOR=3`.
  Creating a GeoTIFF honors `GDAL_DISABLE_READDIR_ON_OPEN=TRUE` without
  listing the output directory.

- **Random-write COG and sidecars (3.13.0).** COG implements
  `GDALDriver::Create()` for random-write creation. GTiff consumes ENVI
  sidecars for wavelength, FWHM, and bad-band metadata, and reports
  `LAYOUT=COG` for structurally valid COGs even without a GDAL ghost area.

- **BigTIFF nodata strings (3.13.1).** LIBERTIFF correctly reads a BigTIFF
  nodata value whose string representation uses four through eight bytes.

- **BigTIFF COG intermediates (3.13.2).** `COGCreate()` always uses BigTIFF
  for its temporary file, so a classic-TIFF intermediate does not constrain
  large output.

- **Multiband COG overviews (3.13.3).** Multithreaded
  `BuildOverviews()` works for multiband COG datasets.

## GTI, STAC, and tiled raster access

- **Richer STAC GeoParquet metadata (3.10.1).** GTI does not require
  `assets.image.href`. It recognizes `assets.XXX.proj:epsg`,
  `assets.XXX.proj:transform`, `proj:code`, `proj:wkt2`, and `proj:projjson`;
  reads `eo:bands` under any asset name, all `common_names`, central
  wavelength, FWHM, and `raster:bands` scale/offset; exposes the `SRS` open
  option; and attaches a sample tile's color table to a one-band dataset.

- **STACIT 1.1 identification (3.10.2).** STACIT supports STAC 1.1 and
  identifies an item when at least two of `proj:transform`, `proj:bbox`, and
  `proj:shape` exist.

- **Timestamp refresh (3.11.1).**
  `gdaladdo --partial-refresh-from-source-timestamp` works with GTI as well as
  VRT.

- **Unreadable sources (3.11.5).** A GTI raster read fails when one source is
  unreadable instead of silently accepting the failed source read.

- **SQL tile sources (3.12.0).** GTI can select tile features with a SQL query,
  not only a layer or table name. STAC GeoParquet `s3://` references are
  translated to `/vsis3/`.

- **Cloud-backed STACTA (3.12.0).** STACTA recognizes `gs://`, `az://`, and
  `azure://` templates, reads WEBP and JPEG XL tiles, and can retry failed
  `/vsicurl/` access through the matching cloud VSI handler. TileDB supports
  `/vsiaz/`.

- **South-up and EO 2.0 STAC (3.12.1).** GTI accepts south-up tiles and warps
  them north-up. STAC GeoParquet recognizes `stac_extensions`, a top-level
  `bands` object, and EO 2.0. URL rewriting is restricted to STAC collection
  catalogs.

- **STACIT pagination (3.12.1).** STACIT no longer begins pagination with an
  empty `{}` request body.

- **GTI warp controls (3.12.3).** GTI exposes `WARPING_MEMORY_SIZE`. Its
  on-the-fly reprojection omits a destination alpha band when none is needed.

- **Relative paths and masked overviews (3.12.4).** Relative tile names in GTI
  XML and `.gti.gpkg` indexes resolve from the main file. Downsampled reads
  with a mask and overviews no longer fail because `panBandMap[0]` is absent.

- **SRS and interleave behavior (3.13.0).** GTI adds
  `SRS_BEHAVIOR=OVERRIDE|REPROJECT` and reports `INTERLEAVE=BAND|PIXEL`,
  honoring band interleave while warping on the fly.

- **TileDB identification on S3 (3.13.1).** TileDB claims `/vsis3/` paths only
  when they have a `.tdb` suffix or no suffix.

## Zarr and reference stores

- **Zarr v3 and reference stores (3.11.0).** Zarr supports the then-current v3
  specification with `zstd`, Kerchunk JSON and Parquet stores, and v2
  `shuffle`, `quantize`, `fixedscaleoffset`, and `imagecodecs_tiff`
  codecs/filters. It reports compressors, filters, and dimensions.

- **Direct metadata-file opens (3.12.0).** Zarr can open `.zarray`, `.zgroup`,
  `.zmetadata`, and `zarr.json` files directly.

- **Missing Kerchunk targets (3.11.5).** A JSON/Kerchunk store reports an error
  when its referenced file cannot be opened.

- **Kerchunk Parquet restoration (3.12.1).** The driver restores the affected
  path for opening Kerchunk Parquet reference stores.

- **Zarr v3 sharding and georeferencing (3.13.0).** Zarr v3 can read, update,
  and create consolidated metadata and supports `sharding_indexed`, `crc32c`,
  variable-length UTF-8, and NumPy datetime/timedelta extensions. Multiscales
  map to GDAL overviews. `spatial` and `proj` conventions are read or written
  with `GEOREFERENCING_CONVENTION=SPATIAL_PROJ`; overview building supports
  arrays with more than two dimensions.

- **Case-insensitive bitround safety (3.13.3).** A non-lowercase Zarr filter
  ID denoting `bitround` no longer causes a null-pointer dereference.

## JPEG, PNG, WEBP, AVIF, HEIF, and JPEG 2000

- **Large AVIF input (3.10.3).** AVIF reads images larger than 10 MB.

- **HEIF and GeoHEIF (3.11.0).** HEIF supports tile reads, `CreateCopy()`, and
  read-only GeoHEIF with libheif 1.19. AVIF supports read-only GeoHEIF with the
  development libavif current at that release. JPEGXL exposes Float16 input as
  Float32.

- **FLIR thermal JPEG (3.11.1).** JPEG reads FLIR thermal data stored as
  little-endian 16-bit PNG. `IRWindowTransmission` is separate from
  `IRWindowTemperature`, and `RelativeHumidity` uses the corrected metadata
  subdomain.

- **IIIF Image API 3.0 (3.11.1).** The WMS driver includes a mini-driver for
  International Image Interoperability Framework Image API 3.0.

- **PNG band caching (3.11.2).** PNG correctly caches bands when the first read
  does not begin with band 1.

- **LIBERTIFF WEBP RGBA (3.11.2).** LIBERTIFF reads WEBP-compressed RGBA when
  an opaque tile or strip omits alpha.

- **LIBERTIFF RGB-to-RGBA (3.11.5).** An RGB pixel-interleaved file reads
  correctly into an RGBA pixel-interleaved buffer.

- **PNG and WEBP controls (3.12.0).** PNG reads/writes background color through
  `BACKGROUND_COLOR` dataset metadata and accepts `ZLEVEL=0` for uncompressed
  output. WEBP supports `.wld` worldfiles.

- **RLE4 BMP (3.12.2).** BMP decodes RLE4-compressed images.

- **JP2 gray plus alpha (3.12.4).** JP2OpenJPEG avoids duplicate
  type/association pairs in CDEF for files with three gray bands plus alpha.

- **New imagery drivers and JP2Grok (3.13.0).** Read-only drivers expose E57
  two-dimensional images and CPHD through the multidimensional API. JP2GROK
  reads and writes JPEG 2000 through the AGPLv3-licensed Grok toolkit.

- **HEIF and AVIF writing (3.13.0).** HEIF writes single-band images. AVIF
  supports 16-bit encode/decode with libavif 1.4 or later.

- **Absent GeoHEIF transform (3.13.1).** A GeoHEIF dataset without a
  geotransform no longer reports one.

- **Masked naked Lerc2 (3.13.1).** MRF decodes naked Lerc2 files containing
  masks when linked with liblerc 3.0 or later.

- **JP2Grok output types (3.13.2).** JP2Grok handles Float32, Float64, and
  16-bit output buffers and provides a genuinely single-threaded decode path.

## Scientific, terrain, and hydrographic formats

- **GRIB2 Transverse Mercator (3.10.3).** GRIB2 reads definitions with negative
  easting/falsing values or a scale factor other than `0.9996`.

- **Restored grid drivers.** GSBG returned after its 3.11.0 removal (3.11.1),
  GSAG returned (3.11.2), and BT returned (3.11.4).

- **ENVI dimension validation (3.11.4).** ENVI warns or errors when samples,
  lines, or bands exceed `INT_MAX`.

- **Current scientific formats (3.12.0).** `DTED_ASSUME_COMPLIANT` disables
  DTED value conversion below `-16000`. PDS4 handles Int64/UInt64 rasters and
  hexadecimal constants. S102 reads Edition 3.0, S104 and S111 read Edition
  2.0, and S10x drivers decode custom coordinate systems.

- **ISIS3 JSON subset (3.12.2).** For `json:ISIS3`,
  `GetMetadataItem(<top-level-key>, json:ISIS3)` returns only the requested
  top-level value.

- **HF2 negatives (3.12.2).** HF2 reads negative elevations correctly.

- **ISIS3 PVL structures (3.12.2).** PVL/JSON conversion handles unit-bearing
  arrays and repeated metadata keywords.

- **NITF extended-header TREs (3.12.1).** NITF reads TREs stored in the
  extended header.

- **NITF and product creation (3.13.0).** NITF writes CADRG and accepts `NOW`
  for `NITF_FDT` and `NITF_IDATIM`; `gdal driver rpftoc create` builds CADRG
  A.TOC indexes. S102 v3.0 and S104/S111 v2.0 support `CreateCopy()` writing.
  MiraMonRaster supports creation.

- **Other creation options (3.13.0).** MBTiles adds `ELEVATION_TYPE`, and PDF
  adds `SAVE_DPI_TO_PAM`.

- **NITF wavelength units (3.13.1).** NITF parses every `WAVE_LENGTH_UNIT`
  case in the `BANDSB` TRE.

- **MRF cache rename (3.13.2).** Replace `MRF_BYPASSCACHING` with
  `MRF_ENABLE_CACHING` in deployments.

- **NITF CADRG compression (3.13.2).** NITF accepts `IC=C4` when
  `PRODUCT_TYPE=CADRG`.

- **Large-offset ENVI BSQ (3.13.3).** ENVI again creates and opens multiband
  BSQ files whose band offset exceeds `INT_MAX`.

## Other imagery and tiled formats

- **WEBP MBTiles updates (3.10.3).** MBTiles can update WEBP-compressed data.

- **MVT zoom-zero output (3.10.2).** MVT can generate more than one tile at
  zoom level 0.

- **Zero-padded MVT reads (3.11.5).** MVT accepts files with zero-byte padding.

- **Additional imagery metadata (3.11.0).** DIMAP exposes PNEO FWHM and RPC
  `HEIGHT_DEFAULT`; NITF represents SAR I/Q pairs as one complex band;
  Sentinel-2 recognizes `S2C_` names; Leveller accepts document versions
  through 12.
