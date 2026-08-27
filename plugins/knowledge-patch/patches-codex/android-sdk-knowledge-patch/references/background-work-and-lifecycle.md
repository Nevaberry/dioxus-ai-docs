# Background Work and Lifecycle

## Scheduled work and quotas

### Runtime quotas across app states

On Android 16 (`api-36`), runtime quotas also cover jobs in the active standby
bucket, jobs that start while the app is visible and continue after it becomes
invisible, and jobs running alongside a foreground service. This applies to
`JobScheduler`, WorkManager, and DownloadManager. Prefer user-initiated
data-transfer jobs where appropriate, inspect stop reasons, and call
`JobScheduler.getPendingJobReasonsHistory()` when a job has not run.

### Abandoned jobs

If a `JobParameters` instance is collected before `jobFinished()` and the job
then times out, Android 16 reports `STOP_REASON_TIMEOUT_ABANDONED`. Repeated
abandonment can reduce the app's future job frequency. Keep the parameters
alive until completion. `setImportantWhileForeground()` no longer helps: the
system ignores it and `isImportantWhileForeground()` returns `false`.

### Fixed-rate scheduling

For apps targeting API 36, `scheduleAtFixedRate` executes at most one missed
invocation when the process returns to a valid lifecycle. It no longer replays
every missed invocation immediately. Test catch-up assumptions with the
`STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` compatibility flag.

### Exact idle alarms

Android 17 (`api-37`) adds an `OnAlarmListener` overload of
`AlarmManager.setExactAndAllowWhileIdle()`. Use it for in-process exact
callbacks when a `PendingIntent` and its associated long partial wakelock are
unnecessary.

## Process and broadcast behavior

On Android 16, ordered-broadcast receiver priorities are honored only inside
the same application process, not between processes or apps. Priorities are
also clamped between `SYSTEM_LOW_PRIORITY + 1` and
`SYSTEM_HIGH_PRIORITY - 1`. Use a separate coordination mechanism when global
ordering matters.

Android 17 applies RAM-based app-memory limits on a subset of devices to all
apps. A limited process exits with `ApplicationExitInfo.REASON_OTHER` and a
description containing `MemoryLimiter:AnonSwap`. `TRIGGER_TYPE_ANOMALY` can
capture a heap dump. Inspect and exercise the limiter with:

```shell
adb shell am memory-limiter status
adb shell am memory-limiter manual <pid> <limit>
adb shell am memory-limiter ignore <uid>
```

## Activity configuration and IME lifecycle

Android 17 no longer recreates activities by default for keyboard,
keyboard-hidden, navigation, touchscreen, color-mode, or desktop UI-mode
transitions. If an app depends on recreation to reload resources, opt in with
`android:recreateOnConfigChanges`.

When an app does not handle a configuration change, Android 17 also stops
restoring the keyboard's previous visibility. Use
`windowSoftInputMode="stateAlwaysVisible"` when it expresses the intended
screen behavior, or explicitly request the IME from `onCreate()` or
`onConfigurationChanged()`.

## Background activity launches

Android 17 extends background-activity launch hardening to `IntentSender`.
Replace the legacy `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` with a granular
mode such as `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE`. Use StrictMode
or lint to find flows that still depend on the broad mode.

## Background audio

On Android 17, invalid background playback and volume calls fail silently, and
invalid audio-focus requests return `AUDIOFOCUS_REQUEST_FAILED`. Apps targeting
API 37 additionally need a foreground service with while-in-use capability.
The exception is an app holding exact-alarm permission while using a
`USAGE_ALARM` stream.

## Profiling and notifications

Android 17 extends `ProfilingManager` with `COLD_START`, `OOM`, and
`KILL_EXCESSIVE_CPU_USAGE` triggers. It also enforces strict size limits on
custom notification views; test every custom collapsed and expanded layout
under the new constraints.
