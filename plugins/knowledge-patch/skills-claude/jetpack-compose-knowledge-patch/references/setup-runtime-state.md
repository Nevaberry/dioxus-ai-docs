# Setup, Runtime, and State

## Build and Dependency Setup

### Android and Kotlin floors (`1.10.0`, `compiler-toolchain`)

Compose Animation, Foundation, Runtime, and UI require `minSdk` 23 from
1.10.0. Consumers of artifacts built with Kotlin 2.0 need Kotlin Gradle Plugin
2.0.0 or newer.

Starting with Compose 1.12.0, Android projects also need Android Gradle Plugin 9
and `compileSdk 37` (written as `compileSdk = 37` in Kotlin DSL). This does not
force `targetSdk = 37`.

```kotlin
android {
    compileSdk = 37
}
```

### Lint floor (`1.9.0`)

Compose lint checks require AGP 8.8.2 or newer and Android Studio Ladybug or
newer. When the project must remain on an older AGP, select standalone Lint
8.8.2 or newer in `gradle.properties`:

```properties
android.experimental.lint.version=8.8.2
```

### Compiler reports and stability configuration (`compiler-toolchain`)

Configure reports and a root-project stability file through the module-level
`composeCompiler` block:

```kotlin
composeCompiler {
    reportsDestination = layout.buildDirectory.dir("compose_compiler")
    stabilityConfigurationFile =
        rootProject.layout.projectDirectory.file("stability_config.conf")
}
```

### Stable BOM setup (`compiler-toolchain`)

Import `androidx.compose:compose-bom:2026.06.00` in both application and
instrumented-test configurations, then omit versions from managed Compose
libraries:

```kotlin
dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2026.06.00")
    implementation(composeBom)
    androidTestImplementation(composeBom)
    implementation("androidx.compose.material3:material3")
}
```

### Testing-channel BOMs (`bom-versioning`)

`compose-bom-alpha` selects each library's latest alpha, beta, RC, or stable
release. `compose-bom-beta` selects its latest beta, RC, or stable release.
These BOMs are intended for testing and may contain a mixture of stable and
prerelease libraries.

```kotlin
dependencies {
    val composeBom =
        platform("androidx.compose:compose-bom-beta:2026.06.00")
    implementation(composeBom)
}
```

### Multiplatform artifact expansion (`1.9.0`, `1.10.0`)

`androidx.compose.runtime:runtime` publishes desktop, iOS, and native targets
through Google Maven. This applies only to Runtime, not to all AndroidX Compose
artifacts. The `runtime-rxjava2` and `runtime-rxjava3` artifacts are also
multiplatform and include JVM as a target from 1.10.0.

### JSpecify nullness (`1.8.0`)

Compose UI carries type-use JSpecify annotations. Kotlin can enforce them with
`-Xjspecify-annotations=strict`; this is already the default in Kotlin 2.1.0.

## Runtime Annotations and Diagnostics

### Annotations without Runtime (`1.9.0`)

Non-Compose modules can depend on `runtime-annotation` to use `@Stable`,
`@Immutable`, and `@StableMarker` without taking a Runtime dependency. It also
provides:

- `@FrequentlyChangingValue`, whose lint warns about direct composition reads.
- `@RememberInComposition`, whose lint rejects construction or calls in
  composition unless remembered.

### Frequently changing scroll state (`1.10.0`)

`PagerState.currentPageOffsetFraction` and `ScrollState.value` carry
`@FrequentlyChangingValue`. Avoid direct composition reads when the result can
be consumed in a draw, layout, or snapshot-flow path instead.

### Compose stack traces (`1.9.0`, `1.10.0`)

`setDiagnosticStackTraceEnabled` is experimental. Compose stack traces include
work launched by `LaunchedEffect` and `rememberCoroutineScope`.

For minified apps, `ComposeStackTraceMode.GroupKeys` uses compiler-generated
group-key mappings. It is off by default; the Compose compiler Gradle plugin
starts producing the required mapping with Kotlin 2.3.0.

### Recomposer diagnostics (`1.11.0`)

The experimental concurrent-recomposition API was removed. Tooling can inspect
the experimental `RecomposerInfo.errorState` instead when reporting recomposer
failures.

## Snapshots and Composition Lifecycle

### Snapshot identifiers (`1.8.0`)

Use `Snapshot.snapshotId`, not deprecated `Snapshot.id`. The widened identifier
avoids `Int` overflow in long-running, high-frame-rate processes. Arithmetic
and special `SnapshotId` constants are internal; convert with `toInt()` or
`toLong()` only when arithmetic is unavoidable.

### Pausable composition (`1.8.0`, `1.9.0`)

`PausableComposition` can pause a subcomposition during composition and apply
it asynchronously, provided the compiler supports pausing. It exposes
`isApplied` and `isCancelled`. Dispose a cancelled instance; reuse now throws.

### End-of-composition work (`1.10.0`)

`awaitOrScheduleNextCompositionEnd()` runs a callback after the current frame's
composition. If the recomposer is idle, it schedules and waits for the next
frame. Composition-local providers may return a non-`Unit` value, and
composition-registration observers run before initial composition.

### Composite-key hashes (`1.9.0`)

Replace deprecated `currentCompositeKeyHash` with
`currentCompositeKeyHashCode`, which retains more hash bits and sharply lowers
unrelated composition-group collisions.

## Saveable State

### Collections and serializers (`1.9.0`)

On Android, `SnapshotStateList` and `SnapshotStateSet` are `Parcelable` and can
be used with `rememberSaveable`. Use `rememberSerializable` for a
`KSerializer`; the `Saver`-based `rememberSaveable` remains supported.

### Positional scoping and owners (`1.9.0`)

The custom-`key` overload of `rememberSaveable` is deprecated because it
bypasses positional scoping and can share or lose state, especially in nested
lazy layouts. Remove the key.

Import `LocalSavedStateRegistryOwner` from `androidx.savedstate.compose`.
`SaveableStateHolder.SaveableStateProvider` now supplies that owner to its
content.

## Retained Values

### Choosing retained state (`1.10.0`)

`retain` preserves a value after its composable leaves the hierarchy without
serializing it. Its lifetime is shorter than saveable state. Android's
lifecycle-aware retain scope carries values across configuration changes.

Keys passed to `retain` are retained as well. Avoid resource-owning keys or
values that can leak, and mark types that must never be retained with
`@DoNotRetain`.

### Effects and stores (`1.10.0`, `1.11.0`)

`RetainedEffect` follows retention rather than composition. The
`RetainObserver.onUnused` callback corresponds to
`RememberObserver.onAbandoned`.

Custom stores implement `RetainedValuesStore`. Prefer
`ManagedRetainedValuesStore`, and install the store through
`LocalRetainedValuesStoreProvider` rather than directly providing
`LocalRetainedValuesStore`:

```kotlin
val store = retainManagedRetainedValuesStore()
LocalRetainedValuesStoreProvider(store) { content() }
```

Replace `RetainedValuesStore.getExitedValueOrDefault` with the renamed
`consumeExitedValueOrDefault`.

## Removed Runtime Flags (`1.11.0`)

Delete assignments to removed runtime flags
`isMovingNestedMovableContentEnabled` and
`isMovableContentUsageTrackingEnabled`. Their former compatibility paths are
no longer selectable.
