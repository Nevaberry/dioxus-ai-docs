# Cargo & Toolchain (1.84–1.94)

## Cargo MSRV-Aware Resolver (v3) — 1.84

Resolver v3 prefers dependency versions compatible with the project's declared `rust-version`. Enabled by default in Rust 2024 Edition.

```toml
# Cargo.toml — raises MSRV to 1.84
[package]
resolver = "3"
rust-version = "1.80"

# Or configure globally without changing MSRV:
# .cargo/config.toml
[resolver]
incompatible-rust-versions = "fallback"  # prefer compatible; fall back if unavailable
# incompatible-rust-versions = "allow"   # old v2 behavior
```

```bash
# CI: test with latest dependencies regardless of MSRV
CARGO_RESOLVER_INCOMPATIBLE_RUST_VERSIONS=allow cargo update
```

**Behavior:** With v3, `cargo add`/`cargo update` selects the newest version still compatible with your `rust-version`. Falls back to incompatible versions if no compatible version exists.

## `cargo publish --workspace` — 1.90

Publish all workspace crates in correct dependency order with a single command.

```bash
cargo publish --workspace
cargo publish --workspace --dry-run   # verify without publishing
cargo publish --workspace --no-verify # skip build check
```

Crates are published in topological order (dependencies before dependents). Fails if any crate fails to publish.

## LLD Now Default Linker on x86_64-linux — 1.90

The `x86_64-unknown-linux-gnu` target now uses LLD by default for faster link times. Opt out if encountering issues:

```toml
# .cargo/config.toml
[target.x86_64-unknown-linux-gnu]
rustflags = ["-Clinker-features=-lld"]
```

## Cargo Config `include` — 1.94

`.cargo/config.toml` can now include additional config files.

```toml
# .cargo/config.toml
include = [
  { path = "ci.toml" },
  { path = "local.toml", optional = true }, # ignored if missing
]
```

Included files are merged, with the including file taking priority on conflicts. Useful for CI-specific settings or user-local overrides that aren't checked in.

## TOML 1.1 in Cargo Manifests — 1.94

Multi-line inline tables and trailing commas now work in `Cargo.toml`.

```toml
# Previously required single-line or standard table syntax:
[dependencies]
serde = {
    version = "1.0",
    features = ["derive"],
}

tokio = {
    version = "1",
    features = [
        "rt",
        "macros",
    ],
}
```

**Note:** Raises the effective dev MSRV (others need a Cargo that supports TOML 1.1). Cargo rewrites to compatible format on `cargo publish` for backwards compatibility.

## `wasm32-wasi` Target Removed — 1.84 (Breaking)

The `wasm32-wasi` target was removed. Use `wasm32-wasip1` (introduced in 1.78, warned since 1.81).

```bash
# Old (removed):
cargo build --target wasm32-wasi

# New:
cargo build --target wasm32-wasip1
```
