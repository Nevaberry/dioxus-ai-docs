# Daemon, CLI, Wrapper, and Platforms

## Daemon JVM selection

### Auto-provision missing JVMs

Since `8.13.0`, Gradle can download a JDK when no installed JDK matches the Daemon JVM criteria. Apply Foojay resolver plugin 0.9.0 or a custom resolver, then run `updateDaemonJvm`:

```kotlin
plugins {
    id("org.gradle.toolchains.foojay-resolver-convention") version "0.9.0"
}
```

```text
./gradlew updateDaemonJvm --jvm-version=17 --jvm-vendor=adoptium
```

The resulting `gradle/gradle-daemon-jvm.properties` records requested vendor and version criteria plus per-platform download URLs.

### Native Image-capable toolchains

Since `8.14.0`, Java and Daemon JVM toolchain selection can require a JDK that provides GraalVM Native Image:

```kotlin
java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
        nativeImageCapable = true
    }
}
```

### Stable daemon toolchains

Since `9.2.0`, daemon toolchains are stable and covered by Gradle's backward-compatibility guarantees. Daemon JVM criteria no longer emit an incubation warning.

### Runtime compatibility

The Gradle 9 daemon needs Java 17 or newer. Compilation, tests, and workers may still use older target toolchains. Since `9.0.0`, Java toolchain auto-detection includes the JDK referenced by `JAVA_HOME`.

Gradle `9.1.0` can run its daemon on Java 25 and use Java 25 toolchains. Tooling API clients on Java 25 must enable native access at startup because the API uses JNI; third-party tool compatibility can lag.

Gradle `9.4.0` adds Java 26 support for both the daemon and toolchains. Check third-party tools separately.

## Daemon networking and cleanup

### Bind a specific address

Since `9.5.0`, `GRADLE_DAEMON_BIND_ADDRESS` bypasses address auto-detection and selects the address used for client-daemon and cross-daemon communication:

```text
GRADLE_DAEMON_BIND_ADDRESS=192.168.1.10 ./gradlew build
```

Use it on multi-interface hosts and networks where automatic selection is unsuitable.

### Log retention

Since `9.4.0`, daemon logs older than 14 days are removed automatically when the daemon shuts down.

## Wrapper version selection

Since `9.0.0`, the Wrapper accepts major and major/minor selectors and resolves the latest matching release:

```text
./gradlew wrapper --gradle-version=9
./gradlew wrapper --gradle-version=9.1
```

This interpretation applies to Gradle 9 or newer. Pre-9 values such as `8.12` are already exact historical versions.

## Wrapper network behavior

### Bearer authentication

Since `9.4.0`, Wrapper distribution downloads accept bearer tokens supplied through system properties. Bearer credentials take priority over Basic credentials. Restrict both authentication types per host so credentials are not sent to unintended servers.

### Retries and backoff

Since `9.5.0`, retries remain disabled by default but can be enabled in `gradle-wrapper.properties`. `retryBackOffMs` is the initial delay and doubles after each failed attempt:

```properties
retries=3
retryBackOffMs=1000
```

### Network timeout API

Since `9.6.1`, `Wrapper.getNetworkTimeout()` is stable rather than incubating and is covered by Gradle's backward-compatibility guarantees.

## Console and unattended execution

### Colored plain console

Since `9.1.0`, `--console=colored` adds color without rich-console features such as progress bars:

```text
./gradlew build --console=colored
```

### Disable color only

Since `9.6.1`, a non-empty `NO_COLOR` environment variable suppresses color but retains other styling and rich-console behavior such as progress bars and animations:

```text
NO_COLOR=1 ./gradlew build
```

### Disable all prompts

Since `9.6.1`, use `--non-interactive` for unattended builds or persist the setting with a Gradle property:

```text
./gradlew --non-interactive build
```

```properties
org.gradle.console.interactive=false
```

## Inspection and dry runs

### Task graph

Since `9.1.0`, the incubating `--task-graph` option prints requested tasks and dependencies without executing them:

```text
./gradlew root r2 --task-graph
```

### Composite builds

Since `9.1.0`, `--dry-run` also prevents execution-phase tasks in included builds from running. Tasks invoked by included-build configuration logic may still execute during configuration.

### Project locations

Since `9.1.0`, the Project Report prints each project's physical filesystem location beside its logical build path. Use it to diagnose non-standard project layouts.

### Task provenance

Since `9.5.0`, failures from non-verification tasks identify the build script, settings script, or plugin that registered the task. `help --task` includes the same provenance, and task listings expose it on request:

```text
./gradlew tasks --provenance
```

## Project creation and Build Scans

### Initialize into a target directory

Since `9.5.0`, `init --into` creates the target directory when necessary and generates the project there:

```text
gradle init --type java-application --into my-new-project
```

### Publish without project configuration

Since `9.5.0`, `--develocity-url` publishes a Build Scan to a selected Develocity server without project configuration:

```text
./gradlew --develocity-url https://develocity.example.com build
```

## Platform behavior

### Windows ARM64

Since `9.2.0`, Gradle runs on Windows ARM64/AArch64, including Windows virtual machines hosted on ARM. The rich console is unavailable, so default console selection and `--console=rich` fall back to plain output.

### File watching with a custom project cache

Since `9.7.0`, file system watching works when `--project-cache-dir` or `org.gradle.projectcachedir` moves project state elsewhere, even if the target file system does not itself support watching:

```text
./gradlew build --watch-fs --project-cache-dir /custom/path
```

## Patch-level guard for the 9.7 line

If upgrading into the Gradle 9.7 line, use `9.7.1` rather than `9.7.0`. It restores compatibility for:

- `BaseExecSpec` streams
- Failed-test diff formatting
- KAPT classpath isolation from bundled ANTLR
- Existing `Transformer` implementations
- Explicit-classpath Ant tasks
- Kotlin DSL `@Option` annotation arguments

## Operational checklist

- Keep launcher JVM, daemon JVM, and compile/test toolchains conceptually separate.
- Commit daemon criteria generated by `updateDaemonJvm` when builds need repeatable cross-platform selection.
- Scope Wrapper credentials by host and test retry behavior against transient failures.
- Use `--non-interactive` in automation that must never wait for input.
- Verify console fallback on Windows ARM64 and file watching when relocating project cache state.
