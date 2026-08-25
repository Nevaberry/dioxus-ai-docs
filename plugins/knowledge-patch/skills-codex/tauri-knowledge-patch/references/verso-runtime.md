# Verso Runtime

Use this reference only when explicitly replacing the usual `tauri-runtime-wry` backend with the experimental Servo-based Verso runtime.

## Bootstrap the runtime

Build the `versoview` executable separately and set its path before creating any webview. Prefer also setting Verso's resource directory so resources such as the user-agent stylesheet can be loaded.

Pass `INVOKE_SYSTEM_SCRIPTS` to `invoke_system`; some Tauri commands depend on these invocation scripts.

```rust
use tauri_runtime_verso::{
    set_verso_path,
    set_verso_resource_directory,
    VersoRuntime,
    INVOKE_SYSTEM_SCRIPTS,
};

fn main() {
    set_verso_path("../verso/target/debug/versoview");
    set_verso_resource_directory("../verso/resources");

    tauri::Builder::<VersoRuntime>::new()
        .invoke_system(INVOKE_SYSTEM_SCRIPTS.to_owned())
        .run(tauri::generate_context!())
        .unwrap();
}
```

## Compatibility boundary

`tauri-runtime-verso` implements only part of the production runtime surface.

Working surfaces include:

- Tauri CLI workflows.
- Official log and opener plugins.
- Basic window sizing, positioning, maximizing, minimizing, and closing.
- Vite CSS hot reload.
- `data-tauri-drag-region`.

Unsupported surfaces include window decorations, window titles, and transparency. Verify every additional runtime or plugin API directly before depending on it.
