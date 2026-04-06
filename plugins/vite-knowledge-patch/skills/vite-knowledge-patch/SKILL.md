---
name: vite-knowledge-patch
description: "Vite changes since training cutoff (latest: 8.0) — Environment API, Rolldown bundler, resolve.conditions, tsconfigPaths, React plugin v6 with Oxc, browser target changes. Load before working with Vite 6+."
license: MIT
metadata:
  author: Nevaberry
  version: "8.0"
---

# Vite 6+ Knowledge Patch

Claude's baseline knowledge covers Vite through 5.x. This skill provides features from 6.0 (November 2024) onwards through 8.0 (March 2026).

## Quick Reference

### Version Timeline

| Version | Date | Key Change |
|---------|------|------------|
| 6.0 | 2024-11-26 | Environment API (experimental), `resolve.conditions` defaults, Sass modern API default |
| 7.0 | 2025-06-24 | Node 20.19+, `baseline-widely-available` target, Rolldown opt-in via `rolldown-vite` |
| 8.0 | 2026-03-12 | Rolldown default bundler, `tsconfigPaths`, `devtools`, React plugin v6 (Oxc) |

### Breaking Changes at a Glance

| Change | Version | Detail |
|--------|---------|--------|
| `resolve.conditions` default | 6.0 | Now `['module', 'browser', 'development\|production']` instead of `[]` |
| Sass API default | 6.0 | Modern API by default (set `api: 'legacy'` to revert) |
| `json.stringify` default | 6.0 | `'auto'` (stringifies large JSON files) |
| Library CSS filename | 6.0 | Uses `package.json` `"name"` instead of `style.css` |
| Node.js minimum | 7.0 | 20.19+ or 22.12+ (Node 18 dropped, ESM-only distribution) |
| `build.target` default | 7.0 | `'baseline-widely-available'` (Chrome 107, Firefox 104, Safari 16) |
| Sass legacy API | 7.0 | Removed entirely |
| `splitVendorChunkPlugin` | 7.0 | Removed entirely |
| Default bundler | 8.0 | Rolldown (Rust) replaces esbuild + Rollup |

See `references/breaking-changes.md` for full migration details.

### New Config Options (8.0)

| Option | Purpose |
|--------|---------|
| `resolve.tsconfigPaths: true` | Built-in tsconfig `paths` resolution (replaces `vite-tsconfig-paths` plugin) |
| `devtools: true` | Enable Vite Devtools for debugging and analysis |
| `server.forwardConsole: true` | Forward browser console to dev server terminal (auto-activates for coding agents) |

See `references/configuration.md` for details.

### Rolldown Bundler

| Version | How to use |
|---------|-----------|
| Vite 7 | `npm install rolldown-vite` (drop-in replacement, no config changes) |
| Vite 8 | Just upgrade `vite` to 8.x (Rolldown is default, `rolldown-vite` no longer needed) |

See `references/rolldown.md` for migration path and compatibility layer details.

## Vite 6: resolve.conditions

The biggest Vite 6 migration issue. Previously `resolve.conditions` defaulted to `[]` with conditions added internally. Now defaults are explicit:

```javascript
import { defaultClientConditions, defaultServerConditions } from 'vite';

export default defineConfig({
  resolve: {
    // If you had custom conditions, merge with new defaults:
    conditions: ['custom', ...defaultClientConditions],
    // defaultClientConditions = ['module', 'browser', 'development|production']
    // defaultServerConditions = ['module', 'node', 'development|production']
  },
});
```

## Vite 8 Typical Config

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  devtools: true,
  resolve: {
    tsconfigPaths: true,
  },
  server: {
    forwardConsole: true,
  },
  plugins: [react()],
});
```

## React Plugin v6 (8.0)

`@vitejs/plugin-react` v6 uses Oxc instead of Babel -- Babel is no longer a dependency. For React Compiler, use `@rolldown/plugin-babel`:

```javascript
import react from '@vitejs/plugin-react';
import babel from '@rolldown/plugin-babel';
import { reactCompilerPreset } from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react(), babel({ presets: [reactCompilerPreset] })],
});
```

See `references/react-plugin.md` for details.

## SSR & Advanced

- **`.wasm?init` in SSR** (8.0): WebAssembly imports work server-side
- **`emitDecoratorMetadata`** (8.0): Built-in TypeScript decorator metadata support, no plugins needed
- **Environment API `buildApp` hook** (7.0, experimental): Plugin hook to coordinate multi-environment builds

See `references/ssr-and-advanced.md` for details.

## Environment API (6.0+, experimental)

Major internal refactoring for framework authors. Enables per-environment module graphs, replacing the Vite 5.1 Runtime API with Module Runner API. End users building SPAs are unaffected. See `references/environment-api.md`.

## Reference Files

| File | Contents |
|------|----------|
| `breaking-changes.md` | All breaking changes across v6, v7, v8 with migration steps |
| `rolldown.md` | Rolldown adoption path, compatibility layer, migration strategies |
| `configuration.md` | New config options: `tsconfigPaths`, `devtools`, `forwardConsole` |
| `react-plugin.md` | Plugin-react v6 with Oxc, React Compiler setup |
| `ssr-and-advanced.md` | WASM SSR, decorator metadata, Environment API hooks |
| `environment-api.md` | Environment API for framework/plugin authors |

## Critical Knowledge

### Library Mode CSS Filename (6.0+)

CSS output now uses `package.json` `"name"` instead of `style.css`. Set `build.lib.cssFileName: 'style'` to keep the old name:

```javascript
export default defineConfig({
  build: {
    lib: {
      entry: 'src/index.ts',
      cssFileName: 'style', // keeps old style.css name
    },
  },
});
```

### Vite 8 Gradual Migration

For complex projects, migrate in two steps:
1. On Vite 7, switch from `vite` to `rolldown-vite` (isolates Rolldown-specific issues)
2. Then upgrade to Vite 8

### Install Size Change (8.0)

Vite 8 is ~15 MB larger: ~10 MB from lightningcss (now a normal dependency for CSS minification) and ~5 MB from the Rolldown binary.
