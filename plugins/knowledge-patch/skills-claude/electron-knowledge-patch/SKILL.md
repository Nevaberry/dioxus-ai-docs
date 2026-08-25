---
name: electron-knowledge-patch
description: Electron
version: 43.0.0
license: MIT
metadata:
  author: Nevaberry
---


# Electron Knowledge Patch

Use this skill when writing, reviewing, or upgrading Electron applications. Check the
project's pinned Electron version first and apply guidance only when the relevant
change has shipped in that version. Treat the application manifest, lockfile, code,
and tests as authoritative when they disagree with this guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Upgrades and runtime](references/upgrades-and-runtime.md) | Embedded runtimes, platform requirements, support windows, installation, and artifacts |
| [Sessions, networking, and extensions](references/sessions-networking-and-extensions.md) | Sessions, service workers, protocols, requests, storage, extensions, and WebAuthn |
| [Processes, diagnostics, and runtime behavior](references/processes-diagnostics-and-runtime.md) | Frames, utility processes, diagnostics, command-line handling, PDF, and process exits |
| [Windows, input, and platform UI](references/windows-input-and-platform-ui.md) | BrowserWindow, menus, shortcuts, dialogs, printing, navigation, and desktop integration |
| [Graphics, media, and NativeImage](references/graphics-media-and-native-image.md) | Offscreen rendering, shared textures, capture, color management, and image APIs |
| [Notifications, security, and packaging](references/notifications-security-and-packaging.md) | Notifications, clipboard isolation, ASAR integrity, safe storage, updates, and signing |

## Upgrade triage

### Prepare for removals

- Electron 44 removes the renderer `clipboard` module. Prefer
  `navigator.clipboard`, or expose narrowly scoped advanced operations from a
  preload with `contextBridge`.
- Electron 44 requires macOS 13 or later and stops publishing 32-bit companion
  artifacts. Electron 43 is the final prebuilt line for Windows x86 and Linux
  ARMv7.
- Linux `showHiddenFiles` was deprecated in Electron 41 and removed in Electron
  43. Do not rely on it outside macOS and Windows.
- `webContents` no longer emits `plugin-crashed`.
- `PrinterInfo.isDefault` and `PrinterInfo.status` are gone.
- Remove `systemPreferences.isAeroGlassEnabled()` branches; the API has no
  replacement.

### Migrate deprecated APIs

- Replace `Session.setPreloads()` and `getPreloads()` with
  `registerPreloadScript()`, `unregisterPreloadScript()`, and
  `getPreloadScripts()`.
- Replace `session.serviceWorkers.fromVersionID()` with
  `getInfoFromVersionID()` or `getWorkerFromVersionID()`.
- Move extension methods and events from `session` to `session.extensions`.
- Replace `NativeImage.getBitmap()` with `toBitmap()`.
- Replace `webFrame.routingId` and `findFrameByRoutingId()` with `frameToken`
  and `findFrameByToken()`; resolve main-process tokens with
  `webFrameMain.fromFrameToken()`.
- Stop passing `quota` or `quotas` to `Session.clearStorageData()`.
- Read `console-message` data from the event object and use `lineNumber`.
- Use `--host-resolver-rules` instead of Chromium's deprecated `--host-rules`.

### Audit changed defaults

- An empty web-request `urls` array matches nothing; use `['<all_urls>']` when
  every URL is intended.
- Electron runs natively on Wayland when available. Pass
  `--ozone-platform=x11` only when Xwayland behavior is required.
- Offscreen rendering uses device scale factor `1.0`; set
  `webPreferences.offscreen.deviceScaleFactor` explicitly for another scale.
- `window.open()` popups are always resizable unless
  `setWindowOpenHandler()` overrides `resizable`.
- Downloads and dialogs without `defaultPath` start in Downloads, falling back
  to Home. Persist and pass a directory to retain last-used behavior.
- `app.commandLine` lowercases switches and arguments. Read application-specific
  arguments from `process.argv`.
- A utility-process `process.exit()` is synchronous, so buffered output may not
  flush.

## Security-critical behavior

### Keep renderer privileges narrow

Direct renderer access to Electron's clipboard API is deprecated before its
removal. Put privileged work in the main or preload context and expose the
smallest possible surface:

```js
const { clipboard, contextBridge } = require('electron');

contextBridge.exposeInMainWorld('clipboardAPI', {
  readText: () => clipboard.readText(),
});
```

Sandboxed windows opened by a top-level frame inherit the opener's sandbox
restrictions. `<webview>` and `window.open()` also inherit
`nodeIntegrationInWorker`; do not assume a child silently resets security
preferences.

### Package and sign correctly

- Stable ASAR integrity terminates the app when the packaged archive hash is
  absent or mismatched. On macOS, embed the ASAR-integrity digest and re-sign.
- macOS notifications require a code-signed application; unsigned apps emit
  `failed` instead of displaying the notification.
- Desktop capture with audio on macOS 14.2 or later needs
  `NSAudioCaptureUsageDescription` or the CoreAudio Tap path can return silent
  audio without an error.
- `allowExtensions: true` is required when Chrome extensions must access a
  privileged custom protocol.

## High-value APIs

### Diagnose hung and failed renderers

To collect a JavaScript stack from an unresponsive renderer, enable the feature
and serve the matching Document Policy header:

```js
app.commandLine.appendSwitch(
  'enable-features',
  'DocumentPolicyIncludeJSCallStacksInCrashReports',
);

webContents.on('unresponsive', async () => {
  console.log(await webContents.mainFrame.collectJavaScriptCallStack());
});
```

Use `WebFrameMain.detached` for unloading state and `isDestroyed()` for final
destruction. Heap tracing and renderer out-of-memory diagnostics can also capture
JavaScript evidence.

### Register per-context preloads

Preload registrations can target either `frame` or `service-worker`. A service
worker preload uses `ipcRenderer`; communicate from the main process through
`ServiceWorkerMain.ipc`. Use `startWorkerForScope()` and
`running-status-changed` when lifecycle control is needed.

### Filter requests explicitly

```js
const filter = {
  urls: ['<all_urls>'],
  excludeUrls: ['https://example.test/private/*'],
};
```

Use `net.request({ bypassCustomProtocolHandlers: true })` when a request must
skip registered protocol handlers. WebSocket authentication arrives through the
`webContents` `login` event.

### Control popups and navigation

```js
webContents.setWindowOpenHandler((details) => ({
  action: 'allow',
  overrideBrowserWindowOptions: {
    resizable: details.features.includes('resizable=yes'),
  },
}));
```

Set `webPreferences.focusOnNavigation` to `false` when navigation must not focus
the `WebContents`. Restore captured history with
`webContents.navigationHistory.restore(index, entries)`.

### Render frames to PDF

Patch releases add per-frame PDF output:

```js
const frame = browserWindow.webContents.mainFrame;
const pdf = await frame.printToPDF({});
```

PDF resources render inside the existing `WebContents`, so detection should
inspect the frame tree rather than wait for a guest `WebContents`.

### Work with notifications

- On Windows, use `Notification.handleActivation()` for clicks, replies, and
  actions that can cold-start the app.
- Use notification IDs and group IDs for grouping; macOS also exposes history
  and removal APIs.
- Windows notification actions support buttons, selects, and replies, while the
  `closed` event reports a dismissal `reason`.

### Handle graphics predictably

- Shared-texture `paint` payload fields live beneath `handle`.
- Imported textures support NV12, NV16, and P010LE; external textures can become
  `VideoFrame` objects.
- `NativeImage` normalizes profiled input to sRGB. Pass a `colorSpace` option to
  `toBitmap()` when source-space output or another conversion is required.
- Use an options object for `createFromNamedImage(name, { hslShift })`; the
  positional HSL array is deprecated.

## Platform checks

### macOS

- Pass `WebContents.focusedFrame` to `Menu.popup({ frame })` for Writing Tools,
  Autofill, and Services integration.
- Use `nativeTheme.shouldUseDarkColorsForSystemIntegratedUI` for system UI and
  `shouldDifferentiateWithoutColor` for the accessibility preference.
- Configure Touch ID WebAuthn through `app.configureWebAuthn()` and handle
  discoverable-account selection on the session.

### Linux

- GTK 4 is the GNOME default. Force GTK 3 before startup when native dependencies
  cannot coexist with GTK 4.
- Frameless windows have rounded corners; disable with `roundedCorners: false`.
- Window Controls Overlay follows the native title-bar button layout. Position
  content with `env(titlebar-area-x)` and `env(titlebar-area-width)`.
- Portal file-dialog backends older than version 4 ignore `defaultPath`; require
  portal version 4 when that option is essential.

### Windows

- Fullscreen hides the menu bar.
- `query-session-end` supports pre-shutdown handling, alongside improved
  `session-end` behavior.
- `roundedCorners` is supported, and MSIX applications can use `autoUpdater`.

## Verification checklist

1. Confirm the pinned Electron version and supported operating systems.
2. Search for removed and deprecated APIs before changing dependencies.
3. Test renderer sandbox, preload, protocol, and child-window inheritance.
4. Exercise Wayland/X11, GTK, macOS signing, and Windows packaging paths used by
   the application.
5. Re-test offscreen scale, image color, media capture, dialogs, notifications,
   printing, and PDF behavior where applicable.
6. Inspect process-exit reasons and utility-process logs under failure.
