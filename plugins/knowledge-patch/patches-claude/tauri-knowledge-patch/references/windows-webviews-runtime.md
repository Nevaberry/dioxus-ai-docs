# Windows, Webviews, and Application Runtime

Use this reference for application lifecycle, window/webview migrations, creation-time options, paths, protocols, platform integration, and WebView2 data-directory constraints.

## Contents

- [Window/webview separation and drag/drop](#native-window-and-webview-separation)
- [Application lifecycle](#application-lifecycle)
- [Focus, navigation, and protocol schemes](#focus-developer-tools-and-navigation-210)
- [Data stores, extensions, badges, and WebView2](#data-stores-and-extensions-220)
- [Cookies and script execution](#cookies-and-script-execution-240)
- [Creation-time controls](#creation-time-controls-250)
- [Per-data-directory settings](#per-data-directory-settings)
- [Paths and ownership](#paths-and-ownership)
- [Platform integration](#platform-integration)

## Native-window and webview separation

The Rust types that represented a native window containing one webview are now `WebviewWindow` and `WebviewWindowBuilder`. `tauri::Window` represents the native window independently of any webviews it contains.

JavaScript code that means a window-with-webview should normally use `getAllWebviewWindows()` or `getCurrentWebviewWindow()`. The renamed `getAllWindows()` and `getCurrentWindow()` functions return native-window handles. Multiwebview support requires the Cargo `unstable` feature.

## Drag and drop

- Replace `FileDropEvent` with `DragDropEvent`.
- Replace `WindowEvent::FileDrop` with `WindowEvent::DragDrop`.
- Replace the disable method with `disable_drag_drop_handler`.
- Listen in the frontend for `tauri://drag-enter`, `tauri://drag-over`, `tauri://drag-drop`, and `tauri://drag-leave`.

## Application lifecycle

### Event-loop readiness and page loads

Window creation and the application `setup` hook occur only after the event loop becomes ready. The page-load hook receives a `Webview`, runs for both load start and load finish, and distinguishes the phase through `PageLoadPayload::event`.

### Close and forced destruction

`WebviewWindow::close()` requests closure and emits the close-requested event. Use `destroy()` when the window must be removed without that request flow.

### Exit and cleanup

`AppHandle::exit()` and restart paths emit `RunEvent::ExitRequested` and `RunEvent::Exit`. `tauri::ExitRequestApi` is publicly exported as of `2.3.0`, so downstream code can name the request API type.

Once `cleanup_before_exit()` returns, terminate the process immediately. Do not invoke more Tauri APIs afterward.

### Returning to the host process (`2.4.0`)

Use `App::run_return()` to run the application event loop without terminating the host process and to receive the requested exit code. It is unavailable on iOS and falls back there to ordinary `App::run()` behavior. Avoid repeated `App::run_iteration()` calls because they produce a busy loop.

### Restart delivery

- Prefer `AppHandle::request_restart()` when `RunEvent::Exit` must reliably fire.
- Direct `AppHandle::restart()` waits for `RunEvent::Exit` to be delivered before restarting.
- Under `App::run_return()`, both restart methods work as of `2.5.0`; earlier behavior ignored them in this mode.

## Focus, developer tools, and navigation (`2.1.0`)

Configured windows and JavaScript-created webviews accept `devtools`. Rust provides both `WebviewWindowBuilder::devtools()` and `WebviewBuilder::devtools()`.

Webviews are focused by default. Use `WebviewBuilder::focused()` to choose a different initial focus state.

`Webview::navigate()` and `WebviewWindow::navigate()` borrow `&self` rather than `&mut self` as of `2.3.0`, so navigation does not require exclusive access.

## Custom-protocol scheme

Windows and Android default custom-protocol origins to `http://<scheme>.localhost`. Set window `useHttpsScheme` or call `WebviewWindowBuilder::use_https_scheme()`/`WebviewBuilder::use_https_scheme()` to use `https://<scheme>.localhost`.

URI-scheme handlers return `http::Response` directly rather than `Result`. Represent failures as responses with status 400 or higher. Register the asynchronous handler variant when resolving a request must not block the main thread.

For an unprocessed local file loaded directly into a webview, prefer `convertFileSrc` over transferring the complete file through IPC.

```json
{
  "app": {
    "windows": [{ "label": "main", "useHttpsScheme": true }]
  }
}
```

## Windows window classes

Set `app.windows[].windowClassname` to choose the native Windows class name. Programmatic native and webview windows expose `WindowBuilder::window_classname()` and `WebviewWindowBuilder::window_classname()`.

## Data stores and extensions (`2.2.0`)

- On macOS, use `WebviewWindowBuilder::data_store_identifier()` or `WebviewBuilder::data_store_identifier()` to choose a webview data-store identifier.
- On Linux and Windows, use `WebviewWindowBuilder::extensions_path()` or `WebviewBuilder::extensions_path()` to choose the directory from which extensions are loaded.

## Platform badge APIs

Choose the badge operation by platform for either `Window` or `WebviewWindow`:

| API | Platforms |
| --- | --- |
| `set_badge_count` | Linux, macOS, iOS |
| `set_overlay_icon` | Windows |
| `set_badge_label` | macOS |

## WebView2 compatibility

The `webview2-com` upgrade to 0.34 can break Windows integrations that customize WebView2 through `with_webview`. Review and retest those integrations when moving to the `2.2.0` API set.

On Windows, undecorated windows with shadows have native resize handles outside the client area as of `2.3.0`. Avoid layering custom edge-resize behavior over those handles without testing hit regions.

## Background throttling

An option to alter the default background-throttling policy was added in `2.3.0`. At that version the option applies only to WebKit, so do not assume equivalent behavior on WebView2 or other engines.

## Cookies and script execution (`2.4.0`)

- Call `cookies()` on `Webview` or `WebviewWindow` for the full cookie collection.
- Call `cookies_for_url()` for cookies applicable to one URL.
- Use `WebviewBuilder::disable_javascript()` or `WebviewWindowBuilder::disable_javascript()` to construct a webview with JavaScript disabled.
- When `zoom_hotkeys_enabled` is `true`, mouse-wheel input changes webview zoom.
- `Webview::eval()` and `WebviewWindow::eval()` accept `impl Into<String>` as of `2.5.0`, so owned strings such as `format!(...)` can be passed directly.

```rust
webview.eval(format!("window.answer = {answer}"))?;
```

## macOS traffic lights

Set configured-window `trafficLightPosition` or call `WebviewWindowBuilder::traffic_light_position()` to place macOS traffic-light buttons.

## Creation-time controls (`2.5.0`)

These options must be selected while constructing the webview or window:

- Run initialization scripts in every frame with `WebviewBuilder::initialization_script_on_all_frames()`, `WebviewWindowBuilder::initialization_script_on_all_frames()`, or `WebviewAttributes::initialization_script_on_all_frames()`. The default behavior runs them only in the main frame.
- On iOS, attach a custom input accessory with `WebviewBuilder::with_input_accessory_view_builder()` or `WebviewWindowBuilder::with_input_accessory_view_builder()`.
- On macOS and iOS, override WebKit's enabled-by-default link previews with `WebviewBuilder::allow_link_preview(false)` or `WebviewWindowBuilder::allow_link_preview(false)`.
- Keep a newly created window within monitor bounds with configured `preventOverflow`, `WindowBuilder::prevent_overflow()`, `WebviewWindowBuilder::prevent_overflow()`, or the margin-bearing `prevent_overflow_with_margin()` variants. The constraint applies at creation.

```json
{
  "app": {
    "windows": [{ "label": "main", "preventOverflow": true }]
  }
}
```

## Per-data-directory settings

Configured `dataDirectory` values are relative to `appDataDir()/${label}`. Use a Rust builder when an absolute directory is required.

On Windows, webviews with different values for any of the following must use different data directories:

- `additionalBrowserArgs`
- `browserExtensionsEnabled`
- `scrollBarStyle`

Setting `additionalBrowserArgs` replaces Wry's default WebView2 feature-disabling arguments; it does not append to them.

The `fluentOverlay` scrollbar style is Windows-only, requires WebView2 125.0.2535.41 or newer, and must match across all webviews sharing a data directory.

A webview `proxyUrl` accepts only `http://` or `socks5://`. On macOS it additionally requires the Cargo `macos-proxy` feature and macOS 14 or newer.

## Paths and ownership

- `PathResolver` implements `Clone` as of `2.3.0`, so it can move into separately owned contexts.
- `PathResolver::home_dir()` works on Android as of `2.1.0`.
- `basename` and `extname` accept Android content URIs as of `2.4.0`. Use `PathResolver::file_name()` to resolve an Android content-URI name; on other platforms it delegates to `std::path::Path::file_name`.
- Do not use deprecated `Manager::unmanage()`. Removing managed state can create use-after-free unsoundness.

## Platform integration

- Linux uses the configured application `identifier` as its GTK application ID. Set `enableGtkAppId` to `false` to opt out.
- Bundles support file associations.
- macOS and iOS deliver deep-link opens through `RunEvent::Opened`.
- `Builder::invoke_system()` accepts `AsRef<str>` as of `2.5.0`, allowing borrowed or owned string-like values.
