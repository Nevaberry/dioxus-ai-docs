# JavaScript and Wasm

## Gradle task and Provider API migration

Plugin code must configure JS and Wasm environments through Provider-based `*EnvSpec` properties instead of mutable extension assignments. Ordinary build scripts are adapted automatically.

```kotlin
the<NodeJsEnvSpec>().version.set("22.0.0")
```

Replace removed task aliases with explicit environment and mode names:

| Removed alias | Replacement |
| --- | --- |
| `wasmJsRun`, `wasmJsBrowserRun` | `wasmJsBrowserDevelopmentRun` |
| `wasmJsNodeRun` | `wasmJsNodeDevelopmentRun` |
| `wasmJsBrowserWebpack` | `wasmJsBrowserProductionWebpack` or `wasmJsBrowserDistribution` |
| `jsBrowserRun` | `jsBrowserDevelopmentRun` |
| `jsNodeRun` | `jsNodeDevelopmentRun` |
| `jsBrowserWebpack` | `jsBrowserProductionWebpack` or `jsBrowserDistribution` |

Wasm infrastructure is independent from JS. Its generated files and dependencies live under `build/wasm`; use `kotlinWasmNpmInstall`, `wasmRootPackageJson`, and Wasm-specific plugin, D8, Binaryen, and environment-spec types. Apply custom Binaryen configuration per project or module, not only at the root.

Deprecated npm/Yarn internals, JavaScript utility APIs, and old `ExperimentalWasmDsl` and `ExperimentalDceDsl` annotations are errors. `NodeJsExec.create()` becomes `register()`, and compiler configuration belongs in `compilerOptions`, not `kotlinOptions` properties.

The legacy JS backend's `KotlinJsDce`, `dceTask`, and related compiler DSLs are removed. The IR backend performs dead-code elimination itself; use `@JsExport` to retain exported APIs.

## Development, testing, and package layout

Development Wasm builds enable browser custom formatters by default, but the browser developer tools must also enable them. Production builds need `-Xwasm-debugger-custom-formatters`. Use `-Xwasm-generate-dwarf` to embed DWARF for compatible standalone VMs and debuggers.

Every Wasm `*DevRun` task serves Kotlin sources automatically. Remove custom `devServer.static` source-serving configuration to avoid conflicts, and never expose these development tasks from cloud or production hosting because they reveal sources.

For `wasmJs`, Kotlin tooling packages live in the Kotlin user home and project packages in `build/wasm/node_modules`; project lockfiles contain only user dependencies. KGP creates `yarn.lock` only when a project has npm dependencies. Kotlin/JS retained the combined layout in Kotlin 2.2.20.

Kotlin 2.4.10 makes `kotlinUpgradeYarnLock` regenerate the lock even when `kotlinNpmInstall` is up to date, preventing a later `kotlinStoreYarnLock` failure.

Kotlin 2.1.21 restores custom environment variables on `KotlinJsTest` tasks and fixes the Wasm `export startUnitTests was not found` startup failure from 2.1.20.

Kotlin 2.2.10 repairs unusable npm build-cache entries from the 2.2 release candidates and Node.js tests that could not load `mocha`.

Calling `passCliArgumentsToMainFunction()` in a JS `nodejs` block strips the Node executable and script path, leaving only user arguments for `main`:

```kotlin
kotlin { js { nodejs { passCliArgumentsToMainFunction() } } }
```

The `org.jetbrains.kotlin.npm-publish` Gradle plugin publishes Kotlin/JS and Kotlin/Wasm artifacts to NPM.

## JavaScript declarations and exports

`@JsPlainObject` copy support belongs to the interface companion so it works with inheritance:

```kotlin
val changed = User.copy(user, age = 35)
```

Do not call `user.copy(...)` for this API.

Files annotated `@file:JsModule` may contain type aliases. `@JsExport` is permitted on a multiplatform `expect` when the JS `actual` is also annotated and all involved types are exportable. An exported `Promise<Unit>` becomes TypeScript `Promise<void>`.

Exported interface companions use `Foo.Companion.bar()` consistently across module systems. Collection factories remain direct, such as `KtList.fromJsArray(...)`. Add `@JsStatic` inside an exported interface companion when JavaScript needs `Foo.bar()` directly.

`@JsQualifier` may annotate an individual external function or class instead of requiring a file-level annotation:

```kotlin
@JsQualifier("jsPackage")
private external fun jsFun()
```

`@JsExport.Default` creates an ES-module default export for a class, object, function, or property. Under other module systems it behaves like ordinary `@JsExport`.

With `-Xenable-suspend-function-exporting`, exported suspend functions and types containing them become JavaScript async/`Promise` APIs, including async overrides.

Kotlin/JS exposes experimental `KClass.isInterface`; opt in with `ExperimentalStdlibApi`.

## Long and typed-array interop

`-Xes-long-as-bigint` represents Kotlin `Long` as JavaScript `BigInt` for ES2020 output. Exported declarations using `Long` additionally need `-XXLanguage:+JsAllowLongInExportedDeclarations`.

With that mapping enabled, `LongArray` is represented as JavaScript `BigInt64Array`, not `Array<bigint>`, enabling direct typed-array interop.

## Wasm reflection and initialization

Before Kotlin 2.3, Wasm rejected `KClass.qualifiedName` unless `-Xwasm-kclass-fqn` stored qualified names at a binary-size cost. Kotlin 2.3 enables qualified names by default.

Kotlin/Wasm performs initialization during Wasm module instantiation instead of through a later external `_initialize()` call. `@EagerInitialization` code may run before module initialization finishes, so avoid it unless required.

Kotlin 2.4.10 fixes `multimodule-closed-world` incremental compilation that omitted files from the compiler output directory. Upgrade affected builds rather than compensating for incomplete output.

Kotlin 2.3.21 fixes incremental KLIB compilation on Wasm.

## Exception handling and deployment requirements

On browsers with `WebAssembly.JSTag`—Chrome 115+, Firefox 129+, and Safari 18.4+ in the extracted compatibility guidance—JavaScript errors preserve details through Wasm and Kotlin exceptions reach JavaScript as catchable errors. Older browsers retain opaque `WebAssembly.Exception` behavior.

Kotlin 2.2.21 repairs exception propagation on Safari 18.2/18.3 and JavaScriptCore.

`wasmWasi` emits the current WebAssembly exception-handling proposal by default. `wasmJs` continues to use legacy handling unless given `-Xwasm-use-new-exception-proposal`.

Browser applications require both WebAssembly garbage collection and legacy exception handling. Verify both features at deployment time even if baseline WebAssembly is available. The `wasm-js` target is Beta.

The standard library supplies DOM and Fetch declarations on Wasm. Declare missing or custom browser APIs through the normal JavaScript interop facilities instead of recreating built-in declarations.

## Calling JavaScript and implementing Kotlin interfaces

On `wasmJs`, experimental `@nativeInvoke` marks an external class or interface's `operator fun invoke` so a Kotlin call directly invokes the JavaScript object. The compiler currently warns because the bridge may change or disappear.

```kotlin
import kotlin.js.nativeInvoke

@OptIn(ExperimentalWasmJsInterop::class)
external class JsAction {
    @nativeInvoke
    operator fun invoke(data: String)
}

val action = JsAction()
action("Run task")
```

To implement exported Kotlin interfaces in JavaScript or TypeScript, generate TypeScript definitions and enable `-Xenable-implementing-interfaces-from-typescript`. Implementations identify themselves with the exported interface symbol and can call Kotlin defaults through `Interface.DefaultImpls`.

```kotlin
js {
    generateTypeScriptDefinitions()
    compilerOptions {
        freeCompilerArgs.add("-Xenable-implementing-interfaces-from-typescript")
    }
}
```

```typescript
class JsonProcessor implements DataProcessor {
  readonly [DataProcessor.Symbol] = true;
  async process(): Promise<string> { return "processed"; }
}
```

## Transpilation and patch fixes

Kotlin/JS can delegate transpilation to experimental SWC while the compiler itself targets up to ES2015:

```properties
kotlin.js.delegated.transpilation=true
```

Kotlin 2.2.21 corrects ES-module exports for interfaces with companions and removes an accidental standard-library dependency on an ES2020 engine caused by a `BigInt` type literal.

Kotlin 2.3.21 fixes false exportability warnings in multi-module builds, missing serializers under `whole-program` IR granularity, incorrect TypeScript for `@JsStatic` suspend functions in class companions, malformed standard-library source maps, and compiler-plugin-generated top-level declarations during incremental compilation.
