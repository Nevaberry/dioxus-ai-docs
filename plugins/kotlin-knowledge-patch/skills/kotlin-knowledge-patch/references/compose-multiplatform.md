# Compose Multiplatform 1.7–1.10

## Version Highlights

- **1.7** — Type-safe Navigation, shared element transitions
- **1.8** — Variable fonts, drag-and-drop on iOS, deep linking on iOS
- **1.9** — Compose for web Beta, customizable shadows, Material 3 Expressive, `@Preview` parameters
- **1.10** — Navigation 3 (Alpha), unified `@Preview` annotation, Compose Hot Reload

## Navigation 3 (1.10, Alpha)

Multiplatform artifacts:

```kotlin
// build.gradle.kts
implementation("org.jetbrains.androidx.navigation3:navigation3-ui:$version")
implementation("org.jetbrains.androidx.lifecycle:lifecycle-viewmodel-navigation3:$version")
implementation("org.jetbrains.compose.material3.adaptive:adaptive-navigation3:$version")
```

## Deprecations in 1.10

Compose dependency aliases (`compose.ui`, etc.) deprecated — use direct library references.

`PredictiveBackHandler()` deprecated — use `NavigationBackHandler()` from Navigation Event library.
