# Upgrades and runtime

Use this reference for embedded runtime changes, package installation, platform
requirements, support lifecycle, and launch-time compatibility.

## Embedded runtime stack

Each Electron major pins a Chromium, Node.js, and V8 tuple. Treat the tuple as a
unit when evaluating native modules, browser behavior, JavaScript semantics, or
allowed Node flags.

| Electron | Embedded components | Change from the preceding major |
| --- | --- | --- |
| 34.0.0 | Chromium `132.0.6834.83`, Node.js `20.18.1`, V8 `13.2` | Chromium 130 → 132; Node.js `20.18.0` → `20.18.1`; V8 13.0 → 13.2 |
| 35.0.0 | Chromium `134.0.6998.44`, Node.js `22.14.0`, V8 `13.5` | Chromium 132 → 134; Node.js `20.18.1` → `22.14.0`; V8 13.2 → 13.5 |
| 36.0.0 | Chromium `136.0.7103.48`, Node.js `22.14.0`, V8 `13.6` | Chromium 134 → 136; Node.js unchanged; V8 13.5 → 13.6 |
| 37.0.0 | Chromium `138.0.7204.35`, Node.js `22.16.0`, V8 `13.8` | Chromium 136 → 138; Node.js `22.14.0` → `22.16.0`; V8 13.6 → 13.8 |
| 38.0.0 | Chromium `140.0.7339.41`, Node.js `22.18.0`, V8 `14.0` | Chromium 138 → 140; Node.js `22.16.0` → `22.18.0`; V8 13.8 → 14.0 |
| 39.0.0 | Chromium `142.0.7444.52`, Node.js `22.20.0`, V8 `14.2` | Chromium `140.0.7339.41` → `142.0.7444.52`; Node.js `22.18.0` → `22.20.0`; V8 14.0 → 14.2 |
| 40.0.0 | Chromium `144.0.7559.60`, Node.js `24.11.1`, V8 `14.4` | Chromium `142.0.7444.52` → `144.0.7559.60`; Node.js `22.20.0` → `24.11.1`; V8 14.2 → 14.4 |
| 41.0.0 | Chromium `146.0.7680.65`, Node.js `24.14.0`, V8 `14.6` | Chromium `144.0.7559.60` → `146.0.7680.65`; Node.js `24.11.1` → `24.14.0`; V8 14.4 → 14.6 |
| 42.0.0 | Chromium `148.0.7778.96`, Node.js `24.15.0`, V8 `14.8` | Chromium `146.0.7680.65` → `148.0.7778.96`; Node.js `24.14.0` → `24.15.0`; V8 14.6 → 14.8 |
| 43.0.0 | Chromium `150.0.7871.46`, Node.js `24.17.0`, V8 `15.0` | Chromium `148.0.7778.96` → `150.0.7871.46`; Node.js `24.15.0` → `24.17.0`; V8 14.8 → 15.0 |

### Electron 41 upgrade target

The initial `41.0.0` package was followed by high-priority fixes. Install
`41.0.2` when first moving an application to the Electron 41 line.

## Electron package installation

### Lazy binary download in Electron 42.0.0

The `electron` npm package no longer downloads the Electron binary from a
`postinstall` script. It downloads on the first run of the package's main bin
script. Script-free package installs are supported:

```sh
npm install electron --save-dev --ignore-scripts
npx install-electron
```

Use `install-electron` when the binary must be fetched explicitly.
`ELECTRON_SKIP_BINARY_DOWNLOAD` has been removed. Set
`ELECTRON_INSTALL_PLATFORM` and `ELECTRON_INSTALL_ARCH` when installation must
target a different platform or architecture.

## Platform requirements and distribution

### macOS minimum versions

Electron 38.0.0 no longer supports macOS 11 Big Sur. Electron 38 and later
require macOS 12 Monterey or later; older Electron lines can still run on Big
Sur.

Electron 44 drops macOS 12 support and requires macOS 13 Ventura or later.
Older Electron releases continue to run on Monterey.

### Native Wayland default in Electron 38.0.0

`ELECTRON_OZONE_PLATFORM_HINT` has been removed, and Chromium's
`--ozone-platform` defaults to `auto`. A Wayland session therefore runs Electron
as a native Wayland application. Pass `--ozone-platform=x11` to retain Xwayland
behavior where required.

### GTK 4 default on GNOME in Electron 36.0.0

Electron defaults to GTK 4 on GNOME. Applications that load GTK 2 or GTK 3
symbols can fail because multiple GTK versions cannot coexist. Force GTK 3
before application startup when necessary:

```js
app.commandLine.appendSwitch('gtk-version', '3');
```

The equivalent CLI form is `electron --gtk-version=3`.

### Linux desktop environment variables

Electron 38 no longer overwrites `XDG_CURRENT_DESKTOP` with `Unity`; it contains
the actual desktop environment. The transitional
`ORIGINAL_XDG_CURRENT_DESKTOP` variable has been removed. Do not branch on the
old synthetic values.

### 32-bit prebuilt binary sunset

Electron 43.0.0 is the final series publishing prebuilt binaries for Windows
x86 (`win32-ia32`) and Linux ARMv7 (`linux-armv7l`). Those platforms stop being
supported after the 43 series reaches end of life in January 2027.

Electron 44 also stops publishing 32-bit `chromedriver`, `mksnapshot`, and
`ffmpeg` companion artifacts, as well as the Windows x86 `node.lib` on the
Electron headers CDN.

### macOS debug symbols in Electron 40.0.0

macOS dSYM archives use xz compression. Tooling that consumed `dsym.zip` must
handle `dsym.tar.xz` instead.

## Command-line behavior and Node flags

### Chromium switch lowercasing in Electron 36.0.0

`app.commandLine` lowercases uppercase switches and arguments. It is intended
for case-insensitive Chromium switches. Read application-specific arguments
from `process.argv` when case must be preserved.

### Accepted Node.js flags

- Electron 37.0.0 accepts `--no-experimental-global-navigator` and
  `--experimental-network-inspection`; both also shipped in Electron 35 and 36.
- Electron 41.0.0 accepts `--experimental-transform-types`; the flag is also
  supported in Electron 39 and 40.
- Electron 43.0.0 passes through
  `--experimental-inspector-network-resource`.

### Host-rule switch migration

Chromium is deprecating `--host-rules`. Use `--host-resolver-rules` instead in
Electron 39.0.0 and later migrations.

## Application paths

`app.getPath('assets')` returns the assets and resources location. This key is
documented with Electron 38.0.0 and is also available in Electron 37.

## Support lifecycle milestones

Use the supported-lines column only as the historical state at that milestone;
it does not assert that those lines remain supported now.

| Milestone | Line reaching end of support | Supported lines at that milestone |
| --- | --- | --- |
| Electron 34.0.0 | Electron 31 | 34, 33, 32 |
| Electron 35.0.0 | Electron 32 | 35, 34, 33 |
| Electron 36.0.0 | Electron 33 | 36, 35, 34 |
| Electron 37.0.0 | Electron 34 | 37, 36, 35 |
| Electron 38.0.0 | Electron 35 | 38, 37, 36 |
| Electron 39.0.0 | Electron 36 | 39, 38, 37 |
| Electron 40.0.0 | Electron 37 | 40, 39, 38 |
| Electron 41.0.0 | Electron 38 | Not specified by this milestone |
| Electron 42.0.0 | Electron 39 | Not specified by this milestone |
| Electron 43.0.0 | Electron 40 | Not specified by this milestone |
