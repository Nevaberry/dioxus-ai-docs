# Tooling API, Problems API, and Build Logic

## Resolve files from settings

Since `8.13.0`, `ProjectLayout.settingsDirectory` exposes the directory containing `settings.gradle` or `settings.gradle.kts`. Use it for build-wide files instead of reaching through `rootProject`:

```kotlin
val versionFile = layout.settingsDirectory.file("version.txt")
```

## Inspect artifact transforms

Since `8.13.0`, the `artifactTransforms` report lists every transform registered in a project, including action type, cacheability, and input/output attributes:

```text
./gradlew artifactTransforms
```

Use it to inspect plugin registrations and diagnose ambiguous transforms.

## Stream Tooling API values

Since `8.13.0`, asynchronous client streaming is stable and covered by Gradle's compatibility guarantees. The promoted surface is:

- `BuildActionExecuter.setStreamedValueListener(StreamedValueListener)`
- `StreamedValueListener`
- `BuildController.send(Object)`

Use streamed values for incremental results from long-running build actions.

## Attach structured problem data

### Producer-side data

Since `8.14.0`, `ProblemSpec.additionalData(...)` accepts typed arbitrary data. The data can contain Provider API properties, bean-style fields, collections, and nested objects. Define the model as an interface extending `AdditionalData`:

```java
public interface SomeData extends AdditionalData {
    Property<String> getSome();
    List<String> getNames();
    void setNames(List<String> names);
}

problem.additionalData(SomeData.class, data -> {
    data.getSome().set("some");
    data.setNames(Collections.singletonList("moreData"));
});
```

### Tooling API views

Also since `8.14.0`, consumers can call `CustomAdditionalData.get(Class)` with a view interface matching the producer's model. This returns structured data without parsing a serialized payload:

```java
SomeDataView data = problem.getAdditionalData().get(SomeDataView.class);
String value = data.getSome();
```

Keep producer and view property shapes aligned.

## Render and locate problems

### Console rendering

Since `9.3.0`, `--warning-mode=all` renders relevant structured Problems API entries in the console with their build location while retaining the link to the HTML Problems report:

```text
./gradlew test --warning-mode=all
```

### Large problem sets

Since `9.7.0`, Gradle attaches source locations to as many as 2,050 problems per build. The first 50 keep full stack traces; the next 2,000 use cheaper location capture. `--warning-mode=all` removes this limit. Beyond the first 50, locations stop at the originating script instead of retaining the complete call chain.

## Control Tooling API execution

### Parallelism

Since `9.4.0`, `org.gradle.tooling.parallel` controls parallel Tooling API actions independently of build task parallelism. When unset, it inherits `org.gradle.parallel`:

```properties
org.gradle.tooling.parallel=true
org.gradle.parallel=false
```

### Version and help models

Since `9.4.0`, `BuildEnvironment.getVersionInfo()` returns the exact `gradle --version` output without starting a daemon. The `Help` model returns rendered `gradle --help` text:

```java
String version = connection
    .getModel(BuildEnvironment.class)
    .getVersionInfo();
String help = connection
    .getModel(Help.class)
    .getRenderedText();
```

## Author Gradle plugins

### Default plugin IDs

Since `9.4.0`, with `java-gradle-plugin`, a plugin registration uses its registration name as its ID unless `id` is set explicitly:

```kotlin
gradlePlugin {
    plugins {
        register("my.plugin-id") {
            implementationClass = "my.PluginClass"
        }
    }
}
```

### Published-plugin validation

Since `9.4.0`, applying `com.gradle.plugin-publish`, `ivy-publish`, or `maven-publish` enables stricter plugin validation automatically. Local plugins in `buildSrc` and included builds are exempt. Other plugin projects can opt in:

```kotlin
tasks.validatePlugins {
    enableStricterValidation = true
}
```

### Plugin Publishing plugin 2.0

Since `9.1.0`, Plugin Publishing plugin 2.0.0 supports Configuration Cache and exposes configuration through the Provider API. It requires Gradle 7.4 or newer. Signed publications require Gradle 8.1.1 or newer for full Configuration Cache compatibility.

### `compileOnly` accessors in precompiled scripts

Since `9.1.0`, precompiled Kotlin script plugins can apply and configure plugins supplied as `compileOnly` dependencies, including their type-safe extension accessors.

### Type-safe accessors in Settings plugins

Since `9.5.0`, precompiled `*.settings.gradle.kts` plugins receive generated type-safe accessors when the convention-plugin build applies `kotlin-dsl`:

```kotlin
// build-logic/build.gradle.kts
plugins {
    `kotlin-dsl`
}

// build-logic/src/main/kotlin/conventions.settings.gradle.kts
plugins {
    id("com.gradle.develocity")
}
develocity {
    buildScan {
        publishing.onlyIf { false }
    }
}
```

## Work with Groovy DSL lazy properties

Since `9.6.1`, Groovy assignment coerces a string to `Property<File>`, `RegularFileProperty`, or `DirectoryProperty`, resolving the string relative to the project directory. A scalar or array can be assigned to `ListProperty<T>` or `SetProperty<T>`:

```groovy
task.workingDir = '../my-build'
task.filter.includePatterns = 'Foo'
task.filter.includePatterns = ['Foo', 'Bar'] as String[]
```

## Eliminate implicit parent-project lookup

Since `9.6.1`, Groovy DSL property or method references that fall through to a parent project are deprecated. So are `findProperty()`, `property()`, and `hasProperty()` when their result comes from a parent. This lookup is scheduled for removal in Gradle 10.

After replacing those references with explicit ownership, enable the preview to reject accidental parent lookup:

```kotlin
// settings.gradle.kts
enableFeaturePreview("NO_IMPLICIT_LOOKUP_IN_PARENT_PROJECTS")
```

## Guard Gradle API integrations

For the `9.0.0-upgrade`:

- A class extending a Gradle-provided class with `@Inject` getters must be abstract.
- `ConfigurationVariant.getDescription()` returns `Property<String>` instead of `Optional<String>`.
- `ComponentIdentifier` handling must accept `RootComponentIdentifier` and future unknown subtypes.
- Public nullability uses JSpecify; Kotlin generic bounds and nullable arguments are checked more precisely.

## Lock collection membership

Since `9.5.0`, plugin authors can call `DomainObjectCollection.disallowChanges()` to prevent later additions and removals without realizing lazy entries. The objects inside the collection remain mutable:

```kotlin
val items = objects.domainObjectContainer(MyType::class)
val main = MyType("main")
items.add(main)
items.disallowChanges()
main.setFoo("bar")
```

## Diagnostics checklist

- Use `artifactTransforms` before changing transform attributes or registrations.
- Stream high-volume Tooling API results rather than collecting one large object.
- Keep custom problem producer and consumer view interfaces structurally aligned.
- Use `--warning-mode=all` when source locations are missing from a large problem set.
- Set Tooling API parallelism explicitly when it should differ from task parallelism.
- Check generated plugin IDs and validation behavior whenever publishing plugins are applied.
- Enable the no-parent-lookup preview only after resolving implicit Groovy references.
