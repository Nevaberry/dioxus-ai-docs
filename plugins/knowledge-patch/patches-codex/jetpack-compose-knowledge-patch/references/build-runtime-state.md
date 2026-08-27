# Build, Runtime, and State

Use this reference for dependency setup, compiler configuration, Runtime behavior, and state lifetime. Resolve each artifact independently when a project does not use a BOM.

## Android and Kotlin build floors

### Compose lint (1.9.0)

Compose lint checks require Android Gradle Plugin 8.8.2 or newer and Android Studio Ladybug or newer. A project that must remain on an older AGP can select standalone Lint 8.8.2 or newer in `gradle.properties`:

```properties
android.experimental.lint.version=8.8.2
```

### Platform and Kotlin requirements (1.10.0)

Compose Animation, Foundation, Runtime, and UI require Android API 23 or newer rather than API 21. Consuming artifacts built with Kotlin 2.0 also requires Kotlin Gradle Plugin 2.0.0 or newer.

### Compose 1.12 Android toolchain (compiler-toolchain)

Android projects using Compose 1.12.0 require `compileSdk = 37` and Android Gradle Plugin 9. `compileSdk` is independent of `targetSdk`; meeting the compile requirement does not itself opt the app into target SDK 37 behavior.

```kotlin
android {
    compileSdk = 37
}
```

### Compiler reports and stability configuration (compiler-toolchain)

Configure reports and the stability file in the module-level `composeCompiler` block:

```kotlin
composeCompiler {
    reportsDestination = layout.buildDirectory.dir("compose_compiler")
    stabilityConfigurationFile =
        rootProject.layout.projectDirectory.file("stability_config.conf")
}
```

## BOM selection

### Stable BOM setup (compiler-toolchain)

The corresponding stable setup imports `androidx.compose:compose-bom:2026.06.00` for both application and instrumented-test configurations. Dependencies governed by the BOM omit individual versions.

```kotlin
dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2026.06.00")
    implementation(composeBom)
    androidTestImplementation(composeBom)
    implementation("androidx.compose.material3:material3")
}
```

### Prerelease-channel BOMs (bom-versioning)

`compose-bom-alpha` selects each library's newest alpha, beta, RC, or stable release. `compose-bom-beta` selects each library's newest beta, RC, or stable release. These testing BOMs may therefore resolve some components to stable versions and others to prereleases.

```kotlin
dependencies {
    val composeBom = platform("androidx.compose:compose-bom-beta:2026.06.00")
    implementation(composeBom)
}
```

## Nullness and runtime annotations

### JSpecify annotations (1.8.0)

Compose UI publishes type-use JSpecify nullness annotations. Kotlin can enforce them with `-Xjspecify-annotations=strict`; Kotlin 2.1.0 already uses strict mode by default.

### Annotations without a Runtime dependency (1.9.0)

The `runtime-annotation` library lets non-Compose modules use `@Stable`, `@Immutable`, and `@StableMarker` without depending on Compose Runtime. It also supplies:

- `@FrequentlyChangingValue`, whose lint warns about direct reads during composition.
- `@RememberInComposition`, whose lint rejects construction or calls in composition that are not remembered.

## Artifact target expansion

### Multiplatform Runtime (1.9.0)

`androidx.compose.runtime:runtime` from Google Maven includes desktop, iOS, and native targets in addition to Android. This applies to Runtime artifacts only, not the rest of AndroidX Compose.

### RxJava Runtime (1.10.0)

`runtime-rxjava2` and `runtime-rxjava3` are multiplatform artifacts and include JVM as a supported target.

## Snapshots and composition identity

### Snapshot IDs (1.8.0)

Use `Snapshot.snapshotId` instead of deprecated `Snapshot.id`. The wider identifier avoids `Int` overflow in long-running, high-frame-rate processes. `SnapshotId` arithmetic and special constants are internal; convert with `toInt()` or `toLong()` only where arithmetic is required.

### Composite key hashes (1.9.0)

Replace deprecated `currentCompositeKeyHash` with `currentCompositeKeyHashCode`. The newer value carries more hash bits and reduces collisions between unrelated composition groups.

## Pausable composition

### Pausing and asynchronous apply (1.8.0)

`PausableComposition` can pause a subcomposition during composition and apply it asynchronously. The feature requires corresponding compiler support.

### Lifecycle requirements (1.9.0)

Inspect `PausableComposition.isApplied` and `isCancelled` to determine state. Dispose a cancelled pausable composition; reusing it throws.

## Saveable state

### Collections and serialization (1.9.0)

On Android, `SnapshotStateList` and `SnapshotStateSet` are `Parcelable`, so `rememberSaveable` can store them. Use `rememberSerializable` for the `KSerializer`-based overload; the `Saver`-based API retains the `rememberSaveable` name.

### Positional scoping and registry owners (1.9.0)

Remove the deprecated custom `key` parameter from `rememberSaveable`. It bypasses positional scoping and can share or lose state, particularly inside nested lazy layouts.

Import `LocalSavedStateRegistryOwner` from `androidx.savedstate.compose`. `SaveableStateHolder.SaveableStateProvider` supplies that owner to its content.

## Retained state

### Choosing `retain` (1.10.0)

`retain` keeps a value after its composable leaves the hierarchy without serializing it. Its lifetime is shorter than saveable state. Android's lifecycle-aware retain scope carries retained values across configuration changes.

Keys passed to `retain` are themselves retained. Avoid keys that hold resources or other leak-prone objects, and annotate unsuitable types with `@DoNotRetain`.

### Effects and custom stores (1.10.0)

`RetainedEffect` follows retention rather than composition lifetime. `RetainObserver.onUnused` corresponds to `RememberObserver.onAbandoned`.

Custom stores implement `RetainedValuesStore`, normally through `ManagedRetainedValuesStore`, and are installed with `LocalRetainedValuesStoreProvider`; do not directly provide `LocalRetainedValuesStore`.

```kotlin
val store = retainManagedRetainedValuesStore()
LocalRetainedValuesStoreProvider(store) { content() }
```

### Runtime retention migrations (1.11.0)

Rename `RetainedValuesStore.getExitedValueOrDefault` to `consumeExitedValueOrDefault`. The experimental concurrent-recomposition API is removed. Tooling can inspect the experimental `RecomposerInfo.errorState`.

## Runtime completion and host defaults

### Composition completion (1.10.0)

`awaitOrScheduleNextCompositionEnd()` invokes a callback after the current frame's composition. If the recomposer is idle, it schedules and waits for the next frame. Composition-local providers may now return non-`Unit` values, and composition-registration observers run before initial composition.

### Host-provided defaults (1.11.0)

`compositionLocalWithHostDefaultOf` defines a composition local whose fallback can come from the host, such as an Android `View` tag. `HostDefaultKey` is an interface; `HostDefaultProvider` and `LocalHostDefaultProvider` allow custom hosts to supply platform-specific values.

## Diagnostics

### Compose stack traces (1.9.0)

`setDiagnosticStackTraceEnabled` is experimental. Compose stack traces include work launched by `LaunchedEffect` and `rememberCoroutineScope`.

### Group-key traces in minified apps (1.10.0)

`ComposeStackTraceMode.GroupKeys` enables Compose stack traces in minified applications. It is disabled by default. Starting with Kotlin 2.3.0, the Compose compiler Gradle plugin generates the required group-key mapping.

## Removed Runtime flags (1.11.0)

Delete assignments to removed `isMovingNestedMovableContentEnabled` and `isMovableContentUsageTrackingEnabled` Runtime flags. The behaviors can no longer be selected through those switches.
