# Dependencies, Publishing, and Distributions

## Declare Scala toolchains

Since `8.13.0`, the `scala` and `scala-base` plugins accept `scalaVersion` in the `scala` extension and resolve the required Scala toolchain dependencies automatically. A `scala-library` dependency is no longer needed solely to select or infer the Scala version:

```kotlin
scala {
    scalaVersion = "3.6.3"
}
```

## Author typed dependency blocks

Since `8.13.0`, the `Dependencies` API used by plugin-defined strongly typed `dependencies` blocks is partially stable. Version-catalog dependencies are still under review and are not included in that promotion.

Since `9.0.0`, Kotlin DSL dependency and constraint `invoke` overloads are stable, including overloads on named configuration providers and overloads accepting `Provider` or `ProviderConvertible` values. These related APIs are stable as well:

- `DependencyHandler.create(String, action)`
- `PluginDependenciesSpec.embeddedKotlin(String)`
- `GroovyBuilderScope.hasProperty(String)`

## Resolve project dependencies

Since `9.0.0`, a detached configuration can resolve a dependency that points to its own project. Temporary, resolution-only configurations can therefore contain project dependencies as well as externally identified components.

## Handle repository failures

Since `9.3.0`, repeated retrieval failures and fatal errors such as an incorrect hostname disable that repository for the rest of the build. Dependency resolution normally fails at that point rather than continuing to later repositories unless continuation has been configured.

## Create custom publishable components

### Component factory on `publishing`

Since `9.2.0`, the `publishing` extension exposes `SoftwareComponentFactory`. A build or plugin can create an ad hoc component without applying a JVM plugin merely to obtain one:

```kotlin
publishing {
    val component = softwareComponentFactory.adhoc("custom")
    component.addVariantsFromConfiguration(consumableConfiguration) {}
    publications {
        create<MavenPublication>("maven") {
            from(component)
        }
    }
}
```

### Lazy configuration providers

Also since `9.2.0`, `AdhocComponentWithVariants.addVariantsFromConfiguration(...)` and `withVariantsFromConfiguration(...)` accept `Provider<ConsumableConfiguration>`. The configuration stays unrealized until its publication is actually published:

```kotlin
val publishedVariant = configurations.consumable("publishedVariant")

publishing {
    val component = softwareComponentFactory.adhoc("custom")
    component.addVariantsFromConfiguration(publishedVariant) {}
}
```

## Generate Maven POM distribution management

Since `9.1.0`, a `MavenPublication` can declare a distribution repository directly and emit it in the generated POM:

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

## Respect publication and signing rules

For the `9.0.0-upgrade`, changing Gradle Module Metadata after an eagerly created publication has been populated from the same component is an error rather than a warning. Complete metadata configuration before population or keep the publication path lazy.

The signing plugin now emits an OpenPGP signature version that matches the key version. A version 6 key produces a version 6 signature rather than an unconditional version 4 signature.

## Build distributions

### Distribution support without `main`

Since `8.13.0`, `distribution-base` provides distribution capabilities without creating a default `main` distribution. The `distribution` plugin applies it and adds `main`:

```kotlin
plugins {
    id("distribution-base")
}

distributions {
    create("custom") {
        distributionBaseName = "customName"
        contents {
            from("src/customLocation")
        }
    }
}
```

### Jakarta EE 11 EAR descriptors

Since `9.1.0`, the EAR plugin generates Jakarta EE 11 deployment descriptors without a custom descriptor file:

```kotlin
tasks.ear {
    deploymentDescriptor {
        version = "11"
    }
}
```

### Artifact lifecycle wiring

For the `9.0.0-upgrade`, applying `ear`, `war`, and `java` makes `assemble` build all corresponding artifacts and places all of them in `archives`. A custom visible configuration does not automatically join those lifecycles:

```kotlin
tasks.named("assemble") {
    dependsOn(special.artifacts)
}
configurations.named("archives") {
    outgoing.artifact(specialJar)
}
```

## Produce and verify archives

### Reproducible defaults

For the `9.0.0-upgrade`, `AbstractArchiveTask` implementations sort entries, use fixed timestamps, and assign `0755` directory and `0644` file permissions by default. Restore filesystem order, timestamps, and permissions only when required by a consumer:

```kotlin
tasks.withType<AbstractArchiveTask>().configureEach {
    isReproducibleFileOrder = false
    isPreserveFileTimestamps = true
    useFileSystemPermissions()
}
```

### One meaningful reproducible timestamp

Since `9.7.0`, `AbstractArchiveTask.reproducibleFileTimestamp` assigns one meaningful, reproducible timestamp to all entries. This supports formats that need a verifiable value such as `SOURCE_DATE_EPOCH` rather than Gradle's fixed default:

```kotlin
tasks.withType<AbstractArchiveTask>().configureEach {
    reproducibleFileTimestamp = providers
        .environmentVariable("SOURCE_DATE_EPOCH")
        .map { Instant.ofEpochSecond(it.toLong()).toEpochMilli() }
}
```

### Distribution signatures

Since `9.3.0`, each Gradle distribution ZIP is published with an ASCII-armored `.asc` signature as well as its `.sha256` checksum. Verify the signature for authenticity; a checksum alone establishes integrity, not signer identity.

## Explain dependency-verification failures

Since `9.7.0`, dependency verification accepts informational `origin` and `reason` attributes on `<trusted-key>` and `<pgp>` entries. Gradle preserves them under the `dependency-verification-1.4.xsd` schema:

```xml
<trusted-key id="8756c4f765c9ac3cb6b85d62379ce192d401ab61"
             group="com.github.javaparser"
             origin="https://keyserver.ubuntu.com"
             reason="Verified against the maintainer's website"/>
```

When an artifact's signing key cannot be found, console and HTML diagnostics count other trusted keys for its module and group. Use that information to recognize likely signing-key rotation.

## Preview Gradle 10 dependency ordering

Since `9.7.0`, the `ENHANCED_GRAPH_ORDERING` preview ignores constraint edges while traversing dependency graphs. Platforms, lockfiles, and other constraints therefore stop reordering artifact lists or classpaths. The preview applies to breadth-first `DEFAULT`, `CONSUMER_FIRST`, and `DEPENDENCY_FIRST` sort orders:

```kotlin
// settings.gradle.kts
enableFeaturePreview("ENHANCED_GRAPH_ORDERING")
```

This previews the planned Gradle 10 default, so verify consumers that depend on classpath or artifact ordering.

## Stable project dependency factory

Since `9.1.0`, `Project.getDependencyFactory()` is a promoted public API covered by Gradle's backward-compatibility guarantees.

## Verification checklist

- Inspect publication variants without forcing provider-backed configurations early.
- Generate POM and Gradle Module Metadata and compare the intended repository and variant data.
- Sign with the actual key type used in release automation and verify the emitted signature version.
- Inspect archive order, timestamps, and permissions, including any `SOURCE_DATE_EPOCH` mapping.
- Treat repository disablement as a build-level state after repeated or fatal retrieval errors.
- Record dependency-verification key provenance so rotations are diagnosable.
