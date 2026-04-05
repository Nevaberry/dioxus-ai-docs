# Breaking Changes

## Vite 7 (2025-06-24)

### Node.js 20.19+ or 22.12+ Required

Vite 7 is distributed as ESM only. Node.js 18 is dropped. The minimum versions ensure `require(esm)` works without a flag, so CJS consumers can still `require()` Vite's JS API.

### Default Browser Target Changed

`build.target` default changed from `'modules'` to `'baseline-widely-available'`:

| Browser | Minimum version |
|---|---|
| Chrome | 107 |
| Edge | 107 |
| Firefox | 104 |
| Safari | 16.0 |

This updates each major to match Baseline Widely Available browser versions.

### Removed Deprecated Features

- **Sass legacy API support** — removed entirely
- **`splitVendorChunkPlugin`** — removed entirely

## Vite 8 (2026-03-12)

### Rolldown Is Now the Default Bundler

Vite 8 replaces esbuild + Rollup with Rolldown (Rust-based). The `rolldown-vite` package from Vite 7 is no longer needed — just upgrade `vite` to 8.x. Existing Rollup/esbuild config options have a compatibility layer but may need adjustment.
