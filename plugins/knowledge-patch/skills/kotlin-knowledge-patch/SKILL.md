---
name: kotlin-knowledge-patch
description: Kotlin
license: MIT
version: 2.3.20
metadata:
  author: Nevaberry
---

# Kotlin Knowledge Patch

Use this patch when writing, reviewing, upgrading, or troubleshooting Kotlin code and builds. Start with the quick references below, then open only the topic files relevant to the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [language-and-compiler.md](references/language-and-compiler.md) | Language semantics, context parameters, diagnostics, annotations, JVM interop, reflection, scripting |
| [jvm-and-build-tooling.md](references/jvm-and-build-tooling.md) | Gradle and Maven compatibility, KGP APIs, kapt, Build Tools API, publishing, ABI validation |
| [multiplatform-and-native.md](references/multiplatform-and-native.md) | Multiplatform source sets, Apple targets, Kotlin/Native, C/Objective-C interop, Swift export |
| [javascript-and-wasm.md](references/javascript-and-wasm.md) | Kotlin/JS, Kotlin/Wasm, JavaScript interop, browser and Node tooling, NPM publishing |
| [standard-library.md](references/standard-library.md) | Time, UUIDs, atomics, arrays, collections, and removed APIs |
| [compose-multiplatform.md](references/compose-multiplatform.md) | Compose compiler changes, resources, navigation, iOS, web, desktop, previews, testing |
| [ecosystem-libraries.md](references/ecosystem-libraries.md) | Coroutines, serialization, Ktor, Exposed, Koog, IDE and editor tooling |

## Upgrade triage

Before changing source code, identify the exact Kotlin, Kotlin Gradle plugin, Gradle, Android Gradle plugin, Compose Multiplatform, and ecosystem-library versions in use. Patch releases repair important compiler, reflection, JavaScript, Native, Wasm, scripting, and Compose regressions, so first check whether upgrading the patch version resolves the failure.

For build upgrades:

1. Remove obsolete Gradle properties and compiler flags before interpreting new failures.
2. Check common and platform dependency resolution separately in multiplatform builds.
3. Update custom Gradle plugins away from removed KGP internals and mutable extension assignments.
4. Clean Native commonization caches after removing obsolete number-commonization properties.
5. Re-run ABI validation, Compose mapping generation, JavaScript/Wasm tests, and Native link tasks.

## Breaking language and compiler changes

### Replace context receivers with context parameters

Context receivers are no longer supported. Rewrite declarations with named context parameters:

```kotlin
context(logger: Logger)
fun report(message: String) = logger.log(message)
```

Declare context parameters only on functions and whole properties. Contextual properties require accessors and cannot have backing fields, initializers, or delegates. Use `_` for a value that participates in context resolution but is not referenced by name.

Context lookup requires exactly one compatible value at the nearest scope level. Same-level matches are ambiguous, and an overload with context parameters is not more specific than a matching overload without them.

### Account for stricter source checks

Expect errors for inaccessible types exposed through indirect dependencies, less-visible type-parameter bounds, private references from non-private inline declarations, nullable type-alias supertypes, serializable inline lambdas, invalid generic Java delegation, and several variance-bearing type-alias uses.

Kotlin 2.3.21 postponed strict rejection of inferred type arguments that violate upper bounds. Do not treat a successful build on that patch as proof that the source satisfies the future restriction.

### Migrate removed language and library forms

- Do not use callable references to Java synthetic properties; call Java accessors directly where necessary.
- Replace `kotlin.native.Throws` with `kotlin.Throws`.
- Replace `AbstractDoubleTimeSource` with `AbstractLongTimeSource`.
- Replace old character/number conversion APIs and `Number.toChar()` with explicit conversions.
- Use `kotlin.io.path.createTempDirectory` and `createTempFile` instead of the removed `kotlin.io` forms.
- Give `String.subSequence` arguments their current `startIndex` and `endIndex` names.
- Do not place a non-local `return` in a default lambda.

### Use current JVM defaults and annotations

Use stable `-jvm-default`; its default mode is `enable`. Select `no-compatibility` to emit only interface defaults or `disable` for the legacy `DefaultImpls`-only scheme.

Use `@JvmExposeBoxed` or `-Xjvm-expose-boxed` when Java callers need boxed entry points for inline value classes. Use `@all:Ann` with `-Xannotation-target-all` when an annotation must propagate to every applicable property-related target.

### Adopt opt-in language features deliberately

- Enable `-Xexplicit-backing-fields` for a public property whose backing storage has a narrower implementation type.
- Enable `-Xreturn-value-checker=check` or `full`, then use `@MustUseReturnValues`, `@IgnorableReturnValue`, or `val _ = call()` to express intent.
- Use name-based destructuring only behind `-Xname-based-destructuring`; its modes intentionally differ in syntax and compatibility behavior.
- Use per-diagnostic `-Xwarning-level=NAME:error|warning|disabled` when global warning settings are too broad.

## Gradle, Android, and compiler tooling

### Migrate Android builds for AGP 9

AGP 9 has built-in Kotlin support. Stop applying `org.jetbrains.kotlin.android`. For multiplatform Android libraries, apply `com.android.kotlin.multiplatform.library` and replace `androidTarget {}` with `android {}`. Keep `androidTarget` only while using an older AGP line where it remains valid.

Compose Multiplatform projects should normally isolate the Android application in its own module. Check the Compose reference before combining AGP 9 with an older Compose Multiplatform release.

### Use current Kotlin Gradle plugin APIs

- Register generated Kotlin through `KotlinSourceSet.generatedKotlin`; read `allKotlinSources` when generated sources must be included.
- Use `source()` to add compile inputs; `KotlinCompileTool.setSource()` now replaces them.
- Configure generated resources through `KotlinSourceSet.resources`.
- Use `compilerOptions`, not legacy `kotlinOptions` properties.
- Configure JS and Wasm runtimes through `*EnvSpec` Gradle properties.
- Use Gradle's `ExtraPropertiesExtension`, not internal `ExtrasProperty`.
- Configure Kotlin dependencies on `KotlinSourceSet`, not `HasKotlinDependencies` helpers.

Do not subclass Kotlin test, JavaScript runtime, webpack, Karma, or Yarn setup classes. Configure them through supported plugin DSLs.

### Expect Build Tools API defaults

Kotlin/JVM Gradle compilation uses the Build Tools API by default. The API supports immutable built operations, best-effort cancellation, common metrics, and structured compiler-plugin configuration. The deprecated out-of-process execution strategy is unsupported; use daemon or in-process compilation.

When the Kotlin Maven plugin is a build extension, it can register standard Kotlin source roots and add `kotlin-stdlib` automatically. Disable both with `kotlin.smart.defaults.enabled=false` only when explicit control is required.

### Update kapt and ABI validation

K2 kapt is the default. If a regression cannot yet be avoided, temporarily set `kapt.use.k2=false`. Use typed `annotationProcessorOptionsProviders` and add providers with `addAll()`.

Use `checkKotlinAbi` and `updateKotlinAbi`; ABI validation wires its check into Gradle's `check` lifecycle. The older task aliases remain temporarily available.

## Multiplatform and Native

### Use concrete targets and current source-set defaults

Replace removed `ios()`, `watchos()`, and `tvos()` shortcuts with concrete targets. The default hierarchy creates `webMain` and `webTest` above JS and Wasm when both targets are declared. Cross-host KLIB publication does not remove the need for macOS when cinterop, CocoaPods, final Apple binaries, or Apple tests are involved.

Multiplatform metadata matching is stricter. If metadata compilation fails after an upgrade, compare resolved dependencies in common and platform source sets rather than assuming a compiler regression.

### Treat Apple baseline changes as deployment constraints

Native deployment baselines are iOS/tvOS 14 and watchOS 7. Apple x86-64 targets are tier 3. Overrides that request older deployment versions are unsupported and can fail during the build or at runtime.

KDoc export and Objective-C block parameter names are enabled by default. Disable them only for a concrete compatibility need.

### Configure Swift export explicitly

Use `swiftExport` to name modules, flatten package prefixes, export dependencies, and pass compiler arguments. Put dependency-required opt-ins in the Kotlin module's `compilerOptions`, not inside an `export` block. Review declaration-shape limits before designing a Swift-facing API.

Do not publish libraries built with experimental direct C/Objective-C call mode.

## JavaScript and Wasm

### Separate JS and Wasm tooling

Wasm build files live under `build/wasm` and use Wasm-specific install, package, environment, D8, and Binaryen APIs. Removed task aliases must be replaced with explicit browser or Node development-run and production-distribution tasks.

Kotlin/Wasm initializes during module instantiation. Avoid `@EagerInitialization` where it could run before initialization completes.

### Choose interop flags intentionally

- `-Xes-long-as-bigint` maps `Long` to JavaScript `BigInt` and `LongArray` to `BigInt64Array`.
- `-Xenable-suspend-function-exporting` exposes exported suspend APIs as JavaScript promises.
- `-Xenable-implementing-interfaces-from-typescript` lets generated TypeScript implementations identify Kotlin interfaces by symbol.
- `@nativeInvoke` enables direct calls to callable external JavaScript objects on Wasm.
- `@JsExport.Default` creates ES-module default exports.

Deploy Wasm browser applications only where WebAssembly garbage collection and the required exception-handling behavior are supported. Use the combined JS/Wasm browser distribution when a JavaScript fallback is required.

## Standard library highlights

`kotlin.time.Clock` and `kotlin.time.Instant` are stable. UUID parsing accepts dashed and plain hexadecimal forms; newer experimental APIs add nullable parsers plus v4 and v7 generation.

Common atomics support functional updates that return the old value, the new value, or no value. Array `copyOf(newSize) { initializer }` fills new slots without widening `Array<T>` to `Array<T?>`.

`Iterable.intersect()` and `subtract()` now apply ordinary `Any.equals` membership consistently, including when the supplied collection uses referential equality internally.

## Compose Multiplatform essentials

Use direct library coordinates instead of deprecated Compose Gradle-plugin dependency aliases. Import the unified `androidx.compose.ui.tooling.preview.Preview` annotation for common previews.

Migrate Java-only resource APIs to the multiplatform resource library. Android library targets may need `androidResources.enable = true`; XCFramework resource embedding requires a current Kotlin Gradle plugin.

On iOS, set `CADisableMinimumFrameDurationOnPhone` to `true`. Concurrent rendering is enabled by default, native interop can be placed as overlays, and the newer text-input path remains opt-in.

On web, prefer `ComposeViewport`, `WebElementView`, and `NavController.bindToBrowserNavigation()`. Accessibility is enabled by default. `CanvasBasedWindow` and `Window.bindToNavigation()` are deprecated.

Compose UI testing now favors the v2 runner with `StandardTestDispatcher`. Delayed composition coroutines can count as idle, so advance the test clock explicitly when delayed work matters.

## Ecosystem checks

Coroutines add `Flow.any`, `all`, `none`, and `chunked`; `runTest` has a 60-second default whole-test timeout. Close dispatcher views with `use` when their backing dispatcher is closeable.

Serialization adds stable JSON leniency options, per-class unknown-key handling, standard `Instant` serializers, sealed-subclass registration, CBOR/COSE options, generated-serializer retention, UUID support, `kotlinx-io` integration, and ProtoBuf `oneof` hierarchies. Match the serialization runtime and compiler plugin requirements noted in the reference.

Ktor, Exposed, Koog, the Kotlin language server, and editor tooling have substantial newer capabilities; consult the ecosystem reference before selecting APIs or assuming lifecycle status.
