# Gradle 9 Upgrade

Use this reference before changing a wrapper from Gradle 8 to Gradle 9. The migration notes in the `9.0.0-upgrade` batch are breaking-change guidance; the `9.0.0` notes describe behavior available after the upgrade.

## Runtime and language baselines

### Daemon JVM

The Gradle 9 daemon requires JVM 17 or newer. Compilation, tests, and workers may still target older JVMs through toolchains. The wrapper and command-line launcher, Tooling API, and TestKit can launch on JVM 8 only if they can locate a JVM 17+ daemon.

### Kotlin DSL

Gradle embeds Kotlin 2.2.0 and uses Kotlin language version 2.2 for scripts, build logic, and plugins. Kotlin language versions 1.4 through 1.7 are unsupported. Script-instance labels such as `this@Build_gradle` no longer compile; use `project`, `settings`, or `gradle` as appropriate.

### Groovy 4

Gradle embeds Groovy 4.0.27. Account for Groovy's package and module changes and its delegate-first dynamic lookup order. Groovy plugins may need recompilation:

- Groovy 3-compiled code can fail to resolve `super` calls.
- Dynamically compiled closures inherited from a parent can lose access to the parent's private members; `@CompileStatic` avoids this lookup problem.

## Plugin compatibility floors

- Kotlin DSL plugins built with Gradle 9 require Gradle 8.11+ unless explicitly compiled against Kotlin 1.x.
- Groovy DSL plugins built with Gradle 9 require Gradle 7.0+.
- Supported floors are Kotlin Gradle Plugin 2.0.0+, Android Gradle Plugin 8.4.0+, and Gradle Enterprise Plugin 3.13.1+.

## Project and native-build structure

### Included projects

Every project included from settings must map to an existing, writable directory. Configuration fails for a missing, read-only, or non-directory project path.

### Native toolchains

The C++ and Swift plugins no longer use software-model infrastructure. Move `toolChains` out of `model {}` and configure it at the build script's top level.

### `ValidatePlugins` toolchain setup

`ValidatePlugins` requires Java Toolchains infrastructure. Apply `jvm-toolchains` when no Java or other JVM plugin already supplies it:

```kotlin
plugins {
    id("jvm-toolchains")
}
```

## Archives and artifact lifecycles

### Reproducible archives by default

`Jar`, `Ear`, `War`, `Zip`, and other `AbstractArchiveTask` tasks now sort entries deterministically, use fixed timestamps, and assign `0755` to directories and `0644` to files. Restore filesystem metadata only for consumers that require it:

```kotlin
tasks.withType<AbstractArchiveTask>().configureEach {
    isReproducibleFileOrder = false
    isPreserveFileTimestamps = true
    useFileSystemPermissions()
}
```

### Explicit lifecycle wiring

When `ear`, `war`, and `java` are combined, `assemble` builds every corresponding artifact and `archives` contains them all. A custom visible configuration does not automatically join either lifecycle; wire both explicitly:

```kotlin
tasks.named("assemble") {
    dependsOn(special.artifacts)
}
configurations.named("archives") {
    outgoing.artifact(specialJar)
}
```

## Test task migration

### Custom `Test` inputs

A newly registered `Test` task no longer inherits classes and runtime classpath from the built-in `test` source set. A task relying on that convention silently runs no tests. Set both inputs or create the target through JVM test suites:

```kotlin
val test by testing.suites.existing(JvmTestSuite::class)
tasks.register<Test>("otherTest") {
    testClassesDirs = files(test.map { it.sources.output.classesDirs })
    classpath = files(test.map { it.sources.runtimeClasspath })
}
```

### No discovered tests

When sources exist and no filters apply, a test task that discovers no tests fails. Set `failOnNoDiscoveredTests = false` on `AbstractTestTask` only when an empty discovery result is intentional.

## Public API migration

### JSpecify nullability

Gradle's public API uses JSpecify rather than JSR-305. Kotlin 2.1+ enforces generic bounds more precisely:

- Extensions on `Provider<T>` commonly need `T : Any`.
- `Property<String?>` is invalid.
- Nullable values cannot be passed where an API declares `Map<String, *>`.

```kotlin
fun <T : Any> Provider<T>.someExtension() = get()
```

### Signature changes

- Classes extending Gradle-provided classes with `@Inject` getters must be abstract.
- `ConfigurationVariant.getDescription()` returns `Property<String>` instead of `Optional<String>`.
- Exhaustive code over `ComponentIdentifier` must tolerate `RootComponentIdentifier` and unknown future subtypes.

### Direct replacements

| Removed API | Replacement |
| --- | --- |
| `JvmVendorSpec.IBM_SEMERU` | `JvmVendorSpec.IBM` |
| `IdeaModule.testSourceDirs` / `testResourceDirs` | `testSources` / `testResources` |
| `WriteProperties.outputFile` | `destinationFile` |
| `GroovySourceSet` / `ScalaSourceSet` | `GroovySourceDirectorySet` / `ScalaSourceDirectorySet` |
| Integer Unix-mode copy APIs | `FilePermissions` / `ConfigurableFilePermissions` |

## Publication, signing, and Configuration Cache

Changing Gradle Module Metadata after an eagerly created publication has been populated from the same component is now an error. Configure metadata before publication population or keep the setup lazy.

The signing plugin emits an OpenPGP signature version matching the key version, including version 6 rather than always generating version 4 signatures.

With Configuration Cache enabled:

- `onTaskCompletion` listeners must be providers created from a registered build service.
- Unsupported listener providers are cache problems rather than silently ignored.
- Incompatible tasks always discard the entry, even under `org.gradle.configuration-cache.problems=warn`.
- `org.gradle.configuration-cache.unsafe.ignore.unsupported-build-events-listeners=true` is the temporary listener escape hatch.

## Updated defaults

The Gradle 9 defaults are Checkstyle 10.24.0, CodeNarc 3.6.0, PMD 7.13.0, JUnit Jupiter 5.12.2, TestNG 7.11.0, and Spock 2.3. Gradle's JGit is 7.2.1 and can use an SSH agent.

## Removed behavior

### Custom build layouts and conventions

The following are removed:

- `-c` / `--settings-file`
- `-b` / `--build-file`
- `GradleBuild.buildFile`
- `Convention`, `Project.getConvention()`, and `Task.getConvention()`

Use extensions, configure `war` and `ear` tasks directly, and use the `base` extension for base-plugin properties.

### Cache cleanup properties

`org.gradle.cache.cleanup` no longer disables cleanup, and `buildCache.local.removeUnusedEntriesAfterDays` no longer controls local build-cache retention. Configure both through Gradle User Home cache-cleanup settings in an init script.

### Kotlin DSL shortcuts

Kotlin DSL no longer supports:

- `"name"()` domain-object references; use `named("name")`.
- Eager provider accessors such as `configurations.compileClasspath.files`; dereference providers explicitly.
- `libraries` and `bundles` catalog access inside `plugins {}`.
- `kotlinDslPluginOptions.jvmTarget`; use a Java toolchain.

### Develocity application

The Kotlin DSL `` `gradle-enterprise` `` shorthand is removed. Apply the renamed plugin explicitly, or temporarily use the deprecated `com.gradle.enterprise` ID:

```kotlin
plugins {
    id("com.gradle.develocity") version "4.0.2"
}
```

### Groovy conveniences

`groovy-test`, `groovy-console`, and `groovy-sql` are no longer bundled or supplied by `localGroovy`. `org.gradle.util.CollectionUtils`, `ConfigureUtil`, and `ClosureBackedAction` are removed. Plugin DSLs should expose methods accepting `Action` rather than Closure-only APIs.

### Process helpers

`Project.exec`, `Project.javaexec`, and their script-level Kotlin and Groovy counterparts are removed. Plugins and build logic cannot launch processes through these helpers.

## Gradle 9 release behavior

### Configuration Cache preference

In `9.0.0`, compatible builds that have not enabled Configuration Cache receive an end-of-build suggestion. Suppress it explicitly with:

```properties
org.gradle.configuration-cache=false
```

Known unsupported features cause an automatic non-cache fallback with the reason in the Configuration Cache report. A cache problem during task execution aborts immediately rather than leaving the task up-to-date or cached.

### Semantic versions and Wrapper selectors

Gradle 9 uses `MAJOR.MINOR.PATCH`. Older releases and backports retain their existing names. Internal and `@Incubating` features are outside the public semantic-versioning guarantee and can change in a minor release.

On Gradle 9 or newer, `wrapper --gradle-version` accepts a major or major/minor selector and resolves the latest matching release:

```text
./gradlew wrapper --gradle-version=9
./gradlew wrapper --gradle-version=9.1
```

Do not apply that interpretation to pre-9 values: `8.12`, for example, is an exact historical version.

### Other promoted behavior

- A detached configuration can resolve a dependency on its own project.
- Java toolchain auto-detection considers the JDK referenced by `JAVA_HOME`.
- Kotlin DSL dependency and constraint `invoke` overloads are stable, including named configuration providers and `Provider` or `ProviderConvertible` arguments.
- `DependencyHandler.create(String, action)`, `PluginDependenciesSpec.embeddedKotlin(String)`, and `GroovyBuilderScope.hasProperty(String)` are stable.
