# Desktop and embedding

## Contents

- [UI and platform thread merging](#ui-and-platform-thread-merging)
- [Engine identity](#engine-identity)
- [Content-sized embedded views](#content-sized-embedded-views)
- [Experimental multi-window APIs](#experimental-multi-window-apis)
- [Windows integration](#windows-integration)
- [Linux integration](#linux-integration)
- [Architectures](#architectures)
- [Build configuration](#build-configuration)

## UI and platform thread merging

Do not assume Flutter's UI runner and the native platform runner are distinct.

- Android and iOS run Dart on the application's main thread, and their embedders no
  longer allow opting out of the merged arrangement.
- Windows and macOS first offered explicit opt-in (`3.32-guide`), then made merged
  UI/platform threads the default (`3.35.0`).
- Linux also uses merged threads by default. Its remaining opt-out was marked for
  removal (`3.41-guide`).

This enables direct FFI calls to APIs that require the platform thread, but it also
means blocking Dart or native work can block the application's main event loop.
Mobile platform interop can consequently move toward synchronous calls without
serializing work between two runners.

For an older Windows embedder that still requires the explicit policy, set it inside
`wWinMain`:

```cpp
project.set_ui_thread_policy(
    flutter::UIThreadPolicy::RunOnPlatformThread);
```

For an older macOS embedder, add this to the top-level `Info.plist` dictionary:

```xml
<key>FLTEnableMergedPlatformUIThread</key>
<true />
```

Do not add these legacy opt-ins to a current template where merging is already the
default.

## Engine identity

Flutter exposes framework version information to application code for diagnostics.
`PlatformDispatcher.instance.engineId` identifies the particular engine, which is
important in multi-engine and add-to-app processes (`3.32.0`).

## Content-sized embedded views

Embedded Flutter views can obtain their size from Flutter content instead of a fixed
native-parent size.

- On iOS, set `FlutterViewController.isAutoResizable` to `true`.
- On Android, enable content sizing in the manifest and make the relevant
  `FlutterView` dimension wrap its content.

The Flutter root must accept unbounded constraints. Do not place a size-dependent
`ListView` or `LayoutBuilder` at the root of that tree.

Experimental desktop windowing also supports content-sized popup and tooltip views
on Linux. `Overlay.alwaysSizeToContent` lets an overlay continue sizing its window
from content outside the usual size-to-content path.

## Experimental multi-window APIs

Desktop windowing remains feature-gated and, for later additions, main-channel-only.
Do not use these APIs as a production portability layer without checking the active
channel and target.

The available experimental surface grew to include:

- regular Win32 windows, dynamic view resizing, and a framework interface for
  dialog-window archetypes (`3.38.0`);
- popup and tooltip windows;
- cross-platform dialog windows on Linux, macOS, and Windows;
- multi-window test APIs;
- Material `showDialog` using a separate child dialog window;
- undecorated windows;
- content-sized popup and tooltip windows on Linux (`3.44-guide`).

The regular-window implementation throws on unsupported platforms rather than
silently emulating support. Gate calls by feature availability and handle errors.

## Windows integration

Windows applications can enumerate connected displays and inspect each display's
resolution, refresh rate, and physical size (`3.38-guide`). Use these values for
monitor-aware placement rather than assuming the primary display's metrics.

The Windows embedder reports stylus pressure and rotation. Applications can also
request a high-power GPU for demanding workloads. Flutter development tooling
supports Visual Studio 2026.

## Linux integration

The Linux embedder supports software rendering, including runs requested with:

```sh
flutter run --enable-software-rendering
```

Flutter tooling recognizes Linux `riscv64`. Dart's compiler can also cross-compile
Linux executables for `arm`, `arm64`, and `riscv64`; see the Dart tooling reference.

## Architectures

Beta and stable SDK releases build Windows ARM engine artifacts (`3.44.0`). Before
shipping, verify that every native plug-in and asset also supplies a compatible
architecture; engine availability does not make third-party binaries portable.

## Build configuration

Linux and Windows builds accept `--config-only`, allowing native project files to be
configured without producing the full application. Use it for native-host migration
steps, not as a substitute for a real target build.
