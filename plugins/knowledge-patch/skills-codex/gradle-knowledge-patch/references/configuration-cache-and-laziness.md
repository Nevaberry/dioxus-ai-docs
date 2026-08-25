# Configuration Cache and Lazy Configuration

## Diagnose cache serialization

### Integrity checking

Since `8.14.0`, enable stricter serialization validation and more precise cache-load diagnostics with:

```properties
org.gradle.configuration-cache.integrity-check=true
```

This mode makes entries larger and slows reads and writes. Use it while troubleshooting, then remove it.

## Choose cache read and write behavior

### Preferred but optional

In `9.0.0`, compatible builds that have not enabled Configuration Cache receive a suggestion after the build. Set `org.gradle.configuration-cache=false` to suppress it explicitly.

Known unsupported features cause an automatic non-cache fallback, recorded in the Configuration Cache report. A cache problem during task execution aborts immediately instead of leaving the task up-to-date or cached.

### Read-only mode

Since `9.1.0`, read-only mode reuses an existing entry on a hit and never stores a new entry on a miss. It is useful when pull-request jobs may consume shared entries but should not populate them:

```text
./gradlew --configuration-cache -Dorg.gradle.configuration-cache.read-only=true
```

### Encryption keystore

Since `9.1.0`, Configuration Cache encryption uses the JVM's default keystore type when that type supports symmetric keys. Gradle falls back to `PKCS12` for known asymmetric-only formats, improving compatibility with customized and FIPS-oriented JVM security settings.

## Preserve cache correctness

### Build-event listeners

For the `9.0.0-upgrade`, an `onTaskCompletion` listener must come from a provider created by a registered build service. Unsupported providers are cache problems rather than silently ignored.

An incompatible task discards the cache entry even with `org.gradle.configuration-cache.problems=warn`. During migration only, the listener-specific escape hatch is:

```properties
org.gradle.configuration-cache.unsafe.ignore.unsupported-build-events-listeners=true
```

### Environment-backed project properties

Since `9.6.1`, project properties supplied through `-Dorg.gradle.project.<name>` or `ORG_GRADLE_PROJECT_<name>` invalidate an entry only if configuration read that property. A provider first consumed during execution observes a new value while the existing entry is reused:

```kotlin
tasks.register("printValue") {
    val value = providers.gradleProperty("value").orElse("N/A")
    doLast { println(value.get()) }
}
```

### `ResolutionResult` task inputs

Since `9.7.0`, a task can declare an entire `ResolutionResult` as `@Input` while using Configuration Cache. This preserves access to `allComponents` and `allDependencies` without extracting only a root component and variant:

```kotlin
abstract class DependencyReport : DefaultTask() {
    @get:Input
    abstract val result: Property<ResolutionResult>

    @TaskAction
    fun report() = println(result.get().allComponents)
}

tasks.register<DependencyReport>("dependencyReport") {
    result = configurations.runtimeClasspath.map {
        it.incoming.resolutionResult
    }
}
```

### Java agents and TestKit

Since `9.7.0`, third-party agents supplied at JVM startup with `-javaagent:` work with Configuration Cache in regular daemon builds and TestKit's default daemon mode. Dynamically attached agents and TestKit embedded mode through `withDebug(true)` remain unsupported. Use `-Dorg.gradle.debug=true` for manual debugging instead.

```properties
org.gradle.jvmargs=-javaagent:/path/to/jacocoagent.jar=destfile=build/jacoco/functionalTest.exec
```

## Migrate to Isolated Projects

### Current controls

Since `9.7.0`, use either the CLI flag or property:

```text
./gradlew --isolated-projects build
```

```properties
org.gradle.isolated-projects=true
org.gradle.isolated-projects.diagnostics=true
```

The legacy `org.gradle.unsafe.isolated-projects` names are deprecated aliases. Isolation rejects mutable access to other projects or the build. The feature is opt-in and is not recommended for production.

For migration experiments only, violations can temporarily become warnings:

```properties
org.gradle.isolated-projects.dangerously-ignore-problems=true
```

Treat the dangerous-ignore property as a diagnostic bridge, not a completed migration.

## Keep configurations lazy

### Registered configurations

Since `8.14.0`, applying `base`—directly or through Java or Kotlin plugins—does not realize every configuration declared with `register` or a role-based factory such as `resolvable`. Prefer registration to eager creation:

```kotlin
configurations {
    register("myLazyConfiguration")
}
```

### Lazy inheritance

Since `9.4.0`, `Configuration.extendsFrom` accepts a `Provider<Configuration>`, avoiding a `get()` on a lazily registered parent:

```kotlin
configurations {
    val parent = dependencyScope("parent")
    resolvable("child") {
        extendsFrom(parent)
    }
}
```

### Lazy attribute merging

Since `9.1.0`, `AttributeContainer.addAllLater(source)` imports attributes lazily. Imported values override attributes already in the destination and track later changes to the source; destination values set afterward take precedence:

```kotlin
target.attributes.addAllLater(source.attributes)
```

## Control domain-object collections

### Freeze membership without realization

Since `9.5.0`, `DomainObjectCollection.disallowChanges()` prevents later additions and removals without realizing lazily added entries. It freezes membership, not the mutable state of contained objects:

```kotlin
val items = objects.domainObjectContainer(MyType::class)
val main = MyType("main")
items.add(main)
items.disallowChanges()
main.setFoo("bar")
```

### Expose elements as a provider

Since `9.7.0`, `elements` exposes a domain-object collection as `Provider<out Collection<T>>` without forcing realization. It also carries task dependencies contributed through `addLater` and `addAllLater`, so it can be wired safely to task inputs:

```kotlin
val items = objects.domainObjectSet(MyType::class.java)
items.addLater(someProvider)
tasks.register("process") {
    inputs.property("items", items.elements)
}
```

## Lazy publication inputs

Since `9.2.0`, `AdhocComponentWithVariants.addVariantsFromConfiguration(...)` and `withVariantsFromConfiguration(...)` accept `Provider<ConsumableConfiguration>`. The provider realizes the configuration only when its publication is published:

```kotlin
val publishedVariant = configurations.consumable("publishedVariant")

publishing {
    val component = softwareComponentFactory.adhoc("custom")
    component.addVariantsFromConfiguration(publishedVariant) {}
}
```

## Review checklist

- Prefer `register`, role-based factories, and providers over `create` and `get()`.
- Ensure values used only at task execution stay inside providers until execution.
- Run the same task set twice and verify the second invocation loads an entry.
- Re-run with integrity checking only when serialization or load diagnostics are unclear.
- Test build-event listener providers and agent mode explicitly.
- Enable Isolated Projects diagnostics before considering the dangerous-ignore bridge.
