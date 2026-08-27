---
name: gradle-knowledge-patch
description: Gradle
version: "9.6.1"
license: MIT
metadata:
  author: Nevaberry
---


# Gradle Knowledge Patch

Load this skill when writing, reviewing, debugging, or upgrading Gradle builds,
plugins, Tooling API clients, or test infrastructure. Inspect the project's
wrapper, build scripts, settings, plugin versions, JVM selection, and tests
before applying guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [CLI, tooling, and platforms](references/cli-tooling-platforms.md) | Wrapper, console, daemon, reports, Tooling API, TestKit, platforms |
| [Configuration Cache and modeling](references/configuration-cache-modeling.md) | Configuration Cache, Isolated Projects, lazy configuration, providers, collections |
| [Dependencies, publishing, and distributions](references/dependencies-publishing-distributions.md) | Dependency resolution, verification, publications, signing, archives, distributions |
| [JVM, languages, and build logic](references/jvm-languages-build-logic.md) | JVM toolchains, Kotlin, Groovy, Scala, ANTLR, native builds, plugin authoring |
| [Gradle 9 migration](references/migration-gradle-9.md) | Runtime floors, removed APIs and options, changed defaults, migration replacements |
| [Testing, quality, and problems](references/testing-quality-problems.md) | Test discovery, reports, metadata, Problems API, validation, PMD |

## First-pass compatibility audit

1. Read `gradle/wrapper/gradle-wrapper.properties`; do not infer the Gradle
   version from a locally installed executable.
2. Identify the daemon JVM separately from Java compilation and test
   toolchains. A build can target an older JVM than the one running Gradle.
3. Inventory Kotlin, Groovy, Android, Develocity, Plugin Publishing, quality,
   and test-framework plugin versions before changing the wrapper.
4. Search build logic for removed conventions, process helpers, Kotlin DSL
   shortcuts, custom archive behavior, and implicit test inputs.
5. Run representative builds with Configuration Cache and review its report;
   warning mode does not preserve entries for incompatible tasks.
6. Inspect publications, archive contents and metadata, dependency verification,
   test discovery, and included-project directories after an upgrade.

## Breaking changes and required migrations

### Run the daemon on a supported JVM

- Gradle 9 daemons require Java 17 or newer. Launchers and clients may start on
  Java 8 only if they can locate a Java 17+ daemon.
- Keep compilation, tests, and workers on their intended Java toolchains; do
  not raise target compatibility merely to satisfy the daemon.
- Apply `jvm-toolchains` when using `ValidatePlugins` without another JVM
  plugin, and enable native access when starting Tooling API clients on Java 25.

### Update Kotlin and Groovy build logic

- Gradle 9 embeds Kotlin 2.2 and Groovy 4. Recompile plugins and fix changed
  Kotlin nullability bounds, Groovy package or module changes, and dynamic
  delegate lookup assumptions.
- Replace Kotlin script-instance labels with `project`, `settings`, or `gradle`.
  Remove `"name"()` domain-object shortcuts, eager provider access, catalog
  library or bundle access in `plugins {}`, and `kotlinDslPluginOptions.jvmTarget`.
- Do not rely on Groovy child projects finding missing properties or methods in
  a parent. Qualify access and use the rejection preview during migration.
- Add explicit dependencies for `groovy-test`, `groovy-console`, and
  `groovy-sql`; `localGroovy` no longer supplies them.

### Replace removed Gradle APIs

- Remove `-c`/`--settings-file`, `-b`/`--build-file`, and
  `GradleBuild.buildFile`; use standard settings and build layouts.
- Replace convention APIs with extensions. Configure `war` and `ear` tasks
  directly and use the `base` extension for base-plugin properties.
- Replace `Project.exec` and `Project.javaexec` and their script helpers with
  injected execution services or task types.
- Replace integer Unix modes with `FilePermissions`, `IBM_SEMERU` with `IBM`,
  legacy IDEA test directories with `testSources` and `testResources`, and
  `WriteProperties.outputFile` with `destinationFile`.
- Replace `GroovySourceSet` and `ScalaSourceSet` with their source-directory-set
  counterparts. Expose `Action` methods instead of removed `org.gradle.util`
  closure helpers.

### Make test tasks explicit

- Custom `Test` tasks no longer inherit classes or runtime classpaths from the
  built-in `test` task. Configure both or create a JVM test suite.
- A test task fails when sources exist but no tests are discovered and no
  filters apply. Set `failOnNoDiscoveredTests = false` only for an intentionally
  empty result.
- For non-class JUnit Platform engines, configure `testDefinitionDirs`; do not
  create dummy suite classes merely to trigger discovery.

### Recheck archives and publications

- Archive tasks are reproducible by default: sorted entries, fixed timestamps,
  and normalized directory and file permissions. Opt back into filesystem
  metadata only for consumers that require it.
- A visible outgoing configuration does not join `assemble` or `archives`
  automatically. Wire its artifact into both lifecycles explicitly.
- Do not mutate Gradle Module Metadata after an eagerly created publication has
  been populated from the same component. Signing follows the key's OpenPGP
  signature version.

### Enforce stricter project and plugin contracts

- Every included project directory must exist, be writable, and be a directory.
- Make Gradle-derived classes abstract when they expose `@Inject` getters.
- Treat `ConfigurationVariant.description` as `Property<String>` and handle
  `RootComponentIdentifier` plus future component-identifier implementations.
- Give every `@Optional` plugin property an input or output annotation; use
  `@Internal` alone for ignored properties.

## Configuration Cache and isolation

### Understand fallback and failure behavior

- Configuration Cache is preferred but optional. Known unsupported features
  can trigger a documented non-cache fallback; a task-execution cache problem
  aborts immediately.
- Incompatible tasks discard the entry even with
  `org.gradle.configuration-cache.problems=warn`.
- Task-completion listeners must be providers from registered build services.
  Use the unsupported-listener escape hatch only as temporary migration aid.

### Diagnose cache behavior deliberately

- Enable `org.gradle.configuration-cache.integrity-check=true` only while
  troubleshooting because it increases entry size and slows cache I/O.
- Read-only mode can consume an existing entry without writing one, which suits
  untrusted or ephemeral CI jobs.
- Environment-backed project properties invalidate an entry only when read
  during configuration. Providers consumed solely during execution can observe
  a changed value while the entry is reused.

### Keep configuration lazy

- Prefer `register` and role-based configuration factories to `create`.
- Pass providers to configuration inheritance and publishing variant APIs.
- Use `AttributeContainer.addAllLater` when source attributes must remain lazy;
  imported values track the source, but later destination values win.
- Use `DomainObjectCollection.elements` to carry collection values and task
  dependencies without forcing realization; use `disallowChanges()` to freeze
  membership without freezing contained objects.

### Treat Isolated Projects as a migration mode

- Enable with `--isolated-projects` or `org.gradle.isolated-projects=true`.
  The `org.gradle.unsafe` names are deprecated aliases.
- Remove mutable cross-project and build access. Use diagnostics to find
  violations; dangerous-ignore mode is experimental migration scaffolding,
  not a production setting.

## High-value current capabilities

### Provision and select JVMs

- Daemon JVM criteria can auto-provision a matching JDK when a resolver is
  installed; `updateDaemonJvm` records per-platform URLs and criteria.
- Toolchains can require GraalVM Native Image, and `JAVA_HOME` participates in
  Java toolchain auto-detection.
- Daemon toolchains are stable. Java 25 and Java 26 can run the daemon and serve
  as toolchains, subject to third-party tool compatibility.

### Improve unattended command-line builds

- Use `--non-interactive` or `org.gradle.console.interactive=false` to disable
  prompts. Use `NO_COLOR` to suppress color without disabling rich-console
  progress and animation.
- Use `--console=colored` for color without rich rendering, `--task-graph` to
  visualize dependencies without execution, and `tasks --provenance` to find
  task registration sites.
- Configure Wrapper retries and bearer authentication carefully, restrict
  credentials by host, and prefer signed distributions for authenticity.

### Build richer test and problem integrations

- Test-event reporters can emit nested Gradle binary and HTML results with
  timestamped metadata for externally run tests.
- JUnit Platform data and attachments flow into HTML and XML, and metadata
  listeners expose the structured events to build logic.
- Problems can carry typed structured additional data that Tooling API clients
  retrieve through matching view interfaces.
- Stream large TestKit output through `BuildResult.getOutputReader()` and close
  the reader after processing.

### Use lazy publishing and distributions

- `distribution-base` provides distribution support without creating `main`.
- Create ad hoc components from the publishing extension and pass
  `Provider<ConsumableConfiguration>` to variant methods to avoid realization
  until publication.
- Configure Maven POM distribution management directly on `MavenPublication`.

## Verification checklist

- Run `./gradlew help`, the relevant build and verification tasks, and at least
  one representative Configuration Cache reuse cycle.
- Confirm the daemon JVM and each Java toolchain with diagnostic output.
- Check that custom tests execute, framework initialization failures are
  visible, and HTML/XML report consumers accept the current schema and timing.
- Inspect `artifactTransforms`, task provenance, publication metadata, archive
  entry order and timestamps, and dependency-verification diagnostics where
  relevant.
- Re-run composite and included builds, especially those with custom project
  directories or configuration-time task execution.
