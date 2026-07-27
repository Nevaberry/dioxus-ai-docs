# Upgrades and architecture

These task-oriented notes draw from extraction batches `0.77-0.81`,
`0.82-0.85`, and `0.86.0`. Version labels below identify behavior boundaries.

## New Architecture migration

React Native 0.82 always runs the New Architecture. Android
`newArchEnabled=false` and iOS `RCT_NEW_ARCH_ENABLED=0` are ignored. Migrate and
test on 0.81 when a Legacy Architecture comparison is still needed; 0.81 is the
last release that can execute the Legacy Architecture. The interop layer
remains available to libraries that support both architectures.

Several styling capabilities introduced in 0.77 also require the New
Architecture. See [ui-components-and-styling.md](ui-components-and-styling.md)
before treating a styling failure as a parser or type-definition problem.

## Legacy implementation removal

On iOS, 0.83 can compile out Legacy Architecture code with
`RCT_REMOVE_LEGACY_ARCH=1`. That setting is incompatible with precompiled
binaries. Version 0.84 removes the Legacy code by default; temporarily restoring
it requires React Native core to be built from source:

```sh
RCT_USE_PREBUILT_RNCORE=0 RCT_REMOVE_LEGACY_ARCH=0 bundle exec pod install
```

Android 0.84 removes these Legacy implementation types:

- `LazyReactPackage`
- `CxxModuleWrapper`
- `CallbackImpl`
- `BridgeDevSupportManager`
- `LayoutAnimationController`
- `OnBatchCompleteListener`

Android 0.85 removes `CatalystInstanceImpl`, leaves
`NativeViewHierarchyManager` as a stub, makes `ReactTextUpdate` internal, and
deprecates `ReactZIndexedViewGroup` and `UIManagerHelper`. Migrate callers to
supported New Architecture entry points rather than importing adjacent internal
classes.

## iOS app bootstrap and module registration

The 0.77 Community Template uses a Swift `AppDelegate`. Objective-C++ remains
supported and is required in the documented setup for apps that register pure
C++ modules. Whether Swift or Objective-C++, every `RCTAppDelegate` must install
`RCTAppDependencyProvider`; otherwise third-party dependencies can fail at
runtime.

```objc
#import <ReactAppDependencyProvider/RCTAppDependencyProvider.h>
self.dependencyProvider = [RCTAppDependencyProvider new];
```

React Native 0.78 adds `RCTReactNativeFactory` for brownfield apps. It can create
a root view within a view controller without routing setup through the app
delegate. `RCTDefaultReactNativeFactoryDelegate` supplies the development or
bundled JavaScript URL.

```swift
reactNativeFactory = RCTReactNativeFactory(delegate: reactNativeDelegate!)
view = reactNativeFactory?.rootViewFactory.view(withModuleName: "MyModule")
```

From 0.79, apps and libraries can register native modules through
`codegenConfig.ios.modulesProvider`. This avoids app-delegate edits and lets a
Swift app delegate use pure C++ TurboModules through an Objective-C++ provider.

```json
{
  "codegenConfig": {
    "ios": {
      "modulesProvider": {
        "NativeSample": "NativeSampleModuleProvider"
      }
    }
  }
}
```

## Hermes V1 and precompiled iOS builds

Precompiled iOS support arrives in stages:

- In 0.80, `RCT_USE_RN_DEP=1` selects a prebuilt XCFramework for third-party
  dependencies such as Folly and GLog.
- In 0.81, `RCT_USE_PREBUILT_RNCORE=1` additionally precompiles React Native
  core. This prevents stepping into React Native internals. With Xcode 26 Beta,
  it also requires `SWIFT_ENABLE_EXPLICIT_MODULES=NO`.

```sh
RCT_USE_RN_DEP=1 RCT_USE_PREBUILT_RNCORE=1 bundle exec pod install
```

In 0.82 and 0.83, Hermes V1 is experimental and requires a source build. Pin the
release's experimental `hermes-compiler`, set `hermesV1Enabled=true` on Android
or `RCT_HERMES_V1_ENABLED=1` for iOS pod installation, and do not enable
`RCT_USE_PREBUILT_RNCORE`.

Version 0.84 makes both Hermes V1 and downloaded precompiled iOS
`.xcframework` binaries the defaults. Set `RCT_USE_PREBUILT_RNCORE=0` during
`pod install` to compile core from source. Since 0.83,
`RCT_SYMBOLICATE_PREBUILT_FRAMEWORKS=1` downloads dSYMs for debugging
precompiled React Native code.

Opting out of Hermes V1 requires all of the following:

1. Resolve `hermes-compiler` to `0.15.0`.
2. Set `hermesV1Enabled=false` on Android or
   `RCT_HERMES_V1_ENABLED=0` during iOS pod installation.
3. Build from source on Android, or set both `RCT_HERMES_V1_ENABLED=0` and
   `RCT_USE_PREBUILT_RNCORE=0` on iOS.

## Android platform targets

With `targetSdk` 35, Android 15 enforces edge-to-edge rendering. Layouts must
consume system-bar insets; `react-native-safe-area-context` already handles this
case. React Native 0.77 also supports devices with 16 KB memory pages, but every
other native binary and dependency in the app must be compatible independently.

React Native 0.81 targets Android 16/API 36 by default. Edge-to-edge is mandatory
on Android 16. The `edgeToEdgeEnabled` Gradle property can extend that behavior
to earlier Android versions. Predictive back is enabled by default, so migrate
custom native `onBackPressed()` handling or use the documented temporary opt-out
only while transitioning.

## Build-tool requirements

- React Native 0.77 builds against Kotlin 2.0.21.
- React Native 0.80 moves to Kotlin 2.1.20.
- React Native 0.81 requires Node.js 20.19.4 or newer and Xcode 16.1 or newer.
- React Native 0.82 moves the Android build to Gradle 9.0.0.
- React Native 0.84 requires Node.js 22.11 or later.
- React Native 0.85 explicitly supports Node.js 20.19.4+, 22, and 24+, but
  rejects end-of-life odd-numbered lines such as 21 and 23.

Match the requirement to the app's exact React Native release; the 0.85 Node.js
matrix is not a continuation of the narrower 0.84 minimum statement.

## Support-policy snapshot

At the 0.86 release snapshot, 0.86 and 0.85 are active, 0.84 is at the end of
its cycle, and 0.83 and older are unsupported. The stated maintenance window is
the latest three minor series. Treat these labels as a release-time snapshot,
not a permanent statement about currently supported branches.
