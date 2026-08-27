# Android platform integration

## Project and embedding migrations

### Gradle plugin application and embedding APIs (3.29.0)

The imperative Flutter Gradle-script application mechanism is removed. Projects
created before Flutter 3.16 that still emit its warning must migrate to declarative
plugin application.

The Android v1 embedding Java APIs are removed (breaking-change-guides). Migrate
applications and plugins to the v2 embedding; do not preserve v1 shims in new work.

Newly created plugins use Gradle Kotlin DSL by default (3.41-guide).

### Build baselines

New templates in 3.32.0 use Kotlin 2.1.0 and Gradle 8.12. Flutter enforces its
Android `minSdk` and warns below Android Gradle Plugin 8.3 instead of 7.3, so older
projects can require upgrades.

By 3.35-guide, Flutter's Android minimum is API 24. The minimum build stack is
Gradle 8.7.0, AGP 8.6.0, and Java 17. Android x86 32-bit is deprecated; ARM 32-bit
and x86_64 remain supported. Projects overriding `flutter.minSdkVersion` must raise
that value.

For 3.38-guide, the tested combination is Kotlin Gradle Plugin 2.2.20 with AGP
8.11.1 and Gradle 8.14; AGP 8.11.1 requires at least Gradle 8.13. The default
`ndkVersion` is NDK r28 to meet 16 KB page-alignment requirements for Android
15-and-newer targets.

Trust the selected Flutter SDK's validation and project templates over mixing these
snapshots into an untested combination.

### Android Gradle Plugin 9 transition

At 3.41-guide, apps using plugins and plugins themselves were not yet supported on
AGP 9; avoid backporting a later migration to that SDK.

At 3.44-guide, AGP 9's built-in Kotlin support requires removing the separately
applied Kotlin Gradle plugin from applications and plugins. A migrated plugin must
declare a minimum Flutter SDK of 3.44, and its dependencies must also migrate before
temporary compatibility is removed.

Gradle 9-compatible configuration uses `minSdk` rather than `minSdkVersion`
(3.38.0). The `disable-abi-filtering` project flag lets product-flavor
`abiFilters` take precedence over Flutter's injected filters (3.41.0).

## System UI, screens, and policy changes

Flutter 3.27 made `SystemUiMode.edgeToEdge` the default
(breaking-change-guides). Layout content around system bars explicitly.

Projects using framework defaults target Android SDK 36 by 3.35.0. Android 16
deprecates edge-to-edge opt-out; `SystemChrome.setPreferredOrientations` can be
ineffective, and embedder methods that set status-bar, navigation-bar, or
navigation-divider colors are deprecated.

On Android 17, large screens ignore application orientation and resizability
restrictions (breaking-change-guides). Build layouts that tolerate resizing and
orientation changes.

`MediaQueryData.displayCornerRadii` exposes physical and logical display-corner
radii so layouts can avoid clipping on aggressively rounded screens
(3.44-guide).

```dart
final cornerRadii = MediaQuery.of(context).displayCornerRadii;
```

On API 35 and later, wrap sensitive UI in `SensitiveContent` when media projection
should obscure the entire app screen (3.35-guide).

## Rendering

### Impeller backend selection

In 3.29.0, Android devices without a working Vulkan driver fall back to Impeller's
OpenGLES backend rather than Skia. By 3.29.3, API 28 and older use Skia while API
29 and newer default to Impeller; the emulator and specified older MediaTek,
PowerVR, and Samsung XClipse configurations use Impeller OpenGLES
(3.32-guide).

Opting out of Impeller on Android is deprecated (3.38.0). Test the selected backend
on representative devices instead of assuming Vulkan, OpenGLES, or Skia from the
OS version alone.

### Hybrid Composition++ platform views (3.44-guide)

Hybrid Composition++ delegates platform-view compositing to Android and provides
reliable `SurfaceView` support. It has device and API requirements and is not the
default.

```sh
flutter run --enable-hcpp
```

Or enable it in `AndroidManifest.xml`:

```xml
<meta-data
  android:name="io.flutter.embedding.android.EnableHcpp"
  android:value="true" />
```

## Threads and embedding behavior

Dart began running on the application main thread on Android and iOS in 3.29.0.
Mobile embedders later made UI/platform thread merging mandatory, with no opt-out
(3.38-guide). Native integrations must not depend on separate runners or on the
serialization that separation implied.

Android content-sized add-to-app views can enable content sizing in the manifest and
give the relevant `FlutterView` a wrap-content dimension (3.41-guide). The Flutter
root must accept unbounded constraints; do not put a size-dependent `ListView` or
`LayoutBuilder` at the root.

`FlutterFragment` and `FlutterFragmentActivity` support Android predictive back,
including fragment-based and add-to-app hosts (3.44.0). `MaterialApp` also defaults
to predictive-back-aware transitions (3.38-guide); test both framework routing and
native host integration.

## Input

Android 14 and later supports stylus handwriting in Material and Cupertino text
fields (3.32-guide). Disable it per field with
`stylusHandwritingEnabled: false` and rename
`SelectionChangedCause.scribble` to `SelectionChangedCause.stylusHandwriting`.

Text editing recognizes Home and End (3.35-guide). `hintLocales` provides language
hints to Android input methods (3.35.0).

On Android API 36, semantic announcement events are deprecated. Use live-region
updates where possible and test the remaining non-focusable-text limitation
(3.32-guide).

## Build artifacts and diagnostics

Android builds no longer strip symbols from `libapp.so` by default, affecting both
artifact contents and native symbolication (3.44.0). Revisit packaging-size
assumptions and crash-symbol workflows.

The experimental `--fast-start` option is removed (3.38.0). Use supported run and
startup-profile controls.

## Android verification

- Run `flutter analyze` and all Android plugin builds.
- Build each flavor and ABI; confirm effective `minSdk`, target SDK, NDK, Kotlin,
  AGP, Gradle, and Java versions.
- Exercise edge-to-edge insets, rounded corners, resize/orientation changes, and
  media projection.
- Test predictive back in activities, fragments, and add-to-app hosts.
- Exercise platform views on supported and unsupported HCPP configurations.
- Verify renderer fallback, stylus handwriting, keyboard editing, native symbols,
  and 16 KB page alignment where applicable.
