# Dependencies, Publishing, and Distributions

## Dependency declarations and resolution

### Use typed dependency blocks with their stability boundary (8.13.0)

The plugin-defined `Dependencies` API for strongly typed `dependencies` blocks
is partially stable. Version-catalog dependencies are still under review and
are not included in that promotion.

### Resolve a project through a detached configuration (9.0.0)

A detached configuration may resolve a dependency on its own project. Temporary
resolution-only configurations are therefore no longer restricted to externally
identified components.

### Use stable Kotlin dependency helpers (9.0.0)

Kotlin DSL dependency and constraint `invoke` overloads are stable, including
overloads on named configuration providers and overloads accepting `Provider`
or `ProviderConvertible`. These APIs are also stable:

- `DependencyHandler.create(String, action)`
- `PluginDependenciesSpec.embeddedKotlin(String)`
- `GroovyBuilderScope.hasProperty(String)`

### Use the stable project dependency factory (9.1.0)

`Project.getDependencyFactory()` is covered by Gradle's backward-compatibility
guarantees.

### Handle repository shutdown after failures (9.3.0)

Gradle disables a repository for the rest of the build after repeated retrieval
failures or a fatal error such as an incorrect hostname. Resolution normally
fails at that point instead of trying later repositories unless continuation
has been configured.

### Preview dependency ordering without constraint edges (9.7.0)

The `ENHANCED_GRAPH_ORDERING` preview ignores constraint edges during graph
traversal, so platforms, lockfiles, and other constraints do not reorder
artifact lists or classpaths. It applies to breadth-first `DEFAULT`,
`CONSUMER_FIRST`, and `DEPENDENCY_FIRST` orders and previews the Gradle 10
default:

```kotlin
enableFeaturePreview("ENHANCED_GRAPH_ORDERING")
```

## Dependency verification

### Record key provenance and diagnose rotation (9.7.0)

The `dependency-verification-1.4.xsd` schema accepts informational `origin` and
`reason` attributes on `<trusted-key>` and `<pgp>` entries and preserves them:

```xml
<trusted-key id="8756c4f765c9ac3cb6b85d62379ce192d401ab61"
             group="com.github.javaparser"
             origin="https://keyserver.ubuntu.com"
             reason="Verified against the maintainer's website"/>
```

When an artifact's signing key is missing, console and HTML diagnostics count
other trusted keys for the same module and group, exposing likely key rotation.

## Distribution and archive tasks

### Create only named distributions (8.13.0)

`distribution-base` supplies distribution capabilities without creating a
default `main` distribution. The `distribution` plugin wraps it and adds `main`:

```kotlin
plugins {
    id("distribution-base")
}

distributions {
    create("custom") {
        distributionBaseName = "customName"
        contents.from("src/customLocation")
    }
}
```

### Publish signed Gradle distributions (9.3.0)

Every distribution ZIP has an ASCII-armored `.asc` signature beside its
`.sha256` checksum. Verify the signature for authenticity rather than treating
the checksum as proof of origin.

### Give archives one meaningful reproducible timestamp (9.7.0)

`AbstractArchiveTask.reproducibleFileTimestamp` assigns one reproducible
timestamp to every entry. This supports formats that need a verifiable value
such as `SOURCE_DATE_EPOCH` instead of Gradle's fixed default:

```kotlin
tasks.withType<AbstractArchiveTask>().configureEach {
    reproducibleFileTimestamp = providers.environmentVariable("SOURCE_DATE_EPOCH").map {
        Instant.ofEpochSecond(it.toLong()).toEpochMilli()
    }
}
```

## Components and publication modeling

### Add Maven distribution management (9.1.0)

`MavenPublication.pom.distributionManagement` emits a distribution repository
directly in the generated POM:

```kotlin
publications.withType<MavenPublication>().configureEach {
    pom {
        distributionManagement {
            repository {
                id = "github"
                url = "https://maven.pkg.github.com/OWNER/REPOSITORY"
            }
        }
    }
}
```

### Generate Jakarta EE 11 EAR descriptors (9.1.0)

The EAR plugin can generate a Jakarta EE 11 descriptor without a custom file:

```kotlin
tasks.ear {
    deploymentDescriptor {
        version = "11"
    }
}
```

### Create ad hoc components from publishing (9.2.0)

The `publishing` extension exposes `SoftwareComponentFactory`, so code can
create an ad hoc publishable component without applying a JVM plugin solely to
obtain one:

```kotlin
publishing {
    val component = softwareComponentFactory.adhoc("custom")
    component.addVariantsFromConfiguration(consumableConfiguration) {}
    publications {
        create<MavenPublication>("maven") { from(component) }
    }
}
```

### Pass lazy publication variants (9.2.0)

`AdhocComponentWithVariants.addVariantsFromConfiguration(...)` and
`withVariantsFromConfiguration(...)` accept a
`Provider<ConsumableConfiguration>`. The provider realizes its configuration
only when that publication is published.

## Plugin publication and validation

### Upgrade Plugin Publishing plugin 2.0 (9.1.0)

Plugin Publishing plugin `2.0.0` supports Configuration Cache and models its
configuration with the Provider API. It requires Gradle 7.4 or newer; signed
publications need Gradle 8.1.1 or newer for complete cache compatibility.

### Default a plugin ID from its registration (9.4.0)

With `java-gradle-plugin`, a registration uses its name as the plugin ID unless
`id` is set explicitly:

```kotlin
gradlePlugin {
    plugins {
        register("my.plugin-id") {
            implementationClass = "my.PluginClass"
        }
    }
}
```

### Enable stricter validation for published plugins (9.4.0)

Applying `com.gradle.plugin-publish`, `ivy-publish`, or `maven-publish` enables
stricter plugin validation. Local `buildSrc` and included-build plugins are
exempt. Other plugin projects can set:

```kotlin
tasks.validatePlugins {
    enableStricterValidation = true
}
```
