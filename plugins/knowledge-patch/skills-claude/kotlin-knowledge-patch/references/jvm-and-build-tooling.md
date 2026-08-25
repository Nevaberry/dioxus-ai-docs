# JVM and build tooling

This reference incorporates build migrations and patch diagnostics from `2.1.20-guide`, `2.1.20`, `2.2-language-guide`, `2.2-tooling-guide`, `2.2.0`, `2.3-language-guide`, `2.3-tooling-guide`, `2.3.0`, and `2.4.10`.

## Compatibility checkpoints

- Kotlin 2.1.20 is generally compatible with Gradle 7.6.3 through 8.11. Upgrade to Kotlin 2.1.21 before moving to Gradle 8.12.
- Kotlin 2.3.0 supports Gradle 7.6.3 through 9.0.0 and Android Gradle plugin 8.2.2 through 8.13.0.
- Kotlin 2.3.20 supports Gradle 7.6.3 through 9.3.0. Later Gradle versions may run with deprecation warnings or without support for their newest features.
- Xcode and Native compatibility are version-specific; consult the Native reference rather than assuming Gradle compatibility implies toolchain compatibility.

## Kapt, Lombok, and generated sources

K2 kapt is the default implementation starting with Kotlin 2.1.20. If it causes a regression that cannot be avoided, temporarily select the old implementation:

```properties
kapt.use.k2=false
```

Kotlin 2.2.10 fixes K2 kapt fake-override backend failures and unresolved `@kotlin.Metadata` in generated Java stubs. Prefer upgrading before disabling K2 kapt.

Replace `BaseKapt.annotationProcessorOptionProviders` with the typed `annotationProcessorOptionsProviders`, a `ListProperty<CommandLineArgumentProvider>`. Add a collection with `addAll()` rather than adding the list as a single element.

The experimental Kotlin Lombok plugin understands Lombok `@SuperBuilder` across class hierarchies and accepts `@Builder` on constructors.

Build logic should register generated Kotlin with `KotlinSourceSet.generatedKotlin`. Read `allKotlinSources`, not `kotlin`, when both generated and ordinary sources are needed. Put generated resources on `KotlinSourceSet.resources`; `KotlinCompilationOutput.resourcesDirProvider` is an error.

`KotlinCompileTool.setSource()` now replaces the compile inputs. Call `source()` when a plugin means to append inputs.

## Android and JVM targets

### AGP 9 migration

AGP 9 provides built-in Kotlin support. Do not apply `org.jetbrains.kotlin.android`. A multiplatform Android library should apply `com.android.kotlin.multiplatform.library` and use `android {}` instead of `androidTarget {}`. The old form triggers migration diagnostics or configuration errors on AGP 9.

Kotlin 2.3.10 deliberately restored `androidTarget` for older AGP lines, so do not rename it until the project actually migrates to AGP 9.

### JVM executables in multiplatform builds

Gradle's Application plugin is incompatible with Kotlin Multiplatform starting with Gradle 8.7. Use the experimental JVM executable DSL to create run tasks and distributions:

```kotlin
kotlin {
    jvm {
        @OptIn(ExperimentalKotlinGradlePluginApi::class)
        binaries {
            executable { mainClass.set("foo.MainKt") }
        }
    }
}
```

Java source sets are created automatically for multiplatform JVM targets while `withJava()` is phased out. Projects using Gradle Java test fixtures should upgrade directly to Kotlin 2.1.21. Kotlin 2.2.10 makes `testFixturesApi` and related JVM fixture configurations affect the multiplatform `jvmTestFixtures` source set correctly.

`testApi` is deprecated because Gradle cannot expose tests between modules. Replace it and source-set `dependencies.api()` calls with `testImplementation` or `implementation`, using JVM test fixtures where appropriate.

## Plugin and DSL API migrations

Remove or replace these APIs and behaviors:

- `KotlinCompilation.source`, target presets, `fromPreset`, obsolete disambiguation-classifier properties, `isCompatibilityMetadataVariantEnabled`, `withGranularMetadata`, and `isKotlinGranularMetadataEnabled` are removed.
- `KotlinCompile.classpathSnapshotProperties.useClasspathSnapshot` and `.classpath` are removed. So are `kotlin.incremental.useClasspathSnapshot` and the older `kotlin.incremental.classpath.snapshot.enabled` property.
- `kotlin.compiler.preciseCompilationResultsBackup` and `kotlin.compiler.keepIncrementalCompilationCachesInMemory` are removed because precise backup is fixed behavior.
- `ExtrasProperty` is internal; use Gradle's `ExtraPropertiesExtension`.
- Move dependency helpers from `HasKotlinDependencies` to `KotlinSourceSet`.
- `CleanableStore`, `CleanDataTask`, and `LanguageSettings.enableLanguageFeature` are deprecated in 2.3.20.
- `KotlinToolingVersionOrNull()` is replaced by `KotlinToolingVersion()`; unused `closureTo()` and `createResultSet()` helpers are gone.
- Do not subclass `KotlinJsTest`, `KotlinKarma`, `KotlinWebpack`, Yarn setup, or other Kotlin test/runtime setup classes. Configure the plugin DSL.
- `KotlinJsTestFramework.createTestExecutionSpec()` is an error.

Applying both `kotlin-dsl` and an independently versioned `kotlin("jvm")` plugin is unsupported and can produce a version diagnostic. Let `kotlin-dsl` provide KGP, use Gradle's `embeddedKotlinVersion`, or omit `kotlin-dsl` for an independently versioned binary plugin.

The obsolete `kotlin-android-extensions` plugin is a configuration error. Ant support was deprecated for removal in Kotlin 2.3.

KGP warnings now follow Gradle `--warning-mode`: `fail` promotes them to errors and `none` suppresses them. Set `kotlin.internal.diagnostics.ignoreWarningMode=true` only when KGP diagnostics must intentionally ignore the global setting.

Groovy DSL scripts now warn that Boolean `is-` properties are headed for deprecation.

## Multiplatform build properties and resolution

Remove `kotlin.mpp.resourcesResolutionStrategy`. The IDE-import escape hatch `kotlin.mpp.import.enableKgpDependencyResolution=false` is deprecated.

In 2.3.20, these properties are deprecated because their enabled behavior is now unconditional:

- `kotlin.kmp.isolated-projects.support`
- `kotlin.mpp.enableKotlinToolingMetadataArtifact`
- `kotlin.publishJvmEnvironmentAttribute`

Earlier 2.1.20 builds had pre-Alpha Isolated Projects support on Gradle 8.10 or newer, excluding JS and Wasm, and allowed disabling it with `kotlin.kmp.isolated-projects.support=disable`. Current builds need no Kotlin-specific setup.

Kotlin 2.1.21 restores dependencies from `commonTest` or `nativeTest` to another multiplatform project and corrects a custom Maven publication's generated POM `artifactId` when `pom.withXml` is used.

KGP recognizes both `JAVA_API` and `JAVA_RUNTIME` for the `org.gradle.usage` attribute, so custom variants carrying those values can resolve.

On Gradle 8.8 or newer, an experimental top-level `kotlin.dependencies` block adds common dependencies as if declared in `commonMain`:

```kotlin
kotlin {
    @OptIn(ExperimentalKotlinGradlePluginApi::class)
    dependencies { implementation("org.example:library:1.0") }
}
```

Stricter multiplatform matching in 2.3.20 can fail metadata compilation when common and platform source sets resolve different dependency graphs. Compare those resolutions before treating it as a compiler failure.

## Publishing and ABI validation

JVM and multiplatform projects can opt into additional publication variants with `adhocSoftwareComponent()`. Variants may be added but existing variants cannot be modified:

```kotlin
kotlin {
    @OptIn(ExperimentalKotlinGradlePluginApi::class)
    publishing {
        adhocSoftwareComponent { /* add variants */ }
    }
}
```

KGP provides `generatePgpKeys`, `uploadPublicPgpKey`, `checkSigningConfiguration`, and `checkPomFileFor<PublicationName>Publication`. The checks cover configured and uploaded signing keys, signatures, and required POM metadata, but are not wired into `build` or `check`. Generated keys initially appear in `build/pgp`; move them to secure storage.

```shell
./gradlew -Psigning.password=secret generatePgpKeys --name "Name <name@example.com>"
./gradlew checkSigningConfiguration checkPomFileForKotlinMultiplatformPublication
```

Enable JVM or KLIB ABI dumps with `abiValidation { enabled.set(true) }`. Early versions used `checkLegacyAbi`, `updateLegacyAbi`, and `dumpLegacyAbi`; current task names are `checkKotlinAbi`, `updateKotlinAbi`, and internal `internalDumpKotlinAbi`. The old aliases remain temporarily, and validation now adds `checkKotlinAbi` to Gradle's `check` lifecycle.

Kotlin 2.4.10 fixes the `kotlinAbiValidationCompatClasspath` dependency range so it does not accidentally resolve `kotlin-build-tools-impl` 2.4.20-Beta1 for a 2.4.0-compatible validation run.

## Build Tools API

Kotlin/JVM Gradle compilation uses the Build Tools API by default in 2.3.20. The earlier opt-in, `kotlin.compiler.runViaBuildToolsApi=true`, made in-process execution incremental and allowed a compiler version distinct from KGP through `compilerVersion`. Compiler plugins may not tolerate mixed versions.

The out-of-process strategy is deprecated in 2.3.20 and unsupported by the API; use daemon or in-process compilation.

Integrations can:

- Configure a mutable operation builder and call `build()` to obtain an immutable operation before execution.
- Implement `CancellableBuildOperation` and use best-effort `cancel()`, receiving `OperationCancelledException` when cancellation succeeds.
- Attach `BuildMetricsCollector` through `BuildOperation.METRICS_COLLECTOR` for a common metric set plus applicable strategy-specific values.
- Supply compiler-plugin configuration objects through `kotlin.buildtools.api.arguments.CommonCompilerArguments.COMPILER_PLUGINS` instead of constructing experimental command-line options.

The `org.jetbrains.kotlin:kotlin-compiler-arguments-description` artifact publishes a common code model and JSON schema for compiler options, including descriptions and introduction or stabilization versions.

## Maven behavior

The Kotlin Maven plugin uses the Kotlin daemon by default. Set `kotlin.compiler.daemon=false` for in-process compilation. Configure comma-separated daemon JVM options without leading dashes through `kotlin.compiler.daemon.jvmArgs`.

```xml
<properties>
  <kotlin.compiler.daemon.jvmArgs>Xmx1500m,Xms500m</kotlin.compiler.daemon.jvmArgs>
</properties>
```

Kotlin Maven 2.2.21 restores Java-class resolution when incremental compilation is enabled and the daemon is disabled; that combination is broken in 2.2.20.

When `kotlin-maven-plugin` is a build extension, it registers existing `src/main/kotlin` and `src/test/kotlin` roots and adds `kotlin-stdlib` if absent. Set `kotlin.smart.defaults.enabled=false` to disable both behaviors.

## Patch-upgrade diagnostics

Upgrade to Kotlin 2.2.10 rather than writing source workarounds for Android dexing null-field failures, duplicate `DebugMetadata` on JVM-default suspend interface methods, the Xcode 16.3/iOS 15.5 simulator linker failure, or Apple Watch `SIGABRT` crashes.

Kotlin 2.2.21 restores Gradle configuration-cache compilation, makes publication helpers compatible with Isolated Projects, and prevents GnuPG signing from breaking configuration-cache use. It also removes the erroneous `NON_PUBLIC_CALL_FROM_PUBLIC_INLINE` diagnostic for `@PublishedApi` fun interfaces.

Kotlin 2.3.21 repairs common `@JvmRecord` metadata compilation and compiler-plugin generated top-level declarations during Kotlin/JS incremental compilation; see the language and JS references for the related fixes.
