# Platform, UI, and Runtime Migration

## Windowing and navigation

### Edge-to-edge

For an API 36-targeted app on Android 16 (`api-36`),
`windowOptOutEdgeToEdgeEnforcement` is deprecated and ignored. The same app
can still opt out on Android 15, but remove the flag and make layouts handle
insets correctly on both releases.

### Predictive back

Apps targeting API 36 receive predictive-back system animations on Android
16. Legacy `onBackPressed` callbacks and `KEYCODE_BACK` dispatch no longer
occur. Migrate to supported back APIs. During migration, opt out per app or
activity with `android:enableOnBackInvokedCallback="false"`. Migrated apps also
receive predictive back from a long press in 3-button navigation.

### Large-screen restrictions

For API 36-targeted apps on displays at least `sw600dp`, the platform ignores
orientation requests, `resizeableActivity`, minimum and maximum aspect ratios,
and related runtime APIs in full-screen and multi-window modes. Games and
smaller screens are exempt. A temporary application- or activity-level opt-out
exists, but no longer works when targeting API 37.

```xml
<property android:name="android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY"
          android:value="true" />
```

## Text, accessibility, and icons

### Font height

When an app targets API 36, `TextView`'s `elegantTextHeight` is deprecated and
ignored, so compact variants of affected fonts cannot be selected. Recheck
layouts for Arabic, Lao, Myanmar, Tamil, Gujarati, Kannada, Malayalam, Odia,
Telugu, and Thai text.

### Accessibility announcements

Android 16 deprecates `announceForAccessibility()` and `TYPE_ANNOUNCEMENT`.
Use pane titles for structural changes, accessibility live regions for
important dynamic content, and error-specific events or `TextView.setError()`
for validation failures.

### Synthesized themed icons

Beginning with Android 16 QPR2, the launcher automatically themes an app icon
that lacks a themed icon. Add a monochrome layer to the adaptive icon to
control the result.

## Runtime implementation constraints

### Lock-free MessageQueue

Apps targeting API 37 on Android 17 (`api-37`) receive the lock-free
`MessageQueue` implementation. Supported APIs behave as before, but reflection
against private `MessageQueue` fields or methods can break. Remove or isolate
all such access.

### Immutable static final fields

API 37-targeted apps cannot mutate `static final` fields. Reflection throws
`IllegalAccessException`; JNI field setters crash the app.

## Text entry and IME behavior

### Complex composition metadata

API 37 adds `TextAttribute.Builder.setTextSuggestionSelected()`,
`TextAttribute.isTextSuggestionSelected()`, and
`AccessibilityEvent.setTextChangeTypes()`/`getTextChangeTypes()`. CJKV IMEs,
custom input connections, and accessibility services can distinguish
composition, candidate selection, and committed changes. Standard `TextView`
handling is automatic for API 37-targeted apps.

### Password visibility by input source

For API 37-targeted apps, `show_passwords_physical` hides every character
entered from a physical device by default, while touchscreen entry follows
`show_passwords_touch`. Framework fields adopt this behavior automatically;
custom fields should use `ShowSecretsSetting`.

## Pointer capture

During pointer capture, Android 17 converts touchpad motion and scrolling into
captured mouse-style relative events. Apps that need raw absolute finger
positions must call
`View.requestPointerCapture(View.POINTER_CAPTURE_MODE_ABSOLUTE)`.

## External displays and desktop presentation

Apps holding both `USE_PINNED_WINDOWING_LAYER` and picture-in-picture
permissions can request an interactive always-on-top pinned window in desktop
mode. Widgets hosted on external displays can use
`OPTION_APPWIDGET_DISPLAY_ID` for host-display metrics, and
`RemoteViews.setViewPadding()` accepts complex DP/SP units.
