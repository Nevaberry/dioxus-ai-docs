# Modules, TypeScript, and WebAssembly

Module loading and resolution, TypeScript execution, compile caches, VM modules, and WebAssembly integration.

## Contents

- [TypeScript execution](#typescript-execution)
- [Loading, hooks, and resolution](#loading-hooks-and-resolution)
- [ES modules and CommonJS](#es-modules-and-commonjs)
- [WebAssembly modules](#webassembly-modules)
- [VM modules](#vm-modules)
- [Module APIs and semantics](#module-apis-and-semantics)

## TypeScript execution

### `import.meta.main` in TypeScript (since 24.3.0)

Built-in TypeScript loading now evaluates `import.meta.main` correctly, so entry-point guards work in TypeScript modules as they do in JavaScript modules.

### Programmatic TypeScript stripping (since 23.2.0)

`node:module` now exports `stripTypeScriptTypes()`: `stripTypeScriptTypes('const answer: number = 42;')` removes erasable type syntax, while `{ mode: 'transform' }` also lowers TypeScript constructs such as enums.

### Removed TypeScript transform flag (since 26.0.0)

The `--experimental-transform-types` command-line option has been removed. Startup scripts and tooling must no longer pass that flag.

### Stable built-in TypeScript type stripping (since 25.2.0)

Built-in TypeScript type stripping is now stable; this changes its support status without expanding the already-supported syntax.

### Type stripping without an experimental warning (since 24.3.0)

Built-in TypeScript type stripping no longer emits an `ExperimentalWarning`. This removes the warning only; it does not extend stripping to TypeScript syntax that requires transformation.

### TypeScript execution enabled by default (since 23.6.0)

The experimental type stripper is now enabled without `--experimental-strip-types`, so files using supported TypeScript syntax can run directly. TypeScript input is also accepted through eval and standard input, including eval-based worker input; the feature remains experimental and does not support all TypeScript syntax.

```console
node file.ts
```

### Unsupported TypeScript syntax errors (since 23.7.0)

Built-in type stripping now reports syntax that requires transformation with the `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX` error code, allowing callers to distinguish it from ordinary JavaScript syntax errors.


## Loading, hooks, and resolution

### `#/` package imports (since 25.4.0)

The package `"imports"` field can now define and resolve aliases whose specifiers start with `#/`.

```json
{
  "imports": {
    "#/*": "./src/*"
  }
}
```

```js
import config from '#/config.js';
```

### CommonJS cycles through the ESM loader (since 24.3.0)

The CommonJS path inside the ESM loader now permits cyclic `require()` dependencies that it previously rejected.

### Dedicated-thread module-hook deprecation (since 25.9.0)

The dedicated-thread `module.register()` customization API is deprecated as DEP0205. Prefer `module.registerHooks()` where synchronous in-thread hooks meet the loader's needs.

### Deferred static imports (since 26.4.0)

The module loader now enables deferred imports for static modules, allowing module evaluation to wait until the imported namespace is used.

```js
import defer * as feature from './feature.js';

feature.run();
```

### Deprecated private stream and TLS modules (since 25.0.0)

Direct imports of the private `_stream_*`, `_tls_common`, and `_tls_wrap` entry points are deprecated. Import supported APIs from `node:stream` and `node:tls` instead.

### Entry-point detection with `import.meta.main` (since 24.2.0)

ES modules can test the boolean `import.meta.main` to determine whether they were the process entry point, allowing an importable module to guard its command-line side effects.

```js
export function main() {
  console.log('started directly');
}

if (import.meta.main) main();
```

### ESM addon imports by default (since 26.5.0)

The module loader now enables import support for native addons by default, so the experimental ESM addon support no longer has to be separately enabled.

### ESM entries in `require.cache` (since 24.9.0)

When `require()` loads ES modules, only the directly required module is placed in `require.cache`; transitive ESM dependencies are no longer inserted. Cache inspection or invalidation code must not treat it as a complete ESM graph.

### Experimental text imports (since 26.5.0)

The new `--experimental-import-text` flag enables experimental text imports; run an entry point with `node --experimental-import-text app.mjs` to opt in.

### Extensionless files in ESM packages (since 26.0.0)

Extensionless files no longer receive a CommonJS exception inside packages whose `package.json` declares `"type": "module"`; they follow the package's ESM interpretation.

### Loader package maps (since 26.4.0)

The module loader now implements package maps, enabling package-map-based module resolution.

### Locating package metadata (since 23.2.0)

The new `findPackageJSON()` export from `node:module` finds the package metadata associated with a module specifier. For example, `findPackageJSON('some-package', import.meta.url)` returns that package's `package.json` path, or `undefined` when none is found.

### Module compile-cache and customization-hook status (since 25.4.0)

The module compile cache is now stable. The synchronous `module.registerHooks()` API advances to release-candidate status, while the dedicated-thread `module.register()` API is classified as active development.

### Opt-in `require(esm)` warnings (since 23.5.0)

Loading eligible ES modules with `require()` no longer emits a warning by default. Run with `--trace-require-module` when those loads should be reported.

### Optional context in synchronous module hooks (since 23.9.0)

Synchronous `module.registerHooks()` callbacks may call `nextResolve(specifier)` or `nextLoad(url)` without forwarding the `context` argument.

### Portable module compile caches (since 25.0.0)

`module.enableCompileCache()` can create a portable cache whose entries remain reusable when the cache and application move together; pass an options object with `portable: true` instead of binding entries to their original absolute location.

```js
import { enableCompileCache } from 'node:module';

enableCompileCache({ directory: '.cache/node', portable: true });
```

### Runtime-deprecated dedicated-thread hooks (since 26.0.0)

Calling the dedicated-thread `module.register()` customization API now emits a runtime deprecation warning. Use the in-thread `module.registerHooks()` API where synchronous hooks are suitable.

The stream behavior tracked by DEP0201 and the crypto APIs tracked by DEP0203 and DEP0204 have likewise advanced to runtime deprecations, so affected calls now warn during execution.

### Stable `require(esm)` and explicit CLI control (since 25.4.0)

Loading eligible ES modules through `require()` is now stable. The new `--require-module` and `--no-require-module` flags explicitly enable or disable this capability.

### Synchronous module customization hooks (since 23.5.0)

`module.registerHooks()` registers `resolve` and `load` callbacks directly in the current thread. Unlike `module.register()`, these synchronous hooks cover modules loaded through `require()`, `import`, and functions returned by `createRequire()`.

```js
import { registerHooks } from 'node:module';

registerHooks({
  resolve(specifier, context, nextResolve) {
    return nextResolve(specifier.replace('alias:', './'), context);
  },
});
```

### Top-level-await detection (since 24.9.0)

`vm.SourceTextModule` now exposes `hasTopLevelAwait()`, allowing custom module loaders to distinguish modules that directly use top-level `await`.

### URL entry points (since 23.0.0)

The module loader can now start an application from a URL entry point, including a `file:` URL.

```console
node file:///absolute/path/app.mjs
```

### WebAssembly JavaScript-string ESM imports (since 25.9.0)

WebAssembly ES modules now support JavaScript string-constant imports.


## ES modules and CommonJS

### Experimental ESM addon support (since 23.6.0)

The ESM loader now has experimental support for addon modules, so native addons are no longer limited entirely to CommonJS-oriented loading paths.

### Stable `import.meta` paths (since 24.0.0)

The Node-specific `import.meta.dirname` and `import.meta.filename` properties are now stable, providing directory and absolute-file paths without converting `import.meta.url` manually.

### Stable JSON modules and import attributes (since 23.1.0)

JSON modules and import attributes are now stable and implement the finalized proposal semantics; JSON can be loaded with `import config from './config.json' with { type: 'json' }`.

### WebAssembly ESM without a startup flag (since 24.5.0)

`--experimental-wasm-modules` is no longer required to use WebAssembly ESM integration. The Phase 3 implementation remains subject to change; this release also integrates the JS-string Wasm built-ins.

### WebAssembly Memory64 and ESM loading (since 24.0.0)

V8 now supports WebAssembly Memory64. Node's experimental WebAssembly ESM integration also accepts a top-level `.wasm` module without a package `type` declaration and supports source-phase imports, which return a compiled module for explicit instantiation.

```js
import source compiled from './math.wasm';

const instance = await WebAssembly.instantiate(compiled, {});
```

```console
node --experimental-wasm-modules app.mjs
```


## WebAssembly modules

### WebAssembly JavaScript Promise Integration (since 25.0.0)

V8 now enables JSPI, allowing WebAssembly to suspend across asynchronous JavaScript imports. Wrap an async import with `WebAssembly.Suspending` and expose an async callable export with `WebAssembly.promising`.

```js
imports.env.read = new WebAssembly.Suspending(asyncRead);
const run = WebAssembly.promising(instance.exports.run);
const result = await run();
```


## VM modules

### Import phases in VM module requests (since 24.4.0)

Entries in `SourceTextModule.moduleRequests` now expose their import phase, allowing custom VM module tooling to distinguish source-phase requests from ordinary evaluation-phase imports.

### Synchronous `SourceTextModule` linkage (since 24.8.0)

Linkage for the experimental `vm.SourceTextModule` API is now synchronous. Custom VM module tooling should not rely on the earlier asynchronous linkage phase.


## Module APIs and semantics

### Deprecated private HTTP modules (since 24.6.0)

The private `_http_*` module entry points are now documentation-deprecated; use the public `node:http` and `node:https` APIs instead.

### Prefix-only built-ins in module discovery (since 23.5.0)

`module.builtinModules` now includes built-in modules that can only be loaded with the `node:` prefix. Code that enumerates or feature-detects built-ins can therefore discover those modules from this list.
