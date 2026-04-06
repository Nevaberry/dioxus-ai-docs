# Kotlin Build & Tooling Changes

## Compose Compiler Merged into Kotlin (2.0)

The Compose compiler is now a Kotlin compiler plugin. Apply `org.jetbrains.kotlin.plugin.compose` instead of the old separate Compose compiler artifact. Version matches the Kotlin version.

```kotlin
plugins {
    kotlin("multiplatform") version "2.0.0"
    kotlin("plugin.compose") version "2.0.0"
}
```

**Migration:** Remove any explicit Compose compiler version configuration and the old `compose-compiler` dependency. The plugin handles everything.

## Power-assert Compiler Plugin (2.0, Experimental)

Generates detailed failure messages showing intermediate expression values in assertions.

```kotlin
plugins {
    kotlin("plugin.power-assert") version "2.0.0"
}
powerAssert {
    functions = listOf("kotlin.assert", "kotlin.test.assertTrue")
}
```

When an assertion fails, the output shows each sub-expression's value, similar to Groovy's power assert or Rust's `assert_eq!` with custom messages.

## KMP Android Target Migration (2.3)

Use Google's `com.android.kotlin.multiplatform.library` Gradle plugin for KMP Android targets. Rename `androidTarget` blocks to `android` in your KMP configuration. The old `kotlin-android` plugin is deprecated with AGP 9.0+.
