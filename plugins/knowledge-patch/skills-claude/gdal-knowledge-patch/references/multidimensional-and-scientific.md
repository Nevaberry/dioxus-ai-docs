# Multidimensional and scientific data

## Multidimensional API and command workflows

### Classic and multidimensional bridging (`3.12.0`)

`GDALDataset::AsMDArray()` exposes a classic dataset as a multidimensional
array. `GDALMDArray::GetRawBlockInfo()` reports raw blocks for HDF5, netCDF,
Zarr, and VRT. Extended data types may carry raster attribute tables, groups
enumerate data types, and classic-dataset views can obtain band metadata from
fully qualified attributes.

`GDALGroup::GetMDArrayFullNamesRecursive()` recursively enumerates arrays
(`3.11.0`). Multidimensional arrays later expose `GetOverviewCount()` and
indexed `GetOverview()` (`3.13.0`).

### Slicing, strides, and raw access

`CreateSlicedArray()` slices indexing variables as well as data. One-element
dimensions work with `GetView(["::-1"])`, and VRT multidimensional sources read
negative steps (`3.11.5`). HDF5 arrays accept non-default strides
(`3.11.4`). Sliced arrays calculate the correct parent `IAdviseRead()` bounds
for non-unit steps (`3.13.2`).

### Multidimensional commands

`gdal mdim mosaic` is available (`3.12.0`). `gdal mdim convert` accepts
multiple `--group`, `--subset`, and `--scale-axes` values (`3.12.1`).
`gdal mdim info --summary` provides abbreviated output, and mosaics accept
dimensions without indexing variables (`3.13.0`).

Multidimensional overview building works on arrays with more than two
dimensions (`3.13.0`).

## Zarr and Kerchunk

### Zarr v3 and reference stores (`3.11.0`)

The Zarr driver supports the then-current v3 specification with `zstd`, plus
Kerchunk JSON and Parquet reference stores. For v2 it supports `shuffle`,
`quantize`, `fixedscaleoffset`, and `imagecodecs_tiff` codecs/filters. It
reports compressor, filters, and dimensions.

Zarr and netCDF expose `LIST_ALL_ARRAYS`, defaulting to `NO`. A missing target
referenced from JSON/Kerchunk raises an error (`3.11.5`). An affected Kerchunk
Parquet open path is restored in `3.12.1`.

### Direct opens and cloud stores (`3.12.0`)

Zarr directly opens `.zarray`, `.zgroup`, `.zmetadata`, and `zarr.json`.
STACTA recognizes Google/Azure URL templates, reads WEBP and JPEG XL tiles, and
can retry curl access through the matching cloud VSI handler. TileDB supports
Azure VSI.

### Zarr v3 sharding and georeferencing (`3.13.0`)

Zarr v3 reads, updates, and creates consolidated metadata. It supports
`sharding_indexed`, `crc32c`, variable-length UTF-8, and NumPy
datetime/timedelta extensions. Multiscales map to GDAL overviews.

Read or write `spatial` and `proj` conventions with
`GEOREFERENCING_CONVENTION=SPATIAL_PROJ`. Multidimensional overview generation
supports more than two dimensions.

A `bitround` filter ID with non-lowercase casing no longer causes a null
dereference (`3.13.3`).

## netCDF

### Discovery and metadata

`GDAL_NETCDF_REPORT_EXTRA_DIM_VALUES` controls reporting of extra-dimension
values (`3.10.1`). The driver can find a geolocation array without a
`coordinates` attribute and uses `GeoTransform` to retain precision
(`3.11.0`).

Rotated Latitude/Longitude mapping yields an SRS and geotransform even without
an ellipsoid definition (`3.11.1`). PACE OCI `rhos` axes are recognized, and a
geolocation array can identify X/Y axes in a 3D variable (`3.11.2`).

`LIST_ALL_ARRAYS=YES` works even when no 2D array exists (`3.11.4`). A stored
`GeoTransform` is used only when consistent with dimension variables
(`3.12.3`).

### Subdatasets and path parsing

`GDALGetSubdatasetInfo()` handles netCDF endpoint names containing a port
(`3.12.3`). The netCDF driver also parses paths containing multiple colons
(`3.13.3`).

## HDF4 and HDF5

### HDF geolocation and reads

HDF5 multidimensional arrays support non-default strides, and `.aux.xml`
geolocation references resolve correctly (`3.11.4`). Swath geolocation fields
are exposed through `GEOLOCATION` metadata instead of GCPs (`3.12.1`).

HDF4 GCP generation skips nodata longitude/latitude coordinates (`3.11.5`).

### Build compatibility

Parallel HDF5 builds correctly (`3.12.3`). Headers from libhdf5 2.1 that
redefine `_POSIX_C_SOURCE` are tolerated (`3.12.4`).

## Planetary formats

### PDS4 and ISIS (`3.12.0`, `3.12.2`)

PDS4 supports `Int64`/`UInt64` rasters and hexadecimal constants. ISIS3
PVL-to-JSON and JSON-to-PVL conversion supports unit-bearing arrays and
repeated metadata keywords. In the `json:ISIS3` domain,
`GetMetadataItem(top_level_key, "json:ISIS3")` returns only that subset rather
than the complete object.

### RPF and polar products

RPFTOC polar zones are georeferenced correctly (`3.12.3`). NITF specification
data corrects swapped RPFIMG coverage latitude and longitude (`3.12.2`).

## Hydrographic S-10x products

S102 opens a product without an uncertainty component and retrieves depth-only
nodata correctly (`3.11.1`). S102 Edition 3.0 and S104/S111 Edition 2.0 are
readable, and the S10x drivers decode custom CRSs (`3.12.0`).

S102 3.0 and S104/S111 2.0 later gain `CreateCopy()` writers (`3.13.0`). Their
writers and validators use corrected `dataCodingFormat` enumeration names
(`3.13.3`).

## Atmospheric, terrain, and sensor products

- GRIB2 reads Transverse Mercator variants with negative false offsets or a
  scale other than 0.9996 (`3.10.3`).
- DIMAP exposes PNEO FWHM and RPC `HEIGHT_DEFAULT` (`3.11.0`); DIMAP2 exposes
  `CLOUD_COVERAGE` and `SNOW_COVERAGE` (`3.13.2`).
- Sentinel-2 recognizes `S2C_` names (`3.11.0`) and tolerates expected missing
  granules for geolocation-enabled subdatasets (`3.12.2`).
- NITF models SAR I/Q pairs as one complex band (`3.11.0`) and reads extended
  header TREs correctly (`3.12.1`).
- RCM is a new read-only raster driver (`3.11.0`). E57 2D images and CPHD are
  new read-only multidimensional sources (`3.13.0`).
- `DTED_ASSUME_COMPLIANT` disables the driver's below-`-16000` value conversion
  (`3.12.0`).

## Geolocation, dimensions, and overviews

The geolocation transformer offers
`GEOLOC_NORMALIZE_LONGITUDE_MINUS_180_PLUS_180` (`3.12.0`). Classic dataset
views can derive band metadata from fully qualified attributes, and raw-block
discovery spans HDF5, netCDF, Zarr, and VRT.

The Pansharpened VRT implementation serializes mismatched panchromatic and
multispectral extents and detects vertical orientation correctly (`3.12.2`).
Pansharpened overview bands carry full-resolution nodata (`3.11.5`).

## Scientific correctness checklist

1. Verify dimension and indexing variables when slicing or reversing arrays.
2. Check whether `LIST_ALL_ARRAYS` is required for netCDF/Zarr discovery.
3. Treat stored geotransforms as conditional on coordinate consistency.
4. Validate Kerchunk targets and cloud URL rewriting before deferred reads.
5. Test overview georeferencing and nodata on multidimensional/classic bridges.
6. Validate exact S-10x edition and output enumeration names when writing.
