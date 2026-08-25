# Windows, menus, and platform integration

Use this reference for BrowserWindow defaults, navigation, menus, dialogs,
notifications, shortcuts, printing, PDF behavior, and OS-specific integration.

## Window appearance and geometry

### Fullscreen menu bars on Windows

Electron 34.0.0 hides the menu bar when a Windows window enters fullscreen,
matching Linux. Earlier releases left it visible. Although this was announced
for Electron 33, it first shipped in Electron 34.

### Appearance controls

Electron 35.0.0 gives `BrowserWindow.setVibrancy()` an optional animation
parameter. The `roundedCorners` constructor option is also supported on Windows.

### System accent and active-window border

Electron 38.0.0 can customize the system accent color and highlight the active
window border. This is also available in Electron 37. After setting a custom
accent, Electron 40.0.0 can resume following the system value with:

```js
window.setAccentColor(null);
```

The reset behavior is also available in Electron 38 and 39.

### Wayland frameless windows

Electron 41.0.0 gives frameless Wayland windows drop shadows and extended resize
boundaries. Set `hasShadow: false` in the constructor when the window must have
no decorations.

### Linux frameless-window corners

Electron 43.0.0 gives frameless Linux windows rounded corners by default. Set
`roundedCorners: false` to disable them.

### Linux Window Controls Overlay

Electron 43.0.0 makes frameless Window Controls Overlay follow the native Linux
title-bar layout and user settings. Available controls and their side can vary.
Do not reserve a fixed button area; constrain content with the provided
environment variables:

```css
.titlebar-content {
  left: env(titlebar-area-x, 0px);
  width: env(titlebar-area-width, 100%);
}
```

### Window inner dimensions

Electron 37.0.0 recognizes `innerWidth` and `innerHeight` in `window.open()`
feature strings. The support also shipped in Electron 35 and 36.

```js
window.open('/child.html', '_blank', 'innerWidth=800,innerHeight=600');
```

### Resizable popups

Electron 39.0.0 always creates `window.open()` popup windows as resizable. To
preserve feature-string-controlled behavior, override generated window options:

```js
webContents.setWindowOpenHandler((details) => {
  return {
    action: 'allow',
    overrideBrowserWindowOptions: {
      resizable: details.features.includes('resizable=yes'),
    },
  };
});
```

## Navigation and input

### Restore navigation history

Electron 35.0.0 adds `webContents.navigationHistory.restore(index, entries)` to
restore a supplied navigation history and its selected entry.

### Navigation focus control

Set `webPreferences.focusOnNavigation` to `false` in Electron 41.0.0 to prevent
a `WebContents` from being focused automatically during navigation. The option
is also available in Electron 40.

### Mouse-event interception

`WebContents` emits `before-mouse-event` in Electron 37.0.0, allowing a listener
to intercept and prevent mouse events before delivery. The event also shipped
in Electron 36.

### Linux workspace visibility

Starting in Electron 37.0.0,
`BrowserWindow.isVisibleOnAllWorkspaces()` returns `false` on Linux when the
window is not currently visible.

### X11 coordinate conversion

Electron 37.0.0 supports `screen.dipToScreenPoint(point)` and
`screen.screenToDipPoint(point)` on Linux X11. This support also shipped in
Electron 35 and 36.

## Menus and shortcuts

### Focused-frame macOS context menus

Electron 36.0.0 adds `WebContents.focusedFrame`. Pass that frame through the new
`Menu.popup()` `frame` option to enable macOS Writing Tools, Autofill, and
Services integrations:

```js
import { BrowserWindow, Menu } from 'electron';

const window = BrowserWindow.getFocusedWindow();
const menu = Menu.buildFromTemplate([{ label: 'Copy', role: 'copy' }]);

menu.popup({
  window,
  frame: window.webContents.focusedFrame,
});
```

### Linux system context menus

The `system-context-menu` event is supported on Linux starting in Electron
36.0.0.

### macOS menu additions

Electron 37.0.0 supports menu sublabels on macOS 14.4 and later. macOS menus
also recognize the `palette` and `header` item roles.

### Accessible menu labels

Electron 43.0.0 adds `accessibilityLabel` to `MenuItem` constructor options and
properties for screen-reader-friendly labels.

### Portal global shortcuts

Electron 35.0.0 can use the desktop portal's global-shortcut support when
launched with `--enable-features=GlobalShortcutsPortal`.

### Suspend global shortcuts

Electron 43.0.0 adds `globalShortcut.setSuspended()` and
`globalShortcut.isSuspended()` to suspend, resume, and query global-shortcut
handling.

## Theme and accessibility preferences

### System-integrated dark appearance

Electron 36.0.0 adds
`nativeTheme.shouldUseDarkColorsForSystemIntegratedUI`, which distinguishes the
operating system's integrated-UI appearance from the application's selected
theme.

### Differentiate without color

On macOS, Electron 42.0.0 exposes
`nativeTheme.shouldDifferentiateWithoutColor` for the accessibility preference
to distinguish information by means other than color.

### macOS display safe area

Electron 35.0.0 sets `NSPrefersDisplaySafeAreaCompatibilityMode` to `false` in
its `Info.plist`, removing the “Scale to fit below built-in camera” app option.

## Dialogs and downloads

### Parent-centered message dialogs

In Electron 38.0.0, `dialog.showMessageDialog()` centers on its parent window
when one is supplied, rather than centering on the monitor.

### Linux hidden files

Electron 41.0.0 deprecates the `showHiddenFiles` dialog property on Linux while
retaining it on macOS and Windows. Electron 43.0.0 removes Linux support for the
option.

### Portal `defaultPath`

Electron 35 lowers the required Linux file-dialog portal version to 3, but
portal backends older than version 4 do not support `defaultPath`. Require a new
enough portal when that option is essential:

```sh
electron --xdg-portal-required-version=4 .
```

### Initial directories and download destination

Electron 43.0.0 makes the user's Downloads folder the default destination for
file downloads, with Home as the fallback when Downloads does not exist.

In Electron 43, open/save dialog calls that omit `defaultPath` also start in
Downloads, or Home if it does not exist, instead of allowing the OS to restore
the last-used directory. Track and pass the directory to retain the old flow:

```js
const { dialog } = require('electron');
const path = require('node:path');

let lastUsedPath;
async function chooseFile() {
  const result = await dialog.showOpenDialog({ defaultPath: lastUsedPath });
  if (!result.canceled && result.filePaths.length) {
    lastUsedPath = path.dirname(result.filePaths[0]);
  }
  return result;
}
```

## Notifications and session end

### Windows session-ending events

Electron 35.0.0 adds the `query-session-end` event and improves the existing
`session-end` events on Windows.

### Windows notification actions

In Electron 41.0.0, the Windows `Notification` `closed` event includes a
`reason` property describing why it was dismissed. Notification actions support
buttons, select dropdowns, and replies. Both additions are also available in
Electron 40.

### macOS signing requirement

Electron 42.0.0 uses `UNNotification` rather than the deprecated
`NSUserNotification` API. Applications must be code-signed for notifications
to display; an unsigned application's `Notification` emits `failed`.

### History, grouping, and activation

Electron 42.0.0 adds these notification capabilities:

- On macOS, `Notification.getHistory()` reads notification history. Constructor
  options `id` and `groupId` provide identifiers and Notification Center
  grouping.
- On Windows, notifications accept `id`, `groupId`, `groupTitle`, and `urgency`.
  `Notification.handleActivation(callback)` handles clicks, replies, and action
  buttons even when a notification cold-starts the application.

### Remove macOS notifications

Electron 43.0.0 adds the static macOS methods `Notification.remove()`,
`removeAll()`, and `removeGroup()` to remove delivered notifications
individually, in bulk, or by group.

## Printing and PDF

### Printer information removals

Electron 35.0.0 removes `PrinterInfo.isDefault` and `PrinterInfo.status` along
with their upstream Chromium counterparts.

### Printer-default page size

Electron 41.0.0 adds `usePrinterDefaultPageSize: true` to
`webContents.print()`:

```js
webContents.print({ usePrinterDefaultPageSize: true });
```

### PDF frame model

In Electron 41.0.0, PDF resources no longer create a separate guest
`WebContents`; they render inside the existing `WebContents`. Detect PDF
resources by inspecting the frame tree rather than looking for another
`WebContents`.

### Per-frame PDF generation

The 41.10.5-43.4.1 batch adds `WebFrameMain.printToPDF()` in Electron 42.9.0 and
43.4.0. It renders one frame instead of the entire `WebContents`:

```js
const frame = browserWindow.webContents.mainFrame;
const pdf = await frame.printToPDF({});
```

## Other OS integration

### macOS system memory

Electron 38.0.0 adds `fileBacked` and `purgeable` to
`process.getSystemMemoryInfo()` on macOS. The fields are also available in
Electron 37.

### Persistent macOS tray identity

Electron 38.0.0 supports the `Tray` constructor's `guid` option on macOS, so a
tray icon can retain its position across launches. This is also available in
Electron 37.

### Recent documents

`app.getRecentDocuments()` is supported on Windows and macOS in Electron 38.0.0
and is also available in Electron 37.

### MSIX auto-updates

Electron 41.0.0 `autoUpdater` supports MSIX applications. An update server can
publish MSIX and Squirrel.Mac updates with essentially the same JSON response
format. MSIX support is also available in Electron 39.5.0 and 40.2.0.

### Disable macOS geolocation

Electron 41.0.0 supports the `--disable-geolocation` command-line flag:

```js
app.commandLine.appendSwitch('disable-geolocation');
```

### Aero Glass detection removal

Electron 35.0.0 deprecates `systemPreferences.isAeroGlassEnabled()` without a
replacement. Supported Windows versions no longer allow DWM composition to be
disabled, and the method had returned `true` since Electron 23. Electron 36
removes it; delete branches based on the method.
