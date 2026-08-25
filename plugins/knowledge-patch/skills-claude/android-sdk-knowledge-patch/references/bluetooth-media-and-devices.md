# Bluetooth, Media, and Device Integration

## Health sensors and session location

### Replace broad health-sensor permissions

Apps targeting API 36 must replace `BODY_SENSORS` with granular health
permissions such as `READ_HEART_RATE`, and replace `BODY_SENSORS_BACKGROUND`
with `READ_HEALTH_DATA_IN_BACKGROUND`. The change also applies to affected Wear
OS APIs and health foreground services.

Mobile apps must declare an activity that shows the privacy-policy rationale.
If the activity is missing, the health permission is revoked.

### Offer session-scoped precise location

Jetpack can embed a system-rendered location button that grants precise
location for the current session without a permission dialog. Declare
`USE_LOCATION_BUTTON` before using the button.

## Companion association

### Handle discovery timeout as a dialog outcome

On Android 16, companion-device discovery timeout no longer returns
`RESULT_DISCOVERY_TIMEOUT` directly. The system displays a timeout dialog and,
after the user dismisses it, reports `RESULT_USER_REJECTED`. Do not interpret
that result only as an explicit rejection.

### Use new profiles and association-time permissions

Android 17 adds Medical Device and Fitness Tracker profiles to Companion Device
Manager. `setExtraPermissions()` can include nearby-device grants in the
association dialog.

### Support cross-device Handoff

Android 17 adds Handoff through `CompanionDeviceManager`. Integrate it with the
association lifecycle instead of building a separate unassociated transfer
channel.

## Bluetooth bonds and sockets

### Android 16 retains a bond after missing keys

When authentication fails, Android 16 disconnects the device, retains the
local bond, and asks the user to pair again rather than silently deleting the
bond and initiating pairing.

API 36 targets can observe `ACTION_KEY_MISSING` and
`ACTION_ENCRYPTION_CHANGE`, but must tolerate OEM implementations that omit
them. For a managed companion association, remove the bond explicitly with
`CompanionDeviceManager.removeBond(int)` when product policy requires it.

### Android 17 can repair a lost bond

Android 17 can pair again in the background after bond loss. It replaces keys
only after a successful connection with equal or stronger security.

`ACTION_PAIRING_REQUEST` adds `EXTRA_PAIRING_CONTEXT`, and
`ACTION_KEY_MISSING` is delayed until autonomous repair fails. Do not trigger a
competing pairing flow before that outcome.

### Treat RFCOMM closure as EOF

For API 37 targets, an RFCOMM `BluetoothSocket` input stream returns `-1` when
the socket closes or the connection drops. Check every read for `-1`; do not
wait exclusively for `IOException`.

```kotlin
while (true) {
    val count = input.read(buffer)
    if (count == -1) break
    consume(buffer, count)
}
```

## Camera capture

Android 17 adds:

- `ImageFormat.RAW14`.
- OEM-defined extension modes discoverable through
  `isExtensionSupported(int)`.
- Camera device-type APIs.
- `CameraCaptureSession.updateOutputConfigurations()` for changing output use
  cases without closing the session.

Query capabilities rather than assuming every camera supports a format,
extension, device type, or live output change.

## Media codecs and audio devices

Android 17 adds platform VVC/H.266 support, constant-quality recording through
`MediaRecorder.setVideoEncodingQuality()`, and the
`c2.android.xheaac.encoder` software encoder with loudness metadata. It also
adds `AudioDeviceInfo.TYPE_BLE_HEARING_AID`.

Continue to query codecs and devices at runtime; do not infer availability from
the platform release alone.

## Time, neural processing, and device categories

### Observe time-zone offset-only changes

Android 17 adds `ACTION_TIMEZONE_OFFSET_CHANGED` for daylight-saving and other
changes where the time-zone offset changes without requiring a different zone
identifier. Refresh offset-derived schedules and UI when receiving it.

### Declare direct NPU use

API 37-targeted apps must declare `FEATURE_NEURAL_PROCESSING_UNIT` before
accessing an NPU directly. Keep a fallback for devices without the feature.
