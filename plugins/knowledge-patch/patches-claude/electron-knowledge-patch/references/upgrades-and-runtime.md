# Upgrades and Runtime

## Embedded runtime stack

Use the exact embedded versions when evaluating Chromium, Node.js, or V8 behavior.

| Electron batch | Chromium | Node.js | V8 | Change from the preceding Electron line |
| --- | --- | --- | --- | --- |
| 34.0.0 | `132.0.6834.83` | `20.18.1` | `13.2` | Chromium 130→132, Node.js `20.18.0`→`20.18.1`, V8 13.0→13.2 |
| 35.0.0 | `134.0.6998.44` | `22.14.0` | `13.5` | Chromium 132→134, Node.js `20.18.1`→`22.14.0`, V8 13.2→13.5 |
| 36.0.0 | `136.0.7103.48` | `22.14.0` | `13.6` | Chromium 134→136 and V8 13.5→13.6; Node.js unchanged |
| 37.0.0 | `138.0.7204.35` | `22.16.0` | `13.8` | Chromium 136→138, Node.js `22.14.0`→`22.16.0`, V8 13.6→13.8 |
| 38.0.0 | `140.0.7339.41` | `22.18.0` | `14.0` | Chromium 138→140, Node.js `22.16.0`→`22.18.0`, V8 13.8→14.0 |
| 39.0.0 | `142.0.7444.52` | `22.20.0` | `14.2` | Chromium `140.0.7339.41`→`142.0.7444.52`, Node.js `22.18.0`→`22.20.0`, V8 14.0→14.2 |
| 40.0.0 | `144.0.7559.60` | `24.11.1` | `14.4` | Chromium `142.0.7444.52`→`144.0.7559.60`, Node.js `22.20.0`→`24.11.1`, V8 14.2→14.4 |
| 41.0.0 | `146.0.7680.65` | `24.14.0` | `14.6` | Chromium `144.0.7559.60`→`146.0.7680.65`, Node.js `24.11.1`→`24.14.0`, V8 14.4→14.6 |
| 42.0.0 | `148.0.7778.96` | `24.15.0` | `14.8` | Chromium `146.0.7680.65`→`148.0.7778.96`, Node.js `24.14.0`→`24.15.0`, V8 14.6→14.8 |
| 43.0.0 | `150.0.7871.46` | `24.17.0` | `15.0` | Chromium `148.0.7778.96`→`150.0.7871.46`, Node.js `24.15.0`→`24.17.0`, V8 14.8→15.0 |

## Upgrade targets and support windows

The initial Electron 41 package received high-priority fixes; target `41.0.2`
rather than `41.0.0` when adopting that major.

Each major ends support for the line three majors behind it:

| Milestone | Line reaching end of support | Supported lines stated at that milestone |
| --- | --- | --- |
| 34.0.0 | 31 | 34, 33, 32 |
| 35.0.0 | 32 | 35, 34, 33 |
| 36.0.0 | 33 | 36, 35, 34 |
| 37.0.0 | 34 | 37, 36, 35 |
| 38.0.0 | 35 | 38, 37, 36 |
| 39.0.0 | 36 | 39, 38, 37 |
| 40.0.0 | 37 | 40, 39, 38 |
| 41.0.0 | 38 | — |
| 42.0.0 | 39 | — |
| 43.0.0 | 40 | — |

## Operating-system requirements

### macOS minimums

Electron 38.0.0 drops macOS 11 Big Sur and requires macOS 12 Monterey or later.
Older Electron releases can continue to run on Big Sur.

The forward `breaking-changes` guidance says Electron 44 drops Monterey and
requires macOS 13 Ventura or later. Older Electron releases can continue to run
on Monterey.

### Linux display and toolkit defaults

Since 36.0.0, GTK 4 is the default on GNOME. Native components that load GTK 2/3
symbols can fail because GTK generations cannot coexist. Force GTK 3 before app
startup when necessary:

```js
app.commandLine.appendSwitch('gtk-version', '3');
```

The equivalent CLI is `electron --gtk-version=3`.

Since 38.0.0, `ELECTRON_OZONE_PLATFORM_HINT` is removed and Chromium's
`--ozone-platform` defaults to `auto`. A Wayland session therefore runs native
Wayland by default; use `--ozone-platform=x11` to retain Xwayland behavior.

## Installation and distributable artifacts

### Lazy binary installation

Since 42.0.0, the `electron` npm package downloads its binary on the first run of
its main bin script instead of from `postinstall`. `--ignore-scripts` installs are
supported, and `install-electron` can fetch explicitly:

```sh
npm install electron --save-dev --ignore-scripts
npx install-electron
```

`ELECTRON_SKIP_BINARY_DOWNLOAD` is removed. Use `ELECTRON_INSTALL_PLATFORM` and
`ELECTRON_INSTALL_ARCH` for cross-platform or cross-architecture binary targets.

### Debug-symbol format

Since 40.0.0, macOS dSYM archives use xz compression. Consumers of `dsym.zip`
must accept `dsym.tar.xz`.

### 32-bit sunset

Electron 43.0.0 is the final series with Windows x86 (`win32-ia32`) and Linux
ARMv7 (`linux-armv7l`) prebuilt binaries. Support ends when that series reaches
end of life in January 2027.

The `breaking-changes` guidance also says Electron 44 stops publishing 32-bit
`chromedriver`, `mksnapshot`, and `ffmpeg` companion artifacts and stops
publishing Windows x86 `node.lib` on the Electron headers CDN.
