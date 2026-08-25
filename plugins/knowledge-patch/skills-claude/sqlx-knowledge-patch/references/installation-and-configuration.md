# Installation and Configuration

## Toolchain and CLI installation

SQLx 0.9 requires Rust 1.94.0 (since `0.9.0-changelog`).

The SQLx repository no longer tracks `Cargo.lock`. Consequently, this command no longer works:

```console
cargo install --locked sqlx-cli
```

Install `sqlx-cli` without `--locked`. If installation must be reproducible, maintain and use a lockfile as part of the installation workflow.

## Runtime and TLS selection

Runtime and TLS selection became separate in `0.8.0`. The combined `runtime-*-native-tls` and `runtime-*-rustls` features were soft-deprecated at that point and removed in the `0.9.0-changelog` batch.

Choose one runtime and the required TLS implementation independently:

```toml
[dependencies]
sqlx = { version = "0.9", features = [
  "runtime-tokio",
  "postgres",
  "tls-rustls-ring-native-roots",
] }
```

Rustls provider and root-store choices include:

| Feature | Selection |
| --- | --- |
| `tls-rustls-ring-native-roots` | `ring` provider with platform-native CA roots |
| `tls-rustls-ring-webpki` | `ring` provider with webpki roots |
| `tls-rustls-aws-lc-rs` | AWS-LC-RS provider |

SQLx 0.9 also adds `runtime-smol` and `runtime-async-global-executor` as replacements for deprecated async-std usage.

The `offline` feature is optional. Leaving it disabled permits a build without `serde` when no other enabled functionality requires it.

## Per-crate `sqlx.toml`

The `sqlx.toml` file added in SQLx 0.9 provides per-crate configuration for:

- renaming the environment variable used instead of `DATABASE_URL`;
- defining global type overrides for macros;
- renaming or relocating the `_sqlx_migrations` directory;
- excluding selected characters, such as whitespace, from migration hashes.

The CLI enables `sqlx.toml` support by default. A library user must opt in with the `sqlx-toml` feature:

```toml
[dependencies]
sqlx = { version = "0.9", features = ["sqlx-toml"] }
```

SQLite extension loading configured through `sqlx.toml` is unsafe, just like calling the extension-loading API directly.

## Macro offline-data location

When the `SQLX_OFFLINE_DIR` environment variable is explicitly set, macros use it in preference to other offline-data locations.

## Bundled and unbundled SQLite

In SQLx 0.8, the `sqlite` feature bundles and statically links SQLite. Use `sqlite-unbundled` to link a system or custom SQLite library instead:

```toml
[dependencies]
sqlx = { version = "0.8", features = ["runtime-tokio", "sqlite-unbundled"] }
```

For the unbundled option:

- SQLite must be installed or otherwise supplied at build time.
- SQLite 3.20.0 or newer is recommended.
- The build may use bindgen and therefore take longer.

## SQLite opt-in APIs

SQLite APIs with extra build, platform, or safety implications are independently gated.

| Feature | Behavior |
| --- | --- |
| `sqlite-preupdate-hook` | Enables SQLite's normally disabled preupdate-hook API. |
| `sqlite-deserialize` | Enables SQLite serialize/deserialize APIs. |
| `sqlite-load-extension` | Enables extension-loading APIs. |
| `sqlite-unlock-notify` | Enables SQLx's internal unlock notification support. |

Example with bundled SQLite and the preupdate hook:

```toml
sqlx = { version = "0.8", features = [
  "runtime-tokio",
  "sqlite",
  "sqlite-preupdate-hook",
] }
```

Combining `sqlite-preupdate-hook` with `sqlite-unbundled` can fail at link time if the chosen system SQLite lacks the preupdate-hook API.

Example enabling serialize/deserialize and extension loading:

```toml
sqlx = { version = "0.9", features = [
  "sqlite",
  "sqlite-deserialize",
  "sqlite-load-extension",
] }
```

Extension loading is now an unsafe operation. Keep the unsafe boundary narrow and validate which extension is loaded.

SQLx may raise the maximum compatible `libsqlite3-sys` version in a non-breaking release, so do not assume that upper-bound changes require a SQLx major or minor release.
