# Bindings, Build, and Packaging

## Build configuration and dependency compatibility

- **CMake minor-version pinning (3.11-migration).** A project that supports
  only GDAL 3.11 should express the constraint as a range:

  ```cmake
  find_package(GDAL 3.11...<3.12 REQUIRED)
  ```

- **Embedded resources and VRT expression dependencies (3.11.0).** CMake
  provides `EMBED_RESOURCE_FILES` and `USE_ONLY_EMBEDDED_RESOURCE_FILES` for
  compiling resource files into libgdal. Muparser is strongly recommended for
  C++ VRT expressions; header-only exprtk can be enabled for advanced
  expressions at an approximately 8 MB library-size cost.

- **Exported targets and build controls (3.11.0).** The CMake package exports
  GDAL library targets and exposes `GDAL_DEBUG` publicly for debug builds.
  `USE_PRECOMPILED_HEADERS` defaults to `OFF`. Ubuntu `ubuntu-full` amd64
  images can optionally add Oracle, ECW, and MrSID drivers, which remain off by
  default.

- **Poppler 25.02 (3.10.2).** Compilation with Poppler 25.02.00 is supported.

- **Windows lean headers (3.10.3).** Builds work when
  `WIN32_LEAN_AND_MEAN` is defined.

- **Poppler 25.10 (3.11.5).** The PDF driver builds with Poppler 25.10 while
  retaining compatibility with older Poppler releases.

- **MongoDB C++ driver 4 (3.11.4).** The MongoDB driver builds with
  `mongo-cpp-driver` 4 and later.

- **Algorithm and raw-VRT gates (3.12.0).** `GDAL_ENABLE_ALGORITHMS` can omit
  algorithms beneath the unified `gdal` front end.
  `GDAL_VRT_ENABLE_RAWRASTERBAND` can compile raw VRT bands out and also exists
  as a runtime configuration option.

- **Installed raster headers (3.12.0).** Public C++ implementation headers
  include `gdal_dataset.h`, `gdal_rasterband.h`, `gdal_geotransform.h`, and
  `gdal_raster_cpp.h`.

- **Newer dependency builds (3.12.2).** Arrow and Parquet build with libarrow
  23.0 when precompiled headers are enabled. PDF supports Poppler 26.01.0, and
  LIBKML builds with Boost 1.90, Clang 21, and C++23.

- **Poppler and parallel HDF5 (3.12.3).** PDF builds with Poppler 26.02.0, and
  the build system properly supports parallel HDF5.

- **Disabled algorithms and newer headers (3.12.4).** Builds with
  `-DGDAL_ENABLE_ALGORITHMS=OFF` succeed. PDF builds against Poppler 26.04.00,
  and HDF5 builds tolerate libhdf5 2.1 headers redefining
  `_POSIX_C_SOURCE`.

- **Additional installed headers (3.13.0).** `gdal_mem.h` exposes the
  `MEMCreate()` C API; `gdal_thread_pool.h` and `ogr_refcountedptr.h` are also
  installed.

- **Poppler and JP2Grok floor (3.13.1).** GDAL builds with Poppler 26.06.00.
  JP2Grok requires Grok 20.3.2 or newer.

- **Current build requirements (3.13.2).** With
  `BUILD_PYTHON_BINDINGS=OFF`, CMake does not search for Python. Builds support
  CMake 4.4, Poppler 26.08 development versions, and SWIG 4.5 development
  versions. JP2Grok requires `libjp2grok` 20.3.5 or newer.

## Python installation and runtime behavior

- **External Python on Debian (3.10.2).** The Python binding install target
  works with a Python interpreter not provided by Debian.

- **Translation color interpretation (3.10.1).** `gdal.Translate()` accepts a
  `colorInterpretation` argument. `gdal.TileIndex()` received a corresponding
  correctness fix.

- **Virtual filesystem bindings (3.11.0).** Python provides
  `osgeo.gdal.VSIFile` and `osgeo.gdal_fsspec`; importing the latter registers
  GDAL VSI handlers as fsspec `AbstractFileSystem` implementations.

- **Raster arrays and accepted inputs (3.11.0).** Python adds
  `Dataset.ReadAsMaskedArray()` and `mask_resample_alg` on `ReadAsArray()`
  methods. Translation accepts `-epo`/`-eco`, and `gdal.VectorTranslate()`
  accepts `relatedFieldNameMatch`. `osr.SpatialReference()` accepts a CRS
  definition, `Driver.Create()` accepts NumPy types, and `Driver.Rename()` and
  `CopyFiles()` accept `os.PathLike`. `GDAL_PYTHON_BINDINGS_WITHOUT_NUMPY`
  recognizes `YES/1/ON/TRUE` and `NO/0/OFF/FALSE`.

- **Range-domain construction (3.11.1).** `ogr.CreateRangeFieldDomain()` and
  `ogr.CreateRangeFieldDomainDateTime()` correctly accept `None` bounds. The
  OpenFileGDB writer still rejects a range domain missing either bound, and
  SWIG `AddFieldDomain()` exposes failures as errors or exceptions.

- **Zero-stride writes (3.11.4).** `Dataset.WriteArray()` and
  `Band.WriteArray()` correctly handle arrays containing a zero stride.

- **Raster iteration and Boolean arrays (3.12.0).** `Band.BlockWindows()` is
  available; `Driver.CreateCopy()` accepts a band as input. NumPy Boolean
  types map to GDAL types and Boolean arrays are not promoted to `float64`
  during writes. Configuration-option values are coerced to strings.

- **Generated algorithm namespace (3.12.0).** The registry is available
  through dynamically generated calls such as:

  ```python
  gdal.alg.raster.convert(input="in.tif", output="out.tif")
  ```

- **No-GIL and progress callbacks (3.12.1).** The bindings support Python 3.13
  and later free-standing/no-GIL builds. Dynamically generated `gdal.alg.*()`
  functions accept `progress`.

- **Keyword and scalar handling (3.13.0).** `Dataset.AdviseRead()` and
  `Band.AdviseRead()` accept keyword arguments, with dataset calls defaulting
  to all bands. Algorithm functions accept visible and hidden aliases, and
  `Feature.SetField()` accepts NumPy values.

- **Open-option list parsing (3.13.1).** Methods such as
  `gdal.VectorTranslate()` recognize `options=["-oo", "FOO=BAR"]`.

- **Setuptools and Python floor (3.13.2).** With setuptools 77 or newer, the
  bindings declare Python 3.9 as the minimum because those setuptools versions
  do not support Python 3.8.

## SWIG, C#, and Java

- **Binding-level vector creation (3.11.0).** SWIG bindings add
  `Driver.CreateVector()`.

- **C# in-memory files (3.11.0).** C# adds `VSIGetMemFileBuffer`.

- **C# CRS matching (3.11.1).** C# adds `SpatialReference.FindMatches`.

- **Java dataset closure (3.11.4).** Closing a dataset obtained through
  `Band.GetDataset().Close()` no longer double-frees it.

- **Feature-definition ownership (3.12.1).** SWIG `Feature.GetDefnRef()` now
  increments the returned `FeatureDefn` reference count.

- **Relationship constants and Java cache control (3.13.0).** Java exposes
  full and partial `/vsicurl/` cache clearing. SWIG exposes the previously
  missing relationship-capability constants.
