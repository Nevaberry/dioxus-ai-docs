# Gradle 9 Migration

Apply this checklist to the 9.0 migration batch (`9.0.0-upgrade`) before
adopting later features.

## Runtime, language, and plugin floors

### Separate the daemon JVM from build toolchains

The daemon requires Java 17 or newer. The Wrapper and command-line launcher,
Tooling API, and TestKit can start on Java 8, but must locate a Java 17+ JVM to
execute a build. Compilation, tests, and workers can continue targeting older
Java through toolchains.

### Compile against the current Kotlin DSL baseline

Gradle embeds Kotlin 2.2.0 and uses language version 2.2 for scripts, build
logic, and plugins. Kotlin language versions 1.4 through 1.7 are unsupported.
Script-instance labels such as `this@Build_gradle` no longer compile; use
`project`, `settings`, or `gradle` according to scope.

### Recompile and test Groovy plugins

Gradle embeds Groovy 4.0.27 with its package/module changes and delegate-first
dynamic lookup. Groovy 3-compiled plugin code can fail to resolve `super` calls.
Dynamically compiled closures inherited from a parent can lose access to the
parent's private members; `@CompileStatic` avoids that lookup issue.

### Meet plugin compatibility floors

- Kotlin DSL plugins built with Gradle 9 require Gradle 8.11 or newer unless
  explicitly compiled against Kotlin 1.x.
- Groovy DSL plugins built with Gradle 9 require Gradle 7.0 or newer.
- Use Kotlin Gradle Plugin 2.0.0+, Android Gradle Plugin 8.4.0+, and Gradle
  Enterprise Plugin 3.13.1+.

### Move native toolchains out of the software model

C++ and Swift plugins no longer use the software-model plugin infrastructure.
Move `toolChains` configuration out of `model {}` and configure it at the top
level.

### Apply toolchains for plugin validation

`ValidatePlugins` requires Java Toolchains. Apply `jvm-toolchains` when no Java
or other JVM plugin already supplies that infrastructure:

```kotlin
plugins {
    id("jvm-toolchains")
}
```

## Project layout and lifecycle

### Make included-project directories valid

Each project included from settings must map to an existing, writable directory
that is actually a directory. Invalid mappings fail during configuration.

### Wire custom artifacts explicitly

When `ear`, `war`, and `java` are combined, `assemble` builds all corresponding
artifacts and `archives` contains all of them. A custom visible configuration,
however, no longer adds its outgoing artifact to either lifecycle. Wire both:

```kotlin
tasks.named("assemble") {
    dependsOn(special.artifacts)
}
configurations.named("archives") {
    outgoing.artifact(specialJar)
}
```

### Remove alternate build-layout options

The `-c`/`--settings-file` and `-b`/`--build-file` options,
`GradleBuild.buildFile`, `Convention`, `Project.getConvention()`, and
`Task.getConvention()` are removed. Use the standard build layout and extension
objects. Configure `war` and `ear` tasks directly; use the `base` extension for
base-plugin properties.

## Archives, publications, and signing

### Account for reproducible archive defaults

`Jar`, `Ear`, `War`, `Zip`, and other `AbstractArchiveTask` types now sort
entries deterministically, use fixed timestamps, and assign `0755` to
directories and `0644` to files. Opt back into filesystem metadata only when a
consumer requires it:

```kotlin
tasks.withType<AbstractArchiveTask>().configureEach {
    isReproducibleFileOrder = false
    isPreserveFileTimestamps = true
    useFileSystemPermissions()
}
```

### Stop late mutation of publication metadata

Changing Gradle Module Metadata after an eagerly created publication has been
populated from the same component is an error, not a warning. The signing plugin
uses the OpenPGP signature version of the key, including version 6 rather than
always emitting version 4.

## Tests and quality tools

### Configure every custom `Test` task input

A newly registered `Test` task no longer inherits the built-in `test` source
set's classes or runtime classpath. A task relying on that convention can run no
tests silently. Configure both values or model the target as a JVM test suite:

```kotlin
val test by testing.suites.existing(JvmTestSuite::class)
tasks.register<Test>("otherTest") {
    testClassesDirs = files(test.map { it.sources.output.classesDirs })
    classpath = files(test.map { it.sources.runtimeClasspath })
}
```

### Decide whether zero discovered tests are valid

When test sources exist and no filters apply, a task that discovers no tests
fails. This exposes test-framework mismatches. Set
`failOnNoDiscoveredTests = false` on `AbstractTestTask` only when the empty
discovery result is intentional.

### Review updated tool defaults

Defaults are Checkstyle 10.24.0, CodeNarc 3.6.0, PMD 7.13.0, JUnit Jupiter
5.12.2, TestNG 7.11.0, and Spock 2.3. Gradle's JGit is 7.2.1 and can use an SSH
agent.

## Plugin API source changes

### Update for JSpecify nullability

The public API uses JSpecify instead of JSR-305. Kotlin 2.1+ enforces generic
bounds more precisely: extensions on `Provider<T>` commonly need `T : Any`,
`Property<String?>` is invalid, and nullable values cannot be passed where an
API declares `Map<String, *>`.

```kotlin
fun <T : Any> Provider<T>.someExtension() = get()
```

### Update changed plugin signatures

Classes extending Gradle types with `@Inject` getters must be abstract.
`ConfigurationVariant.getDescription()` returns `Property<String>` rather than
`Optional<String>`. Exhaustive logic over `ComponentIdentifier` must accept
`RootComponentIdentifier` and future unknown subtypes.

### Replace direct API removals

- `JvmVendorSpec.IBM_SEMERU` -> `JvmVendorSpec.IBM`
- `IdeaModule.testSourceDirs`/`testResourceDirs` ->
  `testSources`/`testResources`
- `WriteProperties.outputFile` -> `destinationFile`
- `GroovySourceSet`/`ScalaSourceSet` -> `GroovySourceDirectorySet`/
  `ScalaSourceDirectorySet`
- integer Unix-mode copy APIs -> `FilePermissions` or
  `ConfigurableFilePermissions`

## Kotlin and Groovy DSL removals

### Remove obsolete Kotlin DSL shortcuts

- Replace `"name"()` domain-object references with `named("name")`.
- Explicitly dereference providers instead of eager access such as
  `configurations.compileClasspath.files`.
- Do not access `libraries` or `bundles` entries from `plugins {}`.
- Replace `kotlinDslPluginOptions.jvmTarget` with a Java toolchain.

### Apply Develocity by explicit ID

The Kotlin DSL `` `gradle-enterprise` `` shorthand is removed. Apply the
renamed plugin explicitly, or temporarily use the deprecated
`com.gradle.enterprise` ID:

```kotlin
plugins {
    id("com.gradle.develocity") version "4.0.2"
}
```

### Replace removed Groovy conveniences

`groovy-test`, `groovy-console`, and `groovy-sql` are no longer bundled or
provided by `localGroovy`; add dependencies explicitly. The
`org.gradle.util.CollectionUtils`, `ConfigureUtil`, and `ClosureBackedAction`
types are removed. Plugin DSLs should expose methods accepting `Action` instead
of Closure-specific APIs.

## Configuration Cache and cleanup

### Register task-completion listeners through services

With Configuration Cache, `onTaskCompletion` listeners must be providers from a
registered build service. Unsupported providers are cache problems rather than
silently ignored. Incompatible tasks discard the cache entry even with
`org.gradle.configuration-cache.problems=warn`. As a temporary escape hatch:

```properties
org.gradle.configuration-cache.unsafe.ignore.unsupported-build-events-listeners=true
```

### Move cache cleanup to Gradle User Home settings

`org.gradle.cache.cleanup` no longer disables cleanup, and
`buildCache.local.removeUnusedEntriesAfterDays` no longer controls local
build-cache retention. Configure both through Gradle User Home cache-cleanup
settings in an init script.

## Process execution

### Replace project-level process helpers

`Project.exec`, `Project.javaexec`, and their Kotlin and Groovy script-level
counterparts are removed. Build logic and plugins must use an appropriate task
type or injected execution service instead.
