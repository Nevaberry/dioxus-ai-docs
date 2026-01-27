# WASM Code Splitting

Splits large WASM binaries into lazy-loaded chunks for faster initial load.

## Output Structure

```
dist/
├── main.wasm           # Core application
├── module_1_*.wasm     # Feature chunk 1
├── module_2_*.wasm     # Feature chunk 2
├── chunk_1_*.wasm      # Shared code between modules
└── __wasm_split.js     # JavaScript runtime loader
```

## Usage

### `#[wasm_split]` Attribute

Marks async functions as split boundaries:

```rust
#[wasm_split(admin_panel)]
async fn load_admin_panel() -> AdminPanel {
    // This code will be in module_admin_panel.wasm
    AdminPanel::new()
}

// Use in application
async fn handle_route(route: Route) {
    match route {
        Route::Admin => {
            let panel = load_admin_panel().await;
            panel.render();
        }
        _ => // ...
    }
}
```

**Generated names** (pattern: `__wasm_split_00<module>00_<type>_<hash>_<function>`):
- `__wasm_split_00admin_panel00_import_<hash>_load_admin_panel`
- `__wasm_split_00admin_panel00_export_<hash>_load_admin_panel`

### `#[lazy_loader]` Macro

For libraries creating lazy-loadable wrappers:

```rust
#[lazy_loader(extern "auto")]
fn my_lazy_fn(x: i32) -> i32;
```

Returns `LazyLoader<Args, Ret>`:
- `.load().await` - Async module loading
- `.call(args)` - Sync invocation after loading

**"auto" ABI**: Combines all modules into one automatically.

## Build Requirements

CLI takes two binary inputs:
1. **original.wasm** - Pre-wasm-bindgen (with `--emit-relocs`)
2. **bindgened.wasm** - Post-wasm-bindgen

Compilation flags needed:
- `--emit-relocs` - Relocation information
- Debug symbols - Function name resolution
- LTO - Symbol consistency

## Processing Pipeline

**Phase 1: Discovery**
```
1. Scan imports/exports for __wasm_split_00<module>00_* pattern
2. Parse relocations from original.wasm
3. Build call graph from CODE/DATA relocations
4. Compute reachability for each split point
```

**Phase 2: Chunk Identification**
- Identify functions used by multiple modules
- Extract into shared chunks
- Build chunk dependency graph

**Phase 3: Module Emission** (parallel via rayon)

**Main Module**:
- Remove split point exports
- Replace element segments with dummy functions
- Create indirect function table
- Convert split imports to stub functions
- Run garbage collection

**Split Modules** (per split point):
- Identify unique vs shared symbols
- Convert chunk functions to imports
- Create element segment initializers
- Export main entry function

**Chunk Modules** (shared code):
- Contains commonly-used functions
- No main export function

## Runtime Loading

### LazyLoader

```rust
pub struct LazyLoader<Args, Ret> { ... }

impl LazyLoader {
    pub async fn load(&self) -> bool;
    pub fn call(&self, args: Args) -> Result<Ret, SplitLoaderError>;
}

pub enum SplitLoaderError {
    NotLoaded,
    LoadFailed,
}
```

### LazySplitLoader States

1. **Deferred** - Not initiated, holds load function
2. **Pending** - Load initiated, waiting for callback
3. **Completed** - Loaded (with success boolean)

### JavaScript Runtime

`__wasm_split.js` `makeLoad()` function:
1. Await chunk dependencies
2. Check if already loaded
3. Fetch module binary
4. Call initSync from main.wasm
5. Construct import object (memory, tables, exports)
6. `WebAssembly.instantiateStreaming()`
7. Add exports to fusedImports
8. Invoke callback with table index

## Key Design Points

### Memory Sharing
- Single memory instance shared across all modules
- Indirect function table shared for cross-module calls
- TLS base pointer coordinated

### Split Point Granularity
- One `#[wasm_split]` per feature chunk
- Too fine-grained = many small fetches
- Too coarse = large chunks

### Shared Code Optimization
- Common functions extracted to chunks
- Prevents duplication across modules
- Chunks loaded before dependent modules

## Limitations

1. **Async boundaries**: Split points must be async functions
2. **Call graph static**: Determined at build time
3. **No dynamic imports**: All split points known at compile time
4. **WASM-specific**: Only works with wasm32 target
