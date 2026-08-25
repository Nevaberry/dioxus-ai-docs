# IPC, State, and Tray Icons

Use this reference for command registration and arguments, raw IPC, channels, managed state, event routing, and tray handlers.

## Contents

- [Command registration and arguments](#command-registration)
- [Raw IPC and serialization](#raw-ipc-requests)
- [Invoke headers](#invoke-headers-250)
- [Events and channels](#events-versus-channels)
- [Managed state](#managed-state)
- [Tray icons](#tray-icons)

## Command registration

`invoke_handler()` is not cumulative. Each call replaces the previously registered handler, so place every application command in one `generate_handler!` invocation.

```rust
tauri::Builder::default()
    .invoke_handler(tauri::generate_handler![open_file, save_file]);
```

Plugin commands belong on the plugin builder instead; see [plugin-mobile-development.md](plugin-mobile-development.md).

## Async commands and borrowed inputs

An asynchronous command with borrowed arguments must either switch to owned inputs such as `String` or return `Result`. Returning `Result` also permits injected borrowed `State<'_, T>`.

```rust
struct Data(String);

#[tauri::command]
async fn read(state: tauri::State<'_, Data>) -> Result<String, ()> {
    Ok(state.0.clone())
}
```

## Rust WASM invoke bindings

Rust cannot express JavaScript's optional second `invoke` argument in one binding. Define separate one- and two-argument bindings, and map the argument-less Rust name to the same JavaScript function with `js_name`.

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(
        js_namespace = ["window", "__TAURI__", "core"],
        js_name = invoke
    )]
    async fn invoke_without_args(command: &str) -> JsValue;

    #[wasm_bindgen(js_namespace = ["window", "__TAURI__", "core"])]
    async fn invoke(command: &str, args: JsValue) -> JsValue;
}
```

## Raw IPC requests

IPC accepts raw bytes and custom serialization in both directions; payloads are not forced through JSON. Pass an `ArrayBuffer` or `Uint8Array` as the JavaScript payload to produce `InvokeBody::Raw`. Inject `tauri::ipc::Request` into the command to inspect both the unprocessed body and request headers.

```rust
#[tauri::command]
fn upload(request: tauri::ipc::Request) -> Result<usize, &'static str> {
    let tauri::ipc::InvokeBody::Raw(bytes) = request.body() else {
        return Err("expected raw body");
    };
    request
        .headers()
        .get("Authorization")
        .ok_or("missing authorization")?;
    Ok(bytes.len())
}
```

```javascript
import { invoke } from "@tauri-apps/api/core";

await invoke("upload", new Uint8Array([1, 2, 3]), {
  headers: { Authorization: "apikey" }
});
```

For a local file that should be loaded directly by a webview without processing, `convertFileSrc` is generally faster than carrying the file through IPC.

## Custom JavaScript serialization (`2.1.0`)

An object passed to `invoke` can implement the function keyed by `SERIALIZE_TO_IPC_FN` from `@tauri-apps/api/core` to produce its IPC representation.

`Size` and `Position` are available from the `dpi` module. `PhysicalSize`, `PhysicalPosition`, `LogicalSize`, and `LogicalPosition` use this serialization hook, allowing matching Rust types to deserialize without manual shape conversion.

```javascript
import { invoke } from "@tauri-apps/api/core";
import { LogicalSize } from "@tauri-apps/api/dpi";

await invoke("set_size", { size: new LogicalSize(800, 600) });
```

## Invoke headers (`2.5.0`)

`invoke` honors `options.headers` when supplied as a JavaScript `Headers` object as well as a plain header mapping. A header containing non-ASCII characters causes `invoke` to throw instead of silently modifying the value.

```javascript
await invoke("command", {}, {
  headers: new Headers({ "X-Trace": "123" })
});
```

## Events versus channels

Events are asynchronous JSON messages without replies or strong typing. A Rust event payload must implement both `Serialize` and `Clone`. Emit globally, target one webview, or route conditionally with `emit_filter`.

```rust
use tauri::{Emitter, EventTarget};

app.emit_filter("open-file", path, |target| match target {
    EventTarget::WebviewWindow { label } => {
        label == "main" || label == "file-viewer"
    }
    _ => false,
})?;
```

As of `2.3.0`, the `Emitter` trait's `emit_str*` family accepts an already JSON-serialized payload and avoids serializing it again.

Use Rust `tauri::ipc::Channel` and the JavaScript `Channel` for ordered, higher-throughput streaming and raw/custom serialization. Cloning `Channel<TSend>` no longer requires `TSend: Clone` as of `2.4.0`; the channel handle clones independently of its payload type.

Capabilities gate command invocations but do not provide fine-grained control over event or channel payload data. Do not use either transport as a substitute for application-level data authorization.

## Managed state

Tauri supplies shared ownership for registered state. Register `Mutex<T>` rather than wrapping it in an `Arc` only for Tauri. Lookup is keyed by the exact registered type.

When a `State` lifetime cannot move into a thread, clone the inexpensive `AppHandle`, move that handle, and reacquire state through `Manager` in the thread.

```rust
use tauri::Manager;

app.manage(std::sync::Mutex::new(Counter::default()));
let handle = app.handle().clone();
std::thread::spawn(move || {
    let state = handle.state::<std::sync::Mutex<Counter>>();
    state.lock().unwrap().value += 1;
});
```

Do not remove managed state through deprecated `Manager::unmanage()`; that operation can cause use-after-free unsoundness.

## Tray icons

### Application-wide Rust handler (`2.2.0`)

Register one application-level tray handler with `tauri::Builder::on_tray_icon_event()`.

`TrayIconBuilder::show_menu_on_left_click()` replaces deprecated `menu_on_left_click()`. Windows supports both this builder setting and the runtime `TrayIcon::set_show_menu_on_left_click()` setter.

### JavaScript construction

JavaScript can construct the complete tray icon and menu. Each menu item receives its own `action` callback. The tray's `action` receives `Click`, `DoubleClick`, `Enter`, `Move`, and `Leave`; click events include button plus press/release state, and pointer events include the tray rectangle.

```javascript
import { invoke } from "@tauri-apps/api/core";
import { Menu } from "@tauri-apps/api/menu";
import { TrayIcon } from "@tauri-apps/api/tray";

const menu = await Menu.new({
  items: [{ id: "quit", text: "Quit", action: () => invoke("quit") }]
});

const tray = await TrayIcon.new({
  menu,
  menuOnLeftClick: true,
  action: event => console.log(event.type)
});
```
