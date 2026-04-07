---
name: vite-knowledge-patch
description: "Vite changes since training cutoff (latest: 8.0) — Rolldown bundler, tsconfigPaths, React plugin v6 with Oxc, Environment API, SSR improvements. Load before working with Vite."
version: "8.0"
license: MIT
metadata:
  author: Nevaberry
---

# Vite Knowledge Patch

Covers Vite 7.0–8.0 (2025-06-24 through 2026-03-12). Claude Opus 4.6 knows Vite through 5.x. It is **unaware** of the features below.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Breaking changes | [references/breaking-changes.md](references/breaking-changes.md) | Node.js 20.19+, browser target, removed APIs, Rolldown default |
| Rolldown bundler | [references/rolldown.md](references/rolldown.md) | Rust-based bundler, v7 opt-in → v8 default |
| Configuration | [references/configuration.md](references/configuration.md) | `resolve.tsconfigPaths`, `devtools`, `server.forwardConsole` |
| React plugin | [references/react-plugin.md](references/react-plugin.md) | `@vitejs/plugin-react` v6, Oxc, React Compiler setup |
| SSR & advanced | [references/ssr-and-advanced.md](references/ssr-and-advanced.md) | `.wasm?init` in SSR, `emitDecoratorMetadata`, Environment API |

---

## Breaking Changes Summary

### Vite 7 (2025-06-24)

| Change | Detail |
|---|---|
| Node.js minimum | 20.19+ or 22.12+ (Node 18 dropped, ESM-only distribution) |
| `build.target` default | `'baseline-widely-available'` (was `'modules'`) — Chrome 107, Edge 107, Firefox 104, Safari 16.0 |
| Sass legacy API | Removed |
| `splitVendorChunkPlugin` | Removed |

### Vite 8 (2026-03-12)

| Change | Detail |
|---|---|
| Default bundler | Rolldown (Rust-based) replaces esbuild + Rollup — `rolldown-vite` package no longer needed |

## Rolldown Bundler

**Vite 7**: Install `rolldown-vite` as drop-in replacement for `vite` to opt in:

```bash
# Vite 7 — opt-in to Rolldown
npm install rolldown-vite # drop-in replacement, no config changes needed
```

**Vite 8**: Rolldown is the default — just upgrade `vite` to 8.x. The `rolldown-vite` package is no longer needed. Existing Rollup/esbuild config options have a compatibility layer but may need adjustment for advanced configurations.

## New Config Options

### `resolve.tsconfigPaths` (8.0-beta)

Built-in tsconfig `paths` resolution — replaces `vite-tsconfig-paths` plugin:

```js
export default defineConfig({
  resolve: {
    tsconfigPaths: true,
  },
})
```

### `devtools` (8.0)

Enable Vite Devtools for debugging and analysis:

```js
export default defineConfig({
  devtools: true,
})
```

### `server.forwardConsole` (8.0)

Forwards browser console output to dev server terminal. Auto-activates when a coding agent is detected:

```js
export default defineConfig({
  server: {
    forwardConsole: true,
  },
})
```

## React Plugin v6 (8.0)

`@vitejs/plugin-react` v6 uses Oxc instead of Babel — Babel is no longer a dependency. For React Compiler, use `@rolldown/plugin-babel`:

```js
import react from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'
import { reactCompilerPreset } from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    react(),
    babel({ presets: [reactCompilerPreset] }),
  ],
})
```

## SSR & Advanced

### `.wasm?init` Works in SSR (8.0)

WebAssembly `.wasm?init` imports now work in SSR environments, not just client-side:

```js
import init from './module.wasm?init'
const instance = await init()
```

### Built-in `emitDecoratorMetadata` (8.0-beta)

Vite 8 automatically handles TypeScript's `emitDecoratorMetadata` when enabled in tsconfig — no extra plugins or config needed.

### Environment API: `buildApp` Hook (7.0, experimental)

New plugin hook to coordinate building of multiple environments. See the Environment API for Frameworks guide.

## Vite 8 Typical Config

A complete example showing common Vite 8 options together:

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  devtools: true,
  resolve: {
    tsconfigPaths: true,
  },
  server: {
    forwardConsole: true,
  },
  plugins: [react()],
})
```

## Reference Files

| File | Contents |
|---|---|
| [breaking-changes.md](references/breaking-changes.md) | Node.js requirements, browser target, removed features, Rolldown as default |
| [rolldown.md](references/rolldown.md) | Rolldown bundler adoption path from v7 to v8 |
| [configuration.md](references/configuration.md) | `resolve.tsconfigPaths`, `devtools`, `server.forwardConsole` |
| [react-plugin.md](references/react-plugin.md) | Plugin-react v6 with Oxc, React Compiler setup |
| [ssr-and-advanced.md](references/ssr-and-advanced.md) | WASM SSR support, decorator metadata, Environment API |
