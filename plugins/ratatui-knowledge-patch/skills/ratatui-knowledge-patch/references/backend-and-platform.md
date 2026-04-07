# Backend & Platform (0.30)

## Multiple Crossterm Versions

Feature flags `crossterm_0_28` and `crossterm_0_29` allow selecting the crossterm version. The latest version is enabled by default.

```toml
# Use older crossterm version
[dependencies]
ratatui = { version = "0.30", default-features = false, features = ["crossterm_0_28"] }
```

## no_std Support

Disable default features for embedded/no_std environments. Re-enable the `layout-cache` feature if layout performance is needed.

```toml
[dependencies]
ratatui = { version = "0.30", default-features = false }
# Optional: re-enable layout caching
ratatui = { version = "0.30", default-features = false, features = ["layout-cache"] }
```

## Modularization: ratatui-core

The crate is modularized into `ratatui-core` for stable, minimal API surface.

- **Widget library authors**: depend on `ratatui-core` for a stable API to build widgets against.
- **Application developers**: continue using `ratatui` as before -- no changes needed.

```toml
# For widget library crates
[dependencies]
ratatui-core = "0.1"
```
