# Migration and API compatibility

## C and C++ source migrations

### Opaque declarations and layer hooks (`3.11-migration`)

Include `gcore/gdal_fwd.h` instead of redeclaring GDAL public opaque types;
stricter aliases can otherwise conflict, particularly in debug builds.

`OGRLayer::GetExtent()` is no longer virtual and its `bForce` argument is
`bool`. Drivers override protected `IGetExtent(int, OGREnvelope*, bool)`.
Likewise, callers use checked `GetExtent3D()` and drivers override
`IGetExtent3D()`. `SetSpatialFilter()` and `SetSpatialFilterRect()` are
non-virtual, return `OGRErr`, and take `const OGRGeometry*`; check their return
and implement `ISetSpatialFilter(int, const OGRGeometry*)` in drivers.

### Half precision and CMake version constraints (`3.11-migration`)

Handle `GDT_Float16` and `GDT_CFloat16` in data-type switches. A consumer
without native half precision can request `GDT_Float32` conversion through the
`RasterIO()` buffer type. To pin only the 3.11 minor line, use a CMake range:

```cmake
find_package(GDAL 3.11...<3.12 REQUIRED)
```

### Partial coordinate-transform failures (`3.11-migration`)

Time-aware `Transform()` and `TransformWithErrorCodes()` return `FALSE` when
any point fails, as do `GDALTransformerFunc` implementations. After aggregate
failure, inspect `pabSuccess[]` or `panErrorCodes[]`; successfully transformed
points may still be usable.

### Const-correct vector APIs (`3.12-migration`)

Out-of-tree drivers must make these overrides const:

- `GDALDataset::GetLayer()`, `GetLayerCount()`, and `TestCapability()`;
- `OGRLayer::GetName()`, `GetGeomType()`, `GetLayerDefn()`, `GetFIDColumn()`,
  `GetGeometryColumn()`, `GetSpatialRef()`, and `TestCapability()`.

`GetLayer()`, `GetLayerDefn()`, `GetSpatialRef()`, and
`OGRFeature::GetDefnRef()` now return const pointers. Store them as const; if
only reference-count mutation is required, the migration guidance permits a
targeted cast.

### Raster attribute tables and geotransforms (`3.12-migration`)

Handle `GFT_Boolean`, `GFT_DateTime`, and `GFT_WKBGeometry` in
`GDALRATFieldType` switches. `GDALRasterAttributeTable::SetValue()` returns
`CPLErr`, so check it and update overrides. Raster driver `GetGeoTransform()`
and `SetGeoTransform()` overrides now use `GDALGeoTransform&` and
`const GDALGeoTransform&`, a wrapper over `std::array<double, 6>`.

### Geometry mutation, macros, and signatures (`3.13-migration`)

All C point-count, point-set, and point-add functions in the `OGR_G_*Point*`
family now return `OGRErr`; check mutations. Replace `MIN`, `MAX`, and `ABS`
from `cpl_port.h` with `CPL_MIN`, `CPL_MAX`, and `CPL_ABS`. GDAL no longer
exports `M_PI`; where needed on supported platforms, define
`_USE_MATH_DEFINES` before `math.h`.

Out-of-tree drivers must also update:

- `GDALDataset::Close(GDALProgressFunc, void*)`, whose arguments may be null;
- option-list arguments on dataset `AddBand()`, `AdviseRead()`,
  `BeginAsyncReader()`, and `CopyLayer()`;
- `GDALDriver::pfnCreate` and `pfnCreateCopy`;
- raster-band `AdviseRead()` and `GetVirtualMemAuto()`.

Those option lists are `CSLConstList`, not `char **`.

### Const metadata and RasterIO resampling (`3.13-migration`)

`SetMetadata()` accepts `CSLConstList`; C++ `GetMetadata()` and C
`GDALGetMetadata()` return it. Declaring returned metadata as `CSLConstList`
also remains source-compatible with earlier versions.

RasterIO resampling and VRT operations work in the output buffer type by
default. Thus non-nearest Byte-to-Float32 resampling can yield fractional
values. Set `GDALRasterIOExtraArg::bOperateInBufType = false` to opt out.

## ABI, drivers, and compatibility surface

### Driver removals and replacements (`3.11.0`)

Removed raster drivers: BLX, BT, CTable2, ELAS, FIT, GSAG, GSBG, JP2Lura, OZI
OZF2/OZFX3, Rasterlite v1, R object `.rda`, RDB, SDTS, SGI, XPM, and DIPex.
Removed vector drivers: Geoconcept Export, OGDI, SDTS, SVG, Tiger, and UK .NTF.
Write support was removed from Interlis 1/2, ADRG, PAux, MFF, MFF2/HKV, LAN,
NTv2, BYN, USGSDEM, and ISIS2.

The OpenCL warper, `gdalwarpsimple`, and `ogrdissolve` were removed. The OGR
`Memory` driver is deprecated and aliases `MEM`. FileGDB updates and creation
route through OpenFileGDB, and PDF creation no longer accepts
`GEO_ENCODING=OGC_BP`. The shared-library major changed.

### Later driver restorations

GSBG was restored in `3.11.1`, GSAG in `3.11.2`, and BT in `3.11.4`. Tiger and
UK .NTF returned in `3.13.0` but remain future-removal candidates. The later
shared-library-major bump still requires binary dependents to rebuild or use a
matching library.

## Error, lifetime, and result contracts

### Core validation and status corrections

- `GDALGCPsToGeoTransform()` returns `FALSE` for an invalid result (`3.10.2`).
- `GDALContourGenerateEx()` returns `CE_None` for a constant raster (`3.10.1`).
- `GDALAlgorithm` rejects malformed list values and range-constrained `NaN`;
  interrupted `Run()` reports `CE_Failure` to progress (`3.11.1`).
- Unix, Win32, sparse, and archive VSI handles tolerate repeat `Close()` calls;
  destructors close them too (`3.11.2`).
- `InitializeDestinationBuffer()` warns and zero-fills rather than returning
  failure for `INIT_DEST=NO_DATA` without nodata (`3.11.5`); the later command
  contract makes this configuration fail, as documented in the raster file.
- Arrow and Parquet datasets expose `Close()`, and destruction flushes pending
  output (`3.11.4`).
- Java closure through `Band.GetDataset().Close()` no longer double-frees
  (`3.11.4`).

### Progressive close and driver capabilities (`3.13.0`)

Use `GDALCloseEx()` or the progress-aware `GDALDataset::Close()` for observable
long closes. `GetCloseReportsProgress()` tells whether progress is available.
Driver metadata can describe append, upsert, close-time visibility,
reopen-after-write, read-after-delete, update, and create-subdataset behavior.
Drivers can also advertise maximum string length. In `GDALOpenEx()`, prefix an
allowed-driver entry with `-` to exclude that driver.

### Geometry and date corrections

- `GeodesicLength()` again supports open line strings (`3.10.2`).
- `OGRParseDate()` keeps `59.999999` within second 59 (`3.11.2`) and accepts
  leap seconds (`3.11.5`).
- `OGRBuildPolygonFromEdges()` can return `MULTIPOLYGON`; callers and DXF HATCH
  handling must accept it (`3.11.5`).
- `OGR_G_SetPoint()` can grow a geometry when the index is at or beyond the
  current point count (`3.13.2`).
- `transformWithOptions()` closes polygons after polar reprojection, including
  with GEOS 3.15 (`3.12.4`).

## Public facilities and algorithm APIs

### CPL, VSI, and raster SDK additions (`3.11.0`)

Public helpers include `CPLIsInteractive()`, `CPLIsDebugEnabled()`, `VSIGlob()`,
`VSIMove()`, `CPLGetKnownConfigOptions()`, `CPLErrorOnce()`, `CPLDebugOnce()`,
and safe path functions. C++ adds `CPLTurnFailureIntoWarningBackuper`,
`CPLErrorAccumulator`, and `CPLQuietWarningsErrorHandler`.

Raster facilities include `gdal::CXXTypeTraits<T>`,
`gdal::GDALDataTypeTraits<T>`, `gdal_minmax_element.hpp`, `gdal::VectorX`,
min/max-location APIs, geolocation-to-pixel/line, interpolation at geolocation,
`GDALTranspose2D()`, recursive multidimensional-array names,
`GDALIsValueInRangeOf()`, and string-form nodata setting.

`GDALMDArray::AsClassicDataset()` accepts `BAND_IMAGERY_METADATA`; built-in tile
matrix sets add `WorldMercatorWGS84Quad`, `PseudoTMS_GlobalMercator`, and
`GoogleCRS84Quad`. `GDAL_CACHEMAX` accepts memory units. Raster APIs reject
`GDT_Unknown` and `GDT_TypeCount`.

### OGR and binding-visible APIs (`3.11.0`)

Generated fields use `OGRFieldDefn::SetGenerated()`/`IsGenerated()`.
`OSRGetAuthorityListFromDatabase()` enumerates CRS authorities, and
`OGR_GT_GetSingle()` is available to SWIG. Arrow streams accept
`DATETIME_AS_STRING`; `ogr2ogr` uses it to preserve time zones and can transfer
dataset relationships.

SWIG adds `Driver.CreateVector()`. C# exposes `VSIGetMemFileBuffer`. Python adds
`VSIFile`, `gdal_fsspec`, masked-array reads, mask resampling, translation
`-epo`/`-eco`, and relationship-field matching. Python constructors and driver
methods accept CRS definitions, NumPy types, and `os.PathLike` as documented;
the no-NumPy build switch accepts common true/false spellings.

### Dataset and multidimensional bridging APIs (`3.12.0`)

New dataset APIs include layer lookup, extent and WGS84 extent, overview
addition, window iteration, and split RasterIO. `GDALGetGDALPath()` returns the
installation path and `GDALRescaleGeoTransform()` rescales transforms.

`GDALDataset::AsMDArray()` bridges a classic dataset to an array;
`GDALMDArray::GetRawBlockInfo()` works with HDF5, netCDF, Zarr, and VRT.
Extended types can expose raster attribute tables, groups enumerate data types,
and classic views can obtain band metadata from fully qualified attributes.

Geolocation can normalize longitude to -180..180. OGR adds envelope-to-geometry
and constrained Delaunay APIs, vector datasets expose `GetSpatialRef()`, schema
overrides can match `*`, `srcType`, and `srcSubType`, and CRS APIs expose
celestial-body names.

### Raster band algebra (`3.12.0`)

C, C++, and Python bands support arithmetic, comparisons, `AsType()`, `abs()`,
`sqrt()`, logarithms, `min()`, `max()`, `mean()`, and `IfThenElse()`.
Algorithm consumers can read typed defaults; implementers have helpers for
geometry type, append/overwrite layer, absolute path, stdout, hidden arguments,
and deprecation. Front ends can inspect pipeline-step availability, direct and
aggregate dependencies, mutual-dependency groups, duplicate-value allowance,
and maximum character counts.

### Public headers and data types (`3.12.0`, `3.13.0`)

Installed raster headers include `gdal_dataset.h`, `gdal_rasterband.h`,
`gdal_geotransform.h`, and `gdal_raster_cpp.h`. Later additions include
`gdal_mem.h` with `MEMCreate()`, `gdal_thread_pool.h`, and
`ogr_refcountedptr.h`.

`GDT_UInt8` is canonical and `GDT_Byte` aliases it. C, C++, and Python expose
inter-band covariance; multidimensional arrays expose indexed overviews.

### Custom VSI handlers and config masking (`3.13.0`)

`VSIVirtualHandle::Read()` and `Write()` take a single `size_t` count, requiring
override updates. Handlers can be installed with `shared_ptr`; handles also add
little-endian `ReadLSB()` and `WriteLSB()`. Passing `CPL_NULL_VALUE` to
`CPLSetConfigOption()` masks an environment variable with an explicit null.

## Language-binding details

### Python array and option behavior

- `Dataset.WriteArray()` and `Band.WriteArray()` support zero-stride arrays
  (`3.11.4`).
- `Band.BlockWindows()`, band input to `CreateCopy()`, Boolean NumPy mapping,
  Boolean writes without Float64 promotion, and string coercion for config
  values arrived in `3.12.0`.
- Free-threaded/no-GIL Python 3.13+ builds are supported; `gdal.alg.*` accepts a
  `progress` keyword (`3.12.1`).
- `Dataset.AdviseRead()` and `Band.AdviseRead()` accept keywords, dataset calls
  default to all bands, algorithm functions accept argument aliases, and
  `Feature.SetField()` accepts NumPy values (`3.13.0`).
- `VectorTranslate()` and related methods parse `options=["-oo", "FOO=BAR"]`
  correctly (`3.13.1`).

### Ownership and C#/Java/SWIG behavior

`Feature.GetDefnRef()` increments the returned definition's reference count
(`3.12.1`). C# adds `SpatialReference.FindMatches` (`3.11.1`). Java exposes
full and partial `/vsicurl/` cache clearing, and SWIG exports relationship
capability constants (`3.13.0`).

## Portability helpers and path behavior

`CPLDebug` accepts `YES`, `TRUE`, and `1`. `CPLGetPath()` and
`CPLGetDirname()` handle `/vsicurl?` and encoded paths, while
`CPLFormFilename()` strips a leading relative `../...` when joining to an
absolute path (`3.10.1`). `CPLLexicallyNormalize()` adds lexical path
normalization (`3.12.3`).

`OGRSpatialReference::importFromEPSG()` tries an ESRI lookup for ESRI-like
codes and warns on successful fallback (`3.10.1`). Transformations also handle
a CRS mislabeled EPSG when its code is actually ESRI (`3.11.2`).
