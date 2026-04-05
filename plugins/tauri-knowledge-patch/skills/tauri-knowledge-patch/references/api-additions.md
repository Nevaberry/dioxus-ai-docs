# API Additions (v2.1–v2.5)

## v2.1

- `Window::set_background_color` / `WindowBuilder::background_color`
- `app > security > headers` config for response headers
- `useHttpsScheme` config option for Windows/Android
- `WebviewBuilder::devtools` to enable/disable per-webview

## v2.2

- Badging APIs: `set_badge_count`, `set_overlay_icon`, `set_badge_label`
- `WebviewBuilder::data_store_identifier` on macOS
- `WebviewBuilder::extensions_path` on Linux/Windows

## v2.3

- `emit_str*` methods for pre-serialized JSON events

## v2.4

- `App::run_return` — returns exit code instead of terminating process
- `AppHandle::request_restart()` — triggers exit event before restart
- `Webview::reload` / `WebviewWindow::reload`
- `Webview::cookies()` / `cookies_for_url()`
- `build > removeUnusedCommands` config to strip unused commands
- `WebviewBuilder::disable_javascript`
- `trafficLightPosition` window config for macOS

## v2.5

- `set_dock_visibility` on macOS
- `initialization_script_on_all_frames` for iframe support
- `preventOverflow` config to clamp window to monitor bounds
- `WebviewBuilder::allow_link_preview` on macOS/iOS
