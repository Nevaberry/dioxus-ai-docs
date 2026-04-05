# TypeScript 7 (tsgo) Transition Guide

## Trying tsgo Now

```bash
npm install -D @typescript/native-preview
npx tsgo --project ./tsconfig.json
```

The `tsgo` executable mirrors `tsc` usage. Eventually `tsgo` will be renamed to `tsc` in the `typescript` package.

## Timeline

- **TypeScript 6.0**: Last JavaScript-based release. Transition/bridge release preparing codebases for 7.0. API-compatible with 5.9. There will be no 6.1 — 6.0 only receives security and high-severity patches.
- **TypeScript 7.0 (`tsgo`)**: Native Go port. All future development happens here.

## New Defaults in TS 7.0 (Breaking)

| Setting | Old Default | New Default |
|---------|-------------|-------------|
| `--strict` | off | **enabled by default** |
| `--target` | `es3` | latest stable ES (e.g. `es2025`) |
| `--target es5` | supported | **removed** — `es2015` is the lowest supported target |
| `--baseUrl` | supported | **removed** — use `paths` with explicit `rootDir` instead |
| `--moduleResolution node10` | supported | **removed** — use `bundler` or `nodenext` |
| `rootDir` | inferred from source files | defaults to `.` — using `outDir` requires explicit `rootDir` or source files next to `tsconfig.json` |

## Required Migration: Module Resolution

tsgo **drops** `--moduleResolution node` (aka `node10`) and `--module commonjs`. If your tsconfig uses these, you'll get errors like:

```
Cannot find module 'blah' or its corresponding type declarations.
Module '"module"' has no exported member 'Thing'.
```

**Fix** — switch to one of:

```jsonc
// For bundler-based projects (Vite, webpack, esbuild, etc.)
{
  "compilerOptions": {
    "module": "preserve",
    "moduleResolution": "bundler"
  }
}
```

```jsonc
// For Node.js projects
{
  "compilerOptions": {
    "module": "nodenext"
  }
}
```

## Migration Tool: `ts5to6`

```bash
npx @andrewbranch/ts5to6 --fixBaseUrl your-tsconfig.json
npx @andrewbranch/ts5to6 --fixRootDir your-tsconfig.json
```

Automatically updates `baseUrl` and `rootDir` settings across project references. Run this before upgrading to TS 7.0 to fix the most common breaking config changes.

## tsgo Compiler Status (as of December 2025)

### What Works
- `--build` mode with project references
- `--incremental` compilation
- Type-checking: 99.6% of error-producing test cases pass

### Current Limitations
- **Emit targets**: Only supports down to `es2021`. No `es2015`-`es2020` targets yet, no decorator downlevel emit.
- **Watch mode**: May be less efficient than tsc. Workaround: use `nodemon` + `tsgo --incremental`.
- **No stable API**: Tools using the TypeScript Strada API (compiler API) won't work with tsgo yet.

## Architecture: Standard LSP

tsgo uses the standard Language Server Protocol (LSP) instead of the custom TSServer protocol:
- Language service plugins that depend on TSServer **will not work**
- Editor integrations using standard LSP work out of the box
- Custom tooling built on TSServer's protocol needs migration

## JSDoc Behavior Changes

In JavaScript files, tsgo drops several legacy behaviors:

| JSDoc Feature | Change |
|---------------|--------|
| `@enum` tag | Not recognized |
| `@constructor` tag | Not recognized |
| `Object` type | No longer treated as `any` in JS files |
| `String` type | No longer coerced to `string` |
| `Foo` type reference | No longer interpreted as `typeof Foo` where the latter would be valid in TS |
| `any`/`unknown`/`undefined`-typed parameters | No longer treated as optional |
