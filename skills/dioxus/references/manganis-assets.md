# Manganis Asset System

Compile-time asset management via `asset!()` macro with automatic optimization and cache-busting.

## Basic Usage

```rust
let img = asset!("/assets/image.png");
let css = asset!("/assets/style.css", AssetOptions::css().minified());

rsx! {
    img { src: "{img}" }
    link { rel: "stylesheet", href: "{css}" }
}
```

## How It Works

### Compile-Time Expansion

```
asset!("/assets/image.png", AssetOptions::image())
    ↓
1. Path Resolution
   - Resolves relative to CARGO_MANIFEST_DIR
   - Validates path exists

2. File Hashing
   - Creates hash from path + options + span
   - Produces 16-character hex hash

3. Generate Link Section
   - Creates __ASSETS__{hash} symbol
   - Uses CBOR serialization via const_serialize

4. Code Generation
   - Emits BundledAsset const with PLACEHOLDER_HASH
   - Uses volatile reads to prevent optimization
```

### Build-Time Processing (dx CLI)

**Phase 1: Binary Scanning**
- Find `__ASSETS__` symbols via objfile parser
- Platform-specific methods (native object tables, Windows PDB, WASM walrus)

**Phase 2: Asset Deserialization**
- Deserialize BundledAsset via const_serialize CBOR
- Extract: absolute_source_path, bundled_path, options

**Phase 3: Deduplication**
- Deduplicate by (absolute_path, options) pair

**Phase 4: Optimization**

| Type | Processing |
|------|------------|
| Image | Resize, convert format (Avif, WebP), optimize |
| CSS | Minify if enabled |
| JS | Minify if enabled |
| Folder | Recursive copy |
| Unknown | Direct copy with optional hash |

**Phase 5: Binary Patching**
- Compute final content hash
- Create new BundledAsset with bundled_path
- Locate `__ASSETS__{hash}` in binary
- Overwrite bytes at symbol offset

## Asset Options

```rust
AssetOptions
├── ImageAssetOptions
│   ├── format: ImageFormat (Png, Jpg, Webp, Avif)
│   ├── size: ImageSize (Manual | Automatic)
│   └── preload: bool
│
├── CssAssetOptions
│   ├── minify: bool (default: true)
│   ├── preload: bool
│   └── static_head: bool
│
├── JsAssetOptions
│   ├── minify: bool (default: true)
│   ├── preload: bool
│   └── static_head: bool
│
├── CssModuleAssetOptions
│   ├── minify: bool
│   └── preload: bool
│
├── FolderAssetOptions
│   └── (no custom options)
│
└── Unknown (generic binary)
```

## CSS Modules

```rust
css_module!(Styles = "/my.module.css", AssetOptions::css_module());

// Generates:
struct Styles {}
impl Styles {
    pub const header: &str = "abc[hash]";  // Scoped class
    pub const button: &str = "def[hash]";
}

rsx! { div { class: Styles::header } }
```

## Runtime Resolution

**Development Mode** (`!is_bundled_app()`):
- Returns `absolute_source_path`
- Browser/native accesses original files

**Production Mode** (`is_bundled_app()`):
- Returns `base_path() + bundled_path`
- Example: `/app/assets/image-a1b2c3d4.webp`

### Platform-Specific Paths

**Web (WASM)**: HTTP fetch via `resolve_web_asset()`

**Desktop**:
- macOS: `../Resources/assets/`
- Linux: `../lib/{product}/assets/`
- Windows: `assets/` (same directory as exe)

**Android**: NDK AssetManager, accesses APK's assets/

## Hash-Based Cache Busting

**INPUT_HASH** (macro generation):
```
= Hash(span + options + asset_path)
Used for: __ASSETS__{INPUT_HASH} symbol
```

**CONTENT_HASH** (build time):
```
= Hash(source_contents + options + manganis_version)
Used for: Final output filename
Example: image.png → image-a1b2c3d4e5f6.webp
```

## Const Serialization

Uses CBOR format (RFC 8949 subset) for compile-time serialization:

```rust
unsafe trait SerializeConst: Sized {
    const MEMORY_LAYOUT: Layout;
}

enum Layout {
    Enum(EnumLayout),       // repr(C, u8) required
    Struct(StructLayout),   // Field offsets
    Array(ArrayLayout),     // Fixed-size
    Primitive(PrimitiveLayout),
    List(ListLayout),       // Variable length
}
```

**ConstStr**: Fixed 256-byte buffer for asset paths.

## Key Patterns

### Volatile Reads
`std::ptr::read_volatile()` prevents optimizing away link section reads. Critical because link section gets patched post-compilation.

### Symbol-Based Discovery
- No manifest file needed
- Binary symbols serve as asset registry
- Scales with multi-crate applications

### Dual Path Resolution
- Dev: Returns absolute_source_path
- Prod: Returns bundled_path with base_path
- Same Asset instance works across configurations

## Version Compatibility

**Legacy (0.7.0-0.7.1)**: const_serialize_07, Symbol: `__MANGANIS__{hash}`

**Current (0.7.2+)**: const_serialize_08 (CBOR), Symbol: `__ASSETS__{hash}`

CLI tries new format first, falls back to legacy.

## Adding Custom Asset Types

1. Create options struct with `#[derive(SerializeConst)]`
2. Add variant to `AssetOptions` enum
3. Implement builder method
4. Register processing in CLI
