# Multiplatform and Native

## Target and source-set migration

### Concrete Apple targets and hierarchy

The `ios()`, `watchos()`, and `tvos()` shortcuts are removed. Declare concrete targets and let the default hierarchy template create shared source sets. For Android publication, replace `publishAllLibraryVariants()` with explicit `publishLibraryVariants()` selections.

When both `js` and `wasmJs` are declared, the default hierarchy places `webMain` and `webTest` above them. Call `applyDefaultHierarchyTemplate()` and first rename any conflicting custom source sets or a target named `js("web")`.

On Gradle 8.8+, an experimental `dependencies` block directly inside `kotlin` adds common dependencies like `commonMain`:

```kotlin
kotlin {
    @OptIn(ExperimentalKotlinGradlePluginApi::class)
    dependencies { implementation("org.example:library:1.0") }
}
```

Kotlin 2.3.20 matches KMP dependencies more strictly. If metadata compilation begins failing, compare common and platform source-set resolution rather than assuming a compiler error. Kotlin 2.3.21 repairs `@JvmRecord` in `commonMain` failing `compileCommonMainKotlinMetadata` because `java.lang.Record` is inaccessible, and removes a false `SUBCLASS_CANT_CALL_COMPANION_PROTECTED_NON_STATIC` diagnostic in multi-module projects.

### Commonization and caches

Remove rejected `kotlin.mpp.enableOptimisticNumberCommonization` and `kotlin.mpp.enablePlatformIntegerCommonization`. They may have left invalid artifacts; run `./gradlew cleanNativeDistributionCommonization` or clear the relevant `~/.konan/*/klib/commonized` cache.

Cross-host KLIB publication can compile publishable KLIBs for all Native targets from supported hosts, making `kotlin.native.enableKlibsCrossCompilation=true` obsolete. macOS is still required for cinterop/CocoaPods dependencies, final Apple binaries, and Apple tests.

Kotlin-to-Java direct actualization is experimental. Kotlin Multiplatform IDE development is supported on Windows and Linux as well as earlier hosts.

## Apple toolchains, targets, and deployment

Xcode 16.3 support and associated cinterop fixes require Kotlin 2.1.21. Xcode 26 support begins with Kotlin 2.2.21 rather than 2.2.20.

Kotlin/Native 2.3 raises deployment floors to iOS/tvOS 14 and watchOS 7. `-Xoverride-konan-properties=minVersion.<target>=...` can request an older floor, but that build is unsupported and may fail at build or runtime.

`macosX64` and `iosX64` became tier 2 in 2.2.20; all Apple x86-64 targets (`macosX64`, `iosX64`, `tvosX64`, and `watchosX64`) were planned for phaseout through 2.4.0 and are tier 3 by Kotlin 2.3.

Kotlin/Native 2.2 raises its Windows baseline from Windows 7 to Windows 10.

## Native compiler and runtime configuration

### Compiler artifacts and stack protection

The legacy `konan/lib/kotlin-native.jar` is no longer published; use the embeddable compiler JAR. Remove `kotlin.native.useEmbeddableCompilerJar=false`, and compiler plugins should replace `getPluginArtifactForNative()` with `getPluginArtifact()`.

Set `kotlin.native.binary.stackProtector=yes` for functions considered vulnerable to stack smashing, `strong` for a broader heuristic, or `all` for every function.

Kotlin/Native uses Concurrent Mark and Sweep garbage collection by default; no explicit opt-in is needed.

### Gradle API migrations and cache workarounds

Replace `CInteropProcess.konanVersion` and `destinationDir` with `kotlinNativeVersion` and `destinationDirectory.set(...)`. The experimental `kotlinArtifacts` API is deprecated in favor of the current native-binaries DSL.

Replace deprecated `kotlin.native.cacheKind` with `disableNativeCache()` on the affected binary. Supply the Kotlin version and reason, with an optional issue URI, so the workaround is explicitly version-scoped:

```kotlin
framework {
    disableNativeCache(
        version = DisableCacheInKotlinVersion.2_3_0,
        reason = "Cache bug",
        issue = java.net.URI("https://youtrack.example/KT-123"),
    )
}
```

### KDoc and Objective-C block names

Native `.klib` artifacts embed KDoc and export it to Objective-C headers by default, making `-Xexport-kdoc` unnecessary. Disable per framework with `@OptIn(ExperimentalKotlinGradlePluginApi::class) exportKdoc.set(false)` only when needed.

Kotlin 2.2 can opt into Objective-C block parameter names with `kotlin.native.binary.objcExportBlockExplicitParameterNames=true`; Kotlin 2.3 enables them by default. Set `kotlin.native.binary.objcExportBlockExplicitParameterNames=false` only for compatibility with unnamed blocks.

### Exception formatting

From Kotlin 2.3.20, Native stack traces do not repeat a cause that was already printed, matching other targets.

## C and Objective-C interop

C and Objective-C library import is Beta. Compatibility across Kotlin, dependency, and Xcode versions is not guaranteed; `@ExperimentalForeignApi` remains required for affected `kotlinx.cinterop` APIs and non-platform native declarations.

Experimental direct-call interop uses `-Xccall-mode direct` on each cinterop invocation. It aims to be a drop-in implementation but does not support all declarations, and libraries produced with it must not be published while the mode remains experimental.

```kotlin
targets.withType<KotlinNativeTarget>().configureEach {
    compilations.configureEach {
        cinterops.configureEach { extraOpts += listOf("-Xccall-mode", "direct") }
    }
}
```

## Swift export

### Build integration

Swift export no longer needs `kotlin.experimental.swift-export.enabled`. It preserves modules, packages, type aliases, overloads, and primitive nullability but still requires direct Xcode integration. Replace the `embedAndSignAppleFrameworkForXcode` phase with `./gradlew :shared:embedSwiftExportForXcode`.

Use `swiftExport` for root and dependency module names, package flattening, and link-task compiler arguments. Outputs include Swift modules, a static library, a header, and a module map in the app build directory.

```kotlin
kotlin {
    swiftExport {
        moduleName = "Shared"
        flattenPackage = "com.example.shared"
        export(project(":subproject")) {
            moduleName = "Subproject"
            flattenPackage = "com.example.subproject"
        }
        configure { freeCompilerArgs.add("-Xexpect-actual-classes") }
    }
}
```

When an exported dependency uses opt-in APIs, add its opt-in to the Kotlin module's `compilerOptions`, outside the dependency's `export` block.

### Declaration shapes

Only final classes directly inheriting `Any` are supported, and Swift cannot subclass exported Kotlin classes or interfaces. Generic parameters erase to upper bounds; generic types and `suspend`, `inline`, or `operator` functions are limited; Kotlin functional types cannot be exported; collection inheritors may be absent or unusable. Swift closures may still be passed to Kotlin.

Kotlin objects become `KotlinBase` subclasses with private initializers and static `shared`; packages become nested Swift enums; an extension receiver becomes the first ordinary parameter. Mappings include `Int` to `Int32`, `Char` to `Unicode.UTF16.CodeUnit`, `Any` to `KotlinRuntime.KotlinBase`, and `Nothing` to `Never`.

Swift export maps Kotlin enums to Swift enums and `vararg` to Swift variadic parameters; generic variadic element types remain unsupported.

## Patch-level Native repairs

- Kotlin 2.1.21 fixes Xcode 16.3 cinterop failures.
- Kotlin 2.2.10 fixes an Xcode 16.3/iOS 15.5-simulator link failure and Apple Watch `SIGABRT` crashes.
- Kotlin 2.2.21 repairs KMP Parcelize, native cinterop commonization, Safari/JavaScriptCore Wasm exceptions, and modern Xcode support.
- Kotlin 2.3.21 repairs undefined iOS symbols from Objective-C frameworks added by Swift Package Manager and `TypeCastException` failures under `genericSafeCasts` for Objective-C protocol metaclasses and an `nw_parameters_create_secure_tcp` block parameter.
- Kotlin 2.4.10 fixes `IrTypeAliasSymbolImpl is already bound` for `kotlinx.datetime.Instant` on `iosSimulatorArm64`.
