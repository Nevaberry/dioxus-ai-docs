# Android platform integration

## Rendering and platform views

- Android devices without working Vulkan fall back to Impeller OpenGLES rather
  than Skia (3.29.0). As of 3.29.3, API 28 and below use Skia while API 29 and
  above default to Impeller; emulators and listed older GPU families use OpenGLES
  (`3.32-guide`).
- Opting out of Android Impeller is deprecated (3.38.0). Do not design a current
  integration around restoring Skia.
- Hybrid Composition++ delegates platform-view compositing to Android and supports
  `SurfaceView`. Enable it with `--enable-hcpp` or
  `io.flutter.embedding.android.EnableHcpp` metadata in `AndroidManifest.xml` only
  after checking its API/device requirements; it was not the default
  (`3.44-guide`).
- `MediaQueryData.displayCornerRadii` exposes physical and logical display corners
  for safe layout on aggressively rounded screens (`3.44-guide`).

## Gradle, SDK, and Java requirements

- Imperative application of Flutter's Gradle script is removed; migrate pre-3.16
  projects to declarative plug-in application (3.29.0).
- New 3.32 templates used Kotlin 2.1.0 and Gradle 8.12. Tooling enforces Flutter's
  `minSdk` and raised the AGP warning threshold from 7.3 to 8.3 (3.32.0).
- The `3.35-guide` floor is API 24, Gradle 8.7.0, AGP 8.6.0, and Java 17. Projects
  overriding `flutter.minSdkVersion` must raise it. Android x86 32-bit is
  deprecated; ARM32 and x86_64 remain supported.
- The tested `3.38-guide` combination is KGP 2.2.20, AGP 8.11.1, and Gradle 8.14;
  AGP 8.11.1 itself requires Gradle 8.13 or newer. NDK r28 is the default needed
  `ndkVersion` for 16 KB page alignment on Android 15-and-newer targets.
- AGP 9 was unsupported for plug-in-using apps and plug-ins in `3.41-guide`.
  With `3.44-guide`, AGP 9's built-in Kotlin requires removing the separately
  applied Kotlin Gradle plug-in from apps and plug-ins. Migrated plug-ins need a
  minimum Flutter SDK constraint of 3.44, and all dependencies must migrate.
- Gradle 9-compatible configuration uses `minSdk`, not `minSdkVersion` (3.38.0).
- `disable-abi-filtering` lets flavor `abiFilters` override Flutter's injected
  filtering (3.41.0).

## Threading and embedding

- Dart moved onto the application main thread on Android and iOS in 3.29.0;
  integrations must not assume separate UI and platform runners.
- Mobile thread merging became mandatory in `3.38-guide`; embedders cannot opt out.
- `FlutterFragment` and `FlutterFragmentActivity` support Android predictive back,
  including fragment and add-to-app embeddings (3.44.0).
- Android v1 embedding Java APIs were removed in Flutter 3.29. Applications and
  plug-ins must use v2 embedding (`breaking-change-guides`).

## System UI, windows, and large screens

- Flutter 3.27 defaults `SystemUiMode` to edge-to-edge. Consume system-bar insets
  explicitly (`breaking-change-guides`).
- Flutter's framework default targets SDK 36 in 3.35.0. On Android 16+, opting out
  of edge-to-edge is being deprecated, `SystemChrome.setPreferredOrientations`
  may be ineffective, and embedder setters for status/navigation bar colors are
  deprecated.
- `SensitiveContent` obscures the whole app during media projection on API 35+
  (`3.35-guide`).
- Android 17 large screens ignore orientation and resizability restrictions;
  layouts must tolerate resizing and rotation (`breaking-change-guides`).

## Build artifacts and native integration

- Android tooling retains symbols in `libapp.so` by default, improving native
  symbolication but changing artifact contents (3.44.0).
- Verify emulator and physical-device renderer selection, 16 KB page alignment,
  ABI filters, native symbols, predictive back, edge-to-edge insets, rotation, and
  screen-share protection on the targeted API levels.
