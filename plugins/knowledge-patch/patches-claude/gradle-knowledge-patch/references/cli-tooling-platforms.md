# CLI, Wrapper, Tooling API, and Platforms

## Daemon JVM selection and provisioning

### Auto-provision a daemon JVM (8.13.0)

When no installed JDK matches the daemon criteria, Gradle can download one.
Apply Foojay resolver convention plugin `0.9.0` or a custom resolver, then run:

```text
./gradlew updateDaemonJvm --jvm-version=17 --jvm-vendor=adoptium
```

The generated `gradle/gradle-daemon-jvm.properties` records the vendor and
version plus per-platform download URLs.

### Use stable daemon toolchains (9.2.0)

Daemon JVM criteria are stable and no longer emit an incubation warning.

### Bind the daemon explicitly (9.5.0)

Set `GRADLE_DAEMON_BIND_ADDRESS` to bypass address auto-detection for
client-daemon and cross-daemon traffic on unusual or multi-interface networks:

```text
GRADLE_DAEMON_BIND_ADDRESS=192.168.1.10 ./gradlew build
```

### Account for daemon housekeeping (9.4.0)

Daemon logs older than 14 days are removed automatically at daemon shutdown.

## Wrapper and distribution transport

### Interpret release numbers using SemVer (9.0.0)

Gradle 9 and newer use `MAJOR.MINOR.PATCH`. This does not rename older releases
or their backports. Internal and `@Incubating` features are outside the public
SemVer compatibility guarantee and may still change in a minor release.

### Select partial versions (9.0.0)

For Gradle 9 or newer, `wrapper --gradle-version` accepts a major or major/minor
selector and resolves its latest matching release:

```text
./gradlew wrapper --gradle-version=9
./gradlew wrapper --gradle-version=9.1
```

Do not apply this interpretation to older releases: a value such as `8.12` is
an exact historical version.

### Use bearer credentials (9.4.0)

Wrapper downloads accept bearer tokens supplied through system properties.
Bearer authentication takes priority over Basic authentication. Restrict both
credential types per host so secrets are not sent to unintended servers.

### Retry downloads deliberately (9.5.0)

Retries are off by default. Configure the attempt count and initial delay in
`gradle-wrapper.properties`; the delay doubles after each failure:

```properties
retries=3
retryBackOffMs=1000
```

### Use the stable timeout API (9.6.1)

`Wrapper.getNetworkTimeout()` is stable and covered by Gradle's compatibility
guarantees.

### Upgrade past the initial 9.7 release (9.7.0)

Use Gradle 9.7.1 rather than 9.7.0 to restore compatibility for `BaseExecSpec`
streams, failed-test diff formatting, KAPT isolation from bundled ANTLR,
existing `Transformer` implementations, Ant tasks with explicit classpaths,
and Kotlin DSL `@Option` annotation arguments.

## Command-line inspection and console behavior

### Inspect transforms and task graphs (8.13.0, 9.1.0)

Run `./gradlew artifactTransforms` to list each registered transform, its action
type, cacheability, and input/output attributes. Use the incubating
`--task-graph` option to print requested tasks and dependencies without running
them:

```text
./gradlew root r2 --task-graph
```

### Locate projects and task registrations (9.1.0, 9.5.0)

The Project Report shows physical filesystem locations alongside logical build
paths. Non-verification task failures and `help --task` identify the script or
plugin that registered a task; request the same information in listings with:

```text
./gradlew tasks --provenance
```

### Choose console output (9.1.0, 9.2.0, 9.6.1)

- `--console=colored` adds color without rich progress rendering.
- Windows ARM64/AArch64 is supported, including ARM-hosted VMs, but its rich
  console is unavailable; automatic selection and `--console=rich` use plain
  output.
- A non-empty `NO_COLOR` suppresses color while retaining other rich styling,
  including progress bars and animations.

### Disable prompts (9.6.1)

Use `--non-interactive` for one invocation or persist the behavior with:

```properties
org.gradle.console.interactive=false
```

### Create a project in another directory (9.5.0)

`gradle init --into my-new-project` targets that directory and creates it when
needed.

### Publish an unconfigured Build Scan (9.5.0)

`--develocity-url` publishes a Build Scan to the named server without project
configuration:

```text
./gradlew --develocity-url https://develocity.example.com build
```

## Tooling API and TestKit

### Stream custom client values (8.13.0)

Asynchronous Tooling API streaming is stable. Register a
`StreamedValueListener` with `BuildActionExecuter.setStreamedValueListener(...)`
and send serializable values from an action with `BuildController.send(...)`.

### Control Tooling API parallelism (9.4.0)

`org.gradle.tooling.parallel` controls parallel Tooling API actions separately
from `org.gradle.parallel`; when absent, it inherits `org.gradle.parallel`.

```properties
org.gradle.tooling.parallel=true
org.gradle.parallel=false
```

### Query version and help without a build (9.4.0)

`BuildEnvironment.getVersionInfo()` returns the exact `gradle --version` text
without starting a daemon. The `Help` model returns rendered `gradle --help`
through `getRenderedText()`.

### Stream TestKit output (9.3.0)

`BuildResult.getOutputReader()` returns a `BufferedReader` for incremental
processing of high-volume runner output. Close the reader after use.

## Composite builds and file watching

### Make dry runs include included builds (9.1.0)

`--dry-run` prevents execution-phase tasks in included builds from running.
Tasks invoked by an included build's configuration logic may still run during
configuration.

### Watch with a custom project cache (9.7.0)

File watching works when `--project-cache-dir` or `org.gradle.projectcachedir`
moves project state elsewhere, even when the destination filesystem cannot be
watched:

```text
./gradlew build --watch-fs --project-cache-dir /custom/path
```
