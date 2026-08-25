# Devices, Bluetooth, Camera, and Media

## Companion devices and Bluetooth

### Pairing timeout results

On Android 16 (`api-36`), companion-device discovery timeouts no longer return
`RESULT_DISCOVERY_TIMEOUT` directly. The system displays a timeout dialog and,
after dismissal, reports `RESULT_USER_REJECTED`. Do not interpret that result
only as an explicit user rejection.

### Bond-loss behavior

Android 16 disconnects a device after authentication failure but retains the
local bond and asks the user to re-pair. Apps targeting API 36 can observe
`ACTION_KEY_MISSING` and `ACTION_ENCRYPTION_CHANGE`, but must tolerate OEMs
that omit them. For a managed companion association, remove the bond with
`CompanionDeviceManager.removeBond(int)` when that is the desired recovery.

Android 17 (`api-37`) can repair a lost bond autonomously in the background.
It replaces keys only after a successful connection at equal or stronger
security. `ACTION_PAIRING_REQUEST` adds `EXTRA_PAIRING_CONTEXT`, and
`ACTION_KEY_MISSING` is delayed until autonomous re-pairing fails.

### RFCOMM end-of-stream

For apps targeting API 37, an RFCOMM `BluetoothSocket` input stream returns
`-1` when the socket closes or the connection drops. Read loops must test for
`-1`; do not rely only on `IOException`.

### Association capabilities

Android 17 adds Medical Device and Fitness Tracker Companion Device Manager
profiles. `setExtraPermissions()` can include nearby-device grants in the
association dialog. Cross-device Handoff is also available through
`CompanionDeviceManager`.

## Photo Picker layout

Android 17 adds `PhotoPickerUiCustomizationParams`, which can change picker
grid cells from the square default to a 9:16 portrait aspect ratio.

## Camera

Android 17 adds:

- `ImageFormat.RAW14`;
- OEM-defined extension modes discoverable with
  `isExtensionSupported(int)`;
- camera device-type APIs; and
- `CameraCaptureSession.updateOutputConfigurations()` for changing use cases
  without closing the session.

Check capabilities before selecting a format, extension, or live
reconfiguration path.

## Media and audio devices

Android 17 adds VVC/H.266 platform support, constant-quality recording through
`MediaRecorder.setVideoEncodingQuality()`, the `c2.android.xheaac.encoder`
software encoder with loudness metadata, and
`AudioDeviceInfo.TYPE_BLE_HEARING_AID`. Feature-detect codec and output-device
support rather than assuming uniform device availability.

## Device integration

Android 17 adds `ACTION_TIMEZONE_OFFSET_CHANGED` for DST and other changes in
UTC offset that do not necessarily change the time-zone identity. Apps
targeting API 37 must declare `FEATURE_NEURAL_PROCESSING_UNIT` before directly
accessing an NPU.
