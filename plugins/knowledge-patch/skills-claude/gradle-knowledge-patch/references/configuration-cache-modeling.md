# Configuration Cache and Lazy Modeling

## Configuration Cache behavior and diagnostics

### Enable integrity checking only for diagnosis (8.14.0)

Set the following property for stricter serialization checks and more precise
cache-load diagnostics:

```properties
org.gradle.configuration-cache.integrity-check=true
```

It increases cache size and slows reads and writes, so disable it after the
investigation.

### Understand prompting and fallback (9.0.0)

Configuration Cache is preferred but remains optional. Compatible builds that
have not enabled it receive an end-of-build suggestion; explicitly set
`org.gradle.configuration-cache=false` to suppress that suggestion. Known
unsupported features automatically fall back to an uncached build and record
the reason in the report. A cache problem during task execution aborts
immediately rather than leaving that task up-to-date or cached.

### Use read-only entries in CI (9.1.0)

Read-only mode reuses an entry on a hit but never creates an entry on a miss:

```text
./gradlew --configuration-cache -Dorg.gradle.configuration-cache.read-only=true
```

This lets pull-request or other restricted jobs consume shared entries without
populating them.

### Respect keystore selection (9.1.0)

Cache encryption uses the JVM's default keystore type when that type supports
symmetric keys. Gradle falls back to `PKCS12` for known asymmetric-only formats,
which accommodates customized and FIPS-oriented JVM security configurations.

### Track environment-backed properties precisely (9.6.1)

Properties supplied with `-Dorg.gradle.project.<name>` or
`ORG_GRADLE_PROJECT_<name>` do not invalidate an entry when configuration never
reads them. A provider read only during task execution can observe the new value
while reusing the existing entry:

```kotlin
tasks.register("printValue") {
    val value = providers.gradleProperty("value").orElse("N/A")
    doLast { println(value.get()) }
}
```

## Cache-compatible inputs and integrations

### Declare a `ResolutionResult` task input (9.7.0)

With Configuration Cache, a task may expose the entire `ResolutionResult` as an
`@Input`. This preserves direct use of `allComponents` and `allDependencies`
without separately extracting the root component and variant:

```kotlin
abstract class DependencyReport : DefaultTask() {
    @get:Input
    abstract val result: Property<ResolutionResult>

    @TaskAction
    fun report() = println(result.get().allComponents)
}

tasks.register<DependencyReport>("dependencyReport") {
    result = configurations.runtimeClasspath.map { it.incoming.resolutionResult }
}
```

### Use startup Java agents carefully (9.7.0)

Agents supplied at JVM startup with `-javaagent:` work with Configuration Cache
in normal daemon builds and TestKit's default daemon mode. Dynamically attached
agents and TestKit embedded mode from `withDebug(true)` remain unsupported. For
manual debugging, use `-Dorg.gradle.debug=true`.

## Lazy configurations and attributes

### Preserve registered configuration laziness (8.14.0)

The `base` plugin, including indirect application through Java or Kotlin
plugins, does not realize every configuration declared with `register` or a
role-based factory such as `resolvable`. Prefer `register` over `create`:

```kotlin
configurations {
    register("myLazyConfiguration")
}
```

### Merge attributes lazily (9.1.0)

`AttributeContainer.addAllLater(source)` imports attributes without eager
evaluation. Imported values override existing destination values and track
later source changes; destination values set after the import take precedence.

```kotlin
target.attributes.addAllLater(source.attributes)
```

### Extend configurations from providers (9.4.0)

`Configuration.extendsFrom` accepts a `Provider<Configuration>`, avoiding a
realizing `get()` call:

```kotlin
configurations {
    val parent = dependencyScope("parent")
    resolvable("child") {
        extendsFrom(parent)
    }
}
```

## Domain-object collection lifecycle

### Freeze membership without realization (9.5.0)

`DomainObjectCollection.disallowChanges()` prevents later additions and
removals without realizing entries added lazily. It freezes collection
membership, not mutable state inside each object.

### Expose elements through a provider (9.7.0)

The `elements` property is a `Provider<out Collection<T>>` that does not force
realization. It also carries task dependencies contributed through `addLater`
and `addAllLater`, so it can be wired into task inputs safely:

```kotlin
val items = objects.domainObjectSet(MyType::class.java)
items.addLater(someProvider)
tasks.register("process") {
    inputs.property("items", items.elements)
}
```

## Isolated Projects

### Use current controls and migrate cross-project access (9.7.0)

The incubating feature uses `--isolated-projects` or:

```properties
org.gradle.isolated-projects=true
org.gradle.isolated-projects.diagnostics=true
# Migration experiments only:
# org.gradle.isolated-projects.dangerously-ignore-problems=true
```

The legacy `org.gradle.unsafe.isolated-projects` names are deprecated aliases.
Isolation rejects mutable access to other projects or the build. Diagnostics
help migration; dangerous-ignore mode can turn violations into warnings but is
not recommended for production. The feature remains opt-in.
