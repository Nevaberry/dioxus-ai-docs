# Build, Packaging, Resources, and Network Runtime

## Toolchain and CMake

- Build PROJ with a C++17-capable compiler and standard library (since 9.6.0).
  Propagate the requirement into downstream targets that compile against C++
  interfaces.
- Do not trust a positive C23 `#embed` probe from an old compiler. The CMake
  detection no longer enables the feature on compilers too old to implement it
  (since 9.6.1).
- Source builds accept CMake 4.3's deprecated `SQLite::SQLite3` target
  arrangement (since 9.8.1). A failure found only with CMake 4.3 may indicate
  that an older PROJ configuration is in use.

## Embedded resources

Use the resource switches according to the intended runtime:

```sh
cmake -S . -B build \
  -DEMBED_RESOURCE_FILES=ON \
  -DUSE_ONLY_EMBEDDED_RESOURCE_FILES=ON \
  -DEMBED_RESOURCE_DIRECTORY=/path/to/resources
```

- `EMBED_RESOURCE_FILES` embeds `proj.db` and `proj.ini` into `libproj` (since
  9.6.0).
- `USE_ONLY_EMBEDDED_RESOURCE_FILES` makes the embedded copies the only resource
  source (since 9.6.0).
- `EMBED_RESOURCE_DIRECTORY` includes `.tif` grid files and `.json` resources
  from the selected directory (since 9.6.0).
- Windows supports enabling both `EMBED_RESOURCE_FILES` and
  `USE_ONLY_EMBEDDED_RESOURCE_FILES` together (since 9.6.1).

When using embedded-only mode, include every grid and JSON resource needed by
operation discovery and exercise the packaged library without the source tree
or a system PROJ data directory.

## Package metadata and symbols

- Packaging can opt to ship PDB debug-symbol files (since 9.6.1). Preserve the
  build's symbol-package choice when repackaging Windows artifacts.
- Generated `proj.pc` contains the correct library name (since 9.8.0). If
  pkg-config emits the wrong link target, inspect whether stale generated
  metadata came from an older build or cached install.

## TLS and native certificate stores

Set `native_ca` in `proj.ini`, or use the `PROJ_NATIVE_CA` environment-variable
equivalent, to make curl use the operating system CA store (since 9.6.0).
Network code also retries an SSL connection timeout. Tests that count requests
or assert immediate timeout failure must allow for that retry behavior.

Keep the configuration source explicit in deployment manifests. An embedded
`proj.ini`, an installed file, and an environment override can otherwise make
two nominally identical builds use different trust stores.

## Grid URLs and cache behavior

- `FileManager::open_resource_file()` honors known URLs recorded in
  `grid_alternatives` even when the host is not `cdn.proj.org` (since 9.6.1).
  Permit the actual alternative hosts in network policy rather than rewriting
  valid database URLs to the default CDN.
- After `proj_download_file()` writes a file, PROJ invalidates caches associated
  with that file in the current context (since 9.6.0). Reuse of that context
  should see the downloaded resource; separately created contexts may have
  their own cache lifecycle.

## Emscripten

The network file manager uses Emscripten Fetch in Emscripten builds (since
9.8.0). Validate:

- Browser or worker URL resolution.
- CORS and content-security policy.
- Asynchronous fetch and failure behavior exposed by the host environment.
- Persistence and caching appropriate to the deployed virtual filesystem.

Do not infer native curl behavior from a WebAssembly test or vice versa.
