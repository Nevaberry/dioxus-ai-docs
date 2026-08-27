# Runtime, UI, and Scheduling

## Background work and timers

### Runtime quotas cover more jobs

On Android 16, runtime quotas also cover jobs in the active standby bucket,
jobs that begin while the app is visible and continue after it becomes
invisible, and jobs running alongside a foreground service. This affects
`JobScheduler`, WorkManager, and DownloadManager.

Use user-initiated data-transfer jobs for qualifying user-started transfers.
Inspect stop reasons, and call `JobScheduler.getPendingJobReasonsHistory()` to
diagnose jobs that have not run.

### Do not abandon JobParameters

Keep each `JobParameters` object alive through completion and call
`jobFinished()` correctly. If the object is collected before completion and the
job times out, Android 16 reports `STOP_REASON_TIMEOUT_ABANDONED`. Repeated
abandonment can cause the system to run the app's jobs less often.

`setImportantWhileForeground()` is ignored;
`isImportantWhileForeground()` returns `false`.

### Fixed-rate catch-up is capped

For API 36 targets, `scheduleAtFixedRate` executes at most one missed invocation
when the process returns to a valid lifecycle. Test logic that depended on
replaying every missed run. Exercise the behavior with the
`STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` compatibility flag.

### Exact idle alarms support in-process callbacks

Android 17 adds an `OnAlarmListener` overload of
`AlarmManager.setExactAndAllowWhileIdle()`. It avoids a `PendingIntent` and the
associated long partial wakelock for an in-process exact callback.

## Process and runtime internals

### Diagnose app memory limits

Android 17 imposes RAM-based limits on a subset of devices for all apps. A
limited process exits with `ApplicationExitInfo.REASON_OTHER` and
`MemoryLimiter:AnonSwap` in the description. A `TRIGGER_TYPE_ANOMALY` profiling
trigger can capture a heap dump.

Inspect or exercise limits with:

```shell
adb shell am memory-limiter status
adb shell am memory-limiter manual <pid> <limit>
adb shell am memory-limiter ignore <uid>
```

### Avoid private MessageQueue internals

API 37 targets receive a lock-free `MessageQueue` implementation. Supported
APIs retain their behavior, but reflection over private queue fields or methods
can fail. Remove such reflection or isolate it behind a safe fallback.

### Static final fields are immutable

On Android 17, API 37 targets cannot change `static final` fields. Reflection
throws `IllegalAccessException`; JNI field setters crash the app. Replace
mutation-based test or initialization techniques.

## Broadcasts and background launches

### Ordered priorities are process-local

On Android 16, receiver priorities are honored only inside one application
process. They do not establish order across processes or apps. Values are also
confined between `SYSTEM_LOW_PRIORITY + 1` and
`SYSTEM_HIGH_PRIORITY - 1`. Use explicit cross-process coordination when order
matters.

### IntentSender launch controls are granular

Android 17 extends background-activity-launch hardening to `IntentSender`.
Replace legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` use with a narrower
mode such as `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE`. Use StrictMode
or lint to locate legacy flows.

## Edge-to-edge, back, and large screens

### Edge-to-edge cannot be disabled

For API 36 targets on Android 16,
`windowOptOutEdgeToEdgeEnforcement` is deprecated and ignored. It still works
for that app on Android 15, so remove the opt-out and verify inset handling on
both releases.

### Predictive back is the default

For API 36 targets on Android 16, predictive back animations are enabled.
Legacy `onBackPressed` callbacks and `KEYCODE_BACK` dispatch no longer occur.
Use supported back APIs.

As a temporary application- or activity-level fallback, set
`android:enableOnBackInvokedCallback="false"`. Migrated apps also receive
predictive back from a long press in 3-button navigation.

### Large screens ignore restrictive declarations

For API 36 targets on displays of at least `sw600dp`, Android 16 ignores
orientation requests, `resizeableActivity`, minimum and maximum aspect ratios,
and related runtime APIs in full-screen and multi-window modes. Games and
smaller displays are exempt.

A temporary application- or activity-level opt-out is available:

```xml
<property android:name="android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY"
          android:value="true" />
```

The opt-out stops working when the app targets API 37. Build adaptive layouts
instead of treating the property as a permanent solution.

## Configuration, IME, and input

### Recreation defaults changed

Android 17 no longer recreates activities by default for keyboard,
keyboard-hidden, navigation, touchscreen, color-mode, or desktop UI-mode
transitions. Apps that rely on recreation to reload resources must opt in with
`android:recreateOnConfigChanges`.

### IME visibility is not restored

When an app does not handle a configuration change, Android 17 does not restore
the keyboard's prior visibility. If visibility is required, use
`windowSoftInputMode="stateAlwaysVisible"` or request the IME explicitly from
`onCreate()` or `onConfigurationChanged()`.

### Complex composition has accessibility metadata

API 37 adds `TextAttribute.Builder.setTextSuggestionSelected()`,
`TextAttribute.isTextSuggestionSelected()`, and
`AccessibilityEvent.setTextChangeTypes()`/`getTextChangeTypes()`. CJKV IMEs,
custom input connections, and accessibility services can distinguish
composition, candidate selection, and committed text. Standard `TextView`
handling is automatic for API 37 targets.

### Password visibility depends on the input device

For API 37 targets, `show_passwords_physical` hides every character entered
from a physical input device by default. Touch input follows
`show_passwords_touch`. Framework fields adopt the split automatically; custom
fields should use `ShowSecretsSetting`.

### Captured touchpads become relative pointers

During pointer capture, Android 17 translates touchpad motion and scrolling to
captured, mouse-style relative events. Apps that require raw absolute finger
positions must call:

```java
view.requestPointerCapture(View.POINTER_CAPTURE_MODE_ABSOLUTE);
```

## Text and accessibility

### Elegant font height is fixed

When targeting API 36, `TextView`'s `elegantTextHeight` is deprecated and
ignored, and compact variants of the affected fonts cannot be selected. Recheck
layouts containing Arabic, Lao, Myanmar, Tamil, Gujarati, Kannada, Malayalam,
Odia, Telugu, and Thai.

### Replace generic accessibility announcements

Android 16 deprecates `announceForAccessibility()` and `TYPE_ANNOUNCEMENT`.
Use pane titles for structural changes, live regions for important dynamic
content, and error-specific events or `TextView.setError()` for validation
failures.

## Audio and visual surfaces

### Background audio is lifecycle-gated

On Android 17, invalid background playback and volume calls fail silently, and
audio-focus requests return `AUDIOFOCUS_REQUEST_FAILED`. API 37 targets also
need a foreground service with while-in-use capability. The exception is an
app holding exact-alarm permission and using a `USAGE_ALARM` stream.

### Themed icons may be synthesized

Beginning with Android 16 QPR2, launchers automatically theme an icon when the
app provides no themed icon. Add a monochrome layer to the adaptive icon to
control the result.

### Photo Picker layout can be customized

Android 17's `PhotoPickerUiCustomizationParams` can change the default square
grid to a 9:16 portrait cell aspect ratio.

### Widgets are display-aware

`RemoteViews.setViewPadding()` accepts complex DP/SP units. Use
`OPTION_APPWIDGET_DISPLAY_ID` to obtain metrics for the external display that
hosts a widget.

### Desktop apps can request a pinned layer

An app holding both `USE_PINNED_WINDOWING_LAYER` and picture-in-picture
permissions can request an interactive, always-on-top pinned window in desktop
mode.

### Test profiling and notifications

`ProfilingManager` supports `COLD_START`, `OOM`, and
`KILL_EXCESSIVE_CPU_USAGE` triggers on Android 17. Custom notification views
also have strict size limits; exercise custom layouts on Android 17 devices.
