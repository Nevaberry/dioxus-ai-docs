# Apple platform integration

## Rendering and text integration

- iOS Skia support is removed and `FLTEnableImpeller` no longer opts out of
  Impeller (3.29.0). SkSL build targets and warm-up artifacts are also removed
  (3.32.0).
- Native iOS editing uses `SystemContextMenu` by default (3.32.0); custom edit-menu
  actions participate in secure-paste handling (3.38.0).
- iOS bounded backdrop blur prevents color bleed at translucent edges
  (`3.41-guide`). macOS supports Display P3, and float32 images can retain float32
  data through `Image.toByteData()` (3.44.0).
- Impeller remains opt-in on macOS: use `flutter run --enable-impeller` for a run or
  top-level `FLTEnableImpeller` inside the `Info.plist` `<dict>` for deployed builds
  (`rendering-and-web`).

## UIScene and embedder lifecycle

- The experimental automatic UIScene migration appeared in `3.38-guide` behind
  `flutter config --enable-uiscene-migration`. Apps, lifecycle-aware plug-ins, and
  add-to-app hosts needed scene events.
- UIScene is the supported default by `3.41-guide`. Move deprecated AppDelegate
  lifecycle logic before platform requirements make the migration mandatory.
- `FlutterSceneLifeCycleProvider.sceneLifeCycleDelegate` is read-only; native
  integrations must not assign it (3.41.0).
- UI/platform thread merging is mandatory on iOS (`3.38-guide`).

## Swift and plug-in APIs

- Public iOS/macOS embedder APIs are consumable from Swift, and iOS provides the
  `FlutterPluginRegistrant` protocol for generated or custom registration
  (3.35.0).
- `FlutterPluginRegistrar.viewController` supports controller-scoped iOS/macOS
  plug-in work, and a Darwin implementation can be shared between platforms
  (3.38.0, 3.41.0).
- One registered iOS plug-in can access another registered plug-in (3.44.0).

## Swift Package Manager

- SwiftPM becomes the default for ordinary iOS/macOS applications in
  `3.44-guide`; CLI build/run may migrate the Xcode project. Plug-ins need SwiftPM
  support and 2024-pilot packages need a `FlutterFramework` dependency. CocoaPods-
  only dependencies trigger a temporary warning/fallback. A blocking project may
  temporarily set `enable-swift-package-manager: false`, but both escape paths are
  planned for removal.
- Automatic migration edits `Runner.xcodeproj/project.pbxproj` and the shared
  `Runner.xcscheme` (`apple-platform-migrations`). Audit both after migration.
- For manual repair, attach the local generated package under
  `ios/Flutter/ephemeral/Packages/FlutterGeneratedPluginSwiftPackage` or its macOS
  equivalent,
  `macos/Flutter/ephemeral/Packages/FlutterGeneratedPluginSwiftPackage`, to the
  Runner target, and embed its product.
- Every flavor needs a **Run Prepare Flutter Framework Script** scheme pre-action,
  with build settings from Runner. Run `xcode_backend.sh prepare` on iOS or
  `macos_assemble.sh prepare` on macOS.
- SwiftPM integration does not support add-to-app. Custom targets require manual
  package-product attachment and must provide the pre-action's build settings from
  that target.
- Disabling SwiftPM selects CocoaPods but does not undo Xcode migration. To remove
  it fully, disable the feature, run `flutter clean`, remove the package dependency
  and embedded product, and delete the prepare pre-action.

## Deployment targets, Xcode, and signing

- The stream first announced a move from iOS 12/macOS 10.14 to iOS 13/macOS 10.15
  (`3.32-guide`). Raise deployment targets deliberately and check package minimums.
- When a Swift package product raises its minimum OS, update **Minimum Deployments**
  and regenerate configuration with `flutter build ios --config-only` or
  `flutter build macos --config-only` (`apple-platform-migrations`).
- Xcode 26 physical-device runs use `devicectl`; use
  `flutter config --no-enable-lldb-debugging` only as the documented fallback
  (`3.38-guide`).
- iOS tooling generates `ExportOptions.plist` for manual signing (3.41.0).
- Flutter framework output can also be generated as a Swift package (3.41.0).
- Minimum supported Xcode is 15 and Xcode 16 is recommended (3.44.0). macOS command
  line and iOS device tools run natively on Apple Silicon; Intel host support is
  planned to end (`3.44-guide`).

## Cupertino presentation and add-to-app sizing

- `CupertinoSheet.showDragHandle` adds the native-style handle (`3.41-guide`).
- `FlutterViewController.isAutoResizable = true` lets an iOS add-to-app view size
  itself from Flutter content. Its Flutter root must accept unbounded constraints;
  avoid a size-dependent `ListView` or `LayoutBuilder` at the root (`3.41-guide`).
- Test scene lifecycle events, custom targets and flavors, plugin-to-plugin access,
  secure paste, signing, device deployment, minimum OS settings, and both SwiftPM
  migration and rollback paths.
