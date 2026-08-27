# Android Hosts, Windows, and Insets

Use this reference for Compose hosted in Android Views or nonstandard windows, configuration-aware resources, window geometry, and inset propagation.

## Layout rectangles and window size (1.8.0)

`Modifier.onLayoutRectChanged` observes root-, window-, or screen-relative bounds. It supports debounce and throttle controls and has lower overhead than `onGloballyPositioned` for this purpose.

Read the current content-container size from `LocalWindowInfo.current.containerSize`. Do not derive window size from configuration screen dimensions; lint reports that pattern.

## Recalculating descendant insets (1.8.0)

Use `Modifier.recalculateWindowInsets()` when an ancestor aligns content without calling `consumeWindowInsets()` and descendants still need correct `insetsPadding` values.

## ComposeView inset pass-through (1.9.0)

`AbstractComposeView.consumeWindowInsets` defaults to `false`. Compose adjusts insets for the view's size and position while allowing child Views to continue receiving inset updates. Set it to `true` only to preserve consuming behavior.

The common `WindowInsetsRulers` API replaces `InsetsRulers`:

- merge rulers with `innermostOf()`;
- use `maximum` instead of `rulersIgnoringVisibility`;
- use `WindowInsetsAnimation` with `getAnimation()` for animation data.

## Configuration-aware resources (1.9.0)

Use `LocalResources.current` for Android resource lookup that must react to configuration changes. Reading it invalidates composition so later lookups observe the new configuration.

## Window geometry and cutouts (1.10.0)

`WindowInfo` exposes window size in dp. `WindowInsets.cutoutPath` exposes the actual display-cutout outline for layouts that need more than inset distances.

## Android constant and parser changes (1.10.0)

`TextDirection`, `TextAlign`, `Hyphens`, and `FontSynthesis` `valueOf` functions throw `IllegalArgumentException` for unknown values. Do not rely on permissive parsing.

The Android-derived `UiModes` constants object is renamed to `AndroidUiModes`.

## Host-default composition locals (1.11.0)

`compositionLocalWithHostDefaultOf` allows a fallback supplied by the hosting environment, such as an Android `View` tag. `HostDefaultKey` is an interface. Custom hosts use `HostDefaultProvider` and `LocalHostDefaultProvider` to provide platform values.

## Composing before View attachment (1.11.0)

`ComposeViewContext` allows a `ComposeView` to compose before it is attached to a View hierarchy:

```kotlin
composeView.createComposition(composeViewContext)
```

The entry point is `AbstractComposeView.createComposition(composeViewContext)`.

## Dialog and popup host windows (1.11.0)

Android Compose dialogs accept a custom `windowToken`. Popups accept custom `windowToken` and `windowType` values. `DialogProperties.windowType` also lets a service show a Compose dialog in an overlay window.

Use these values deliberately: the hosting token and window type determine where Android attaches and layers the window.

## Per-view inset ruler control (1.11.0)

Replace the global `ComposeUiFlags.areWindowInsetsRulersEnabled` flag with the per-view `ComposeView.disableWindowInsetsRulers()` API.

## Android paint interop (1.11.0)

The `androidx.compose.ui.graphics.NativePaint` typealias is deprecated. Use `android.graphics.Paint` directly on Android.

Replace `Paint.asFrameworkPaint()` with the `Paint.nativePaint` extension. This keeps common APIs from exposing Android through the deprecated typealias while preserving access to the native paint object on Android.
