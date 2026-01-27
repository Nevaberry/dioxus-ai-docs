# Subsecond Hot-Patching

Hot-reloads Rust code without restart via **jump table indirection**. This is different from RSX hot-reload (template literals only).

## How It Works

### Jump Table Architecture

1. Hot-reloadable functions called through `subsecond::call()` or `HotFn::current()`
2. Runtime looks up function pointer in global `APP_JUMP_TABLE`
3. Jump table points to latest compiled version
4. On patch: only jump table is updated, original binary untouched

**Key insight**: Decouples running binary from patched code. Safe memory model.

### Patch Application Flow

```
1. ThinLink compiles only modified functions → patch dylib
2. Patch sent via devtools WebSocket
3. subsecond::apply_patch() loads via libloading::Library
4. Base address calculated using main as anchor
5. Jump table updated: old_addr → new_addr
```

### ASLR Handling

Operating systems randomize addresses (ASLR), so compiled addresses don't match runtime.

**Solution**:
1. Running app captures real address of `main` via `dlsym()`/`GetProcAddress()`
2. ASLR reference sent to devserver
3. Devserver computes offset: `old_offset = aslr_reference - table.aslr_reference`
4. All jump table addresses adjusted by offset
5. Final mapping: `(old_address + old_offset) → (new_address + new_offset)`

## Thread-Local Storage (TLS) Gotchas

- **Globals and statics**: Generally supported
- **Thread-locals in tip crate**: Reset to initial value on patches
- **Thread-locals in dependencies**: Work correctly (not re-patched)

**Why TLS resets**: New thread-local variables exist in patch library's TLS segment, separate from main executable's TLS.

## Limitations

1. **Struct changes**: Not supported - size/alignment changes cause crashes
2. **Pointer versioning**: Not implemented - all function pointers considered "new"
3. **Workspace support**: Only tip crate patches, library crates ignored
4. **Static initializers**: Changes not observed
5. **Global destructors**: Newly added globals have destructors that never run

## Platform Support

| Platform | Status |
|----------|--------|
| Desktop (Linux, macOS, Windows) | Supported (x86_64, aarch64) |
| Android | Supported (arm64-v8a, armeabi-v7a) |
| iOS Simulator | Supported |
| iOS Device | Not supported (code-signing) |
| WASM | Limited module reloading |

## Usage

### Standard Dioxus App

```rust
fn main() {
    dioxus::launch(app);
    // Devtools automatically connects during init
}
```

### Non-Dioxus Apps

```rust
fn main() {
    dioxus_devtools::connect_subsecond();

    loop {
        dioxus_devtools::subsecond::call(|| {
            handle_request()
        });
    }
}
```

### Async Integration

```rust
#[tokio::main]
async fn main() {
    dioxus_devtools::serve_subsecond_with_args(
        state,
        |state| async { app_main(state).await }
    ).await;
}
```

**Process**:
1. Catches patch message
2. Applies jump table
3. Drops current future
4. Creates new future with hot function
5. Continues execution

## RSX Hot-Reload (Orthogonal)

RSX hot-reload handles template literals, NOT Rust code:

**Hot-reloadable**:
- Formatted segments: `"{variable}"`
- Literal component properties: `Component { value: 123 }`
- Dynamic text nodes

**Not hot-reloadable** (needs Subsecond):
- Rust code changes
- Component structure changes
- Control flow changes

### Template Diffing

1. Parse old and new files
2. Replace all rsx! bodies with empty `rsx! {}`
3. Compare modified files
4. If identical → proceed with template diff
5. If different → requires full rebuild

## Build Modes

**Fat Build** (initial):
- Full build with all symbols
- Creates `HotpatchModuleCache`

**Thin Build** (patches):
- Compiles only modified functions
- Uses cached dependency symbols
- Produces minimal patch dylib

## JumpTable Structure

```rust
pub struct JumpTable {
    pub lib: PathBuf,           // Path to patch dylib
    pub map: HashMap<u64, u64>, // old_addr → new_addr
    pub aslr_reference: u64,
    pub new_base_address: u64,
    pub ifunc_count: u32,
}
```

## Devtools Protocol

WebSocket at `ws://localhost:3000/_dioxus` with query params: `build_id`, `pid`, `aslr_reference`.

```rust
pub enum DevserverMsg {
    HotReload(HotReloadMsg),  // Templates + optional jump table
    HotPatchStart,            // Binary patching starting
    FullReloadStart,          // Rebuilding entire app
    FullReloadFailed,         // Build failed
    FullReloadCommand,        // Full page reload needed
    Shutdown,
}
```
