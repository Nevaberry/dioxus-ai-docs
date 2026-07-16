# JVM and build tooling

## Kotlin Gradle plugin migrations

### Removed and replaced APIs

`KotlinCompileTool.setSource()` has conventional replacement semantics rather than appending to existing sources. Gradle plugins that intend to add inputs must call `source()`.

Replace `BaseKapt.annotationProcessorOptionProviders` with `annotationProcessorOptionsProviders`, a `ListProperty<CommandLineArgumentProvider>`, and use `addAll()` rather than adding a list as one element. Move additional resources from the erroring `KotlinCompilationOutput.resourcesDirProvider` to `KotlinSourceSet.resources`.

Kotlin 2.2 removes `KotlinCompilation.source`, target presets and `fromPreset`, obsolete disambiguation-classifier properties, and the legacy metadata options `isCompatibilityMetadataVariantEnabled`, `withGranularMetadata`, and `isKotlinGranularMetadataEnabled`. It also removes `kotlin.incremental.useClasspathSnapshot`; classpath-based incremental compilation has been the default since 1.8.20.

`KotlinCompile.classpathSnapshotProperties.useClasspathSnapshot` and `.classpath` are removed. The opt-outs `kotlin.compiler.preciseCompilationResultsBackup` and `kotlin.compiler.keepIncrementalCompilationCachesInMemory` are also removed now that precise backup is fixed behavior.

`ExtrasProperty` is internal; use Gradle's `ExtraPropertiesExtension`. Move dependency APIs exposed through `HasKotlinDependencies` to `KotlinSourceSet`. `CleanableStore`, `CleanDataTask`, and `LanguageSettings.enableLanguageFeature` are deprecated in 2.3.20.

Gradle plugins and build logic should register generated Kotlin through `KotlinSourceSet.generatedKotlin`. Read `allKotlinSources` instead of `kotlin` when all generated and ordinary sources are required.

### Removed properties and fixed modes

Applying `kotlin-android-extensions` is a configuration error. The obsolete `kotlin.incremental.classpath.snapshot.enabled` property is removed.

`kotlin.mpp.resourcesResolutionStrategy` is removed, and the old IDE-import switch `kotlin.mpp.import.enableKgpDependencyResolution=false` is deprecated. In 2.3.20, `kotlin.kmp.isolated-projects.support`, `kotlin.mpp.enableKotlinToolingMetadataArtifact`, and `kotlin.publishJvmEnvironmentAttribute` are deprecated because isolated-project support is the only mode, tooling metadata is always generated, and the JVM environment attribute is published conventionally.

Gradle Groovy scripts receive notice that Boolean `is-` properties are headed for deprecation.

### Warning mode

KGP warnings obey Gradle `--warning-mode`: `fail` promotes them to errors and `none` hides them. Set `kotlin.internal.diagnostics.ignoreWarningMode=true` only when KGP diagnostics must ignore the global setting.

## Gradle and Android compatibility

### Gradle versions and Isolated Projects

Kotlin 2.1.20 is generally compatible with Gradle 7.6.3 through 8.11. Kotlin 2.1.21 is required for Gradle 8.12, so upgrade Kotlin before moving a build from Gradle 8.11 to 8.12.

Kotlin Gradle plugins need no Kotlin-specific setup for Gradle Isolated Projects. The initial pre-Alpha support requires Gradle 8.10 or newer, excludes JS and Wasm targets, and can be disabled for a multiplatform build with `kotlin.kmp.isolated-projects.support=disable`. That opt-out is deprecated in 2.3.20 because isolated-project support is then the only mode.

Kotlin 2.3.0 is fully compatible with Gradle 7.6.3 through 9.0.0. Kotlin 2.3.20 extends full compatibility through Gradle 9.3.0; later Gradle releases may work with deprecation warnings or unavailable features.

Kotlin 2.2.21 restores `compileKotlin` with Gradle's configuration cache, makes KGP publication helpers compatible with Isolated Projects, and prevents GnuPG signing from breaking configuration-cache use.

### Android Gradle plugin 9

The supported Android Gradle plugin range for Kotlin 2.3.0 is 8.2.2 through 8.13.0. AGP 9 has built-in Kotlin support, so Android projects should stop applying `org.jetbrains.kotlin.android`.

Multiplatform Android targets should migrate to `com.android.kotlin.multiplatform.library` and rename `androidTarget {}` to `android {}`. Keeping the old setup triggers migration diagnostics or configuration errors under AGP 9. Kotlin 2.3.10 reverts the `androidTarget` deprecation for projects using older AGP versions, where the old target remains valid.

### Kotlin DSL plugin versions

Applying both `kotlin-dsl` and an independently versioned `kotlin("jvm")` plugin is unsupported and can produce a version diagnostic. Let `kotlin-dsl` supply KGP, use Gradle's `embeddedKotlinVersion`, or omit `kotlin-dsl` for an independently versioned binary plugin.

## kapt, Lombok, and Java integration

### K2 kapt default

Kotlin 2.1.20 enables the Beta K2 implementation of kapt by default for all projects. If a regression remains, temporarily restore the old implementation in `gradle.properties`:

```properties
kapt.use.k2=false
```

Kotlin 2.2.10 fixes K2 kapt fake-override backend failures and unresolved `@kotlin.Metadata` in generated Java stubs.

### Lombok builders

The Experimental Kotlin Lombok compiler plugin understands Lombok's `@SuperBuilder` for class hierarchies and permits `@Builder` on constructors.

## Build Tools API

### Gradle compiler path

The initial Experimental, JVM-only Build Tools API opt-in used `kotlin.compiler.runViaBuildToolsApi=true`. It made the `in-process` execution strategy incremental and allowed a compiler version different from the plugin version:

```kotlin
kotlin {
    @OptIn(
        org.jetbrains.kotlin.buildtools.api.ExperimentalBuildToolsApi::class,
        org.jetbrains.kotlin.gradle.ExperimentalKotlinGradlePluginApi::class,
    )
    compilerVersion.set("2.1.21")
}
```

Compiler plugins may not tolerate mixed compiler and plugin versions. The API at that stage was not ready for third-party build-tool integrations.

Kotlin/JVM compilation through KGP now uses the Build Tools API by default, replacing the previous internal path. Kotlin 2.3.20 deprecates the slow `out-of-process` execution strategy, which the API does not support; use daemon or in-process compilation.

### Operation model and integrations

Operations implementing `CancellableBuildOperation` support best-effort cancellation through `cancel()`, reported as `OperationCancelledException`. Configure an operation through its mutable builder and call `build()` before execution to prevent changes after it starts.

Attach a `BuildMetricsCollector` through `BuildOperation.METRICS_COLLECTOR`. It receives a build-tool-independent metric set across execution strategies, with strategy-specific values only when applicable.

Configure compiler plugins as configuration objects through `kotlin.buildtools.api.arguments.CommonCompilerArguments.COMPILER_PLUGINS` rather than constructing experimental command-line options.

### Compiler option schema

`org.jetbrains.kotlin:kotlin-compiler-arguments-description` publishes a common code model and JSON description of compiler options, including descriptions and introduction or stabilization versions, for IDE and build-tool integrations.

## Maven builds

### Daemon and incremental compilation

`kotlin-maven-plugin` uses the Kotlin daemon by default. Set `kotlin.compiler.daemon=false` to restore in-process compilation, or configure comma-separated JVM options without leading dashes through `kotlin.compiler.daemon.jvmArgs`:

```xml
<properties>
  <kotlin.compiler.daemon.jvmArgs>Xmx1500m,Xms500m</kotlin.compiler.daemon.jvmArgs>
</properties>
```

Kotlin Maven plugin 2.2.21 restores Java-class resolution when incremental compilation is enabled and the daemon is disabled; the combination is broken in 2.2.20.

### Smart defaults

Setting the Kotlin Maven plugin as a build extension registers existing `src/main/kotlin` and `src/test/kotlin` roots and supplies `kotlin-stdlib` when it is not declared:

```xml
<plugin>
  <groupId>org.jetbrains.kotlin</groupId>
  <artifactId>kotlin-maven-plugin</artifactId>
  <version>2.3.20</version>
  <extensions>true</extensions>
</plugin>
```

Set `<kotlin.smart.defaults.enabled>false</kotlin.smart.defaults.enabled>` in project properties to disable both behaviors.

Maven uses the Build Tools API by default. `KotlinScriptMojo` is deprecated; scripting compatibility details are in [language-and-compiler.md](language-and-compiler.md).

## Publication and variants

### Custom publication variants

JVM and multiplatform projects can opt in and add, but not modify, publication variants through `adhocSoftwareComponent()`:

```kotlin
kotlin {
    @OptIn(ExperimentalKotlinGradlePluginApi::class)
    publishing {
        adhocSoftwareComponent { /* configure custom variants */ }
    }
}
```

KGP supports `JAVA_API` and `JAVA_RUNTIME` values for the `org.gradle.usage` attribute, so variants published with those values participate in dependency resolution.

Kotlin 2.1.21 corrects the generated POM `artifactId` when a Maven publication customizes `pom.withXml`.

### Maven Central helpers

KGP adds `generatePgpKeys` and `uploadPublicPgpKey`, plus `checkSigningConfiguration` and `checkPomFileFor<PublicationName>Publication`. Verification checks configured and uploaded signing keys, signed publications, and required POM metadata, but is not wired into `build` or `check` automatically.

```shell
./gradlew -Psigning.password=secret generatePgpKeys --name "Name <name@example.com>"
./gradlew checkSigningConfiguration checkPomFileForKotlinMultiplatformPublication
```

Generated keys initially land in `build/pgp` and should be moved to secure storage.

## ABI validation

The initial Experimental KGP ABI validation generated and compared JVM or KLIB ABI dumps after `abiValidation { enabled.set(true) }`. It used `checkLegacyAbi` to validate and `updateLegacyAbi` to accept a new dump, required per-module configuration, and was not yet recommended for production.

KGP renames `checkLegacyAbi` to `checkKotlinAbi`, `updateLegacyAbi` to `updateKotlinAbi`, and `dumpLegacyAbi` to `internalDumpKotlinAbi`, retaining old aliases during 2.3.20. Enabling ABI validation now wires `checkKotlinAbi` into Gradle's `check` task.

## Tests, tasks, and extensibility

`testApi` is deprecated because Gradle cannot expose tests between modules. Replace it and source-set `dependencies.api()` calls with `testImplementation` or `implementation`, using JVM test fixtures when appropriate. `KotlinJsTestFramework.createTestExecutionSpec()` is an error.

The unused `closureTo()` and `createResultSet()` helpers are removed, and `KotlinToolingVersionOrNull()` becomes `KotlinToolingVersion()`. Kotlin test tasks and JavaScript runtime/setup classes such as `KotlinJsTest`, `KotlinKarma`, `KotlinWebpack`, and `YarnRootExtension` cannot be subclassed; configure them through the plugin DSL.

Java source sets are created automatically for multiplatform JVM targets as `withJava()` is phased out. Projects using Gradle Java test fixtures should upgrade directly to Kotlin 2.1.21. Kotlin 2.2.10 also fixes JVM test-fixture dependency configurations such as `testFixturesApi` so they affect `jvmTestFixtures` in a multiplatform build.

## JVM executables in multiplatform builds

Gradle's Application plugin is incompatible with the Kotlin Multiplatform plugin starting with Gradle 8.7. The Experimental replacement creates JVM execution tasks and distributions through `binaries.executable`:

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

## Removed legacy tooling

Ant support is deprecated for removal in Kotlin 2.3. The legacy JS-backend `KotlinJsDce`, `dceTask`, and related compiler-option DSLs are removed; the current JS IR backend performs DCE itself and uses `@JsExport` to retain exported APIs.
