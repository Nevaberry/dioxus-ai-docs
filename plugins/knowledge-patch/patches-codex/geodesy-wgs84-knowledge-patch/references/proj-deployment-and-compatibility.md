# PROJ Deployment and Compatibility

## Database and result compatibility

### EPSG rollback in PROJ 9.8.1

PROJ 9.8.0 shipped EPSG v12.049, but PROJ 9.8.1 reverted the EPSG content to v12.029, the version used by 9.7.1. The rollback removes national `ETRS89-XXX` datum and CRS records introduced in 9.8.0 because they caused incompatible ETRS89 transformation selection for Austria, Belgium, Catalonia, the Netherlands, Romania, and Serbia.

A newer PROJ patch is therefore not necessarily a superset of the preceding patch’s EPSG records. Pin both PROJ and database expectations when operation selection must remain reproducible.

### Version floors for corrected transformations

- Require PROJ 9.3.1 to correct the sign of the ITRF2008 `dry` parameter for `EURA` and `EURA_T`.
- Require PROJ 9.6.0 to correct an ITRF97 parameter typo in the ITRF2014 file.
- Require PROJ 9.6.1 to prevent NAD83(CSRS)-realization transformations from routing through generic NAD83.

Results from older versions are not equivalent for those cases.

## Build and source compatibility

- PROJ 7 requires a C99 compiler.
- PROJ 8 removes the deprecated `proj_api.h`; migrate callers to `proj.h`.
- PROJ 9 removes Autotools, leaving CMake as the bundled build system.
- PROJ 9.4 raises the CMake minimum to 3.16.
- Building PROJ 9.6 requires C++17.

Upgrade build tooling before crossing these boundaries.

## Resource packaging and lookup

### Embedded resources

Since PROJ 9.6:

- `EMBED_RESOURCE_FILES` embeds `proj.db` and `proj.ini`.
- `USE_ONLY_EMBEDDED_RESOURCE_FILES` selects embedded-only lookup.
- `EMBED_RESOURCE_DIRECTORY` adds `.tif` and `.json` resources to `libproj`.

Also since 9.6, `proj_download_file()` invalidates related in-memory caches for the current context after downloading a resource.

### Search paths and writable data

PROJ 9.1 introduced `PROJ_DATA` and deprecated `PROJ_LIB`. Multiple resource directories have been accepted since PROJ 6.0. User-set search paths take priority over the environment path since 6.1.

Use `projinfo --searchpaths`, available since PROJ 7.0, to inspect effective locations. PROJ 9.5 added `proj_context_set_user_writable_directory()` to control the per-context writable resource directory.

### Network grids and certificates

PROJ 7 introduced Geodetic TIFF transformation grids, access to `cdn.proj.org`, and the `projsync` downloader. TIFF-grid reading requires a build with `libtiff`; online access requires `libcurl`. An operation’s presence in `proj.db` does not guarantee that a deployment can read or fetch its grid.

PROJ 9.6 added the `native_ca` setting in `proj.ini` and the `PROJ_NATIVE_CA` environment variable. They make curl-backed resource access use the operating system CA store instead of relying only on a separately configured CA bundle.

## Application and command-line integration

### Embedded `projinfo`

PROJ 9.8.0 exposed `projinfo` as a library function and installs `projapps_lib.h`. Applications can embed the same inspection facility instead of invoking only the executable.

### Stream behavior

- Since PROJ 5.2, `cct` copies text after input coordinates to output, preserving record payloads.
- Since PROJ 7.2, `projinfo` emits multiline PROJ strings by default; use `--single-line` for one line.
- Since PROJ 8.0, `cct` accepts operation codes or names and `@filename` input.

## Grid validation

PROJ 7 and newer reject NTv2 files whose `GS_TYPE` is not `SECONDS`. Correct or convert a legacy NTv2 file with another declared shift unit instead of relying on implicit interpretation.
