---
name: react-native-knowledge-patch
description: React Native
version: 0.86.0
license: MIT
metadata:
  author: Nevaberry
---


# React Native Knowledge Patch

## Use this patch

- Inspect the app's exact `react-native` version before applying
  version-dependent guidance.
- Treat the manifest, native projects, build configuration, code, and tests as
  authoritative when they disagree with this patch.
- Read the architecture and native-extension references before upgrading a
  native app or library.
- Read the focused reference before changing Metro, DevTools, networking,
  styling, input, platform behavior, or error reporting.
- Treat experimental and `unstable_` APIs as integration surfaces rather than
  compatibility promises.
- For a release newer than the frontmatter version, verify current behavior in
  the project and current release documentation.

## Reference index

| Reference | Topics |
|---|---|
| [upgrades-and-architecture.md](references/upgrades-and-architecture.md) | New Architecture enforcement, Legacy removal, iOS bootstrap, Hermes V1, precompiled iOS builds, toolchains, Android targets, support policy |
| [native-extension-migrations.md](references/native-extension-migrations.md) | Android/Kotlin signatures, C++ flags and headers, removed native APIs, view transitions, iOS request hooks, window lifecycle, privacy manifests |
| [ui-components-and-styling.md](references/ui-components-and-styling.md) | CSS additions and parsing, images, `Modal`, DOM refs, React APIs, animations, accessibility, touch behavior |
| [platform-behavior.md](references/platform-behavior.md) | Android hardware events, platform colors, autofill, system bars, modal windows, image dimensions |
| [javascript-and-observability.md](references/javascript-and-observability.md) | Error semantics, promise rejections, Performance APIs, instrumentation hooks, JavaScript API changes, DevTools diagnostics |
| [metro-networking-and-tooling.md](references/metro-networking-and-tooling.md) | Metro resolution and TLS, Community CLI hooks, bundle compression, WebSockets, network inspection, optimized debug builds, ESLint |

## Architecture upgrade essentials

### New Architecture is mandatory from 0.82

From 0.82, the runtime ignores Android `newArchEnabled=false` and iOS
`RCT_NEW_ARCH_ENABLED=0`. Test migration on 0.81 when an app still needs a
Legacy Architecture comparison. Dual-architecture libraries may continue to
use the interop layer.

iOS can compile out Legacy implementation code in 0.83 and does so by default
in 0.84. Restoring it requires a source build:

```sh
RCT_USE_PREBUILT_RNCORE=0 RCT_REMOVE_LEGACY_ARCH=0 bundle exec pod install
```

Android removes or stubs several bridge and UIManager implementation types in
0.84 and 0.85. Do not replace them with similarly named internals; move to
supported extension APIs described in the native migration reference.

### Keep iOS bootstrap dependencies explicit

The Swift Community Template does not make Objective-C++ invalid. Keep an
Objective-C++ `AppDelegate` when pure C++ registration requires it, but install
`RCTAppDependencyProvider` on every `RCTAppDelegate`:

```objc
#import <ReactAppDependencyProvider/RCTAppDependencyProvider.h>
self.dependencyProvider = [RCTAppDependencyProvider new];
```

For brownfield embedding, `RCTReactNativeFactory` can create a root view from a
view controller without moving setup through the app delegate. For generated
native modules, prefer `codegenConfig.ios.modulesProvider` over app-delegate
registration edits.

## Engine and iOS binary defaults

Hermes V1 changes from an experimental source-build opt-in in 0.82–0.83 to the
default engine in 0.84. Downloaded precompiled iOS frameworks also become the
default in 0.84.

Build React Native core from source when native debugging, Legacy restoration,
or the selected Hermes mode requires it:

```sh
RCT_USE_PREBUILT_RNCORE=0 bundle exec pod install
```

Set `RCT_SYMBOLICATE_PREBUILT_FRAMEWORKS=1` when precompiled React Native code
needs dSYMs. Hermes V1 opt-out is coordinated dependency and build work: resolve
`hermes-compiler` to `0.15.0`, disable V1, and use source builds on the
applicable platform.

## Android upgrade essentials

- With `targetSdk` 35, Android 15 forces edge-to-edge layout. Consume
  system-bar insets; `react-native-safe-area-context` handles this case.
- Framework support for 16 KB memory pages does not make every native
  dependency compatible. Audit all app and third-party native binaries.
- React Native 0.81 targets Android 16/API 36. Edge-to-edge is mandatory on
  Android 16, and predictive back is enabled by default.
- Use `edgeToEdgeEnabled` to extend edge-to-edge behavior to earlier Android
  versions. Migrate custom native `onBackPressed()` handling or use only the
  documented temporary predictive-back opt-out during transition.
- Check version-specific Node.js, Xcode, Kotlin, and Gradle requirements before
  diagnosing build failures.

## Metro and package resolution

Metro 0.82, shipped with React Native 0.79, enables package `"exports"` and
`"imports"` resolution by default. A temporary compatibility switch is:

```js
module.exports = {
  resolver: {unstable_enablePackageExports: false},
};
```

From 0.80, React Native itself has an `"exports"` map. For matched exports,
Metro does not expand platform extensions, and Jest deep-import mocks may
resolve differently. Fix package exports and test imports before relying on
the compatibility switch.

React Native 0.81 starts honoring Community CLI `resolveRequest` and
`getModulesRunBeforeMainModule`. Remove stale settings if a project depended on
them being ignored. Middleware integrations should make `serverBaseUrl`
relative to the middleware host.

## Native library migration essentials

Custom New Architecture CMake projects should apply the supplied compiler
helper so `RN_SERIALIZABLE_STATE` and required C++ flags stay synchronized:

```cmake
target_compile_reactnative_options(myLibraryName PRIVATE)
```

Codegen libraries without a custom `CMakeLists.txt` do not need this call.
Custom Fabric text integrations must model `textAlignVertical` as a paragraph
attribute.

Android Java-to-Kotlin migrations tighten nullability and sometimes parameter
types. Recompile overrides against the pinned version; do not preserve an old
signature with unsafe casts. C++ include roots and shared-pointer aliases also
change, so consult the native migration reference before patching compiler
errors.

## JavaScript behavior that can break upgrades

### Error reporting becomes more complete

Uncaught JavaScript errors include their original message and stack, `cause`,
and a component Owner Stack from 0.81. Unhandled promise rejections enter the
`console.error` and JavaScript error-reporting path from 0.82. Expect previously
hidden errors and possible ingestion-volume changes after an upgrade.

Only the literal boolean `false` keeps the special behavior of
`reportErrorsAsExceptions`; other falsey values do not. Normalize configuration
before passing it.

### Stricter public values

- Reset `Appearance.setColorScheme()` with `'unspecified'`, not `null` or
  `undefined`.
- Replace removed `StyleSheet.absoluteFillObject` with
  `StyleSheet.absoluteFill`.
- Add units to CSS string lengths such as `box-shadow` and `filter` offsets.
- Use space-separated `hwb()` syntax rather than comma-separated components.

## UI and component behavior

New Architecture styling includes `display: 'contents'`,
`boxSizing: 'content-box'`, blend modes with isolation, and outline properties.
Outlines render outside the border box without affecting layout, and
`boxSizing` still defaults to `border-box`.

`Modal` forwards `style` to its inner container while `transparent` and
`backdropColor` retain precedence. Views with non-invertible transforms such as
`scaleX: 0` or `scaleY: 0` no longer receive touches on either mobile platform.

Native component refs expose a DOM-compatible subset, including traversal,
document lookup, and `getBoundingClientRect()`, while retaining legacy methods
such as `measure`. Do not assume browser-complete DOM support.

## Diagnostics quick reference

- Use the stable Web Performance subset for marks, measures, entry queries,
  Event Timing, long tasks, and production `PerformanceObserver` collection.
- `PerformanceObserver.observe({type: 'event'})` defaults to a 104 ms duration
  threshold. Set `durationThreshold` explicitly to capture shorter events.
- DevTools network inspection covers `fetch`, `XMLHttpRequest`, and `<Image>`,
  but not arbitrary custom networking libraries.
- Performance traces combine JavaScript, React, network, and User Timing data;
  0.86 adds a React Native Renderer operations track.
- `debugOptimized` preserves JavaScript debugging with optimized C++, but is
  unsuitable for native C++ debugging.
- Treat `unstable_getViewTransitionInstance` and the experimental shared
  animation backend as unstable surfaces that require version pinning and
  release-channel checks.
