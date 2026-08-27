# Desktop and embedding

## UI and platform threads

The thread model changed in stages:

- Dart moved onto the application main thread on Android and iOS in 3.29.0.
- Windows and macOS could opt into merging with
  `UIThreadPolicy::RunOnPlatformThread` and `FLTEnableMergedPlatformUIThread` in
  3.32-guide.
- Windows and macOS made merging the default, and Linux adopted the merged
  arrangement, in 3.35.0.
- Mobile embedders removed the opt-out in 3.38-guide.
- Linux made merging the default in 3.41-guide, with its remaining opt-out planned
  for removal.

Native code must not assume distinct UI and platform runners. Re-evaluate
serialization, reentrancy, synchronous FFI, and callbacks that were designed around
the old separation.

For historical Windows opt-in code, `project.set_ui_thread_policy(...)` belonged
inside `wWinMain`. The macOS key belonged inside the `Info.plist` `<dict>`. These
explicit opt-ins are unnecessary once merging is the platform default.

## Runtime and engine identity (3.32.0)

Application code can read Flutter version information at runtime for diagnostics.
`PlatformDispatcher.instance.engineId` identifies a specific engine in multi-engine
and add-to-app processes; log it when correlating engine-scoped state.

## Content-sized add-to-app views (3.41-guide)

Embedded Flutter views can derive their size from Flutter content rather than a
fixed native-parent size.

- iOS: set `FlutterViewController.isAutoResizable` to true.
- Android: enable content sizing in the manifest and give the relevant
  `FlutterView` a wrap-content dimension.

The Flutter root receives unbounded constraints. Do not put a size-dependent
`ListView` or `LayoutBuilder` at the top of the tree.

## Experimental multi-window APIs

Treat all APIs in this section as gated. Check the current channel and target
implementation before use.

### Window types and resizing

The experimental surface grew from popup and tooltip windows plus cross-platform
dialog windows and multi-window test APIs (3.41-guide) to separate Material dialog
child windows and content-sized Linux popup/tooltip views (3.44-guide).

Win32 support includes regular windows, a dialog-window archetype interface, and
dynamic view resizing (3.38.0). A regular-window implementation on an unsupported
platform throws instead of emulating the feature.

Windows can be created without decorations, and `Overlay.alwaysSizeToContent` can
keep sizing a window from overlay content beyond the normal size-to-content path
(3.44.0).

These windowing additions were main-channel-only and not intended for production
when introduced. Feature-gate them and provide a supported fallback.

## Windows

Applications can enumerate displays and inspect resolution, refresh rate, and
physical size for monitor-aware placement (3.38-guide).

The embedder reports stylus pressure and rotation (3.44-guide). Test real hardware,
including coordinate mapping and pressure/rotation ranges.

Tooling supports Visual Studio 2026, and an application can request a high-power GPU
for demanding workloads (3.41.0).

Beta and stable releases build Windows ARM engine artifacts (3.44.0). Confirm that
native plugins and other bundled binaries also provide the required architecture.

## Linux

The embedder supports software rendering, including
`flutter run --enable-software-rendering` (3.35.0). Linux and Windows builds accept
`--config-only` for configuration-only generation (3.38.0).

Flutter tooling recognizes Linux `riscv64` (3.44.0). Dart can cross-compile Linux
executables for ARM64 and later ARM32 and RISC-V, but application plugins and native
assets must independently match the target architecture.

## Native plugin and host checks

- On Apple platforms, public embedder APIs are callable from Swift and
  `FlutterPluginRegistrant` supports generated or custom registration (3.35.0).
- `FlutterFragment` and `FlutterFragmentActivity` support Android predictive back
  for fragment and add-to-app hosts (3.44.0).
- iOS plugins can access other registered plugins (3.44.0).
- SwiftPM integration does not support add-to-app hosts
  (apple-platform-migrations); keep host dependency wiring separate.

## Desktop verification

- Test UI/platform-thread assumptions under nested callbacks and synchronous FFI.
- Exercise every experimental window archetype only on explicitly supported
  platforms, and verify unsupported paths fail safely.
- Test content-sized roots with unbounded constraints and changing intrinsic size.
- Verify monitor enumeration, high-DPI scaling, stylus data, dialog parenting,
  decoration, and overlay-driven sizing.
- Build each architecture and inspect native plugin and asset binaries, not only the
  Flutter engine artifact.
- Exercise Linux software rendering and the configured Windows GPU preference.
