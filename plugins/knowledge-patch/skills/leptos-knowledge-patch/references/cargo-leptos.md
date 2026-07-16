# cargo-leptos

## Install a pinned prebuilt release

Releases provide ready-to-run archives for:

- AArch64 and x86-64 macOS;
- x86-64 Windows;
- AArch64 and x86-64 Linux using either GNU or MUSL.

Each archive has a SHA-256 checksum. Pin the desired release, use its shell or
PowerShell installer, and verify the downloaded artifact rather than requiring
a local Rust build of the CLI.

```shell
curl --proto '=https' --tlsv1.2 -LsSf \
  https://github.com/leptos-rs/cargo-leptos/releases/download/v0.3.7/cargo-leptos-installer.sh \
  | sh
```

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://github.com/leptos-rs/cargo-leptos/releases/download/v0.3.7/cargo-leptos-installer.ps1 | iex"
```

## Development and generated assets

Hot reloading works on stable Rust (since 0.8.0); a nightly toolchain is not
needed solely for that development loop.

Features that emit lazy-loaded code require a matching `cargo-leptos` release.
Lazy output can use file hashing. For stylesheet hashing, render
`HashedStylesheet` with its corresponding props: `Stylesheet` no longer
integrates automatically with CLI-generated hashed filenames (since 0.7.0).
