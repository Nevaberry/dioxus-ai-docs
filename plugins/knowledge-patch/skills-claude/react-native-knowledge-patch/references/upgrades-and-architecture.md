# Upgrades and architecture

## New Architecture enforcement

The runtime is New Architecture-only from 0.82. Android
`newArchEnabled=false` and iOS `RCT_NEW_ARCH_ENABLED=0` are ignored. Complete
app migration and comparison testing on 0.81, the last version that can run the
Legacy Architecture. The interop layer remains available for libraries that
support both architectures. This transition comes from batch `0.82-0.85`.

## Legacy implementation removal

iOS 0.83 can compile out Legacy code with `RCT_REMOVE_LEGACY_ARCH=1`, but this
cannot be combined with precompiled binaries. Version 0.84 removes that code by
default. Temporarily restore it by building core from source:

```sh
RCT_USE_PREBUILT_RNCORE=0 RCT_REMOVE_LEGACY_ARCH=0 bundle exec pod install
```

Android 0.84 removes `LazyReactPackage`, `CxxModuleWrapper`, `CallbackImpl`,
`BridgeDevSupportManager`, `LayoutAnimationController`, and
`OnBatchCompleteListener`. Version 0.85 removes `CatalystInstanceImpl`, stubs
`NativeViewHierarchyManager`, makes `ReactTextUpdate` internal, and deprecates
`ReactZIndexedViewGroup` and `UIManagerHelper`.

## iOS application bootstrap

The 0.77 Community Template uses a Swift `AppDelegate`. Objective-C++ remains
supported and is required when registration of pure C++ modules occurs there.
Every `RCTAppDelegate`, including a retained Objective-C++ delegate, must
install the dependency provider or third-party dependencies can fail at
runtime:

```objc
#import <ReactAppDependencyProvider/RCTAppDependencyProvider.h>
self.dependencyProvider = [RCTAppDependencyProvider new];
```

React Native 0.78 adds `RCTReactNativeFactory` for brownfield applications to
create a root view in a view controller without routing setup through the app
delegate. `RCTDefaultReactNativeFactoryDelegate` supplies the development or
bundled JavaScript URL:

```swift
reactNativeFactory = RCTReactNativeFactory(delegate: reactNativeDelegate!)
view = reactNativeFactory?.rootViewFactory.view(withModuleName: "MyModule")
```

From 0.79, apps and libraries can register generated iOS native modules through
`codegenConfig.ios.modulesProvider`. This avoids app-delegate edits and lets a
Swift app delegate use pure C++ TurboModules through an Objective-C++ provider:

```json
{
  "codegenConfig": {
    "ios": {"modulesProvider": {"NativeSample": "NativeSampleModuleProvider"}}
  }
}
```

These bootstrap migrations belong to batch `0.77-0.81`.

## Hermes V1 and precompiled iOS builds

In 0.80, `RCT_USE_RN_DEP=1` uses a prebuilt XCFramework for third-party
dependencies such as Folly and GLog. In 0.81,
`RCT_USE_PREBUILT_RNCORE=1` also precompiles React Native core. Core prebuilds
prevent stepping into React Native internals, and Xcode 26 Beta additionally
requires `SWIFT_ENABLE_EXPLICIT_MODULES=NO`.

```sh
RCT_USE_RN_DEP=1 RCT_USE_PREBUILT_RNCORE=1 bundle exec pod install
```

Hermes V1 is an experimental source-build opt-in in 0.82 and 0.83. Pin the
release's experimental `hermes-compiler`, set `hermesV1Enabled=true` on Android
or `RCT_HERMES_V1_ENABLED=1` for iOS pod installation, and do not use
`RCT_USE_PREBUILT_RNCORE`.

Version 0.84 makes Hermes V1 the default engine and downloaded precompiled iOS
`.xcframework` binaries the default. Set `RCT_USE_PREBUILT_RNCORE=0` during
`pod install` to build core from source. From 0.83,
`RCT_SYMBOLICATE_PREBUILT_FRAMEWORKS=1` downloads dSYMs for precompiled React
Native code.

Opting out of Hermes V1 requires resolving `hermes-compiler` to `0.15.0`, then
setting `hermesV1Enabled=false` and building Android from source, or installing
iOS pods with both `RCT_HERMES_V1_ENABLED=0` and
`RCT_USE_PREBUILT_RNCORE=0`.

## Android platform targets

With `targetSdk` 35, Android 15 forces edge-to-edge rendering. Account for
system-bar insets; `react-native-safe-area-context` handles this case. React
Native 0.77 supports devices using 16 KB memory pages, but every other native
binary in the app must also be compatible.

React Native 0.81 targets Android 16/API 36. Edge-to-edge is mandatory on
Android 16, while the `edgeToEdgeEnabled` Gradle property extends it to earlier
Android versions. Predictive back is enabled by default, so migrate custom
native `onBackPressed()` handling or use the documented temporary opt-out only
during transition.

## Toolchain requirements

- React Native 0.77 builds against Kotlin 2.0.21.
- React Native 0.80 moves to Kotlin 2.1.20.
- React Native 0.81 requires Node.js 20.19.4 or later and Xcode 16.1 or later.
- React Native 0.82 moves the Android build to Gradle 9.0.0.
- React Native 0.84 requires Node.js 22.11 or later.
- React Native 0.85 supports Node.js 20.19.4+, 22, and 24+, but rejects EOL
  lines such as 21 and 23.

## Support and patch-release selection

At the 0.86.0 release snapshot, 0.86 and 0.85 were active, 0.84 was at the end
of its cycle, and 0.83 and older were unsupported. The stated maintenance
window is the latest three minor series.

React Native 0.86.1 was not published because of a Maven issue. The included
`0.86.2` guidance therefore directs upgrades from 0.86.0 to 0.86.2 rather than
to the absent patch release.
