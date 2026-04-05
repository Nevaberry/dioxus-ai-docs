# Plugin System v2

Most v1 built-in APIs moved to official plugins. Install with `cargo tauri add <plugin>`.

## v1 to v2 Plugin Migration

| v1 API | v2 Plugin | JS Package |
|---|---|---|
| `tauri.allowlist.fs` | `tauri-plugin-fs` | `@tauri-apps/plugin-fs` |
| `tauri.allowlist.http` | `tauri-plugin-http` | `@tauri-apps/plugin-http` |
| `tauri.allowlist.dialog` | `tauri-plugin-dialog` | `@tauri-apps/plugin-dialog` |
| `tauri.allowlist.shell` | `tauri-plugin-shell` | `@tauri-apps/plugin-shell` |
| `tauri.updater` | `tauri-plugin-updater` | `@tauri-apps/plugin-updater` |
| `@tauri-apps/api/clipboard` | `tauri-plugin-clipboard-manager` | `@tauri-apps/plugin-clipboard-manager` |
| `@tauri-apps/api/notification` | `tauri-plugin-notification` | `@tauri-apps/plugin-notification` |
| `@tauri-apps/api/os` | `tauri-plugin-os` | `@tauri-apps/plugin-os` |
| `@tauri-apps/api/process` | `tauri-plugin-process` | `@tauri-apps/plugin-process` |

## JS Import Path Changes

- `@tauri-apps/api/tauri` -> `@tauri-apps/api/core`
- `@tauri-apps/api/window` -> `@tauri-apps/api/webviewWindow`

## Registering Plugins in Rust

```rust
tauri::Builder::default()
    .plugin(tauri_plugin_fs::init())
    .plugin(tauri_plugin_store::Builder::new().build())
```
