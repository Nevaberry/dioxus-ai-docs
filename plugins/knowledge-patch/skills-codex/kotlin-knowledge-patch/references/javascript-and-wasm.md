# JavaScript and Wasm

## Build layout and Gradle APIs

### Separate Wasm infrastructure

Wasm files and dependencies live under `build/wasm`, not `build/js`. Use `kotlinWasmNpmInstall`, `wasmRootPackageJson`, and `Wasm*` plugin/environment types instead of JS-only `kotlinNpmInstall` and `rootPackageJson`. Apply custom Binaryen configuration per project or module, not only at the root.

Replace direct mutable runtime extension assignments in plugins with `*EnvSpec` properties, for example `the<NodeJsEnvSpec>().version.set("2.0.0")`; ordinary build scripts are adapted automatically. D8 and Binaryen types must come from Wasm packages, `NodeJsExec.create()` becomes `register()`, and removed `ExperimentalWasmDsl`/`ExperimentalDceDsl` and npm/Yarn internal APIs may no longer be used.

### Task-name migrations

Replace old run/webpack aliases:

- `wasmJsRun` and `wasmJsBrowserRun` → `wasmJsBrowserDevelopmentRun`
- `wasmJsNodeRun` → `wasmJsNodeDevelopmentRun`
- `wasmJsBrowserWebpack` → `wasmJsBrowserProductionWebpack` or `wasmJsBrowserDistribution`
- use corresponding `jsBrowserDevelopmentRun`, `jsNodeDevelopmentRun`, `jsBrowserProductionWebpack`, and `jsBrowserDistribution` names for JS

Every Wasm `*DevRun` task now serves Kotlin sources automatically. Remove custom `devServer.static` source serving, and never expose these development tasks as production/cloud hosting because they publish source.

### NPM layout and publication

For `wasmJs`, Kotlin tooling packages live under the Kotlin user home and user dependencies in `build/wasm/node_modules`; project lockfiles contain only user dependencies. KGP creates `yarn.lock` only when npm dependencies exist. Kotlin/JS retained the combined layout in 2.2.20.

The `org.jetbrains.kotlin.npm-publish` Gradle plugin publishes Kotlin/JS and Kotlin/Wasm artifacts to NPM.

Kotlin 2.4.10 makes `kotlinUpgradeYarnLock` regenerate the lock even when `kotlinNpmInstall` is up-to-date, preventing a following `kotlinStoreYarnLock` failure.

## Debugging, tests, and execution

Development Wasm builds enable browser custom formatters by default, though browser developer tools must also enable them. Production builds still need `-Xwasm-debugger-custom-formatters`. Use `-Xwasm-generate-dwarf` to embed DWARF for compatible standalone runtimes and debuggers.

Kotlin 2.1.21 restores custom environment variables on `KotlinJsTest` tasks and fixes the Wasm test startup error `export startUnitTests was not found` from 2.1.20.

Within Kotlin/JS `nodejs`, call `passCliArgumentsToMainFunction()` to strip the Node executable and script paths from `main` arguments, leaving only user CLI arguments.

The legacy JS backend's `KotlinJsDce`, `dceTask`, and related compiler-option DSLs are removed. JS IR performs dead-code elimination and `@JsExport` retains public exports.

## JavaScript interop

### Plain objects, modules, and exports

`@JsPlainObject` copying is a companion operation so inheritance works: use `User.copy(user, age = 35)`, not `user.copy(...)`.

Files annotated `@file:JsModule` may contain type aliases. Multiplatform `expect` declarations may use `@JsExport` when the JS `actual` is also annotated and all types are exportable. Exported `Promise<Unit>` maps to TypeScript `Promise<void>`.

`@JsExport.Default` emits ES-module `export default` for a class, object, function, or property; other module systems treat it as ordinary `@JsExport`. `@JsQualifier` may annotate an individual external function or class instead of an entire file.

### Companion objects and suspend APIs

Exported interface companions use `Foo.Companion.bar()` consistently across module systems instead of old module-specific forms such as `Foo.getInstance().bar()`. Collection factories stay direct, such as `KtList.fromJsArray(...)`. `@JsStatic` in an exported interface companion exposes `Foo.bar()` directly.

With `-Xenable-suspend-function-exporting`, exported suspend functions and types map to JavaScript async/Promise APIs, including async overrides.

### Long values and arrays

`-Xes-long-as-bigint` maps Kotlin `Long` to JavaScript `BigInt` for ES2020. Exporting a declaration containing `Long` additionally needs `-XXLanguage:+JsAllowLongInExportedDeclarations`. With the flag enabled, `LongArray` maps to `BigInt64Array` rather than `Array<bigint>`.

### TypeScript implementations of Kotlin interfaces

With generated definitions and `-Xenable-implementing-interfaces-from-typescript`, JavaScript/TypeScript implementations identify themselves through the exported interface symbol and may call Kotlin defaults through `Interface.DefaultImpls`.

```kotlin
js {
    generateTypeScriptDefinitions()
    compilerOptions {
        freeCompilerArgs.add("-Xenable-implementing-interfaces-from-typescript")
    }
}
```

### Reflection and transpilation

Kotlin/JS provides experimental `KClass.isInterface` under `ExperimentalStdlibApi`.

Kotlin/JS may delegate transpilation to experimental SWC while the compiler still targets up to ES2015. Enable `kotlin.js.delegated.transpilation=true` in `gradle.properties`.

## Wasm interop and runtime

### Browser requirements and exception behavior

Kotlin/Wasm browser applications require WebAssembly garbage collection and legacy exception handling. On browsers with `WebAssembly.JSTag`—Chrome 115+, Firefox 129+, or Safari 18.4+ in the source guidance—JavaScript errors retain details across Wasm and Kotlin exceptions are catchable JavaScript errors; older browsers retain opaque wrapper behavior.

Kotlin 2.2.21 repairs exception crossings on Safari 18.2/18.3 and JavaScriptCore. Older exception support can expose opaque `WebAssembly.Exception` wrappers. For `wasmWasi`, Kotlin 2.3 emits the current WebAssembly exception proposal by default; `wasmJs` retains legacy handling unless given `-Xwasm-use-new-exception-proposal`.

The `wasm-js` target is Beta. The standard library supplies DOM and Fetch declarations; declare absent/custom browser APIs through ordinary JavaScript interop.

### Qualified class names and initialization

Kotlin 2.2 Wasm rejects `KClass.qualifiedName` unless `-Xwasm-kclass-fqn` stores names at a binary-size cost. Kotlin 2.3 enables qualified names by default.

Wasm module initialization now runs during instantiation rather than a later `_initialize()` call. `@EagerInitialization` can execute too early; avoid it unless required.

### Callable JavaScript objects

On `wasmJs`, experimental `@nativeInvoke` on `operator fun invoke` in an external class/interface compiles a Kotlin call into a direct call of the JavaScript object. It currently emits a warning and may change.

```kotlin
@OptIn(ExperimentalWasmJsInterop::class)
external class JsAction {
    @nativeInvoke
    operator fun invoke(data: String)
}
```

## Patch-level JS and Wasm repairs

- Kotlin 2.2.10 repairs npm cache entries from release candidates and Node tests unable to load Mocha.
- Kotlin 2.2.21 fixes ES-module interface-companion exports and removes an accidental ES2020 engine requirement caused by a `BigInt` literal.
- Kotlin 2.3.21 supports compiler-plugin-generated top-level declarations during incremental JS compilation and fixes false exportability warnings, missing whole-program serializers, incorrect TypeScript for companion `@JsStatic` suspend functions, and bad standard-library source maps.
- Kotlin 2.3.21 repairs incremental Wasm KLIB compilation.
- Kotlin 2.4.10 repairs `multimodule-closed-world` incremental compilation omitting files from the output directory; upgrade instead of compensating for incomplete output.

## Distribution fallback

When a browser may lack required Wasm features, Compose Multiplatform's `composeCompatibilityBrowserDistribution` packages JS and Wasm browser distributions together so the application can fall back to JS.
