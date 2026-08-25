# Desktop and embedding

## UI and platform thread merging

- Windows and macOS first offered explicit thread merging in `3.32-guide`.
  Windows used `project.set_ui_thread_policy(
  flutter::UIThreadPolicy::RunOnPlatformThread)` in `wWinMain`; macOS used
  `FLTEnableMergedPlatformUIThread` in `Info.plist`.
- Windows and macOS default to merged threads in 3.35.0; Linux also adopted merged
  execution. `3.41-guide` confirms the Linux default and warns not to depend on
  separate runners.
- Mobile embedders made merging mandatory in `3.38-guide`. Treat the merged
  UI/platform thread as the baseline across supported targets and audit blocking
  FFI or platform calls accordingly.

## Rendering and display integration

- The Linux embedder supports software rendering, including
  `--enable-software-rendering` runs (3.35.0).
- Windows display discovery exposes each monitor's resolution, refresh rate, and
  physical size for monitor-aware placement (`3.38-guide`).
- Windows apps can request a high-power GPU (3.41.0).

## Content-sized add-to-app views

`3.41-guide` adds content-sized embedded views. Set
`FlutterViewController.isAutoResizable` on iOS. On Android, enable content sizing
in the manifest and let the relevant `FlutterView` dimension wrap content. The
Flutter root receives unbounded constraints, so do not place a size-dependent
`ListView` or `LayoutBuilder` directly at the root.

## Experimental multi-window support

- The feature-gated 3.38.0 APIs cover regular Win32 windows, dialog-window
  archetypes, and dynamic resizing. A regular-window implementation on an
  unsupported platform throws instead of emulating support.
- `3.41-guide` expands the experiment with popup and tooltip windows,
  cross-platform Linux/macOS/Windows dialogs, and multi-window test APIs.
- `3.44-guide` makes Material `showDialog` create a child dialog window and adds
  content-sized Linux popup/tooltip views in supported experimental configurations.
  These main-channel-only APIs were not production-ready.
- 3.44.0 adds undecorated windows and `Overlay.alwaysSizeToContent`, which keeps
  sizing a window from overlay content beyond the ordinary size-to-content path.

## Input and embedder APIs

- Windows reports stylus pressure and rotation (`3.44-guide`). Test native
  coordinate conversion and pointer-kind handling for drawing workflows.
- Public Apple embedder APIs are usable from Swift (3.35.0), and iOS plug-ins can
  access other registered plug-ins (3.44.0).
- Android fragment embeddings support predictive back (3.44.0).

## Architectures and development hosts

- Flutter recognizes Linux `riscv64`; beta and stable channels build Windows ARM
  engine artifacts (3.44.0).
- Visual Studio 2026 is supported for Windows development (3.41.0).
- Apple development command-line tools run natively on ARM hosts; Intel Mac host
  support is planned to end (`3.44-guide`).

Gate every experimental window feature at runtime, expect unsupported operations
to throw, and verify thread, display, input, sizing, architecture, and native-host
behavior on the actual platform.
