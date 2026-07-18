---
name: tauri-knowledge-patch
description: Tauri
license: MIT
version: 2.5.0
metadata:
  author: Nevaberry
---

# Tauri Knowledge Patch

## Apply the patch

1. Inspect `tauri.conf.json`, `Cargo.toml`, capability files, plugin permissions, and the frontend API imports before changing code.
2. Identify whether the work concerns migration, configuration, windows/webviews, IPC, security, plugin development, a core plugin, or the experimental runtime.
3. Read every matching reference from the index; cross-cutting work commonly needs both the configuration and security references.
4. Keep platform branches explicit. Many window, filesystem, installer, and mobile APIs are target-specific.
5. Validate capability grants and scope enforcement separately: permission to invoke a command does not make its scoped arguments safe.

## Route common tasks

- For an application migration, read the migration, configuration, windows/webviews, and capabilities references together.
- For a new command, read the IPC and capabilities references; add the plugin reference when the command is plugin-owned.
- For mobile-native work, read the plugin reference plus the relevant configuration, filesystem, or window section.
- For release packaging, read configuration/distribution and the updater section of the core-plugin reference.
- For runtime replacement, read the Verso boundary before assuming ordinary Wry behavior is available.

## Reference index

| Reference | Topics |
| --- | --- |
| [configuration-security.md](references/configuration-security.md) | Configuration hierarchy, app manifests, capabilities, permissions, scopes, CSP, asset protocol, remote origins, command pruning |
| [core-plugins.md](references/core-plugins.md) | Dialog, filesystem, HTTP, store, and updater behavior |
| [ipc-state-tray.md](references/ipc-state-tray.md) | Commands, raw requests, serialization, channels, events, managed state, tray icons |
| [migration.md](references/migration.md) | Rust, Cargo, asset-provider, handle, argument, and feature migrations |
| [plugin-mobile-development.md](references/plugin-mobile-development.md) | Plugin scaffolding, typed configuration, ACL generation, native mobile bridges, OS permissions, official plugin surfaces |
| [project-distribution.md](references/project-distribution.md) | Project setup, build hooks, frontend assets, bundle resources, installers, signing inputs, build/bundle workflow |
| [verso-runtime.md](references/verso-runtime.md) | Experimental Servo-based runtime setup and compatibility boundary |
| [windows-webviews-runtime.md](references/windows-webviews-runtime.md) | Native windows versus webviews, application lifecycle, paths, protocols, platform behavior, WebView2 and Apple options |

## Breaking migration rules

### Separate native windows from webviews

- Use Rust `WebviewWindow`/`WebviewWindowBuilder` for the former window-containing-a-webview behavior. Rust `Window` now means the native container independently of its webviews.
- In JavaScript, normally use `getAllWebviewWindows` and `getCurrentWebviewWindow`; `getAllWindows` and `getCurrentWindow` return native-window handles.
- Treat multiwebview support as unstable and enable the Cargo `unstable` feature when using it.
- Replace `FileDropEvent` and `WindowEvent::FileDrop` with `DragDropEvent` and `WindowEvent::DragDrop`, and use the four `tauri://drag-*` frontend events.

### Migrate configuration before debugging APIs

- Put `productName`, `version`, and `identifier` at the root; rename `tauri` to `app`; move bundle settings to root `bundle`.
- Rename build keys to `frontendDist` and `devUrl`. `devUrl` must be a URL.
- Move the security pattern to `app.security.pattern`, the global frontend API switch to `app.withGlobalTauri`, and updater settings to `plugins.updater`.
- Move platform bundle settings under `bundle.macOS.dmg`, `bundle.linux.deb`, and `bundle.linux.appimage`; use `bundle.license` and `bundle.licenseFile` for shared licensing.
- Replace the old file-drop flag with `app.window.dragDropEnabled`.

### Update renamed Rust APIs and Cargo features

- Get paths through `Manager::path()` and `tauri::path::PathResolver`; use `tauri::ipc` for command/IPC types.
- Replace `tauri::Icon` with `tauri::image::Image` and old path/plugin result aliases with `tauri::Result` or an application result type.
- Use `tauri::scope::fs::{Scope, Pattern, Event}`; filesystem checks resolve symlinks, and the old HTTP, shell, and IPC scope types no longer exist.
- Rename features: `default-tls` to `native-tls`, `system-tray` to `tray-icon`, `window-data-url` to `webview-data-url`, and `icon-ico`/`icon-png` to `image-ico`/`image-png`.
- Remove `reqwest-*` features. `linux-protocol-headers` is always active; `linux-libxdo` opts native Linux editing menu items into `libxdo`.
- Rename the automation variable to `TAURI_WEBVIEW_AUTOMATION`.

### Choose close, exit, and restart deliberately

- `WebviewWindow::close()` emits a close-requested event; call `destroy()` for forced closure.
- `AppHandle::exit()` and restart paths emit exit-request events. After `cleanup_before_exit()`, exit immediately and make no further Tauri calls.
- Prefer `AppHandle::request_restart()` when exit-event delivery matters. Direct `restart()` waits for `RunEvent::Exit` before relaunching.
- Use `App::run_return()` when the host process must continue and receive the exit code. Do not build a polling loop around deprecated `run_iteration()`.

## Security and capability quick reference

### Register controllable application commands

Commands present only in `invoke_handler` are callable by every window and webview. Put application command names in the build-time `AppManifest` before expecting capabilities to restrict them.

```rust
tauri_build::try_build(
    tauri_build::Attributes::new()
        .app_manifest(tauri_build::AppManifest::new().commands(&["save_file"])),
)
.unwrap();
```

### Enforce scope inside the command

Capabilities decide whether an invocation reaches a command and attach configured scope. The command or plugin must interpret `CommandScope`/`GlobalScope` and enforce the allow/deny data; deny entries win. Native application code can use `WebviewWindow::resolve_command_scope` for runtime checks.

### Understand capability selection

- If `app.security.capabilities` is absent or empty, all files in `./capabilities/` are included. Once populated, the list becomes an explicit selection of identifiers or inline objects.
- Use capability `platforms` for target filters and `remote.urls` only when matching remote origins must invoke commands. Bundled content has access by default; remote content does not.
- Enable the `config-json5` feature before relying on `.json5` capability files.
- Treat `build.removeUnusedCommands` cautiously: runtime-added ACLs are invisible to build-time pruning.

## IPC, state, and events quick reference

### Register one invoke handler

Each `invoke_handler(...)` call replaces the previous handler. Put every application command in one `generate_handler![...]` list.

### Select the right transport

- Pass `ArrayBuffer` or `Uint8Array` to `invoke` for a raw `InvokeBody::Raw`; inject `tauri::ipc::Request` to read the unprocessed body and headers.
- Implement `SERIALIZE_TO_IPC_FN` for custom JavaScript argument serialization. Tauri's DPI classes already use it.
- Use events for asynchronous JSON broadcasts without replies or strong typing. Rust payloads must implement `Serialize + Clone`.
- Use `Channel` for ordered, higher-throughput streams and raw/custom serialization. Capabilities do not finely filter event or channel payload data.

### Manage state by exact type

Register `Mutex<T>`, not `Arc<Mutex<T>>` merely to add shared ownership; Tauri supplies it. State lookup uses the exact registered type. Clone an `AppHandle` into a thread, then retrieve state through `Manager` there. Do not call deprecated `Manager::unmanage`.

## Configuration and distribution quick reference

- `build.frontendDist` accepts an embedded directory, an array flattened into the asset root, or a custom-protocol/remote URL with no embedded assets. Without `devUrl`, the CLI can serve it with simple hot reload.
- Hook values may be strings or `{ script, cwd }`; `beforeDevCommand` also accepts `wait`, defaulting to `false`. Use the `TAURI_ENV_*` variables for target-aware hooks.
- `tauri build` bundles by default. Use `--no-bundle`, followed by `tauri bundle`, to separate compilation from packaging.
- Resource arrays preserve paths; resource maps control destinations, but glob matches in a map are flattened into the destination.
- Updater verification is mandatory. Preserve the private signing key, provide public-key/signature contents rather than paths, and inject the private key through `TAURI_SIGNING_PRIVATE_KEY`.
- Keep WiX `upgradeCode` stable across product renames, and remember Windows bundles allow downgrades unless `allowDowngrades` is `false`.

## Window and webview quick reference

- Window creation and `setup` run only after the event loop is ready. The page-load hook receives a `Webview` for both start and finish; inspect `PageLoadPayload::event`.
- Webviews start focused. Configure `devtools` per webview/window and use `WebviewBuilder::focused` when initial focus differs.
- On Windows and Android, custom protocols default to `http://<scheme>.localhost`; opt into HTTPS with `useHttpsScheme` or the builder method.
- Webviews sharing a Windows data directory must agree on WebView2 settings. Distinct `additionalBrowserArgs`, extension state, or scrollbar styles require distinct directories.
- Creation-only constraints such as `preventOverflow`, its margin builder variant, initialization scripts for all frames, Apple link previews, and iOS accessory views must be set before `build()`.

## Plugin and mobile quick reference

- Official plugin major versions follow Tauri's major, but a plugin may still document breaking minor releases.
- Register plugin commands on the plugin builder and invoke them as `plugin:<name>|<command>`; registration does not bypass permissions.
- Use the second plugin `Builder` generic for typed `plugins.<name>` configuration and read it from the `PluginApi` passed to `setup`.
- Generate allow/deny permissions and scope schemas in `build.rs`. Commands must inspect injected scope values themselves.
- Call Kotlin or Swift commands with `PluginHandle::run_mobile_plugin`. There is no native-to-Rust reverse bridge; use JNI on Android or C FFI on iOS when suspended-webview work must enter Rust.
- Use NDK 28 or newer for Android 16 KB page alignment, or add the documented linker maximum-page-size flag.

## Core-plugin traps

- Filesystem grants need both an operation permission and a matching path scope. `$APPDATA/*` covers direct children, not the directory plus its full tree.
- `http:default` enables the fetch workflow but grants no origins; add URL allow scopes and narrower denies.
- Store instances are shared by path across Rust and JavaScript; options from later `load()` calls are ignored until Rust closes the resource.
- Updater endpoints advance only after non-2xx responses, not malformed successful responses. Static manifests are validated in full before version comparison.
- Windows `quiet` updater installation cannot request elevation and therefore needs a per-user install or an already elevated process.

## Final checks

- Confirm every frontend invoke has the intended command registration, permission, capability, window/webview binding, and scope enforcement.
- Test configuration on each target represented by platform-specific settings.
- Exercise close, exit, restart, and updater paths using their real event-loop mode.
- Rebuild generated mobile projects when native frameworks or platform metadata require regeneration.
- Treat `tauri-runtime-verso` as experimental and verify each required API against its documented compatibility boundary.
