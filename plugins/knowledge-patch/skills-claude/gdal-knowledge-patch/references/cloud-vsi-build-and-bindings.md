# Cloud, VSI, builds, and bindings

## Build-system and dependency compatibility

### Core build controls (`3.11.0`)

CMake can embed resource files with `EMBED_RESOURCE_FILES` and restrict runtime
lookups with `USE_ONLY_EMBEDDED_RESOURCE_FILES`. `muparser` is strongly
recommended for C++ VRT expressions; optional header-only `exprtk` enables
advanced expressions at roughly 8 MB of library-size cost.

The exported CMake package provides GDAL library targets and publicly exports
`GDAL_DEBUG` for debug builds. `USE_PRECOMPILED_HEADERS` defaults to `OFF`.
Ubuntu `ubuntu-full` amd64 images may add Oracle, ECW, and MrSID drivers, which
remain disabled by default.

### Algorithm and raw-VRT feature gates (`3.12.0`)

`GDAL_ENABLE_ALGORITHMS` can omit algorithms beneath the unified command. The
build now succeeds with it disabled (`3.12.4`).

`GDAL_VRT_ENABLE_RAWRASTERBAND` can compile out raw VRT support and is also a
runtime option. Independently, raw VRT file access is restricted by default;
deployments requiring raw files must account for the
`vrtrawrasterband_restricted_access` policy.

### Dependency-specific fixes

- Poppler 25.02 builds work (`3.10.2`); compatibility later extends through
  25.10 (`3.11.5`), 26.01 (`3.12.2`), 26.02 (`3.12.3`), 26.04 (`3.12.4`),
  26.06 (`3.13.1`), and 26.08 development versions (`3.13.2`).
- `WIN32_LEAN_AND_MEAN` builds work (`3.10.3`).
- MongoDB builds against `mongo-cpp-driver` 4+ (`3.11.4`).
- Arrow/Parquet works with libarrow 23 and precompiled headers; LIBKML works
  with Boost 1.90, Clang 21, and C++23 (`3.12.2`).
- Parallel HDF5 is supported (`3.12.3`); libhdf5 2.1 headers redefining
  `_POSIX_C_SOURCE` are tolerated (`3.12.4`).
- CMake 4.4 and SWIG 4.5 development versions are supported (`3.13.2`).
- JP2Grok requires Grok 20.3.2+ (`3.13.1`) and then `libjp2grok` 20.3.5+
  (`3.13.2`).

When `BUILD_PYTHON_BINDINGS=OFF`, CMake does not search for Python (`3.13.2`).

## S3 authentication and behavior

### Identity Center and credential flows

`/vsis3/` supports AWS IAM Identity Center/SSO (`3.10.1`). The SSO cache-file
location and region handling were corrected later, and path-specific options
are honored by directory reads (`3.11.4`).

New connections using EC2 credentials no longer take the WebIdentity path
(`3.11.5`). S3 also supports `credential_process` and directory buckets
(`3.12.0`). `AWS_S3_ENDPOINT` may include an `http://` or `https://` prefix
(`3.11.0`).

### S3 and redirect safety

When `/vsicurl/` follows an S3-like redirect, authentication from the original
URL is not forwarded (`3.12.2`). Path-specific redirect-authorization policy
is available; multi-range reads retry HTTP 429 and 5xx responses (`3.13.0`).

## Azure, Google, Swift, and WebHDFS

- Changing authentication invalidates cached `/vsigs/` and `/vsiaz/` file and
  directory state (`3.10.3`).
- `/vsigs/` supports batch unlink and bearer-token file metadata via
  `GDAL_HTTP_HEADERS`; `/vsiswift/` forwards HTTP options while listing, and
  `/vsiwebhdfs/` forwards them for listing, deletion, and directory creation
  (`3.11.1`).
- `/vsiaz/ ReadDir()` works with `AZURE_NO_SIGN_REQUEST=YES` (`3.11.4`).
- Cloud VSI paths lexically squash `/./` and `/../`; set
  `GDAL_HTTP_PATH_VERBATIM` to preserve them (`3.12.0`).
- TileDB adds `/vsiaz/` access, while STACTA understands `gs://`, `az://`, and
  `azure://` URL templates (`3.12.0`).
- `/vsigs/` recognizes Google Cloud Run for GCE authentication (`3.13.0`).
- Azure/ADLS option metadata includes `AZURE_STORAGE_ACCESS_TOKEN` and
  `AZURE_STORAGE_SAS_TOKEN` (`3.13.2`).

## HTTP and `/vsicurl/`

### Headers, query strings, and connection limits (`3.11.0`)

`VSICURL_QUERY_STRING` is path-specific. A `/vsicurl?` URL accepts
`header.<key>=<value>`. `GDAL_HTTP_MAX_CACHED_CONNECTIONS` and
`GDAL_HTTP_MAX_TOTAL_CONNECTIONS` bound connections. Cache and chunk sizes
accept memory units. `/vsicurl_streaming/` follows HTTP 303 redirects.

GeoJSON-like drivers combine `GDAL_HTTP_HEADERS` with their generated `Accept`
header, so custom headers do not suppress content negotiation (`3.10.1`).

### Retry, redirect, and size fixes

- CPL HTTP retries `SSL connection timeout` (`3.10.3`).
- `/vsicurl_streaming/` reports correct sizes; `/vsicurl/` handles 302 replies
  to `HEAD` (`3.12.2`).
- If `HEAD` advertises byte ranges without `Content-Length`, `/vsicurl/` retries
  using a limited-range `GET` (`3.12.4`).
- Nginx directory listings produced with `autoindex_exact_size off` yield
  correct sizes (`3.13.2`).
- `/vsicurl?header_file=...` accepts only permitted filenames (`3.13.2`).

### Cache and open controls

`VSIFOpenEx2L()` accepts `CACHE=ON/OFF` to control post-close caching of
curl-style files (`3.12.0`). Java exposes full and partial `/vsicurl/` cache
clearing (`3.13.0`).

## VSI operations and archives

### APIs and CLI-visible behavior

Public facilities include `VSIGlob()` and `VSIMove()` (`3.11.0`). Unix,
Win32, sparse-file, and archive handles may be closed repeatedly and are also
closed by their destructors (`3.11.2`). A single-file `gdal vsi list` displays
its modification timestamp (`3.13.1`).

`VSISync()` includes empty files in either direction when multithreaded cloud
synchronization is enabled (`3.13.2`).

### Archive and path fixes

`/vsirar/` reads a single-file archive without returning a negative read count
(`3.11.4`). Path APIs handle `/vsicurl?` and URL-encoded paths, and forming a
filename strips a leading `../...` when joined to an absolute path (`3.10.1`).

## Python packaging and runtime

### Installation and supported runtimes

On Debian, binding installation works with a Python interpreter not supplied
by Debian (`3.10.2`). Free-threaded/no-GIL Python 3.13+ builds are supported
(`3.12.1`). With setuptools 77+, package metadata declares Python 3.9 as the
minimum because those setuptools releases do not support 3.8 (`3.13.2`).

### Virtual filesystems and accepted inputs (`3.11.0`)

Python exposes `osgeo.gdal.VSIFile` and `osgeo.gdal_fsspec`; importing the
latter registers GDAL VSI handlers as fsspec `AbstractFileSystem`
implementations. `Driver.CreateVector()` is exposed through SWIG.

`Dataset.ReadAsMaskedArray()` is available, and `ReadAsArray()` methods accept
`mask_resample_alg`. `gdal.VectorTranslate()` accepts
`relatedFieldNameMatch`. `osr.SpatialReference()` accepts a CRS definition,
`Driver.Create()` accepts NumPy types, and `Rename()`/`CopyFiles()` accept
`os.PathLike`.

`GDAL_PYTHON_BINDINGS_WITHOUT_NUMPY` accepts `YES/1/ON/TRUE` and
`NO/0/OFF/FALSE`.

### Arrays, algorithms, and options

- Zero-stride arrays can be written through dataset and band `WriteArray()`
  (`3.11.4`).
- `Band.BlockWindows()` is available, a band can be input to `CreateCopy()`,
  Boolean NumPy types map correctly, Boolean output avoids Float64 promotion,
  and config option values are string-coerced (`3.12.0`).
- `gdal.alg.*` methods accept `progress` (`3.12.1`).
- `Dataset.AdviseRead()` and `Band.AdviseRead()` accept keyword arguments;
  dataset calls default to all bands. `Feature.SetField()` accepts NumPy values
  (`3.13.0`).
- List-form open options such as `options=["-oo", "FOO=BAR"]` are parsed by
  `VectorTranslate()` and similar methods (`3.13.1`).

## Other binding contracts

C# adds `VSIGetMemFileBuffer` (`3.11.0`) and
`SpatialReference.FindMatches` (`3.11.1`). SWIG `AddFieldDomain()` propagates
errors or exceptions (`3.11.1`), `Feature.GetDefnRef()` retains the returned
definition (`3.12.1`), and relationship capability constants are exposed
(`3.13.0`). Java dataset closure no longer double-frees (`3.11.4`).

## Build and runtime checklist

1. Match ABI and dependency versions before enabling optional drivers.
2. Set algorithm and raw-VRT feature gates deliberately.
3. Test cloud auth refresh, path-specific options, and cache invalidation.
4. Scope HTTP headers and query strings by path; validate redirect credential
   policy.
5. Explicitly close output datasets and verify flush errors.
6. Test the exact Python packaging toolchain and interpreter mode in use.
