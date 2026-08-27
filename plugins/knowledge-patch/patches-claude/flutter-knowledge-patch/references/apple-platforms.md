# Apple platform integration

## Rendering and threading

On iOS, Skia support and the `FLTEnableImpeller` opt-out were removed in 3.29.0.
Do not build an iOS fallback path around Skia. Mobile UI/platform thread merging
later became mandatory (3.38-guide), so native interop must not assume separate
thread runners.

Impeller remains opt-in on macOS (rendering-and-web). Use
`flutter run --enable-impeller` for development or put `FLTEnableImpeller` in the
top-level `Info.plist` dictionary for deployed builds:

```xml
<key>FLTEnableImpeller</key>
<true />
```

macOS rendering supports Display P3, and float32 images can preserve float32 output
through `Image.toByteData()` (3.44.0). Test color and image paths on the selected
renderer and display.

## UIScene lifecycle

Flutter 3.38 added an experimental automatic migration for existing iOS apps:

```sh
flutter config --enable-uiscene-migration
```

Plugins that consume application lifecycle events must adopt scene events.
Add-to-app hosts may migrate so plugins receive them (3.38-guide).

`UIScene` lifecycle support is the default by 3.41-guide. Move logic out of
deprecated `AppDelegate` lifecycle paths. In 3.41.0,
`FlutterSceneLifeCycleProvider.sceneLifeCycleDelegate` is read-only; native code
must stop assigning it.

## Swift Package Manager

### Default dependency manager (3.44-guide)

Swift Package Manager replaces CocoaPods as the default for ordinary iOS and macOS
Flutter applications. Build or run can migrate the Xcode project automatically.
Plugin authors must add SwiftPM support; packages upgraded from the 2024 pilot need
a `FlutterFramework` dependency.

A dependency that still requires CocoaPods triggers a warning and temporary
fallback. A blocking project can temporarily set
`enable-swift-package-manager: false` in `pubspec.yaml`. Both escape paths are
planned for removal.

Flutter's SwiftPM integration does not support add-to-app hosts
(apple-platform-migrations).

### Audit automatic migration

Automatic migration changes `Runner.xcodeproj/project.pbxproj` and the shared
`Runner.xcscheme`. For a customized project that cannot migrate automatically, add
the local generated package to the `Runner` target and embed its product:

- iOS:
  `ios/Flutter/ephemeral/Packages/FlutterGeneratedPluginSwiftPackage`
- macOS:
  `macos/Flutter/ephemeral/Packages/FlutterGeneratedPluginSwiftPackage`

Every flavor needs a scheme pre-action named **Run Prepare Flutter Framework
Script**, with build settings provided by `Runner`:

```sh
# iOS
"$FLUTTER_ROOT/packages/flutter_tools/bin/xcode_backend.sh" prepare

# macOS
"$FLUTTER_ROOT"/packages/flutter_tools/bin/macos_assemble.sh prepare
```

Custom targets follow the same manual path: attach the generated package product to
the custom target and use that target for **Provide build settings from**.

### Disable or remove SwiftPM

Disabling SwiftPM makes Flutter use CocoaPods but does not undo Xcode migration. To
remove the integration fully, or before opening the project with a Flutter SDK older
than 3.24:

1. Disable the feature and run `flutter clean`.
2. Remove the `FlutterGeneratedPluginSwiftPackage` dependency and embedded product
   in Xcode.
3. Delete the **Run Prepare Flutter Framework Script** pre-action.

### Raise a plugin's minimum OS

When a Swift package product requires a newer platform version, raise the target's
**Minimum Deployments** value in Xcode, then regenerate configuration:

```sh
flutter build ios --config-only
flutter build macos --config-only
```

Flutter had already announced that the next stable after 3.32-guide would deprecate
iOS 12 and macOS 10.14 and raise minimums to iOS 13 and macOS 10.15. Always verify
the selected SDK's current floor.

## Xcode, signing, and plugin APIs

The minimum supported Xcode is 15 and Xcode 16 is recommended (3.44.0). All macOS
command-line tools, including iOS device communication binaries, run natively on
Apple Silicon by 3.44-guide; Rosetta is unnecessary, and Intel development-host
support is planned to end.

With Xcode 26, `flutter run` normally uses `devicectl` for physical-device install,
launch, and debugging. If that path fails, disable it with
`flutter config --no-enable-lldb-debugging` (3.38-guide).

Plugin tooling can share one Darwin implementation between iOS and macOS. iOS
tooling generates `ExportOptions.plist` for manual signing, and Flutter framework
output can be emitted as a Swift package (3.41.0).

Public iOS and macOS embedder APIs are consumable from Swift. iOS exposes
`FlutterPluginRegistrant` for generated or custom registration (3.35.0).

The iOS/macOS `FlutterPluginRegistrar` protocol exposes `viewController` for
controller-scoped plugin work (3.38.0). An iOS plugin can access another registered
plugin for native composition and coordination (3.44.0).

## Text editing and Cupertino integration

Editable text uses `SystemContextMenu` by default on iOS (3.32.0). Ordinary paste
no longer prompts for cross-app permission by default, although custom context-menu
actions were initially outside that change (3.32-guide). Custom edit-menu actions
later gained secure-paste handling (3.38.0).

`TextField.enableInlinePrediction` opts into experimental iOS inline predictive
text; it is off by default and styling is experimental (3.44-guide).

`CupertinoSheet.showDragHandle` adds a native-styled drag handle. On iOS,
`BackdropFilter` uses bounded blur so translucent content does not bleed color at
its edges (3.41-guide).

`CupertinoDynamicColor`-specific `withAlpha` and `withOpacity` methods are
deprecated; use the standard `Color` methods (3.38-guide).

## Add-to-app sizing

An iOS embedded view can size from Flutter content by setting
`FlutterViewController.isAutoResizable = true` (3.41-guide). The Flutter root must
accept unbounded constraints; a size-dependent `ListView` or `LayoutBuilder` cannot
sit at the root.

## Apple verification

- Build every target, flavor, and scheme and inspect SwiftPM migration diffs.
- Verify scheme pre-actions, generated package products, signing export options,
  minimum deployments, Xcode version, and Apple Silicon tooling.
- Exercise `UIScene` activation/background flows and lifecycle-aware plugins.
- Test add-to-app hosts separately; do not apply ordinary-app SwiftPM assumptions.
- Exercise system context menus, secure paste, inline prediction, sheets, blur,
  wide-gamut color, float images, and the selected macOS renderer.
