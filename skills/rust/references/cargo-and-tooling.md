# Cargo and Tooling

## LLD as Default Linker (x86_64 Linux)

`x86_64-unknown-linux-gnu` now uses LLD by default. Significantly faster linking for large binaries.

**Opt-out** (in `.cargo/config.toml`):

```toml
[target.x86_64-unknown-linux-gnu]
rustflags = ["-Clinker-features=-lld"]
```

## `cargo publish --workspace`

Publish all workspace crates in dependency order.

```bash
cargo publish --workspace
cargo publish --workspace --dry-run
```

## Cargo Automatic Cache Cleaning

Cargo garbage-collects its cache automatically:
- Network-downloaded files: removed after 3 months unused
- Local build artifacts: removed after 1 month unused

No action required.
