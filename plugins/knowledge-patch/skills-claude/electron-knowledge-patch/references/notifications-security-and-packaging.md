# Notifications, Security, and Packaging

## Renderer privilege boundaries

### Clipboard migration

At 40.0.0, direct use of Electron's `clipboard` API in renderer processes was
deprecated. Move privileged operations to a preload and expose only what the page
needs:

```js
const { clipboard, contextBridge } = require('electron');

contextBridge.exposeInMainWorld('clipboardAPI', {
  readText: () => clipboard.readText(),
});
```

The forward `breaking-changes` guidance says Electron 44 no longer exposes the
Electron `clipboard` module to renderers. Prefer `navigator.clipboard` for
ordinary access, or the narrow preload bridge for advanced operations.

Since 35.0.0, permission handling also covers
`document.executeCommand('paste')`; account for it in permission handlers.

### Disabling macOS geolocation

Since 41.0.0, disable location services for a macOS application with:

```js
app.commandLine.appendSwitch('disable-geolocation');
```

## ASAR integrity

### Stable integrity enforcement

Since 39.0.0, ASAR integrity is stable. When enabled, it verifies packaged
`app.asar` against its build-time hash and forcefully terminates the application
if the hash is missing or mismatched. Electron Packager 19 separately enables
ASAR packaging by default.

### macOS integrity digest

Since 41.0.0, macOS applications can embed a digest of their ASAR Integrity data
so the integrity metadata itself is validated at launch. With `@electron/asar`
4.1.0 or later, enable the digest and then re-sign the application:

```bash
asar integrity-digest on /path/to/YourApp.app
```

## Updates and package formats

### MSIX auto-updates

`autoUpdater` supports MSIX applications in Electron 39.5.0 and 40.2.0, and in
the 41.0.0 line. An update server can publish MSIX and Squirrel.Mac updates using
essentially the same JSON response format.

## Safe storage

Since 42.0.0, asynchronous `safeStorage` functionality enables several additional
storage backends. Prefer the asynchronous surface when using those backends.

## macOS notifications

### Signing requirement

Since 42.0.0, macOS notifications use `UNNotification` instead of deprecated
`NSUserNotification`. The application must be code-signed for notifications to
display; an unsigned application's `Notification` emits `failed`.

### History and grouping

Also since 42.0.0, `Notification.getHistory()` reads macOS notification history.
The constructor's `id` and `groupId` options provide custom identity and
Notification Center grouping.

### Removing delivered notifications

Since 43.0.0, macOS `Notification` exposes static `remove()`, `removeAll()`, and
`removeGroup()` methods for removing one delivered notification, all delivered
notifications, or a group.

## Windows notifications

### Dismissal reasons and rich actions

Since Electron 40, including 41.0.0, the Windows `Notification` `closed` event
includes `reason`, identifying why it was dismissed. Notification actions support
buttons, select dropdowns, and replies.

### Identity, grouping, urgency, and cold-start activation

Since 42.0.0, Windows notifications accept `id`, `groupId`, `groupTitle`, and
`urgency`. Use `Notification.handleActivation(callback)` for clicks, replies, and
action buttons, including activations that cold-start the application.

## macOS media packaging requirement

Since 39.0.0, desktop audio capture on macOS 14.2 or later requires
`NSAudioCaptureUsageDescription` in `Info.plist`. Without it, the newer capture
path can produce silent audio without an error. See the graphics and media
reference for the temporary feature-disable switch.
