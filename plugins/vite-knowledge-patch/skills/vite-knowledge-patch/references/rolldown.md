# Rolldown Bundler

Rolldown is a Rust-based bundler that replaces esbuild + Rollup in Vite. It reduces build times for larger projects.

## Adoption Path

### Vite 7 (2025-06-24) — Opt-in

Install `rolldown-vite` as a drop-in replacement for `vite` to use Rolldown:

```bash
npm install rolldown-vite
```

No config changes needed — `rolldown-vite` is API-compatible with `vite`.

### Vite 8 (2026-03-12) — Default

Rolldown is the default bundler. Just upgrade `vite` to 8.x — the `rolldown-vite` package is no longer needed.

Existing Rollup/esbuild config options have a compatibility layer but may need adjustment for advanced configurations.
