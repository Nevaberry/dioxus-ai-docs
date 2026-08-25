---
name: gradle-knowledge-patch
description: Gradle
version: 9.6.1
license: MIT
metadata:
  author: Nevaberry
---


# Gradle Knowledge Patch

Use this skill when upgrading, configuring, debugging, or extending Gradle builds. Start with the project wrapper version and the plugins actually applied, then use the reference that matches the work at hand.

## How to use this patch

1. Read `gradle/wrapper/gradle-wrapper.properties` before proposing version-sensitive syntax.
2. Inspect `settings.gradle(.kts)`, root and convention-plugin build scripts, and `gradle.properties` for active feature flags.
3. For a Gradle 9 upgrade, apply the breaking-change checklist before introducing newer APIs.
4. Preserve lazy configuration: prefer providers, `register`, role-based configuration factories, and deferred publication inputs.
5. Distinguish daemon JVM requirements from Java compilation and test toolchains.
6. Verify report consumers when changing test engines, report structures, timestamps, attachments, or aggregation.
7. Treat incubating APIs and feature previews as opt-in behavior that can still change.

## Reference index

| Reference | Topics |
| --- | --- |
| [Gradle 9 upgrade](references/gradle-9-upgrade.md) | Runtime and plugin floors, removed APIs, Kotlin and Groovy changes, archives, tests, publications |
| [Configuration Cache and laziness](references/configuration-cache-and-laziness.md) | Cache modes and correctness, Isolated Projects, providers, lazy configurations and collections |
| [Daemon, CLI, Wrapper, and platforms](references/daemon-cli-and-platforms.md) | JVM toolchains, daemon behavior, consoles, Wrapper security and reliability, platform support |
| [Testing, reports, and quality tools](references/testing-and-quality.md) | Test discovery and events, HTML/XML reports, TestKit, ANTLR, PMD, validation |
| [Dependencies, publishing, and distributions](references/dependencies-publishing-and-distribution.md) | Resolution, repositories, verification, publications, distributions, reproducible archives |
| [Tooling API, Problems API, and build logic](references/tooling-problems-and-build-logic.md) | Tooling models and streaming, structured problems, plugin authoring, layout and diagnostics |

## Breaking changes first

### Gradle 9 runtime and language baselines

- Run the daemon on Java 17 or newer. Older targets remain available through Java toolchains.
- Expect embedded Kotlin 2.2 and Groovy 4 behavior in scripts and build logic.
- Check plugin compatibility floors before changing the wrapper, especially Kotlin DSL, Android, and enterprise build plugins.
- Ensure every included project maps to an existing writable directory.

See [Gradle 9 upgrade](references/gradle-9-upgrade.md) for exact compatibility floors and migration details.

### Removed build-layout and convention APIs

Do not use `-c`/`--settings-file`, `-b`/`--build-file`, `GradleBuild.buildFile`, or the removed `Convention` APIs. Use standard settings and build locations, extensions, direct task configuration, and the `base` extension.

Replace removed Kotlin DSL domain-object shortcuts and eager provider access. Apply Develocity by explicit plugin ID, stop relying on removed bundled Groovy modules and `org.gradle.util` helpers, and replace removed process helpers in build logic.

### Test tasks require explicit intent

Custom `Test` tasks no longer inherit the built-in `test` source set. Set `testClassesDirs` and `classpath`, or model the target with JVM test suites. A test task with sources, no filters, and no discovered tests now fails unless `failOnNoDiscoveredTests` is deliberately disabled.

### Archive and artifact lifecycle behavior

Archives are reproducible by default. Filesystem order, timestamps, and permissions are no longer preserved unless explicitly requested. Standard EAR, WAR, and Java artifacts join `assemble` and `archives`, but artifacts on custom visible configurations require explicit lifecycle wiring.

### API and nullability migrations

Gradle API nullness annotations use JSpecify. Kotlin extensions over `Provider<T>` commonly require `T : Any`, and nullable `Property` declarations may no longer type-check. Injected getters on Gradle subclasses require abstract classes; account for `RootComponentIdentifier` and unknown future component identifiers.

## Configuration Cache quick reference

### Enabling, suppressing, and troubleshooting

Gradle 9 suggests Configuration Cache for compatible builds but does not force it. Set `org.gradle.configuration-cache=false` to suppress the suggestion. Known unsupported features can fall back automatically; task-execution cache problems still abort.

Use the integrity check only for diagnosis because it increases cache size and read/write cost:

```properties
org.gradle.configuration-cache.integrity-check=true
```

Read-only mode consumes hits without storing misses:

```text
./gradlew --configuration-cache -Dorg.gradle.configuration-cache.read-only=true
```

### Correctness rules

- Register `onTaskCompletion` listeners through a registered build service provider.
- Incompatible tasks discard the entry even when cache problems are warnings.
- Environment-backed project properties only invalidate an entry if configuration actually read them.
- Startup `-javaagent:` agents work in normal daemons and TestKit's default daemon mode; dynamic attachment and embedded TestKit mode do not.
- A whole `ResolutionResult` can be a task `@Input` while Configuration Cache is active.

See [Configuration Cache and laziness](references/configuration-cache-and-laziness.md) for flags, provider patterns, and Isolated Projects migration.

## Common workflows

### Select and provision daemon JVMs

Daemon JVM criteria can auto-provision a missing JDK when a resolver is configured. Native Image-capable JDKs can be required for Java or daemon toolchains. `JAVA_HOME` participates in toolchain auto-detection, and daemon toolchains are stable APIs.

Keep the daemon runtime separate from compile/test toolchains. Use `updateDaemonJvm` to materialize cross-platform daemon criteria and download URLs. See [Daemon, CLI, Wrapper, and platforms](references/daemon-cli-and-platforms.md).

### Keep configuration lazy

Prefer these patterns:

```kotlin
configurations {
    val parent = dependencyScope("parent")
    resolvable("child") {
        extendsFrom(parent)
    }
}
```

Use `AttributeContainer.addAllLater(...)` for deferred attribute merging, provider overloads when publishing configuration variants, and `DomainObjectCollection.elements` when wiring a collection to task inputs without realization.

### Run unattended and diagnostic builds

- `--non-interactive` disables prompts; `org.gradle.console.interactive=false` persists the choice.
- `NO_COLOR` disables color while retaining rich-console behavior; `--console=colored` provides color without progress UI.
- `--task-graph` prints requested tasks and dependencies without execution.
- `tasks --provenance` and `help --task` identify where tasks were registered.
- `--warning-mode=all` renders structured problems and lifts the source-location cap.

### Configure modern test reporting

Gradle reports framework hierarchy, parameterized invocations, metadata, and attachments with stronger source attribution. Non-class JUnit Platform engines can supply `testDefinitionDirs`, and custom runners can use `TestEventReporterFactory`. Aggregate reports keep each source separate rather than merging identical structures.

When consuming JUnit XML, accept millisecond timestamps, nested-class filenames, properties emitted from test data, and attachment markers. See [Testing, reports, and quality tools](references/testing-and-quality.md).

### Publish components and distributions

Create ad hoc software components through the `publishing` extension's `softwareComponentFactory`. Pass `Provider<ConsumableConfiguration>` values to preserve laziness. Use `distribution-base` when a plugin needs distribution support without an automatic `main` distribution.

POM distribution management, signing behavior, distribution signatures, dependency-verification diagnostics, and repository-failure behavior are covered in [Dependencies, publishing, and distributions](references/dependencies-publishing-and-distribution.md).

### Author plugins and integrations

- Strongly typed dependency blocks have partially stable APIs, except version-catalog dependencies.
- `ProblemSpec.additionalData(...)` and Tooling API typed views carry structured custom diagnostics.
- Stream Tooling API and TestKit output rather than materializing large results.
- `ProjectLayout.settingsDirectory` resolves build-wide files without reaching through `rootProject`.
- Precompiled Kotlin Settings plugins can receive generated accessors from `kotlin-dsl`.
- Lock domain-object collection membership with `disallowChanges()` without realizing lazy entries.

See [Tooling API, Problems API, and build logic](references/tooling-problems-and-build-logic.md).

## Upgrade verification checklist

After changing a Gradle wrapper or build feature:

1. Run `./gradlew help` to validate settings, included-project paths, and plugin application.
2. Run `./gradlew tasks --all` and inspect unexpected configuration realization or task registration.
3. Run the relevant test tasks with `--warning-mode=all`; inspect console, HTML, and XML output.
4. Exercise Configuration Cache twice: the first run stores and the second loads an entry.
5. Verify archives for deterministic order, timestamp, and permissions expected by consumers.
6. Publish to a local repository and inspect Gradle Module Metadata, POM content, variants, and signatures.
7. Run integration tests through the same TestKit daemon mode used in CI.
8. Check Wrapper authentication, timeout, and retry settings without exposing credentials to unrelated hosts.

## Compatibility judgment

Prefer the wrapper, applied plugin versions, source code, and observed task behavior over assumptions. If a build is newer than this patch's frontmatter version, use the guidance only for features known to exist in the project's actual Gradle version and verify current behavior before changing the build.
