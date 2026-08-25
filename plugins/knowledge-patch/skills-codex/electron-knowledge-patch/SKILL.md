---
name: electron-knowledge-patch
description: Electron
version: 43.0.0
license: MIT
metadata:
  author: Nevaberry
---


# Electron Compatibility Patch

Use this skill when upgrading, packaging, debugging, or integrating an Electron
application whose behavior may depend on recent Electron APIs and defaults.
Check the application's pinned Electron version before applying version-specific
guidance. If the project is newer than the frontmatter version, prefer its
manifest, code, release documentation, and observed tests where they differ.

## Reference index

| Reference | Read when working on |
| --- | --- |
| [Upgrades and runtime](references/upgrades-and-runtime.md) | Embedded Chromium, Node.js, and V8 versions; support lifecycle; installation; platform requirements; command-line behavior |
| [Processes, security, and diagnostics](references/processes-security-and-diagnostics.md) | Renderer and utility-process failures; frame identity; preload boundaries; ASAR integrity; OOM and tracing diagnostics |
| [Sessions, protocols, and extensions](references/sessions-protocols-and-extensions.md) | Preload registration; service workers; request filters; storage; protocols; WebUSB; WebAuthn; extension behavior |
| [Graphics, media, and native image](references/graphics-media-and-native-image.md) | Offscreen rendering; shared textures; color spaces; NativeImage; desktop-capture audio |
| [Windows, menus, and platform integration](references/windows-menus-and-platform-integration.md) | BrowserWindow behavior; dialogs; menus; notifications; shortcuts; printing; PDF; Linux and macOS integration |

## Upgrade triage

Audit these changes before changing the Electron major version:

1. Verify the runtime tuple. A major Electron upgrade also changes Chromium,
   Node.js, and V8; native modules and Node flags may need adjustment.
2. Recheck packaging and installation. Electron 42 installs its binary lazily,
   accepts `--ignore-scripts`, removes `ELECTRON_SKIP_BINARY_DOWNLOAD`, and
   provides `install-electron` for an explicit fetch.
3. Recheck platform support. Electron 38 requires macOS 12 and defaults to
   native Wayland in a Wayland session. Electron 44 requires macOS 13 and ends
   publication of remaining 32-bit companion artifacts.
4. Recheck process boundaries. Renderer `clipboard` access was deprecated in
   Electron 40 and removed in Electron 44; move privileged operations to a
   preload or use `navigator.clipboard`.
5. Recheck browser-window and dialog defaults. Popup resizing, offscreen scale,
   Linux rounded corners, Window Controls Overlay geometry, download paths, and
   open/save starting directories changed.
6. Recheck protocol and sandbox behavior. Late patch releases made legacy
   protocol `no-cors` responses opaque and tightened preference inheritance for
   windows opened by sandboxed or embedded content.

## Breaking changes and changed defaults

### Renderer clipboard access

Do not import Electron's `clipboard` module in a renderer. Use
`navigator.clipboard` for ordinary web access. For advanced operations, expose
the smallest required surface from a preload with `contextBridge`.

```js
// preload.js
const { clipboard, contextBridge } = require('electron');

contextBridge.exposeInMainWorld('clipboardAPI', {
  readText: () => clipboard.readText(),
});
```

### Electron package installation

The npm package downloads its binary on the first run of its main bin script,
not from `postinstall`. A script-free installation can fetch explicitly:

```sh
npm install electron --save-dev --ignore-scripts
npx install-electron
```

Use `ELECTRON_INSTALL_PLATFORM` and `ELECTRON_INSTALL_ARCH` for a different
target. Do not rely on the removed `ELECTRON_SKIP_BINARY_DOWNLOAD` variable.

### Dialog and download destinations

Electron 43 defaults downloads to Downloads, falling back to Home. Open/save
dialogs without `defaultPath` also start there instead of restoring the last
OS-selected directory. Persist a chosen directory and pass it explicitly when
the application needs the former behavior.

### Linux windows and dialogs

Electron 43 gives frameless Linux windows rounded corners by default; set
`roundedCorners: false` to opt out. Window Controls Overlay follows the native
title-bar layout, so position content with `titlebar-area-x` and
`titlebar-area-width` environment variables. The Linux `showHiddenFiles` dialog
option, deprecated in Electron 41, is removed in Electron 43.

Portal file-dialog backends older than version 4 ignore `defaultPath`. Launch
with `--xdg-portal-required-version=4` when that option is required.

### Offscreen rendering

Electron 42 makes the default offscreen device scale factor a constant `1.0`.
Set `webPreferences.offscreen.deviceScaleFactor` explicitly for other output
scales. Shared-texture payload layout and supported texture formats also changed;
read the graphics reference before handling native texture handles.

### Popup resizing

Electron 39 makes `window.open()` popups resizable regardless of the feature
string. Restore application-controlled behavior through
`setWindowOpenHandler()` and `overrideBrowserWindowOptions.resizable`.

### Wayland and macOS support

Electron 38 removes `ELECTRON_OZONE_PLATFORM_HINT`; `--ozone-platform` defaults
to `auto`, selecting native Wayland in Wayland sessions. Pass
`--ozone-platform=x11` only when Xwayland behavior is required.

Electron 38 requires macOS 12 or later. Electron 44 raises that minimum to
macOS 13. macOS notifications require code signing from Electron 42 onward.

## Deprecation and removal map

| Old API or behavior | Replacement or action |
| --- | --- |
| `Session.setPreloads()` / `getPreloads()` | Register scripts individually with `registerPreloadScript()`, `unregisterPreloadScript()`, and `getPreloadScripts()` |
| `serviceWorkers.fromVersionID()` | Use `getInfoFromVersionID()` or `getWorkerFromVersionID()` |
| Positional `console-message` arguments | Read `level`, `message`, `lineNumber`, `sourceId`, and `frame` from the event object |
| Empty `WebRequestFilter.urls` for all URLs | Use `urls: ['<all_urls>']` |
| `PrinterInfo.isDefault` and `.status` | Remove usage; the properties are gone |
| `systemPreferences.isAeroGlassEnabled()` | Remove the branch; the API has no replacement |
| `NativeImage.getBitmap()` | Use `toBitmap()` |
| Extension methods and events on `Session` | Use `session.extensions` |
| `app.commandLine` for app-specific arguments | Read `process.argv`; command-line switches are lowercased |
| `ProtocolResponse.session: null` | Supply a real session, optionally a unique partition |
| `webFrame.routingId` and routing-ID lookup | Use `frameToken`, token lookup, and `webFrameMain.fromFrameToken()` |
| `--host-rules` | Use `--host-resolver-rules` |
| Renderer `clipboard` module | Use `navigator.clipboard` or a narrow preload bridge |
| Linux `showHiddenFiles` | Remove it; support ended in Electron 43 |
| Positional `hslShift` in `createFromNamedImage()` | Pass `{ hslShift: [...] }` as an options object |
| `options.quota` / `options.quotas` in storage clearing | Omit quota selection; the remaining upstream option was later removed |

## Security-sensitive patterns

### New windows

Do not assume a child can relax its opener's restrictions. In corrected 41–43
patch releases, windows opened by sandboxed top-level frames inherit sandboxing,
and `<webview>` plus `window.open()` inherit `nodeIntegrationInWorker` from the
embedder along with other Node and sandbox preferences.

### Custom protocols

Prefer `protocol.handle()`. Corrected patch releases make cross-origin
`no-cors` responses from legacy `registerFileProtocol()` and
`registerHttpProtocol()` opaque as well. Renderer code must not depend on
reading those bodies. Use `net.request({ bypassCustomProtocolHandlers: true })`
when a request must deliberately skip registered handlers.

### Packaged application integrity

ASAR integrity terminates the application when enabled integrity metadata is
missing or mismatched. On macOS, use `@electron/asar` 4.1.0 or later to embed an
integrity digest, then re-sign the application.

### Clipboard and paste

Treat paste and clipboard access as privileged operations. Permission handling
covers `document.executeCommand('paste')`; renderer module access is no longer
a durable design.

## Diagnostic quick reference

- On an unresponsive renderer, call
  `webContents.mainFrame.collectJavaScriptCallStack()` after enabling the
  document-policy feature and response header described in the process
  reference.
- Distinguish `WebFrameMain.detached` from `isDestroyed()` during teardown.
- Listen for utility-process `error` to capture fatal V8 diagnostics.
- Handle utility-process unhandled rejections explicitly if fail-fast behavior
  is required; they warn instead of crashing.
- Recognize `memory-eviction` as a child-process exit reason.
- Use heap profiling and renderer OOM JavaScript stacks when diagnosing memory
  failures.
- A utility-process `process.exit()` is synchronous, so buffered output may not
  flush before termination.

## Platform integration quick reference

- On Windows, fullscreen hides the menu bar; handle `query-session-end` and
  improved `session-end` notifications for logoff and shutdown flows.
- On macOS, pass `WebContents.focusedFrame` to `Menu.popup({ frame })` for
  Writing Tools, Autofill, and Services integration.
- On Linux, use `--gtk-version=3` when a dependency cannot coexist with the GTK
  4 default on GNOME.
- Do not assume fixed Linux title-bar button positions or sides.
- Use `globalShortcut.setSuspended()` and `isSuspended()` when shortcuts must be
  paused temporarily.
- Code-sign macOS applications that display notifications; unsigned apps emit
  `failed`.

## Working method

1. Read the project manifest and identify the exact Electron line.
2. Start with the upgrade and runtime reference for a major-version change.
3. Load only the topic references relevant to the APIs the application uses.
4. Search for removed symbols, renamed options, changed event payloads, and
   assumptions about platform defaults.
5. Update code and packaging configuration together when a behavior spans the
   main process, preload, renderer, or distribution pipeline.
6. Exercise platform-specific paths on the operating systems they affect; many
   changes intentionally have no cross-platform analogue.
7. Prefer project behavior and tests when an application pins a later patch
   release or deliberately overrides a default described here.
