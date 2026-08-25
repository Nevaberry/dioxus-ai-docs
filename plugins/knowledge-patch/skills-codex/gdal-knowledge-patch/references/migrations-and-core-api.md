# Migrations and Core API

## C and C++ source migrations

- **Canonical opaque declarations (3.11-migration).** Include
  `gcore/gdal_fwd.h` for public opaque types. Downstream redeclarations can
  conflict with GDAL's canonical declarations, especially in DEBUG builds with
  stricter aliases.

- **Extent override hooks (3.11-migration).** Public `OGRLayer::GetExtent()`
  overloads are no longer virtual and take `bool bForce`. Drivers override
  protected `IGetExtent(int, OGREnvelope*, bool)`. The public
  `GetExtent3D(int, OGREnvelope3D*, bool)` performs checks; override
  `IGetExtent3D()`.

- **Spatial-filter errors and hooks (3.11-migration).** `SetSpatialFilter()`
  and `SetSpatialFilterRect()` are nonvirtual, return `OGRErr` instead of
  `void`, and accept `const OGRGeometry*`. Callers must check the result;
  drivers implement `ISetSpatialFilter(int, const OGRGeometry*)`.

- **Half-precision types (3.11-migration).** Raster bands may report
  `GDT_Float16` or `GDT_CFloat16`. Add both to type dispatch, or request
  conversion with a `GDT_Float32` RasterIO buffer.

- **Partial transform failure (3.11-migration).** Time-aware
  `OGRCoordinateTransformation::Transform()` and `TransformWithErrorCodes()`
  return `FALSE` when any point fails. `GDALTransformerFunc` follows the same
  aggregate rule. Inspect `pabSuccess[]` or `panErrorCodes[]` to find which
  points succeeded.

- **Const-correct dataset and layer APIs (3.12-migration).** Out-of-tree
  drivers must make `GDALDataset::GetLayer()`, `GetLayerCount()`, and
  `TestCapability()`, plus `OGRLayer::GetName()`, `GetGeomType()`,
  `GetLayerDefn()`, `GetFIDColumn()`, `GetGeometryColumn()`, `GetSpatialRef()`,
  and `TestCapability()` const. `GetLayer()`, `GetLayerDefn()`, and
  `GetSpatialRef()` return pointers to const objects. `OGRFeature::GetDefnRef()`
  returns `const OGRFeatureDefn*`; cast away const only when reference-count
  mutation is the sole requirement.

- **Raster attribute tables (3.12-migration).** `GDALRATFieldType` adds
  `GFT_Boolean`, `GFT_DateTime`, and `GFT_WKBGeometry`. Handle them in switches
  over `GDALRATGetTypeOfCol()`. `GDALRasterAttributeTable::SetValue()` returns
  `CPLErr`; check it and update subclass overrides.

- **Restricted raw VRT bands (3.12-migration).** Raw-file access through
  `VRTRawRasterBand` is restricted by default. Honor the
  `vrtrawrasterband_restricted_access` policy rather than assuming unrestricted
  access.

- **Geotransform override parameters (3.12-migration).** Raster-driver
  `GetGeoTransform()` and `SetGeoTransform()` overrides now use
  `GDALGeoTransform&` and `const GDALGeoTransform&`, not pointers to six
  doubles. `GDALGeoTransform` wraps `std::array<double, 6>`.

- **Geometry point mutation results (3.13-migration).** The C functions
  `OGR_G_SetPointCount`, all `OGR_G_SetPoint*` and `OGR_G_AddPoint*` variants,
  `OGR_G_SetPoints`, and `OGR_G_SetPointsZM` return `OGRErr` instead of `void`.
  Check every mutation result.

- **CPL macros and pi (3.13-migration).** Replace `MIN`, `MAX`, and `ABS` from
  `port/cpl_port.h` with `CPL_MIN`, `CPL_MAX`, and `CPL_ABS`. GDAL no longer
  exports `M_PI`; on platforms that require it, define `_USE_MATH_DEFINES`
  before including `math.h`.

  ```c
  #define _USE_MATH_DEFINES
  #include <math.h>
  ```

- **Driver signature updates (3.13-migration).** `GDALDataset::Close()`
  overrides accept `(GDALProgressFunc pfnProgress, void *pProgressData)`; both
  may be null. Option lists on `GDALDataset::AddBand()`, `AdviseRead()`,
  `BeginAsyncReader()`, and `CopyLayer()`, `GDALDriver::pfnCreate` and
  `pfnCreateCopy`, and `GDALRasterBand::AdviseRead()` and
  `GetVirtualMemAuto()` use `CSLConstList` instead of `char **`.

- **Const metadata lists (3.13-migration).** `SetMetadata()` accepts
  `CSLConstList`; `GDALMajorObject::GetMetadata()` and `GDALGetMetadata()`
  return it. Storing returned metadata in `CSLConstList` remains compatible
  with earlier releases.

- **RasterIO calculation type (3.13-migration).** Resampling and VRT
  operations run in the output buffer type by default. Set
  `GDALRasterIOExtraArg::bOperateInBufType` to false to opt out. For example,
  non-nearest Byte-to-Float32 resampling generally yields fractional values.

## Portability, error handling, and filesystem-neutral helpers

- **Debug values and URL-aware paths (3.10.1).** `CPLDebug` accepts `YES`,
  `TRUE`, and `1`. `CPLGetPath()` and `CPLGetDirname()` handle `/vsicurl?` and
  URL-encoded paths. `CPLFormFilename()` strips a relative `../...` component
  when joining it to an absolute path.

- **Invalid GCP transforms (3.10.2).** `GDALGCPsToGeoTransform()` returns
  `FALSE` when the generated geotransform is invalid; reject the conversion.

- **Core helper additions (3.11.0).** Public helpers include
  `CPLIsInteractive()`, `CPLIsDebugEnabled()`, `VSIGlob()`, `VSIMove()`,
  `CPLGetKnownConfigOptions()`, `CPLErrorOnce()`, `CPLDebugOnce()`, and safe
  path-manipulation functions. C++ also provides
  `CPLTurnFailureIntoWarningBackuper`, `CPLErrorAccumulator`, and
  `CPLQuietWarningsErrorHandler`.

- **Algorithm validation and cancellation (3.11.1).** `GDALAlgorithm` rejects
  malformed list arguments and `NaN` for range-constrained arguments. An
  interrupted `Run()` reports `CE_Failure` through its progress function.

- **Repeatable handle closure (3.11.2).** Unix, Win32, sparse-file, and archive
  VSI handles tolerate multiple `Close()` calls; their destructors also close
  them.

- **Date parsing edge cases.** `OGRParseDate()` parses `59.999999` seconds as
  `59.999` rather than rounding to `60.0` (3.11.2), and accepts leap-second
  timestamps (3.11.5).

- **Lexical path normalization (3.12.3).** `CPLLexicallyNormalize()` performs
  lexical file-path normalization.

- **Null configuration masking (3.13.0).** Passing `CPL_NULL_VALUE` to
  `CPLSetConfigOption()` explicitly masks an environment value with null.

- **Unix read buffering (3.13.3).** Unix file reads restore the behavior lost
  to a buffering regression introduced in 3.13.0.

## Dataset, raster, and algorithm APIs

- **Raster SDK additions (3.11.0).** Additions include
  `gdal::CXXTypeTraits<T>`, `gdal::GDALDataTypeTraits<T>`,
  `gdal_minmax_element.hpp`, `gdal::VectorX`,
  `GDALRasterComputeMinMaxLocation()` and
  `GDALRasterBand::ComputeMinMaxLocation()`,
  `GDALDataset::GeolocationToPixelLine()`,
  `GDALRasterBand::InterpolateAtGeolocation()`, `GDALTranspose2D()`,
  `GDALGroup::GetMDArrayFullNamesRecursive()`, `GDALIsValueInRangeOf()`, and
  `GDALRasterBand::SetNoDataValueAsString()`.

- **Capability and metadata contracts (3.11.0).** Driver metadata reports
  update support. `GDAL_DCAP_CREATE_SUBDATASETS` identifies support for
  `APPEND_SUBDATASET=YES`. `GDALMDArray::AsClassicDataset()` accepts
  `BAND_IMAGERY_METADATA`. `GDAL_CACHEMAX` accepts memory units. Built-in tile
  matrix sets include `WorldMercatorWGS84Quad`, `PseudoTMS_GlobalMercator`,
  and `GoogleCRS84Quad`. Raster APIs reject `GDT_Unknown` and
  `GDT_TypeCount`.

- **Typed algorithm and driver capabilities (3.12.0).** Drivers can advertise
  maximum string length plus append, upsert, close-time visibility,
  reopen-after-write, and read-after-delete support. Algorithm consumers can
  retrieve typed defaults through C/SWIG getters; implementers have helpers
  for geometry types, append/overwrite layer, absolute paths, stdout, hidden
  arguments, and deprecations.

- **Dataset extent and window APIs (3.12.0).** New calls include
  `GDALDataset::GetLayerIndex()`, `GetExtent()`, `GetExtentWGS84LongLat()`, and
  `AddOverviews()`, plus `GDALRasterBand::IterateWindows()` and
  `SplitRasterIO()`. `GDALGetGDALPath()` returns the installation path, and
  `GDALRescaleGeoTransform()` rescales a geotransform.

- **Progressive closure (3.13.0).** `GDALCloseEx()` and the
  `GDALDataset::Close()` progress callback make long closes observable.
  `GetCloseReportsProgress()` reports whether a dataset supports progress.

- **Unsigned byte and covariance (3.13.0).** `GDT_UInt8` is canonical and
  `GDT_Byte` aliases it. C, C++, and Python expose inter-band covariance-matrix
  APIs; multidimensional arrays provide `GetOverviewCount()` and indexed
  `GetOverview()`.

- **Driver exclusion and dependency metadata (3.13.0).** A leading `-` in an
  allowed-driver entry excludes that driver in `GDALOpenEx()`. Algorithm APIs
  expose pipeline-step availability, direct and aggregate dependencies,
  mutual-dependency groups, duplicate-value allowance, and maximum lengths.

- **Custom VSI handlers (3.13.0).** `VSIVirtualHandle::Read()` and `Write()`
  take one `size_t` count, so custom overrides must change. Handlers can be
  installed with `shared_ptr`; handles add little-endian `ReadLSB()` and
  `WriteLSB()`.

## CRS and geometry APIs

- **ESRI fallback and transforms.** `importFromEPSG()` attempts an ESRI lookup
  when a code resembles an ESRI code and warns on success (3.10.1).
  Transformations also work when a CRS labels an ESRI code as EPSG (3.11.2).

- **Open-line geodesic lengths (3.10.2).** `GeodesicLength()` again works on
  non-closed line strings.

- **Polar reprojection and edge-built polygons (3.11.5).** Polar-to-geographic
  geometry reprojection is corrected in core and `gdal vector reproject`.
  `OGRBuildPolygonFromEdges()` may return a multipolygon, including for DXF
  `HATCH`; callers must accept that result type.

- **Geolocation, schema, and celestial APIs (3.12.0).** The geolocation
  transformer accepts `GEOLOC_NORMALIZE_LONGITUDE_MINUS_180_PLUS_180`. OGR can
  create a geometry from an envelope and perform constrained Delaunay
  triangulation. Vector datasets expose `GetSpatialRef()`. Schema overrides
  accept `*` layer matching and `srcType`/`srcSubType` matching, and CRS APIs
  report celestial-body names.

- **Closed polar polygons (3.12.4).**
  `OGRGeometryFactory::transformWithOptions()` closes polygons emitted by the
  polar-reprojection path, including with GEOS 3.15.

- **Geometry and SQL additions (3.13.0).** Geometry APIs add polygon-based
  concave hull generation and invalidity-reason access in C, C++, and SWIG.
  GeoPackage and SQLite dialects add `ST_Hilbert()`. `ExportToKML()` fails
  instead of writing coordinates with invalid latitudes.

- **Point-array growth restored (3.13.2).** `OGR_G_SetPoint()` can grow a
  geometry when the supplied index is at or beyond the current point count.
