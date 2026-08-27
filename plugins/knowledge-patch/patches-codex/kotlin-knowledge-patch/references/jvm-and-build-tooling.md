# JVM and build tooling

## Kapt, Lombok, and compiler execution (`2.1.20-guide`)

Kotlin 2.1.20 enables the Beta K2 kapt implementation by default. If it regresses, temporarily set `kapt.use.k2=false`. The Kotlin Lombok compiler plugin remains experimental but understands `@SuperBuilder` inheritance and `@Builder` on constructors.

Use typed `annotationProcessorOptionsProviders: ListProperty<CommandLineArgumentProvider>` instead of `BaseKapt.annotationProcessorOptionProviders`, adding providers with `addAll()`. Kotlin 2.2.10 fixes K2 kapt fake-override backend failures and unresolved `@kotlin.Metadata` in generated Java stubs.

Kotlin 2.3.20 deprecates out-of-process compilation, which the Build Tools API does not support. Use the daemon or in-process execution.

## Gradle compatibility and configuration

### Version combinations and patch corrections (`2.1.20`)

Kotlin 2.1.20 supports Gradle 7.6.3 through 8.11; Gradle 8.12 requires Kotlin 2.1.21. Kotlin 2.3.0 supports through Gradle 9.0.0, and 2.3.20 supports through 9.3.0. Later Gradle releases may work with warnings or without their newest features.

Kotlin 2.1.21 restores `commonTest`/`nativeTest` dependency resolution to another multiplatform project and corrects custom `pom.withXml` publication `artifactId` values. Kotlin 2.2.21 restores `compileKotlin` with Gradle's configuration cache, makes publication helpers work with Isolated Projects, and prevents GnuPG signing from breaking configuration-cache use.

KGP recognizes `JAVA_API` and `JAVA_RUNTIME` as `org.gradle.usage` values. Gradle Groovy DSL users are warned that Boolean `is-` properties are headed for deprecation.

### Isolated Projects and multiplatform execution

Kotlin 2.1.20's pre-Alpha Isolated Projects support requires Gradle 8.10+, excludes JS/Wasm, and needs no Kotlin-specific setup beyond Gradle's system property. It may be disabled in a multiplatform build with `kotlin.kmp.isolated-projects.support=disable`. By 2.3.20 isolated-project support is the sole mode and that property is deprecated.

The Gradle Application plugin is incompatible with KMP from Gradle 8.7. Create JVM execution tasks/distributions with the experimental `binaries.executable` DSL:

```kotlin
kotlin {
    jvm {
        @OptIn(ExperimentalKotlinGradlePluginApi::class)
        binaries { executable { mainClass.set("foo.MainKt") } }
    }
}
```

### Custom publication variants and signing

JVM and multiplatform projects can add, but not modify, publication variants with experimental `adhocSoftwareComponent()`.

KGP supplies `generatePgpKeys`, `uploadPublicPgpKey`, `checkSigningConfiguration`, and `checkPomFileFor<PublicationName>Publication`. The checks validate keys, signatures, and required POM metadata but are not wired into `build` or `check`. Generated keys initially appear in `build/pgp`; move them to secure storage.

## Kotlin Gradle plugin API migrations

### Source and resource APIs

`KotlinCompileTool.setSource()` now replaces its inputs. Plugins adding inputs must call `source()`. Register generated Kotlin through `KotlinSourceSet.generatedKotlin`, and read `allKotlinSources` to include generated and ordinary sources.

Move additional resources from removed/erroring `KotlinCompilationOutput.resourcesDirProvider` to `KotlinSourceSet.resources`.

### Removed and internal APIs

Kotlin 2.2 removes `KotlinCompilation.source`, target presets and `fromPreset`, disambiguation-classifier properties, the metadata options `isCompatibilityMetadataVariantEnabled`, `withGranularMetadata`, and `isKotlinGranularMetadataEnabled`, and `kotlin.incremental.useClasspathSnapshot`.

In Kotlin 2.3, use Gradle `ExtraPropertiesExtension` instead of internal `ExtrasProperty`; move `HasKotlinDependencies` helpers to `KotlinSourceSet`. `CleanableStore`, `CleanDataTask`, and `LanguageSettings.enableLanguageFeature` are deprecated in 2.3.20.

Do not subclass Kotlin test tasks or JavaScript runtime/setup classes such as `KotlinJsTest`, `KotlinKarma`, `KotlinWebpack`, or `YarnRootExtension`; configure them with supported DSLs. The unused `closureTo()` and `createResultSet()` helpers are gone, and `KotlinToolingVersionOrNull()` becomes `KotlinToolingVersion()`.

Use `compilerOptions`, not properties under legacy `kotlinOptions`. Removed incremental switches include `KotlinCompile.classpathSnapshotProperties.useClasspathSnapshot`, `.classpath`, `kotlin.compiler.preciseCompilationResultsBackup`, and `kotlin.compiler.keepIncrementalCompilationCachesInMemory`.

### Property cleanup

Remove `kotlin.incremental.classpath.snapshot.enabled`, `kotlin.mpp.resourcesResolutionStrategy`, and the old incremental switches. The IDE-import escape hatch `kotlin.mpp.import.enableKgpDependencyResolution=false` is deprecated. In 2.3.20, `kotlin.mpp.enableKotlinToolingMetadataArtifact` and `kotlin.publishJvmEnvironmentAttribute` are deprecated because their behavior is now conventional.

Java source sets are automatically created for KMP JVM targets as `withJava()` is phased out. Applying `kotlin-android-extensions` is a configuration error. If Gradle Java test fixtures are involved, upgrade Kotlin 2.1.20 projects directly to 2.1.21.

## Android, JVM, and test configuration

Kotlin 2.3.0 supports Android Gradle plugin 8.2.2 through 8.13.0. AGP 9 supplies built-in Kotlin, so stop applying `org.jetbrains.kotlin.android`. KMP Android libraries should apply `com.android.kotlin.multiplatform.library` and use `android {}`. On older AGP lines, Kotlin 2.3.10 keeps `androidTarget {}` valid.

Applying `kotlin-dsl` together with independently versioned `kotlin("jvm")` is unsupported. Let `kotlin-dsl` supply KGP, use Gradle's `embeddedKotlinVersion`, or omit `kotlin-dsl` for a separately versioned binary plugin.

Replace deprecated `testApi` and test source-set `dependencies.api()` with `testImplementation` or `implementation`; use JVM test fixtures to expose test support. `KotlinJsTestFramework.createTestExecutionSpec()` is an error.

Kotlin 2.2.10 makes JVM test-fixture configurations such as `testFixturesApi` affect KMP `jvmTestFixtures` correctly.

## Build Tools API

Kotlin/JVM Gradle compilation uses the Build Tools API by default from Kotlin 2.3.20. Earlier experimental KGP use set `kotlin.compiler.runViaBuildToolsApi=true`; it made in-process compilation incremental and allowed a compiler version different from KGP, although compiler plugins might not tolerate that mix.

Build operations expose a mutable builder whose `build()` result is immutable. `CancellableBuildOperation.cancel()` performs best-effort cancellation reported as `OperationCancelledException`. Attach a `BuildMetricsCollector` via `BuildOperation.METRICS_COLLECTOR` for consistent cross-strategy metrics, and configure compiler plugins through `kotlin.buildtools.api.arguments.CommonCompilerArguments.COMPILER_PLUGINS` objects rather than experimental command-line assembly.

Maven already used the Build Tools API by default in Kotlin 2.2. The API at that point was not ready for third-party build-tool integrations.

`org.jetbrains.kotlin:kotlin-compiler-arguments-description` publishes a common model and JSON schema of compiler options with descriptions and introduction/stabilization versions.

## Maven builds

The Kotlin Maven plugin uses the daemon by default. Set `kotlin.compiler.daemon=false` for in-process compilation; configure comma-separated JVM options without leading dashes through `kotlin.compiler.daemon.jvmArgs`.

As a build extension, `kotlin-maven-plugin` registers `src/main/kotlin` and `src/test/kotlin` and adds `kotlin-stdlib` when absent. Set `<kotlin.smart.defaults.enabled>false</kotlin.smart.defaults.enabled>` to disable both. Kotlin Maven 2.2.21 repairs Java-class resolution when incremental compilation is enabled and the daemon is disabled.

## ABI and binary compatibility validation

Experimental KGP ABI validation originally used per-module `abiValidation { enabled.set(true) }` with `checkLegacyAbi` and `updateLegacyAbi`. Current task names are `checkKotlinAbi`, `updateKotlinAbi`, and internal `internalDumpKotlinAbi`, replacing `checkLegacyAbi`, `updateLegacyAbi`, and `dumpLegacyAbi`; 2.3.20 retains old aliases and wires `checkKotlinAbi` into `check`.

Kotlin 2.4.10 fixes `kotlinAbiValidationCompatClasspath` resolving a future `kotlin-build-tools-impl` prerelease through an open range, keeping binary validation on the intended compatible implementation.

## Patch-level build repairs (`2.2.0`)

Prefer a patch upgrade over source workarounds for these known repairs:

- Kotlin 2.2.10 fixes Android dexing null-field failures, duplicate `DebugMetadata` on JVM-default suspend methods, an Xcode 16.3/iOS 15.5-simulator linker failure, and Apple Watch `SIGABRT` crashes.
- It repairs unusable npm build-cache entries from 2.2 release candidates and Node tests unable to load `mocha`.
- Kotlin 2.2.21 fixes Parcelize in KMP and cinterop commonization failures involving `kotlinNativeBundleConfiguration`, POSIX `size_t`, or commonized test-cinterop imports.
- Compose metrics/reports use target-specific directories and source information regains parameter names in 2.2.10.

## Kotlin distribution command

Kotlin 2.4.10 includes the `kotlinr` command in the distribution; no separate tool package is needed for installations of that release.
