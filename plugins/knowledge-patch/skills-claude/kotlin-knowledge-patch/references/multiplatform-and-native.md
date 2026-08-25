# Multiplatform and Native

## Source sets, targets, and publication

Replace the removed `ios()`, `watchos()`, and `tvos()` target shortcuts with concrete targets such as `iosArm64()` and let the default hierarchy template create shared source sets.

When both `js()` and `wasmJs()` are declared, the default hierarchy places `webMain` and `webTest` above them. Call `applyDefaultHierarchyTemplate()` and first rename any custom `webMain`/`webTest` source sets or a target declared as `js("web")` that would collide.

```kotlin
kotlin {
    js()
    wasmJs()
    applyDefaultHierarchyTemplate()
}
```

Supported hosts can cross-compile publishable KLIBs for all Native targets, so `kotlin.native.enableKlibsCrossCompilation=true` is obsolete. A Mac is still required for cinterop or CocoaPods dependencies and for final Apple binaries and Apple tests.

Kotlin-to-Java direct actualization is an experimental multiplatform preview available since Kotlin 2.1.0. Account for pre-stable compatibility in libraries that adopt it.

Multiplatform metadata dependency matching is stricter in 2.3.20. If metadata compilation starts failing, compare the dependencies resolved in common and platform source sets.

## Apple toolchains and deployment support

- Xcode 16.3 support, including its cinterop compilation fix, requires Kotlin 2.1.21 rather than 2.1.20.
- Xcode 26 support begins with Kotlin 2.2.21 rather than 2.2.20.
- `macosX64` and `iosX64` became tier 2 in 2.2.20. All Apple x86-64 targets moved to tier 3 by Kotlin 2.3 and are being phased out.
- Kotlin 2.3 raises supported deployment baselines to iOS/tvOS 14 and watchOS 7. A `-Xoverride-konan-properties=minVersion.<target>=...` override may request an older version, but that output is unsupported and can fail during the build or at runtime.

Kotlin 2.2.10 fixes an Xcode 16.3/iOS 15.5-simulator linker failure and Apple Watch `SIGABRT` crashes. Kotlin 2.2.21 repairs broken Parcelize support in multiplatform projects and native cinterop commonization failures involving missing `kotlinNativeBundleConfiguration`, unresolved POSIX `size_t`, and imports from commonized test cinterops. Upgrade instead of preserving workarounds for those regressions.

Kotlin 2.3.21 fixes undefined symbols when an iOS target links Objective-C frameworks supplied through Swift Package Manager. It also fixes `TypeCastException` for Objective-C protocol metaclasses with `genericSafeCasts` and for the block parameter of `nw_parameters_create_secure_tcp`.

Kotlin 2.4.10 fixes `IrTypeAliasSymbolImpl is already bound` for `kotlinx.datetime.Instant` when building `iosSimulatorArm64`.

## Native compiler and Gradle APIs

`CInteropProcess.konanVersion` and `destinationDir` are errors; use `kotlinNativeVersion` and `destinationDirectory.set(...)`. The experimental `kotlinArtifacts` API is deprecated in favor of the Native binaries DSL.

The old `konan/lib/kotlin-native.jar` is no longer published. Remove `kotlin.native.useEmbeddableCompilerJar=false`; the embeddable compiler JAR is always used. Compiler plugins should replace `getPluginArtifactForNative()` with `getPluginArtifact()`.

Remove `kotlin.mpp.enableOptimisticNumberCommonization` and `kotlin.mpp.enablePlatformIntegerCommonization`; Kotlin 2.2 rejects them, and they may have produced invalid cached commonized artifacts. Then run:

```shell
./gradlew cleanNativeDistributionCommonization
```

If necessary, clear the matching commonized KLIB cache beneath the Kotlin/Native user cache.

Replace deprecated global `kotlin.native.cacheKind` with a version-scoped workaround on the affected binary. Supply the Kotlin version, reason, and optionally an issue URI:

```kotlin
framework {
    disableNativeCache(
        version = DisableCacheInKotlinVersion.2_3_0,
        reason = "Cache bug",
        issue = java.net.URI("https://youtrack.example/KT-123"),
    )
}
```

For stack-smashing protection, set `kotlin.native.binary.stackProtector=yes` for vulnerable functions, `strong` for broader heuristics, or `all` for every function.

Kotlin/Native raises its Windows baseline from Windows 7 to Windows 10 starting with Kotlin 2.2.

Concurrent Mark and Sweep garbage collection is the default in the Native runtime; no explicit opt-in is needed.

Native exception formatting no longer repeats a cause that has already appeared in the stack trace starting with Kotlin 2.3.20.

## Objective-C export and C interop

KDoc is embedded in KLIBs and exported to Objective-C headers by default. A framework can opt out with `@OptIn(ExperimentalKotlinGradlePluginApi::class) exportKdoc.set(false)`; the old `-Xexport-kdoc` opt-in is unnecessary.

Kotlin function-type parameter names are emitted in Objective-C block types by default in Kotlin 2.3. Before that default, `kotlin.native.binary.objcExportBlockExplicitParameterNames=true` enabled them. Set the property to `false` only for a concrete compatibility requirement.

C and Objective-C library import is Beta, but binary compatibility is not guaranteed across Kotlin, dependency, and Xcode versions. `@ExperimentalForeignApi` remains required for affected `kotlinx.cinterop` APIs and non-platform native-library declarations.

To evaluate the experimental direct-call compatibility mode, add `-Xccall-mode direct` to every cinterop invocation:

```kotlin
targets.withType<org.jetbrains.kotlin.gradle.plugin.mpp.KotlinNativeTarget>().configureEach {
    compilations.configureEach {
        cinterops.configureEach {
            extraOpts += listOf("-Xccall-mode", "direct")
        }
    }
}
```

The mode does not support every declaration. Do not publish libraries built with it while it remains experimental.

## Swift export configuration

Swift export is available without `kotlin.experimental.swift-export.enabled`. It preserves modules, packages, type aliases, overloads, and primitive nullability. Direct Xcode integration is still required: replace `embedAndSignAppleFrameworkForXcode` in the build phase with `./gradlew :shared:embedSwiftExportForXcode`.

The `swiftExport` block sets root and dependency module names. `flattenPackage` removes a package prefix, and `configure` forwards compiler arguments to link tasks. Output includes generated Swift modules, a static `.a` library, a header, and a module map in the app build directory.

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

When an exported dependency needs an opt-in, add it to the Kotlin module's `compilerOptions`, outside its `export` block:

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

Swift export maps Kotlin enums to Swift enums and `vararg` to Swift variadic parameters, except that generic variadic element types are not supported.

## Swift-facing declaration limits

Design the exported API around these constraints:

- Only final Kotlin classes that directly inherit from `Any` are supported; Swift cannot subclass exported Kotlin classes or interfaces.
- Generic parameters are erased to upper bounds. Generic types and `suspend`, `inline`, or `operator` functions have limited support.
- Kotlin functional types cannot be exported, though Swift closures can be passed into Kotlin.
- Collection inheritors may be absent or unusable in Swift.
- A Kotlin `object` becomes a `KotlinBase` subclass with a private initializer and a static `shared` property.
- Kotlin packages become nested Swift enums.
- An extension receiver becomes the first ordinary Swift parameter.
- `Int` maps to `Int32`, `Char` to `Unicode.UTF16.CodeUnit`, `Any` to `KotlinRuntime.KotlinBase`, and `Nothing` to `Never`.

## IDE host support

The Kotlin Multiplatform IDE plugin supports Windows and Linux as development hosts in addition to the earlier supported host set.
