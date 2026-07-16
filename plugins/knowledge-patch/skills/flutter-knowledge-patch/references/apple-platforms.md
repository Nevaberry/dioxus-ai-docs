# Apple platform integration

## Contents

- [iOS scene lifecycle](#ios-scene-lifecycle)
- [Swift Package Manager](#swift-package-manager)
- [Deployment targets and Xcode](#deployment-targets-and-xcode)
- [Native APIs and plug-ins](#native-apis-and-plug-ins)
- [Development hosts](#development-hosts)
- [Rendering behavior](#rendering-behavior)
- [Content-sized embedded views](#content-sized-embedded-views)

## iOS scene lifecycle

Flutter fully supports the iOS `UIScene` lifecycle by default (`3.41-guide`). Existing
applications that still put lifecycle behavior only in deprecated `AppDelegate`
callbacks must migrate it. Lifecycle-aware plug-ins must consume scene events, and
add-to-app hosts must expose scene events if their plug-ins depend on them.

Earlier projects can use the automatic migration path supplied with `3.38-guide`:

```sh
flutter config --enable-uiscene-migration
```

Use the manual migration when automatic edits cannot preserve a customized host.
`FlutterSceneLifeCycleProvider.sceneLifeCycleDelegate` is read-only; native code must
not assign it.

## Swift Package Manager

Swift Package Manager is the default dependency manager for ordinary iOS and macOS
Flutter applications (`3.44-guide`). During build or run, Flutter can migrate the
Xcode project. Plug-in authors must publish SwiftPM support; a plug-in updated from
the 2024 pilot also needs a `FlutterFramework` dependency.

Dependencies that still require CocoaPods produce a warning and temporarily fall
back. A project with a blocking incompatibility can temporarily add this to
`pubspec.yaml`:

```yaml
flutter:
  config:
    enable-swift-package-manager: false
```

The fallback and opt-out are transitional. Do not use them as the final migration.
SwiftPM integration does not support add-to-app hosts.

### Audit automatic migration

Automatic migration edits `Runner.xcodeproj/project.pbxproj` and the shared
`Runner.xcscheme`. For a customized project that cannot be repaired automatically:

1. Add the local generated package to the `Runner` target:
   `ios/Flutter/ephemeral/Packages/FlutterGeneratedPluginSwiftPackage` or
   `macos/Flutter/ephemeral/Packages/FlutterGeneratedPluginSwiftPackage`.
2. Add its product under **Frameworks, Libraries, and Embedded Content**.
3. Give every flavor a scheme build pre-action named
   **Run Prepare Flutter Framework Script**.
4. Set **Provide build settings from** to `Runner`, or to the corresponding custom
   target.
5. Run the platform command from that pre-action.

```sh
# iOS
"$FLUTTER_ROOT/packages/flutter_tools/bin/xcode_backend.sh" prepare

# macOS
"$FLUTTER_ROOT"/packages/flutter_tools/bin/macos_assemble.sh prepare
```

Custom Xcode targets require the same manual package-product attachment and must be
the source of build settings for their scheme pre-action.

### Fully remove SwiftPM integration

Disabling SwiftPM switches Flutter back to CocoaPods but does not undo Xcode project
edits. To remove integration completely, or before opening the project with a Flutter
SDK older than 3.24:

1. Disable SwiftPM.
2. Run `flutter clean`.
3. Remove `FlutterGeneratedPluginSwiftPackage` from package dependencies.
4. Remove its embedded product.
5. Delete the **Run Prepare Flutter Framework Script** pre-action.

## Deployment targets and Xcode

- The announced Apple platform floor moved from iOS 12 and macOS 10.14 toward iOS 13
  and macOS 10.15 (`3.32-guide`). Check the selected SDK's current minimum before
  raising a host or plug-in target.
- When a Swift package product requires a newer OS, raise **Minimum Deployments** in
  Xcode and regenerate the corresponding Flutter configuration:

```sh
flutter build ios --config-only
flutter build macos --config-only
```

- The supported Xcode floor is 15 and Xcode 16 is recommended (`3.44.0`). Upgrade
  development and CI hosts that still use older Xcode releases.
- With Xcode 26, `flutter run` normally installs, launches, and debugs physical devices
  through command-line `devicectl`. If that path fails, temporarily use:

```sh
flutter config --no-enable-lldb-debugging
```

Flutter tooling generates `ExportOptions.plist` for manually signed iOS builds.
Flutter framework output can also be generated as a Swift package.

## Native APIs and plug-ins

Public iOS and macOS embedder APIs are available to Swift. iOS provides the
`FlutterPluginRegistrant` protocol for generated or custom registration (`3.35.0`).
The iOS/macOS `FlutterPluginRegistrar` protocol exposes `viewController` for work
scoped to the host controller.

An iOS plug-in can access another registered plug-in, allowing native implementations
to coordinate without routing every interaction through Dart. Plug-in tooling can
share one Darwin implementation between iOS and macOS. New Apple plug-ins should use
Swift because the Objective-C plug-in template is deprecated.

## Development hosts

All macOS command-line tools, including iOS device communication binaries, run
natively on ARM. Apple Silicon development hosts therefore do not need Rosetta.
Support for Intel Mac development hosts is planned to end in a future release.

## Rendering behavior

- iOS no longer supports Skia; `FLTEnableImpeller` cannot opt out of Impeller.
- Impeller remains opt-in on macOS. Enable it for a debug run or deployed application:

```sh
flutter run --enable-impeller
```

```xml
<key>FLTEnableImpeller</key>
<true />
```

- macOS rendering supports Display P3. See the graphics reference for float image and
  color-space behavior.
- On iOS, `BackdropFilter` uses bounded blur behavior so translucent sheet content no
  longer bleeds color at its edges.

## Content-sized embedded views

An iOS embedded Flutter view can size itself from Flutter content by setting
`FlutterViewController.isAutoResizable = true`. The Flutter root must accept unbounded
constraints; do not put a size-dependent `ListView` or `LayoutBuilder` at the root.
Android content sizing and experimental desktop equivalents are covered in the
embedding reference.
