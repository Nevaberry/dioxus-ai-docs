# Migration

Use this reference for Rust-side API, type, Cargo-feature, asset-provider, handle, and argument migrations. Read [windows-webviews-runtime.md](windows-webviews-runtime.md) for lifecycle, protocol, path, and platform behavior; migration work may also require the configuration, IPC, security, or plugin references.

## API and toolchain migration (`2.0.0-migration`, `2.0.0`)

### Toolchain and feature names

- Use Rust 1.78 or newer.
- Rename Cargo features as follows:

  | Old | New |
  | --- | --- |
  | `default-tls` | `native-tls` |
  | `system-tray` | `tray-icon` |
  | `window-data-url` | `webview-data-url` |
  | `icon-ico` | `image-ico` |
  | `icon-png` | `image-png` |

- Remove the former `reqwest-*` features.
- Treat `linux-protocol-headers` as always enabled. Enable `linux-libxdo` only to back native Linux Cut, Copy, Paste, and Select All menu actions with `libxdo`.
- Replace `TAURI_AUTOMATION` with `TAURI_WEBVIEW_AUTOMATION`.
- The application `custom-protocol` feature no longer identifies production builds. Gate production-only Rust with `#[cfg(not(dev))]`.

```rust
#[cfg(not(dev))]
fn production_only() {
    // Production custom-protocol behavior.
}
```

### Module and type moves

- Replace functions under `tauri::api::path` with methods on `tauri::path::PathResolver`, acquired through `Manager::path()`.
- Import command and IPC items from `tauri::ipc`.
- Replace `tauri::Icon` with `tauri::image::Image`.
- Replace old path/plugin `Result` aliases with `tauri::Result` or an application-defined result type.
- Replace `FsScope`, `GlobPattern`, and `FsScopeEvent` with `tauri::scope::fs::{Scope, Pattern, Event}`. Filesystem scope checks now resolve symlinks.
- Remove usages of the deleted IPC, HTTP, and shell scope types.

### Context and custom assets

`Context` and `Assets` carry the runtime generic, while `Context` no longer has a separate assets-implementation generic. Replace `assets_mut()` with `set_assets()`. `Context::assets()` returns `&dyn Assets`, so an assets implementation can be exchanged at runtime.

### Signatures and handles

- Plugin `setup` receives both the application and a `PluginApi` argument.
- `App::handle()` and `Manager::app_handle()` return borrowed `AppHandle`s. Clone the handle when owned access is required.
- `Env.args` is now `args_os`, contains `OsString`s, and includes the executable path.
- The migrated `run_iteration` takes a callback and returns nothing; it is now deprecated for repeated use because that pattern spins a busy loop.
- `WebviewWindow::url()` returns a result.
- Do not import `WebviewAttributes` from the removed accidental `tauri-runtime` re-export (removed in `2.5.0`). Import it from its defining API when needed.
