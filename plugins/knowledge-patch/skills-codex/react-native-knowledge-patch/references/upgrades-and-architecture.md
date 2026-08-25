# Upgrades and architecture

## New Architecture cutover

React Native 0.82 always uses the New Architecture: Android
`newArchEnabled=false` and iOS `RCT_NEW_ARCH_ENABLED=0` are ignored. Test the
migration on 0.81 when comparison with the Legacy Architecture is still
needed. The interop layer remains available for libraries that support both
architectures. (Batch `0.82-0.85`.)

### Legacy implementation removal

On iOS, 0.83 can compile out Legacy Architecture code when
`RCT_REMOVE_LEGACY_ARCH=1`; that option is incompatible with precompiled
binaries. Version 0.84 excludes the Legacy implementation by default. A
temporary restoration must build React Native core from source:

```sh
RCT_USE_PREBUILT_RNCORE=0 RCT_REMOVE_LEGACY_ARCH=0 bundle exec pod install
```

Android 0.84 removes these Legacy types:

- `LazyReactPackage`
- `CxxModuleWrapper`
- `CallbackImpl`
- `BridgeDevSupportManager`
- `LayoutAnimationController`
- `OnBatchCompleteListener`

In 0.85, `CatalystInstanceImpl` is removed, `NativeViewHierarchyManager` is a
stub, `ReactTextUpdate` becomes internal, and `ReactZIndexedViewGroup` and
`UIManagerHelper` are deprecated. Migrate to supported extension points rather
than copying or importing similarly named implementation classes.

## iOS bootstrap and embedding

### Install the dependency provider

The 0.77 Community Template uses a Swift `AppDelegate`, but Objective-C++
remains supported and is required when an app registers pure C++ modules there.
Every `RCTAppDelegate`, including one retained in Objective-C++, must install
`RCTAppDependencyProvider`; omitting it can make third-party dependencies fail
at runtime. (Batch `0.77-0.81`.)

```objc
#import <ReactAppDependencyProvider/RCTAppDependencyProvider.h>
self.dependencyProvider = [RCTAppDependencyProvider new];
```

### Embed without app-delegate ownership

From 0.78, a brownfield app can use `RCTReactNativeFactory` to create a root
view inside a view controller without routing setup through the app delegate.
`RCTDefaultReactNativeFactoryDelegate` provides the development or bundled
JavaScript URL.

```swift
reactNativeFactory = RCTReactNativeFactory(delegate: reactNativeDelegate!)
view = reactNativeFactory?.rootViewFactory.view(withModuleName: "MyModule")
```

### Register generated native modules

From 0.79, apps and libraries can register native modules through
`codegenConfig.ios.modulesProvider`. This avoids `AppDelegate` edits and lets a
Swift app delegate use pure C++ TurboModules through an Objective-C++ provider.

```json
{
  "codegenConfig": {
    "ios": {"modulesProvider": {"NativeSample": "NativeSampleModuleProvider"}}
  }
}
```

## Hermes V1 and precompiled iOS builds

### Early precompiled-build opt-ins

React Native 0.80 can set `RCT_USE_RN_DEP=1` during pod installation to use a
prebuilt XCFramework for third-party dependencies such as Folly and GLog. In
0.81, `RCT_USE_PREBUILT_RNCORE=1` additionally precompiles React Native core.
Core prebuilds prevent stepping into React Native internals. With Xcode 26 Beta,
these builds also require `SWIFT_ENABLE_EXPLICIT_MODULES=NO`.

```sh
RCT_USE_RN_DEP=1 RCT_USE_PREBUILT_RNCORE=1 bundle exec pod install
```

### Hermes V1 opt-in and default

In 0.82 and 0.83, Hermes V1 is experimental and must be built from source. Pin
the release's experimental `hermes-compiler`, set `hermesV1Enabled=true` on
Android or `RCT_HERMES_V1_ENABLED=1` during iOS pod installation, and do not use
`RCT_USE_PREBUILT_RNCORE`.

React Native 0.84 makes Hermes V1 the default and also makes downloaded,
precompiled iOS `.xcframework` binaries the default. To build core from source,
run pod installation with:

```sh
RCT_USE_PREBUILT_RNCORE=0 bundle exec pod install
```

Since 0.83, `RCT_SYMBOLICATE_PREBUILT_FRAMEWORKS=1` downloads dSYMs when
precompiled React Native code must be debugged.

Opting out of Hermes V1 requires all of the following:

- Resolve `hermes-compiler` to `0.15.0`.
- Set `hermesV1Enabled=false` and build from source on Android.
- On iOS, install pods with both `RCT_HERMES_V1_ENABLED=0` and
  `RCT_USE_PREBUILT_RNCORE=0`.

## Android platform upgrades

### Android 15 edge-to-edge and 16 KB pages

With `targetSdk` 35, Android 15 forces edge-to-edge rendering. Layouts must
consume system-bar insets; `react-native-safe-area-context` already handles
this case. React Native 0.77 supports Android devices with 16 KB memory pages,
but the app's own native code and every third-party native dependency must also
be compatible.

### Android 16 defaults

React Native 0.81 targets Android 16/API 36 by default. Edge-to-edge is
mandatory on Android 16, while `edgeToEdgeEnabled` can extend that behavior to
earlier Android versions. Predictive back is enabled by default. Migrate custom
native `onBackPressed()` handling; use a temporary opt-out only during the
transition.

## Build-tool requirements

- React Native 0.77 builds against Kotlin 2.0.21.
- React Native 0.80 moves to Kotlin 2.1.20.
- React Native 0.81 requires Node.js 20.19.4 or newer and Xcode 16.1 or newer.
- React Native 0.82 moves its Android build to Gradle 9.0.0.
- React Native 0.84 requires Node.js 22.11 or later.
- React Native 0.85 supports Node.js 20.19.4+, 22, and 24+, and rejects EOL
  lines such as 21 and 23.

Apply the requirements for the exact React Native release being built rather
than assuming that a later release's toolchain rules apply to an earlier one.

## Release support and patch targeting

At the 0.86.0 release snapshot, 0.86 and 0.85 are active, 0.84 is at the end of
its cycle, and 0.83 and older are unsupported. The stated maintenance window
is the latest three minor series. (Batch `0.86.0`.)

React Native 0.86.1 was not published because of a Maven issue. Upgrade from
0.86.0 directly to 0.86.2 instead of targeting the absent patch release.
(Batch `0.86.2`.)
