# cargo-leptos

## Install a pinned prebuilt CLI

`cargo-leptos` releases provide prebuilt binaries for Apple Silicon and Intel
macOS, x64 Windows, and ARM64/x64 GNU and MUSL Linux. Each archive has a
SHA-256 checksum. Prefer the release's shell or PowerShell installer for a
pinned version over compiling the CLI locally.

```shell
curl --proto '=https' --tlsv1.2 -LsSf \
  https://github.com/leptos-rs/cargo-leptos/releases/download/v0.3.7/cargo-leptos-installer.sh \
  | sh
```

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://github.com/leptos-rs/cargo-leptos/releases/download/v0.3.7/cargo-leptos-installer.ps1 | iex"
```

Pin the URL to the intended release and verify the downloaded archive against
the published checksum before use.

## Use stable Rust for hot reloading

Development hot reloading works on stable Rust (since 0.8.0). Do not select a
nightly toolchain solely to support the hot-reload loop.

## Keep lazy loading support aligned

The `#[lazy]` and `#[lazy_route]` facilities require a matching
`cargo-leptos` release. Lazy output can use hashed filenames, so keep the CLI
and application-side lazy-loading support compatible. See
[Server functions and lazy loading](server-functions-and-lazy-loading.md).
