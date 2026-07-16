# JavaScript and Wasm

## Gradle task and provider migrations

### Environment specifications

Plugin code should replace direct mutable extension assignments with `*EnvSpec` Gradle properties, for example:

```kotlin
the<NodeJsEnvSpec>().version.set("2.0.0")
```

Ordinary build scripts are adapted automatically.

Deprecated npm/Yarn internals, JavaScript utility APIs, and the old `ExperimentalWasmDsl` and `ExperimentalDceDsl` annotations produce errors. D8 and Binaryen types must come from the Wasm package, `NodeJsExec.create()` becomes `register()`, and compiler configuration must use `compilerOptions` rather than `kotlinOptions` properties.

### Removed task aliases

Replace the removed Wasm aliases as follows:

| Removed alias | Replacement |
| --- | --- |
| `wasmJsRun`, `wasmJsBrowserRun` | `wasmJsBrowserDevelopmentRun` |
| `wasmJsNodeRun` | `wasmJsNodeDevelopmentRun` |
| `wasmJsBrowserWebpack` | `wasmJsBrowserProductionWebpack` or `wasmJsBrowserDistribution` |

The JS equivalents are `jsBrowserDevelopmentRun`, `jsNodeDevelopmentRun`, `jsBrowserProductionWebpack`, and `jsBrowserDistribution`.

## Separate Wasm build infrastructure

Wasm files and dependencies move from `build/js` to `build/wasm`. Use `kotlinWasmNpmInstall` and `wasmRootPackageJson` instead of the JS-only `kotlinNpmInstall` and `rootPackageJson`, plus the new `Wasm*` plugin and environment-spec types. Apply custom Binaryen configuration per project or module rather than only at the root.

For `wasmJs`, Kotlin tooling packages live under the Kotlin user home while user packages remain in `build/wasm/node_modules`; project lockfiles contain only user dependencies. KGP creates `yarn.lock` only when the project has npm dependencies. Kotlin/JS retains the combined layout in the corresponding 2.2 tooling generation.

The `org.jetbrains.kotlin.npm-publish` Gradle plugin publishes Kotlin/JS and Kotlin/Wasm artifacts to NPM.

## Debugging and development servers

Development Wasm builds enable browser custom formatters by default, but the formatters must also be enabled in browser developer tools. Production builds still need `-Xwasm-debugger-custom-formatters`.

Pass `-Xwasm-generate-dwarf` to embed DWARF for standalone Wasm VMs and debuggers that support it.

KGP serves Kotlin sources automatically for every Wasm `*DevRun` task. Remove old custom `devServer.static` setup to avoid conflicts. These tasks expose source files and must not be hosted in cloud or production environments.

## Wasm runtime behavior

### Browser requirements

Kotlin/Wasm browser applications require both WebAssembly garbage collection and legacy exception-handling proposal support. This remains a deployment constraint even where baseline WebAssembly is available.

The `wasm-js` target is Beta, with a stronger stability commitment than its former Experimental status.

### Exception handling

On browsers with `WebAssembly.JSTag`—Chrome 115+, Firefox 129+, or Safari 18.4+—JavaScript errors retain details through Wasm and Kotlin exceptions reach JavaScript as catchable errors instead of opaque `WebAssembly.Exception` wrappers. Older browsers retain the previous behavior.

Kotlin 2.2.21 fixes Wasm exception handling on Safari 18.2 and 18.3 and in JavaScriptCore, where JavaScript exceptions could fail while crossing the Wasm boundary.

For WASI, `wasmWasi` emits the current WebAssembly exception-handling proposal by default for compatibility with modern standalone runtimes. `wasmJs` retains legacy handling unless `-Xwasm-use-new-exception-proposal` is supplied.

### Module initialization

Kotlin/Wasm performs module initialization during Wasm module instantiation rather than through a later external `_initialize()` call. Code using `@EagerInitialization` can run before module initialization completes and fail, so avoid the annotation unless required.

### Runtime reflection names

The earlier behavior rejects `KClass.qualifiedName` rather than silently returning an empty string. Add `-Xwasm-kclass-fqn` to store names and permit the call, accepting a binary-size increase.

Qualified names are now stored and available by default on Wasm targets, without `-Xwasm-kclass-fqn`, improving compatibility with reflection code ported from the JVM.

## JavaScript export and module interop

### Expanded exports

Files marked `@file:JsModule` may contain type aliases. `@JsExport` is allowed on multiplatform `expect` declarations when the JS `actual` is also annotated and all types are exportable. Exported `Promise<Unit>` results map to TypeScript `Promise<void>`.

With `-Xenable-suspend-function-exporting`, `@JsExport` exposes suspend functions and types containing them as JavaScript async/`Promise` APIs, including async overrides.

`@JsExport.Default` exports a class, object, function, or property as an ES-module `export default`; in other module systems it behaves like ordinary `@JsExport`.

### Companions and static members

Exported interface companions are accessed as `Foo.Companion.bar()` in every module system, replacing module-specific `Foo.bar()` or `Foo.getInstance().bar()` forms. Exported collection factories remain directly available, for example `KtList.fromJsArray(...)`.

An exported interface companion may mark members with `@JsStatic`, exposing `Foo.bar()` directly just as class companions do.

Kotlin 2.2.21 fixes ES-module exports for interfaces with companions. Kotlin 2.3.21 fixes incorrect TypeScript for `@JsStatic` suspend functions in class companions.

### Qualifiers

`@JsQualifier` can annotate an individual external function or class rather than forcing all qualified externals into a file-level annotation.

```kotlin
@JsQualifier("jsPackage")
private external fun jsFun()
```

### Plain objects

`@JsPlainObject` copy support moved from an instance method to the interface companion so it works with inheritance:

```kotlin
val changed = User.copy(user, age = 35)
```

Do not call `user.copy(age = 35)` for this API.

## JavaScript numeric interop

`-Xes-long-as-bigint` maps Kotlin `Long` to JavaScript `BigInt` for ES2020 output. Exported declarations containing `Long` additionally require `-XXLanguage:+JsAllowLongInExportedDeclarations`.

With the flag enabled, Kotlin/JS represents `LongArray` with `BigInt64Array` instead of `Array<bigint>`, allowing direct use with JavaScript typed-array APIs.

Kotlin 2.2.21 removes an accidental standard-library dependency on an ES2020-compatible engine caused by a `BigInt` type literal.

## JavaScript objects and TypeScript implementations

### Callable JavaScript objects on Wasm

On `wasmJs`, `@nativeInvoke` marks an `operator fun invoke` member of an external class or interface so Kotlin calls compile to direct calls of the JavaScript object. This Experimental bridge emits a compiler warning and may change or be removed.

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

### Implementing Kotlin interfaces in TypeScript

With `-Xenable-implementing-interfaces-from-typescript` and generated TypeScript definitions, external implementations identify themselves with the exported interface symbol and can reuse Kotlin defaults through `Interface.DefaultImpls`.

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

## Browser and Node APIs

The Kotlin/Wasm standard library supplies browser declarations including DOM and Fetch APIs, so applications need not recreate those externals. Declare missing or custom browser APIs with the same JavaScript interop facilities used to expose Kotlin code to JavaScript.

Calling `passCliArgumentsToMainFunction()` in a Kotlin/JS `nodejs` block removes the Node executable and script paths from the array passed to `main`, leaving only user CLI arguments:

```kotlin
kotlin { js { nodejs { passCliArgumentsToMainFunction() } } }
```

Kotlin/JS provides Experimental `KClass.isInterface`; opt in with `ExperimentalStdlibApi`.

## Transpilation

Kotlin/JS can delegate transpilation to SWC while the compiler itself targets up to ES2015. Enable the Experimental path in `gradle.properties`:

```properties
kotlin.js.delegated.transpilation=true
```

## Patch-sensitive JS and Wasm fixes

Kotlin 2.1.21 restores custom environment variables configured on `KotlinJsTest` tasks and fixes the `export startUnitTests was not found` failure that prevented Wasm tests after upgrading to 2.1.20.

Kotlin 2.2.10 repairs unusable npm build-cache entries from release candidates and Node.js tests that could not load `mocha`.

Kotlin 2.2.21 fixes Kotlin/JS interface companion exports and an accidental ES2020 engine requirement. It also repairs Wasm exceptions on Safari and JavaScriptCore as described above.

Kotlin 2.3.21 supports top-level declarations generated by compiler plugins during incremental JS compilation. It fixes false exportability warnings in multi-module builds, missing serializers with `whole-program` IR granularity, incorrect TypeScript for `@JsStatic` suspend companion functions, and bad standard-library source-map data.

The same patch fixes KLIB compilation failures when Kotlin/Wasm incremental compilation is enabled.
