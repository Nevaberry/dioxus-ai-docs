# cargo-leptos

## Install a pinned prebuilt CLI

Releases provide prebuilt `cargo-leptos` binaries for these targets:

- Apple Silicon and Intel macOS
- x64 Windows
- ARM64 and x64 GNU Linux
- ARM64 and x64 MUSL Linux

Prefer the release's shell or PowerShell installer over compiling the CLI
locally when an archive exists for the target. Pin the release in the download
URL and verify the SHA-256 checksum published for the archive.

```shell
curl --proto '=https' --tlsv1.2 -LsSf \
  https://github.com/leptos-rs/cargo-leptos/releases/download/v0.3.7/cargo-leptos-installer.sh \
  | sh
```

```powershell
powershell -ExecutionPolicy Bypass -c \
  "irm https://github.com/leptos-rs/cargo-leptos/releases/download/v0.3.7/cargo-leptos-installer.ps1 | iex"
```

## Stable hot reload

The development hot-reload loop works on stable Rust (since 0.8.0). Do not
select a nightly toolchain solely for hot reloading.

## Match lazy-loading support

The `#[lazy]`, `#[lazy_route]`, lazy output hashing, and `lazy_preload`
features require a matching `cargo-leptos` release. Treat the CLI and framework
versions as a compatibility pair when enabling lazy code splitting.

## Hashed stylesheets

When `cargo-leptos` asset hashing is enabled, use `HashedStylesheet` with the
corresponding props. `Stylesheet` does not integrate automatically with the
CLI's hashed stylesheet filenames (since 0.7.0).
