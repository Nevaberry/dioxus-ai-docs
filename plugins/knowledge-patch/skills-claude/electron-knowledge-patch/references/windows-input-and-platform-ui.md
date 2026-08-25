# Windows, Input, and Platform UI

## Window appearance and geometry

### Fullscreen menu bars on Windows

Since 34.0.0, entering fullscreen on Windows hides the menu bar, matching Linux.
Although announced for Electron 33, the behavior first shipped in Electron 34.

### Vibrancy and rounded corners

Since 35.0.0, `BrowserWindow.setVibrancy()` accepts an optional animation
parameter, and the `roundedCorners` constructor option works on Windows.

Since 43.0.0, frameless Linux windows have rounded corners by default. Set
`roundedCorners: false` to disable them.

### Inner dimensions for child windows

Since Electron 35 and 36, and in 37.0.0, `window.open()` recognizes `innerWidth`
and `innerHeight`:

```js
window.open('/child.html', '_blank', 'innerWidth=800,innerHeight=600');
```

### Always-resizable popups

Since 39.0.0, `window.open()` always creates resizable popup windows. To preserve
feature-string-controlled resizing, override the generated window options:

```js
webContents.setWindowOpenHandler((details) => ({
  action: 'allow',
  overrideBrowserWindowOptions: {
    resizable: details.features.includes('resizable=yes'),
  },
}));
```

### Wayland frameless windows

Since 41.0.0, frameless Wayland windows have drop shadows and extended resize
boundaries. Set `hasShadow: false` in the window constructor when no decorations
are desired.

### Linux Window Controls Overlay

Since 43.0.0, frameless windows using Window Controls Overlay follow the native
Linux title-bar layout and user preferences. Button availability and side can
vary. Constrain title-bar content with the environment values rather than fixed
coordinates:

```css
.titlebar-content {
  left: env(titlebar-area-x, 0px);
  width: env(titlebar-area-width, 100%);
}
```

## Colors, themes, and accessibility

### CSS corner smoothing

The `-electron-corner-smoothing` property first landed in Electron 36 and is
documented in 37.0.0. It changes rounded corners to a continuous, squircle-like
curve, including borders, outlines, and shadows. It accepts `0%` through `100%`;
`system-ui` resolves to 60% on macOS and 0% elsewhere.

```css
.box {
  border-radius: 24px;
  -electron-corner-smoothing: system-ui;
}
```

### Native theme preferences

Since 36.0.0, `nativeTheme.shouldUseDarkColorsForSystemIntegratedUI`
distinguishes the operating system's integrated-UI appearance from the app's
selected theme.

Since 42.0.0, macOS
`nativeTheme.shouldDifferentiateWithoutColor` exposes the system accessibility
preference to differentiate by means other than color.

### Accent color

Electron can customize the system accent color and highlight the active-window
border since Electron 37, including 38.0.0. Since Electron 38 and 39, and in the
40.0.0 line, call `window.setAccentColor(null)` to stop overriding the system
accent color.

### Menu accessibility labels

Since 43.0.0, `MenuItem` constructor options and properties support
`accessibilityLabel` for a screen-reader-friendly label.

## Menus and input events

### Focused-frame macOS context menus

Since 36.0.0, `WebContents.focusedFrame` identifies the focused frame. Pass it as
`Menu.popup()`'s `frame` option to enable macOS Writing Tools, Autofill, and
Services integration:

```js
import { BrowserWindow, Menu } from 'electron';

const window = BrowserWindow.getFocusedWindow();
const menu = Menu.buildFromTemplate([{ label: 'Copy', role: 'copy' }]);
menu.popup({ window, frame: window.webContents.focusedFrame });
```

### Linux system context menus

The `system-context-menu` event is supported on Linux since 36.0.0.

### macOS menu additions

Since 37.0.0, macOS 14.4 or later supports menu sublabels. macOS menus also
recognize the `palette` and `header` item roles.

### Mouse-event interception

Since Electron 36, including 37.0.0, `WebContents` emits `before-mouse-event`.
A listener can prevent a mouse event before delivery.

## Global shortcuts

Since 35.0.0, Electron can use the desktop portal's global-shortcut support when
started with `--enable-features=GlobalShortcutsPortal`.

Since 43.0.0, `globalShortcut.setSuspended()` temporarily suspends and resumes
global-shortcut handling; `globalShortcut.isSuspended()` queries that state.

## Navigation and desktop integration

### Navigation history and focus

Since 35.0.0,
`webContents.navigationHistory.restore(index, entries)` restores supplied history
entries and selects the requested entry.

Since Electron 40, including 41.0.0, set
`webPreferences.focusOnNavigation: false` to prevent navigation from
automatically focusing a `WebContents`.

### Recent documents and assets

Since Electron 37, including 38.0.0, `app.getRecentDocuments()` works on Windows
and macOS. `app.getPath('assets')` exposes the assets and resources location.

### Linux protocol application information

Since 43.0.0, `app.getApplicationInfoForProtocol()` is supported on Linux.

### Linux workspace visibility

Since 37.0.0, `BrowserWindow#isVisibleOnAllWorkspaces()` returns `false` on Linux
when the window is not currently visible.

### X11 coordinate conversion

Since Electron 35 and 36, including 37.0.0, `screen.dipToScreenPoint(point)` and
`screen.screenToDipPoint(point)` work on Linux X11.

## Dialogs and downloads

### Parented message dialogs

Since 38.0.0, `dialog.showMessageDialog()` centers on its parent window when a
parent is supplied, rather than centering on the monitor.

### Hidden-file option

At 41.0.0, `showHiddenFiles` was deprecated on Linux while remaining supported on
macOS and Windows. At 43.0.0, Linux support was removed.

### Download and initial-dialog directories

Since 43.0.0, file downloads default to the user's Downloads folder, falling back
to Home when Downloads does not exist.

The `breaking-changes` guidance describes the related Electron 43 open/save
dialog change: omitting `defaultPath` starts in Downloads, or Home if Downloads
is absent, rather than letting the OS restore the last-used directory. Persist
the chosen directory and pass it explicitly:

```js
const path = require('node:path');

let lastUsedPath;
const result = await dialog.showOpenDialog({ defaultPath: lastUsedPath });
if (!result.canceled && result.filePaths.length) {
  lastUsedPath = path.dirname(result.filePaths[0]);
}
```

### Linux portal `defaultPath`

The `breaking-changes` guidance notes that Electron 35 lowered the required
file-dialog portal version to 3, but portal backends older than version 4 do not
support `defaultPath`. Require version 4 when necessary:

```sh
electron --xdg-portal-required-version=4 .
```

## Printing

Since 41.0.0, pass `usePrinterDefaultPageSize: true` to `webContents.print()` to
use the printer's default page size:

```js
webContents.print({ usePrinterDefaultPageSize: true });
```

`PrinterInfo.isDefault` and `PrinterInfo.status` were removed at 35.0.0 with their
upstream Chromium counterparts.

## Operating-system events and settings

### Windows shutdown

Since 35.0.0, Windows exposes `query-session-end` and improves the existing
`session-end` events.

### macOS display-safe-area compatibility

Since 35.0.0, Electron's `Info.plist` sets
`NSPrefersDisplaySafeAreaCompatibilityMode` to `false`, removing the “Scale to
fit below built-in camera” app option.

### Persistent macOS tray position

Since Electron 37, including 38.0.0, the `Tray` constructor accepts `guid` on
macOS so an icon can retain its position across launches.

### Linux desktop-environment variables

The `breaking-changes` guidance records that since Electron 38,
`XDG_CURRENT_DESKTOP` contains the actual desktop environment instead of being
overwritten with `Unity`; `ORIGINAL_XDG_CURRENT_DESKTOP` is removed.

### Aero Glass API

At 35.0.0, `systemPreferences.isAeroGlassEnabled()` was deprecated without a
replacement because it had always returned `true` since Electron 23. The
`breaking-changes` guidance records its removal in Electron 36. Delete branches
that depend on it.
