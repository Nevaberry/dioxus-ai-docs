---
name: tauri-knowledge-patch
description: "Tauri 2.0-2.5 changes since training cutoff — capabilities replacing allowlist, IPC channels, plugin system v2, mobile support, config v2 structure. Load before working with Tauri."
version: "2.5.0"
license: MIT
metadata:
  author: Nevaberry
---

# Tauri Knowledge Patch

Covers Tauri 2.0–2.5 (Oct 2024 – Apr 2025). Claude knows Tauri v1.x (Rust backend + web frontend, `tauri::command`, v1 allowlist, `tauri.conf.json` v1). It is **unaware** of the v2 architecture and any of the changes below.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Config v2 | [references/config-v2.md](references/config-v2.md) | `tauri` key renamed to `app`, top-level `productName`/`identifier`, `frontendDist`/`devUrl` |
| Permissions & Capabilities | [references/permissions-capabilities.md](references/permissions-capabilities.md) | Replaces allowlist, capability files, platform-specific, remote URL access |
| IPC: Channels & Response | [references/ipc.md](references/ipc.md) | `Channel<T>` streaming, `ipc::Response` for binary data |
| Mobile support | [references/mobile.md](references/mobile.md) | `mobile_entry_point`, lib.rs/main.rs split, crate-type config |
| Plugin system v2 | [references/plugin-system.md](references/plugin-system.md) | Built-in APIs moved to plugins, `cargo tauri add`, JS import changes |
| Event system | [references/events.md](references/events.md) | `Emitter`/`Listener` traits, `emit_to`, `listen_any`, `emit_str*` |
| API additions | [references/api-additions.md](references/api-additions.md) | Window colors, badging, reload, cookies, restart, dock visibility |

---

## Config v2 Quick Reference

`tauri.conf.json` restructured. Key renames:

| v1 Key | v2 Key |
|---|---|
| `tauri` | `app` |
| `package.productName` | `productName` (top-level) |
| `build.distDir` | `build.frontendDist` |
| `build.devPath` | `build.devUrl` |
| `tauri.allowlist` | removed (use capabilities) |
| `tauri.systemTray` | `app.trayIcon` |
| `tauri.bundle` | `bundle` (top-level) |
| cli/updater config | `plugins.cli` / `plugins.updater` |

Must add `identifier` (reverse-domain) and `mainBinaryName` at top level.

```json
{
  "productName": "my-app",
  "version": "0.1.0",
  "identifier": "com.example.myapp",
  "mainBinaryName": "my-app",
  "build": {
    "frontendDist": "../dist",
    "devUrl": "http://localhost:5173"
  },
  "app": {
    "security": {
      "capabilities": [
        "main-capability"
      ]
    },
    "windows": [
      {
        "title": "My App",
        "width": 800,
        "height": 600
      }
    ]
  },
  "bundle": {},
  "plugins": {}
}
```

---

## Capabilities (replaces v1 allowlist)

Place JSON/TOML files in `src-tauri/capabilities/` (auto-enabled). Each capability grants permissions to specific windows:

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "main-capability",
  "windows": ["main"],
  "permissions": [
    "core:path:default",
    "core:event:default",
    "core:window:default",
    "core:app:default",
    "fs:read-files",
    "fs:scope-home"
  ]
}
```

Platform-specific: add `"platforms": ["linux", "macOS", "windows"]` or `["iOS", "android"]`. Remote access: use `"remote": { "urls": ["https://*.example.com"] }` instead of `"windows"`.

Custom permission sets in `src-tauri/permissions/<name>.toml`:

```toml
[[set]]
identifier = "allow-home-read"
description = "Read access to home directory"
permissions = ["fs:read-files", "fs:scope-home"]
```

---

## IPC Channels

`tauri::ipc::Channel<T>` for ordered Rust-to-frontend streaming (replaces events for progress/streaming):

```rust
use serde::Serialize;
use tauri::ipc::Channel;

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase", tag = "event", content = "data")]
enum DownloadEvent {
    Started { url: String, content_length: usize },
    Progress { chunk_length: usize },
    Finished,
}

#[tauri::command]
fn download(url: String, on_event: Channel<DownloadEvent>) {
    on_event
        .send(DownloadEvent::Started {
            url,
            content_length: 1000,
        })
        .unwrap();
    on_event.send(DownloadEvent::Finished).unwrap();
}
```

```typescript
import { invoke, Channel } from '@tauri-apps/api/core';

const onEvent = new Channel<DownloadEvent>();
onEvent.onmessage = (msg) => console.log(msg.event, msg.data);
await invoke('download', { url: 'https://example.com', onEvent });
```

Binary returns without JSON overhead: `fn read_file(path: String) -> tauri::ipc::Response { Response::new(std::fs::read(path).unwrap()) }`

---

## Mobile Entry Point

```rust
// src-tauri/src/lib.rs (shared)
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![/* commands */])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

Desktop-only `main.rs` calls `app_lib::run()`. Add `crate-type = ["staticlib", "cdylib", "rlib"]` to `Cargo.toml [lib]`.

---

## Plugin System v2

Built-in v1 APIs moved to plugins. Install: `cargo tauri add <plugin>`. Register: `.plugin(tauri_plugin_fs::init())`.

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

JS imports: `@tauri-apps/api/tauri` -> `@tauri-apps/api/core`. `@tauri-apps/api/window` -> `@tauri-apps/api/webviewWindow`.

---

## Event System

`Emitter` and `Listener` are now traits — `use tauri::{Emitter, Listener}`. `emit` sends to all. `emit_to` targets a webview. `emit_filter` filters by `EventTarget`. `listen_global` renamed to `listen_any`.

---

## Notable API Additions (v2.1–v2.5)

| API | Version |
|---|---|
| `Window::set_background_color` / `WindowBuilder::background_color` | v2.1 |
| `app > security > headers` config for response headers | v2.1 |
| `useHttpsScheme` config option (Windows/Android) | v2.1 |
| `WebviewBuilder::devtools` (per-webview) | v2.1 |
| `set_badge_count`, `set_overlay_icon`, `set_badge_label` | v2.2 |
| `WebviewBuilder::data_store_identifier` (macOS) | v2.2 |
| `WebviewBuilder::extensions_path` (Linux/Windows) | v2.2 |
| `emit_str*` methods (pre-serialized JSON) | v2.3 |
| `App::run_return` (returns exit code) | v2.4 |
| `AppHandle::request_restart()` | v2.4 |
| `Webview::reload` / `WebviewWindow::reload` | v2.4 |
| `Webview::cookies()` / `cookies_for_url()` | v2.4 |
| `build > removeUnusedCommands` config | v2.4 |
| `WebviewBuilder::disable_javascript` | v2.4 |
| `trafficLightPosition` window config (macOS) | v2.4 |
| `set_dock_visibility` (macOS) | v2.5 |
| `initialization_script_on_all_frames` (iframe) | v2.5 |
| `preventOverflow` config (clamp to monitor) | v2.5 |
| `WebviewBuilder::allow_link_preview` (macOS/iOS) | v2.5 |
