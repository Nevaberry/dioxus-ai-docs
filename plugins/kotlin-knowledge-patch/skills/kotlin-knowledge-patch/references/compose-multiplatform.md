# Compose Multiplatform 1.8–1.10

## Navigation Uses SavedState (1.8)

Navigation 2.9.x replaces `Bundle` with `SavedState`. Access arguments via `SavedState` accessors instead of `arguments?.getString()`.

## Compose Multiplatform for Web in Beta (1.9)

Web target is promoted to Beta stability.

## Navigation 3 Support (1.10)

`PredictiveBackHandler()` is deprecated in favor of `NavigationBackHandler()` from the Navigation Event library.

## Unified `@Preview` Annotation (1.10)

Use `androidx.compose.ui.tooling.preview.Preview` in `commonMain` for all platforms. Old platform-specific preview annotations are deprecated.

## Deprecated Dependency Aliases (1.10)

`compose.ui`, `compose.material3`, and similar aliases in the Gradle plugin are deprecated. Add direct library references to your version catalogs instead:

```toml
# gradle/libs.versions.toml
[libraries]
compose-ui = { group = "androidx.compose.ui", name = "ui" }
compose-material3 = { group = "androidx.compose.material3", name = "material3" }
```
