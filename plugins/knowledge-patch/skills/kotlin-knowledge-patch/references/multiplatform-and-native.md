# Multiplatform and Native

## Source sets and dependency topology

### Default web source sets

The default multiplatform hierarchy places `webMain` and `webTest` above both `js` and `wasmJs`. Declare both targets and call `applyDefaultHierarchyTemplate()`; first rename conflicting custom source sets or a target named `js("web")`.

```kotlin
kotlin {
    js()
    wasmJs()
    applyDefaultHierarchyTemplate()
}
```

### Top-level common dependencies

On Gradle 8.8 or newer, an Experimental `dependencies` block directly inside `kotlin` adds common dependencies as though they were declared in `commonMain`:

```kotlin
kotlin {
    @OptIn(ExperimentalKotlinGradlePluginApi::class)
    dependencies { implementation("org.example:library:1.0") }
}
```

### Dependency matching and regressions

Kotlin 2.3.20 can fail metadata compilation when dependency resolution differs between common and platform source sets because multiplatform dependency matching is stricter. Compare those resolutions when an upgrade introduces a metadata compilation failure.

Kotlin 2.1.21 restores dependency resolution from `commonTest` or `nativeTest` to another multiplatform project after a 2.1.20 regression.

Kotlin 2.2.21 repairs Parcelize in multiplatform projects and Native cinterop commonization failures involving a missing `kotlinNativeBundleConfiguration`, unresolved POSIX `size_t`, or imports from commonized test cinterops.

## Target DSL migration and publication

The `ios()`, `watchos()`, and `tvos()` shortcuts are removed. Declare concrete Apple targets and let the default hierarchy template create shared source sets. Android publications should replace `publishAllLibraryVariants()` with explicit `publishLibraryVariants()` selections.

Supported hosts can compile publishable `.klib` artifacts for all Native targets by default, so `kotlin.native.enableKlibsCrossCompilation=true` is obsolete. A Mac remains necessary for cinterop or CocoaPods dependencies and for building or testing final Apple binaries.

Experimental Kotlin-to-Java direct actualization has been available since Kotlin 2.1.0. Treat it as pre-stable and account for compatibility changes when adopting it.

## Native Gradle and compiler migration

`CInteropProcess.konanVersion` and `destinationDir` produce errors; use `kotlinNativeVersion` and `destinationDirectory.set(...)`. The Experimental `kotlinArtifacts` API is deprecated in favor of the current native-binaries DSL.

The legacy `konan/lib/kotlin-native.jar` is no longer published; the embeddable compiler JAR is always used. Remove `kotlin.native.useEmbeddableCompilerJar=false`. Compiler plugins must replace `getPluginArtifactForNative()` with `getPluginArtifact()`.

Remove `kotlin.mpp.enableOptimisticNumberCommonization` and `kotlin.mpp.enablePlatformIntegerCommonization`, which Kotlin 2.2 rejects and which may have cached invalid artifacts. Then run:

```shell
./gradlew cleanNativeDistributionCommonization
```

Alternatively, clear the appropriate `~/.konan/*/klib/commonized` cache.

## Apple toolchains and deployment

### Xcode compatibility

Kotlin/Native support for Xcode 16.3, including a cinterop compilation fix, starts in Kotlin 2.1.21 rather than 2.1.20.

Kotlin 2.2.10 repairs an Xcode 16.3/iOS 15.5-simulator linker failure and Apple Watch `SIGABRT` crashes. Xcode 26 support starts in Kotlin 2.2.21 rather than 2.2.20.

### Deployment baselines and target tiers

The minimum supported Windows target rises from Windows 7 to Windows 10 in Kotlin/Native 2.2.

Apple x86-64 targets enter a phaseout: `macosX64` and `iosX64` become tier 2 in 2.2.20, with `macosX64`, `iosX64`, `tvosX64`, and `watchosX64` planned for gradual deprecation and removal during the 2.2.20–2.4.0 cycle.

The current minimum Apple deployment versions are iOS/tvOS 14 and watchOS 7. The four Apple x86-64 targets move to tier 3. `-Xoverride-konan-properties=minVersion.<target>=...` can attempt an older baseline, but the build is unsupported and may fail at build time or runtime.

## Native runtime and diagnostics

### Garbage collection

Concurrent Mark and Sweep (CMS) garbage collection is the default for the Kotlin/Native runtime; Native projects receive it without an explicit opt-in.

### Stack protection

Set `kotlin.native.binary.stackProtector=yes` for functions considered vulnerable to stack smashing, `strong` for a broader heuristic, or `all` for every function.

### Stack traces

Starting in 2.3.20, Native exception formatting matches other platforms by not printing an additional cause when that same cause was already printed.

### Version-scoped cache disabling

Replace the deprecated `kotlin.native.cacheKind` property with `disableNativeCache()` on the affected binary. The DSL requires the Kotlin version and a reason and accepts an optional issue URI, making temporary workarounds explicit.

```kotlin
framework {
    disableNativeCache(
        version = DisableCacheInKotlinVersion.2_3_0,
        reason = "Cache bug",
        issue = java.net.URI("https://youtrack.example/KT-123")
    )
}
```

## Objective-C export and C interop

### Block parameter names and KDoc

The earlier opt-in `kotlin.native.binary.objcExportBlockExplicitParameterNames=true` carries Kotlin function-type parameter names into exported Objective-C block types, improving Xcode completion and avoiding Clang warnings.

Parameter names are now emitted by default. Set `kotlin.native.binary.objcExportBlockExplicitParameterNames=false` only when compatibility requires unnamed parameters.

Native compilation embeds KDoc in KLIBs and exports it to Objective-C headers by default without `-Xexport-kdoc`. A framework can opt out with `@OptIn(ExperimentalKotlinGradlePluginApi::class) exportKdoc.set(false)`, conventionally formatted as:

```kotlin
@OptIn(ExperimentalKotlinGradlePluginApi::class)
exportKdoc.set(false)
```

### C and Objective-C library import

C and Objective-C library import is Beta, but binary compatibility across Kotlin, dependency, and Xcode versions is not guaranteed. `@ExperimentalForeignApi` remains required for affected `kotlinx.cinterop` APIs and non-platform native-library declarations.

Native cinterops can test the Experimental, compatibility-oriented direct call mode by adding `-Xccall-mode direct` to every cinterop invocation:

```kotlin
targets.withType<org.jetbrains.kotlin.gradle.plugin.mpp.KotlinNativeTarget>().configureEach {
    compilations.configureEach {
        cinterops.configureEach {
            extraOpts += listOf("-Xccall-mode", "direct")
        }
    }
}
```

The mode is intended as a drop-in replacement but does not support every declaration. Do not publish libraries built with it while it remains Experimental.

## Swift export

### Build integration

Experimental Swift export is available without `kotlin.experimental.swift-export.enabled`. It preserves modules, packages, type aliases, overloads, and primitive nullability and supports module/package flattening.

It requires direct Xcode integration: replace the `embedAndSignAppleFrameworkForXcode` build-phase task with:

```shell
./gradlew :shared:embedSwiftExportForXcode
```

The `swiftExport` Gradle block controls the root module and exported dependency module names. `flattenPackage` removes a Kotlin package prefix; `configure` forwards compiler arguments to link tasks. The build places generated Swift modules, a static `.a` library, a header, and a module map in the app build directory.

```kotlin
kotlin {
    swiftExport {
        moduleName = "Shared"
        flattenPackage = "com.example.shared"

        export(project(":subproject")) {
            moduleName = "Subproject"
            flattenPackage = "com.example.subproject"
        }

        configure {
            freeCompilerArgs.add("-Xexpect-actual-classes")
        }
    }
}
```

When an exported dependency uses opt-in declarations, add the opt-in to the Kotlin module's `compilerOptions`, outside the dependency's `export` block:

```kotlin
kotlin {
    swiftExport {
        export("org.jetbrains.kotlinx:kotlinx-datetime:0.7.1") {
            moduleName = "KotlinDateTime"
            flattenPackage = "kotlinx.datetime"
        }
    }
    compilerOptions {
        optIn.add("kotlin.time.ExperimentalTime")
    }
}
```

### Exported shapes and limitations

Only final Kotlin classes that directly inherit from `Any` are supported. Swift cannot subclass exported Kotlin classes or interfaces. Generic parameters are erased to upper bounds; generic types and `suspend`, `inline`, or `operator` functions have limited support. Kotlin functional types cannot be exported, and collection inheritors may be omitted or unusable from Swift, although Swift closures can be passed into Kotlin.

A Kotlin `object` becomes a `KotlinBase` subclass with a private initializer and static `shared` property. Packages become nested Swift enums, and an extension function's receiver becomes its first ordinary Swift parameter. Kotlin `Int` maps to Swift `Int32`, `Char` to `Unicode.UTF16.CodeUnit`, `Any` to `KotlinRuntime.KotlinBase`, and `Nothing` to `Never`.

Swift export maps Kotlin enums to native Swift enums and Kotlin `vararg` parameters to Swift variadic parameters. Generic element types in variadic parameters are not yet supported.

## Patch-sensitive Native fixes

Kotlin 2.3.21 fixes undefined symbols when linking iOS targets against Objective-C frameworks added through Swift Package Manager. It also repairs `TypeCastException` for Objective-C protocol metaclasses with `genericSafeCasts` and for the block parameter of `nw_parameters_create_secure_tcp`.

## Multiplatform IDE host support

The Kotlin Multiplatform IDE plugin supports Windows and Linux, so supported development hosts are no longer limited to the earlier platform set.
