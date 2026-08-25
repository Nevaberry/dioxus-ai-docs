# Plugin and Mobile Development

Use this reference to scaffold a plugin, define typed configuration and permissions, bridge Rust to Kotlin or Swift, and choose newer official plugin surfaces.

## Contents

- [Compatibility and scaffolding](#compatibility-and-bridge-architecture)
- [Configuration and commands](#typed-configuration)
- [Permissions and scopes](#generate-permissions-and-scope-schemas)
- [Rust-to-mobile calls](#call-native-mobile-commands-from-rust)
- [Native lifecycle, events, and permissions](#native-configuration-and-lifecycle)
- [Native-to-Rust FFI](#call-rust-from-native-code)
- [Android alignment and official plugins](#android-16-kb-page-alignment)

## Compatibility and bridge architecture

Official plugin major versions follow Tauri's major version. Each plugin owns its stability policy, however, and may publish breaking API changes in a minor release; read the plugin's release notes before updating it.

On mobile, a plugin may expose Kotlin methods annotated with `@Command` and Swift `Plugin` subclass methods directly to the frontend. Native code can instead be reached indirectly through a Rust Tauri command when the application needs a Rust-owned boundary.

Plugin `setup` receives the application plus a second `PluginApi` argument. Typed plugin configuration is available through that API.

## Scaffold a plugin

`plugin new` creates a `tauri-plugin-<name>` Cargo crate and a JavaScript API package. Pass `--no-api` to omit the JavaScript package, and `--android` and/or `--ios` to include native library projects.

```sh
npx @tauri-apps/cli plugin new camera --android --ios
```

## Typed configuration

Use the second `tauri::plugin::Builder` generic as the plugin configuration type. Tauri deserializes `plugins.<name>` into it and exposes it through the `PluginApi` passed to `setup`. Wrap the configuration type in `Option` when the entire plugin configuration is optional.

```rust
#[derive(serde::Deserialize)]
struct Config {
    timeout: usize,
}

fn init<R: tauri::Runtime>() -> tauri::plugin::TauriPlugin<R, Config> {
    tauri::plugin::Builder::<R, Config>::new("camera")
        .setup(|_, api| {
            let _timeout = api.config().timeout;
            Ok(())
        })
        .build()
}
```

## Namespaced, permission-gated commands

Register plugin commands on the plugin's own builder. Frontend command names use `plugin:<name>|<command>`. Registration does not make a plugin command callable until an applicable permission and capability allow it.

```rust
fn init<R: tauri::Runtime>() -> tauri::plugin::TauriPlugin<R, ()> {
    tauri::plugin::Builder::<R, ()>::new("camera")
        .invoke_handler(tauri::generate_handler![commands::open_camera])
        .build()
}
```

```javascript
import { invoke } from "@tauri-apps/api/core";

await invoke("plugin:camera|open_camera", { quality: 90 });
```

## Generate permissions and scope schemas

In the plugin's `build.rs`, give `tauri_plugin::Builder` snake-case command names to generate matching `allow-<command>` and `deny-<command>` permissions.

Scope types should derive `schemars::JsonSchema`. Register the generated schema in the same builder to give capability authors validation and completion. If the same scope module is compiled by the plugin and `build.rs`, add `schemars` to both normal and build dependencies.

```rust
#[path = "src/scope.rs"]
mod scope;

const COMMANDS: &[&str] = &["open_camera"];

fn main() {
    tauri_plugin::Builder::new(COMMANDS)
        .global_scope_schema(schemars::schema_for!(scope::Entry))
        .build();
}
```

## Read and enforce scope

Inject `tauri::ipc::CommandScope<'_, Entry>` into a plugin command to read scope attached to that allowed command invocation. Inject `GlobalScope<'_, Entry>` to read scope-only permissions for the plugin. Inspect `allows()` and `denies()` and enforce them in command code; deny values take precedence.

## Call native mobile commands from Rust

Call Kotlin or Swift through `PluginHandle::run_mobile_plugin`, which serializes the request and deserializes the response.

```rust
let photo = self
    .0
    .run_mobile_plugin::<Photo>("openCamera", request)?;
```

Android argument classes, including nested argument classes, require `@InvokeArg` and parsing with `invoke.parseArgs`. Run suspend work in a coroutine scope owned by the plugin. On iOS, make argument types `Decodable` and parse them with `try invoke.parseArgs`.

## Native configuration and lifecycle

Decode plugin configuration during native `load`:

- Android: `getConfig(Config::class.java)`
- iOS: `parseConfig(Config.self)`

An Android plugin may override `onNewIntent` to handle notification taps or deep links that relaunch the application.

## Native events

Consume events emitted through the native `trigger` function with the plugin-aware JavaScript listener, not the ordinary application event listener.

```javascript
import { addPluginListener } from "@tauri-apps/api/core";

const listener = await addPluginListener(
  "camera",
  "newIntent",
  event => console.log(event)
);
```

## Mobile OS permissions

Android declares named OS-permission groups in `@TauriPlugin`. iOS implements checks in `checkPermissions` and requests in `requestPermissions`. Tauri exposes these two namespaced commands to JavaScript and Rust. Returned states include `prompt-with-rationale`.

```javascript
import { invoke } from "@tauri-apps/api/core";

const state = await invoke("plugin:example|checkPermissions");
await invoke("plugin:example|requestPermissions", {
  permissions: ["postNotification"]
});
```

## Call Rust from native code

Tauri has no reverse Kotlin/Swift-to-Rust plugin bridge. When native code must enter Rust while the webview may be suspended, use platform FFI:

- Android: load Cargo's `libapp_lib.so` with `System.loadLibrary("app_lib")`, then export a JNI symbol named `Java_<package>_<class>_<method>`.
- iOS: export a C ABI symbol from Rust, bind it in Swift with `@_silgen_name`, and explicitly free any C allocation returned to Swift.

## Android 16 KB page alignment

NDK 28 or newer should build 16 KB-compatible Android bundles automatically. With an older NDK or an unaligned generated binary, force the maximum page size in `.cargo/config.toml`:

```toml
[target.aarch64-linux-android]
rustflags = ["-C", "link-arg=-Wl,-z,max-page-size=16384"]
```

## Additional official plugin surfaces

The official catalog also includes:

- `barcode-scanner` for camera scanning, including QR and EAN-13.
- `biometric` for biometric authentication.
- `geolocation`, including altitude, heading, and speed when available.
- Mobile `haptics`.
- `nfc` for tag reading and writing.
- `persisted-scope` for saving runtime scope changes.
- `upload` for HTTP file uploads.
- `websocket` for controlling a Rust WebSocket client from JavaScript.
