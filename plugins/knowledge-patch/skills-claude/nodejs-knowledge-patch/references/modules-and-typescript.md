# Modules, TypeScript, and WebAssembly

Use this reference for modules, typescript, and webassembly work.

## `#/` package imports (`25.4.0`)

Package `imports` maps may now use keys beginning with `#/`, allowing slash-shaped internal aliases.

```json
{
  "imports": {
    "#/parser": "./src/parser.js"
  }
}
```

```js
import { parse } from '#/parser';
```

## `.cts` imports use CommonJS loading (`24.10.0`)

Importing a `.cts` file now uses the synchronous CommonJS loader, preserving CommonJS semantics even when the file is reached through `import`.

## Consolidated module-mock exports (`25.9.0`)

`MockModuleOptions.defaultExport` and `namedExports` are replaced by one `exports` object. Its `default` own property supplies the default export, while its other own enumerable properties become named exports; existing tests can migrate with `npx codemod @nodejs/mock-module-exports`.

```js
t.mock.module('./dependency.mjs', {
  exports: { default: defaultMock, parse: parseMock },
});
```

## Dedicated unsupported TypeScript error (`23.7.0`)

Built-in TypeScript stripping now reports syntax it cannot handle with `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`, so callers can distinguish unsupported TypeScript constructs from other parse failures.

## Deferred static imports (`26.4.0`)

The loader now implements package maps and enables deferred static-module imports. `import defer` postpones evaluation until the imported namespace is used.

```js
import defer * as feature from './feature.js';

feature.run();
```

## Direct top-level-await detection (`24.9.0`)

`vm.SourceTextModule.prototype.hasTopLevelAwait()` reports whether a module itself contains top-level `await`, allowing custom module loaders to distinguish it without evaluating the module.

```js
import { SourceTextModule } from 'node:vm';

const module = new SourceTextModule('await Promise.resolve()');
console.log(module.hasTopLevelAwait()); // true
```

## Direct-run detection for ES modules (`24.2.0`)

ES modules now expose the boolean `import.meta.main`, which is true when the current module is the process entry point. This lets a module run CLI-only work without also running it when imported.

```js
if (import.meta.main) {
  main();
}
```

## Disposable synchronous module hooks (`26.7.0`)

The `ModuleHooks` object returned by `registerHooks()` implements `Symbol.dispose`, so a hook registration can be scoped with `using` and removed automatically.

```js
import { registerHooks } from 'node:module';

{
  using hooks = registerHooks({
    resolve(specifier, context, nextResolve) {
      return nextResolve(specifier, context);
    },
  });
}
```

## Dynamic source-phase loader hooks (`24.2.0`)

The ESM loader now supports hooks for dynamic source-phase imports, extending custom-loader integration beyond static source-phase imports.

## ESM entries in `require.cache` (`24.9.0`)

When `require()` loads ES modules, only the directly required module is placed in `require.cache`; transitive ESM dependencies are no longer inserted. Cache inspection and invalidation code must not treat it as a complete ESM graph.

## Experimental text imports (`26.5.0`)

The `--experimental-import-text` flag opts the module loader into experimental text imports.

```sh
node --experimental-import-text app.mjs
```

## Explicit resource management, 16-bit floats, and WebAssembly (`24.0.0`)

V8 13.6 enables JavaScript explicit resource management and `Float16Array`; WebAssembly Memory64 is also available. ESM can load top-level WebAssembly without a package type and supports source-phase imports.

```js
import source wasmModule from './module.wasm';

using resource = {
  [Symbol.dispose]() {
    console.log('closed');
  },
};
```

## Finding a package manifest (`23.2.0`)

`node:module` adds `findPackageJSON()` for locating the relevant `package.json` for a module specifier relative to a base URL.

```js
import { findPackageJSON } from 'node:module';

const manifestPath = findPackageJSON('some-package', import.meta.url);
```

## Import phases in VM module requests (`24.4.0`)

Entries exposed by `SourceTextModule.moduleRequests` now include their import phase, allowing VM module tooling to distinguish source-phase requests from evaluation-phase imports.

## Imported CommonJS modules invoke resolve hooks once (`24.14.0`)

Module resolve hooks are no longer invoked twice for an imported CommonJS module, so side-effectful hooks now see a single resolution pass.

## Internal HTTP modules are deprecated (`24.6.0`)

Direct use of the private `_http_*` modules is now documentation-deprecated. Applications should import the supported public APIs from `node:http` and `node:https` instead.

## JSON modules and import attributes are stable (`23.1.0`)

JSON modules and import attributes are now stable, with Node's implementation matching the stage 4 proposal semantics.

## Opt-in `require(ESM)` tracing (`23.5.0`)

Loading an ES module through `require()` no longer emits its warning by default; the warning is now emitted only when `--trace-require-module` is requested.

## Portable compile caches (`25.0.0`)

The module compile-cache API gains a portable option so a cache can be reused when it moves with an application rather than remaining tied to its original absolute location.

```js
import { enableCompileCache } from 'node:module';

enableCompileCache({ portable: true });
```

## Prefix-only built-in modules (`23.5.0`)

`module.builtinModules` now includes modules that can only be loaded with the `node:` prefix. Code that consumes this list must preserve that prefix instead of assuming every entry also has an unprefixed form.

## Private modules and embedding APIs (`25.0.0`)

Imports of `_stream_*`, `_tls_common`, and `_tls_wrap` are deprecated, while `Module._debug` is removed; applications should use public module entry points. Native embedders must also migrate away from the removed callback-without-async-context APIs and the removed `node::EmitBeforeExit`, `node::EmitExit`, `node::CreatePlatform`, `node::FreePlatform`, and `node::InitializeNodeWithArgs` functions.

## Programmatic TypeScript stripping (`23.2.0`)

Built-in TypeScript support is now classified as active development, and `node:module` adds `stripTypeScriptTypes()` for stripping TypeScript types from source text.

```js
import { stripTypeScriptTypes } from 'node:module';

const js = stripTypeScriptTypes('const answer: number = 42;');
```

## Stable synchronous `require(ESM)` controls (`25.4.0`)

Synchronous loading of eligible ES modules through `require()` is now stable. `--require-module` and `--no-require-module` let launchers explicitly enable or disable the behavior.

```sh
node --no-require-module app.cjs
```

## Synchronous `SourceTextModule` linkage (`24.8.0`)

Linkage for the experimental `vm.SourceTextModule` API is now synchronous. Custom VM-module tooling must not rely on the earlier asynchronous linkage phase.

## Synchronous hook short circuits from imported CommonJS (`24.18.0`)

Synchronous module-hook short circuits are now honored by `require()` calls made from an imported CommonJS module. A `registerHooks()` hook can return its short-circuit result reliably on that loading path.

## Type stripping is stable (`25.2.0`)

Built-in TypeScript type stripping is now stable, so its existing erasable-syntax execution path no longer needs to be treated as an experimental surface.

## Type stripping no longer emits an experimental warning (`24.3.0`)

Built-in TypeScript type stripping no longer produces an experimental warning at startup. Launchers and tests no longer need to filter that warning from stderr.

## TypeScript and extensionless-module migrations (`26.0.0`)

The `--experimental-transform-types` option is removed, so launchers must stop passing it. Extensionless files inside packages with `"type": "module"` no longer receive a CommonJS exception and follow ESM interpretation.

## TypeScript stripping is enabled by default (`23.6.0`)

`--experimental-strip-types` is now enabled by default, so Node can execute supported `.ts` files without additional configuration. TypeScript input is also accepted through standard-input/eval execution and evaluated worker source; the feature remains experimental and supports only the documented subset of TypeScript syntax.

```sh
node file.ts
```

## WebAssembly ESM integration no longer needs a flag (`24.5.0`)

Source- and instance-phase WebAssembly module integration can now be used without `--experimental-wasm-modules`. The implementation and its underlying proposal remain subject to change.

## WebAssembly globals in module namespaces (`24.2.0`)

WebAssembly globals exposed through an ES module namespace are now unwrapped instead of being returned as `WebAssembly.Global` wrapper objects.

## WebAssembly JavaScript Promise Integration (`25.0.0`)

WebAssembly JSPI is enabled, allowing WebAssembly execution to suspend across promise-returning JavaScript imports instead of requiring synchronous-only interoperation.

## WebAssembly JavaScript-string ESM imports (`25.9.0`)

WebAssembly modules loaded through ESM can now use JavaScript-string constant imports, extending Node's WebAssembly ESM integration to that built-in import form.
