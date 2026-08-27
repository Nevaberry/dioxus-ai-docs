# Platform, Window, and Interop

## Geometry and Bounds

### Layout rectangle observation (`1.8.0`)

`Modifier.onLayoutRectChanged` observes root-, window-, or screen-relative
bounds. Its debounce and throttle controls make it cheaper and more precise
than using `onGloballyPositioned` for ongoing position observation.

For the current content-container size, read
`LocalWindowInfo.current.containerSize`. Compose lint warns when code derives
window size from configuration screen dimensions.

### Window geometry (`1.10.0`)

`WindowInfo` exposes window size in dp. `WindowInsets.cutoutPath` exposes the
display cutout's actual outline for shape-aware layouts.

## Window Insets and Rulers

### Recalculating insets (`1.8.0`)

Use `Modifier.recalculateWindowInsets()` when an ancestor has repositioned a
subtree without calling `consumeWindowInsets()`. Descendants can then apply
`insetsPadding` against recalculated coordinates.

### ComposeView pass-through (`1.9.0`)

`AbstractComposeView.consumeWindowInsets` defaults to `false`. Insets are
adjusted automatically for the Compose view's size and position, and child
Views continue receiving inset updates. Set it to `true` only to preserve
consuming behavior.

### Common ruler APIs (`1.9.0`)

`WindowInsetsRulers` replaces `InsetsRulers`. Merge rulers with
`innermostOf()`. The former `rulersIgnoringVisibility` property is named
`maximum`. Animation data comes through `WindowInsetsAnimation` and
`getAnimation()`.

### Per-view ruler control (`1.11.0`)

Replace the global `ComposeUiFlags.areWindowInsetsRulersEnabled` flag with
`ComposeView.disableWindowInsetsRulers()` on the view that should opt out.

## Host-Provided Composition

### Host-default locals (`1.11.0`)

`compositionLocalWithHostDefaultOf` creates a local whose fallback comes from
the host, such as an Android `View` tag. `HostDefaultKey` is an interface.
Custom hosts can provide platform values with the public `HostDefaultProvider`
and `LocalHostDefaultProvider` APIs.

### Unattached `ComposeView` (`1.11.0`)

`ComposeViewContext` allows a `ComposeView` to compose before attachment to a
View hierarchy. Start it with
`AbstractComposeView.createComposition(composeViewContext)`:

```kotlin
composeView.createComposition(composeViewContext)
```

The callable is declared on `AbstractComposeView`; retain clear ownership of
the context and composition lifecycle.

## Dialog and Popup Windows

### Custom tokens and window types (`1.11.0`)

Android Compose dialogs accept a custom `windowToken`. Popups accept both
custom `windowToken` and `windowType` values. `DialogProperties.windowType`
also allows a service to show a Compose dialog in an overlay window. Validate
the token, overlay permission, and service lifecycle before creating the host.

## Android Graphics Interop

### Packed colors and `ColorLong` (`1.9.0`)

Compose packed colors are not directly comparable with Android `ColorLong`
values. Convert explicitly with `toColorLong()` and `fromColorLong()`.

### Native paint (`1.11.0`)

The `androidx.compose.ui.graphics.NativePaint` typealias is deprecated. Use
`android.graphics.Paint` directly. Replace `Paint.asFrameworkPaint()` with the
`Paint.nativePaint` extension so common code does not expose an Android type
through a typealias.

## Display and Frame Rate

### Per-composable frame-rate requests (`1.9.0`)

Use `Modifier.preferredFrameRate` to request a frame rate or
`FrameRateCategory` from `androidx.compose.ui`. It replaces
`requestedFrameRate`; `FrameRateCategory.NoPreference` was removed.

## Android Constants

### UI mode names (`1.10.0`)

The Android-derived `UiModes` constants container is named `AndroidUiModes`.
Update imports and qualified references.
