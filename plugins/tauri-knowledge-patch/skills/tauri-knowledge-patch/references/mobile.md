# Mobile Support (iOS/Android)

To target iOS/Android, restructure `src-tauri/src/`:

## Entry Point

```rust
// src-tauri/src/lib.rs (shared by desktop and mobile)
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![/* commands */])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

```rust
// src-tauri/src/main.rs (desktop only)
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
fn main() {
    app_lib::run();
}
```

## Cargo.toml Configuration

Add to `Cargo.toml` to support mobile targets:

```toml
[lib]
name = "app_lib"
crate-type = ["staticlib", "cdylib", "rlib"]
```
