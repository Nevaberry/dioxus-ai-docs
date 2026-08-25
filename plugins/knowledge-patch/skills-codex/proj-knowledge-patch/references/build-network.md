# Build, Packaging, and Network Resources

## Compiler and CMake Requirements

- PROJ builds as C++17 (since 9.6.0). Downstream compilers, standard-library
  implementations, package recipes, and build flags must support that language
  version.
- CMake avoids reporting C23 `#embed` support on compilers too old to provide a
  usable implementation (since 9.6.1). Reconfigure rather than forcing the
  detected result when an older compiler selects an invalid embedding path.
- The CMake configuration handles the deprecated `SQLite::SQLite3` target in
  CMake 4.3 (since 9.8.1), allowing source builds to use that CMake release.

## Embedding Runtime Resources

Since 9.6.0, CMake can embed `proj.db` and `proj.ini` in `libproj`:

```sh
cmake -S . -B build \
  -DEMBED_RESOURCE_FILES=ON \
  -DUSE_ONLY_EMBEDDED_RESOURCE_FILES=ON \
  -DEMBED_RESOURCE_DIRECTORY=/path/to/resources
```

- `EMBED_RESOURCE_FILES` enables embedding of the core files.
- `USE_ONLY_EMBEDDED_RESOURCE_FILES` prevents fallback to external resource
  files.
- `EMBED_RESOURCE_DIRECTORY` adds `.tif` and `.json` resources to the library.

Windows builds support enabling `EMBED_RESOURCE_FILES` and
`USE_ONLY_EMBEDDED_RESOURCE_FILES` together (since 9.6.1).

Treat embedded-only mode as a closed resource set. Inventory all grids required
by the selected operations; network availability cannot compensate for a build
that intentionally prohibits external resources.

## Packaging and Consumer Metadata

- A build option can include PDB debug-symbol files in PROJ packages (since
  9.6.1). Packaging jobs should explicitly choose whether symbols belong in the
  main package or a separate debug artifact.
- Generated `proj.pc` uses the correct library name (since 9.8.0). Downstream
  pkg-config checks should verify the emitted link target instead of retaining
  a workaround for incorrect metadata.

## TLS and Native CA Trust

The `native_ca` setting in `proj.ini` configures curl to use the operating
system CA store (since 9.6.0). Its environment equivalent is
`PROJ_NATIVE_CA`. Use the value form expected by the deployment’s PROJ
configuration. Network access also retries an SSL connection timeout.

This setting changes trust-source selection; it does not enable network access,
install certificates, or guarantee that a platform curl build supports the
same TLS backend.

## Grid URLs and Cache State

`FileManager::open_resource_file()` honors known URLs from
`grid_alternatives` even when the URL does not use `cdn.proj.org` (since
9.6.1). A restricted-host allowlist must therefore be derived from the actual
database and deployment policy rather than hardcoded to the PROJ CDN.

After `proj_download_file()` downloads a file, caches associated with that file
are invalidated in the current context (since 9.6.0). This prevents that
context from continuing to use stale negative or resource lookup state.
Do not infer that independent contexts or processes were invalidated.

## Emscripten and WebAssembly

The network file manager uses Emscripten Fetch in Emscripten builds (since
9.8.0). WebAssembly applications should validate:

- network enablement and origin policy;
- asynchronous/browser fetch constraints in their runtime;
- certificate and URL policy at the hosting layer;
- persistence or caching of downloaded grids; and
- behavior when resources are embedded-only.

## Build Verification

After configuration or package changes:

1. Inspect CMake’s detected compiler features.
2. Confirm the chosen embedded/external resource policy.
3. Load `proj.db`, `proj.ini`, and at least one required grid.
4. Check PDB artifacts on applicable Windows packages.
5. Query `pkg-config --libs proj` from the staged installation.
6. Exercise a TLS download using the deployment’s CA-store policy.
7. For Emscripten, test a real remote-resource request in the target runtime.
