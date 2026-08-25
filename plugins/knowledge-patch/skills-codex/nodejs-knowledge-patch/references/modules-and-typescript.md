# Modules, TypeScript, and WebAssembly

## TypeScript execution and stripping

- In 23.2.0, built-in TypeScript support is active development and
  `node:module` exports `stripTypeScriptTypes()` for programmatic stripping of
  source text.
- In 23.6.0, `--experimental-strip-types` is enabled by default. Supported
  `.ts` files, standard input, eval input, and evaluated worker source can run
  without extra setup. The feature is still experimental here and supports
  only the documented subset of TypeScript.
- In 23.7.0, unsupported built-in stripping syntax reports
  `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX` rather than an undifferentiated parse
  failure.
- In 24.3.0, type stripping stops emitting an experimental warning at startup.
- In 25.2.0, the existing erasable-syntax type-stripping path is stable.
- In 26.0.0, `--experimental-transform-types` is removed.

## ESM and CommonJS loading

- In 23.1.0, JSON modules and import attributes are stable and follow the
  stage-4 proposal semantics.
- In 23.2.0, `findPackageJSON(specifier, base)` locates the relevant
  `package.json` relative to a base URL.
- In 23.4.0, `--experimental-default-type` is removed.
- In 23.5.0, `module.builtinModules` includes modules available only with the
  `node:` prefix. Preserve the prefix rather than assuming each list entry has
  an unprefixed form. `require(ESM)` warnings are opt-in through
  `--trace-require-module`.
- In 23.8.0, `module.builtinModules` omits `node:quic` unless the QUIC flag is
  active, so disabled QUIC is no longer reported as available.
- In 24.2.0, `import.meta.main` is true when an ES module is the process entry
  point. Loader hooks also cover dynamic source-phase imports.
- In 24.10.0, importing `.cts` uses the synchronous CommonJS loader and retains
  CommonJS semantics.
- In 24.9.0, when `require()` loads ESM, only the directly required module is
  inserted into `require.cache`; transitive ESM dependencies are not. Do not
  treat that cache as a complete ESM graph.
- In 25.4.0, synchronous `require(ESM)` is stable. Launchers can select it with
  `--require-module` or `--no-require-module`. Package `imports` maps accept
  keys beginning with `#/`, such as `"#/parser": "./src/parser.js"`.
- In 26.0.0, extensionless files inside packages with `"type": "module"` no
  longer receive a CommonJS exception and follow ESM interpretation.
- In 26.4.0, the loader implements package maps and deferred static imports.
  `import defer * as feature from './feature.js'` delays evaluation until the
  namespace is used.
- In 26.5.0, `--experimental-import-text` opts into experimental text imports.

## Module hooks

- In 23.5.0, `module.registerHooks()` installs synchronous `resolve` and `load`
  hooks in the current thread. They cover `require()`, `import`, and
  `createRequire()`, including paths not covered by asynchronous
  `module.register()` hooks.
- In 24.13.0, the 24.13.1 release classifies synchronous
  `module.registerHooks()` as release candidate and dedicated-thread
  `module.register()` as active development. It also fixes synchronous
  resolution hooks for `require()` of `node:`-prefixed built-ins.
- In 24.14.0, imported CommonJS modules invoke resolution hooks once rather
  than twice, so side-effectful hooks see one pass.
- In 25.9.0, dedicated-thread `module.register()` is documentation-deprecated
  as DEP0205. Prefer `module.registerHooks()` when a dedicated thread is not
  required.
- In 26.0.0, calling `module.register()` emits a runtime deprecation warning;
  use synchronous hooks where suitable.
- In 24.18.0, synchronous hook short-circuit results are honored by `require()`
  calls made from imported CommonJS modules.
- In 26.7.0, the `ModuleHooks` object returned by `registerHooks()` implements
  `Symbol.dispose`, allowing a `using` scope to remove registration.

## Native addon module loading

- In 23.6.0, the ESM loader has experimental support for native addon modules.
- In 26.5.0, ESM import support for native addons is enabled by default and no
  longer needs separate enablement.

## VM modules

- In 24.4.0, each `SourceTextModule.moduleRequests` entry includes its import
  phase, distinguishing source-phase from evaluation-phase requests.
- In 24.8.0, linkage for experimental `vm.SourceTextModule` is synchronous;
  custom VM tooling must not depend on the earlier asynchronous linkage phase.
- In 24.9.0, `SourceTextModule.prototype.hasTopLevelAwait()` reports whether a
  module directly contains top-level `await` without evaluating it.

## WebAssembly integration

- In 24.0.0, WebAssembly Memory64 is available. ESM can load top-level
  WebAssembly without a package type and supports source-phase imports.
- In 24.2.0, WebAssembly globals in an ES module namespace are unwrapped rather
  than returned as `WebAssembly.Global` wrappers.
- In 24.5.0, source- and instance-phase WebAssembly module integration no
  longer requires `--experimental-wasm-modules`; the implementation and
  proposal remain subject to change.
- In 25.0.0, WebAssembly JavaScript Promise Integration is enabled, allowing
  WebAssembly to suspend across promise-returning JavaScript imports.
- In 25.9.0, WebAssembly ESM modules can use JavaScript-string constant imports.

## Compile caches

- In 25.0.0, the module compile-cache API accepts `portable: true`, allowing a
  cache to move with an application instead of remaining tied to its original
  absolute path.
- In 25.9.0, single executable applications can build and use an ESM entry
  point's code cache with `useCodeCache: true`.
