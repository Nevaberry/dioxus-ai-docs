# Android platform integration

## Contents

- [Required project migrations](#required-project-migrations)
- [SDK and build-tool requirements](#sdk-and-build-tool-requirements)
- [Architectures and artifacts](#architectures-and-artifacts)
- [Rendering](#rendering)
- [Display and privacy APIs](#display-and-privacy-apis)
- [Threads and native interop](#threads-and-native-interop)
- [Removed and changed tool controls](#removed-and-changed-tool-controls)

## Required project migrations

### Gradle plug-in application

The imperative script mechanism for applying Flutter's Gradle plug-in has been
removed. Projects created before the declarative setup was introduced must migrate
their `settings.gradle` and application plug-in declarations instead of suppressing
the old warning (`3.29.0`).

New plug-in projects use Gradle's Kotlin DSL. Remove `pluginClass: none` from a
Flutter plug-in platform declaration; omitting `pluginClass` is the supported way to
declare a platform implementation with no native code. Also omit
`dartPluginClass: 'none'` when there is no Dart plug-in class.

### Embedding and system UI

- Android v1 embedding Java APIs are removed. Migrate applications and plug-ins to
  the v2 embedding.
- `SystemUiMode.edgeToEdge` is the default system-UI mode. Layout content around
  system-bar insets rather than assuming Flutter keeps it outside the bars.
- On Android 16 and later, edge-to-edge opt-out is being deprecated,
  `SystemChrome.setPreferredOrientations` can be ineffective, and embedder methods
  that set status-bar, navigation-bar, or navigation-divider colors are deprecated.
- Android 17 large screens ignore application orientation and resizability
  restrictions. Design every large-screen route for resizing and orientation changes.

`FlutterFragment` and `FlutterFragmentActivity` support predictive back, extending
the system gesture to fragment-based and add-to-app embeddings (`3.44.0`). Material
route defaults are described in the navigation reference.

## SDK and build-tool requirements

Flutter enforces its Android `minSdk`. The floor moved to API 24, so projects that
override `flutter.minSdkVersion` must raise it. The supported build floor at that
point was Gradle 8.7.0, Android Gradle Plugin 8.6.0, and Java 17 (`3.35-guide`).
Newer templates and tool checks also introduced Kotlin 2.1.0, Gradle 8.12, and an
AGP warning threshold of 8.3; do not copy one isolated version from a template into
an older project without checking the whole combination.

For the later tested stack, Kotlin Gradle Plugin 2.2.20 was the maximum known
supported version with AGP 8.11.1 and Gradle 8.14; AGP 8.11.1 requires Gradle 8.13
or newer (`3.38-guide`). Flutter also defaults `ndkVersion` to NDK r28, which
supplies the native toolchain needed for correct 16 KB page alignment for Android
15-and-newer targets.

### Android Gradle Plugin 9

Do not apply one migration recipe across SDK releases:

- The `3.41-guide` contract says Flutter applications using plug-ins and Flutter
  plug-ins must not move to AGP 9 because those combinations are unsupported.
- The later `3.44-guide` migration supports AGP 9's built-in Kotlin compilation.
  Remove the separately applied Kotlin Gradle plug-in from applications and plug-ins
  because it conflicts with built-in Kotlin. A migrated plug-in must set a minimum
  Flutter SDK constraint of 3.44, and its dependencies must migrate before Flutter's
  temporary compatibility layer disappears.

Use `minSdk` rather than `minSdkVersion` in Gradle 9-compatible configuration. When
product flavors define their own `abiFilters`, set the Android project flag
`disable-abi-filtering` so those filters take precedence over Flutter's injected
filters.

## Architectures and artifacts

- Android 32-bit x86 is deprecated; 32-bit ARM and x86_64 remain supported.
- Android tooling no longer strips symbols from `libapp.so` by default. Account for
  the artifact-size change and use the retained information for native symbolication.
- `flutter test integration_test` builds native assets from development dependencies;
  see the Dart tooling reference for hook and asset identity rules.

## Rendering

### Impeller backends

On Android, a device without a functional Vulkan driver falls back to Impeller's
OpenGLES backend rather than Skia. The Android emulator and several older MediaTek,
PowerVR, and Samsung XClipse configurations also use OpenGLES. As of Flutter 3.29.3,
API 28 and older use Skia, while API 29 and newer default to Impeller.

Opting out of Impeller on Android is deprecated. Do not build a long-term workaround
around restoring Skia on supported devices.

### Hybrid Composition++ platform views

Hybrid Composition++ delegates Android platform-view compositing to the operating
system and provides reliable `SurfaceView` support. It has device and API
requirements, remains opt-in, and is not the default. Enable it for a run:

```sh
flutter run --enable-hcpp
```

Or enable it in `AndroidManifest.xml`:

```xml
<meta-data
  android:name="io.flutter.embedding.android.EnableHcpp"
  android:value="true" />
```

Test unsupported devices and fallback behavior before adopting it.

## Display and privacy APIs

`MediaQueryData.displayCornerRadii` reports physical and logical display corner radii,
allowing layouts to keep controls away from heavily rounded corners:

```dart
final cornerRadii = MediaQuery.of(context).displayCornerRadii;
```

On Android API 35 and newer, `SensitiveContent` protects sensitive UI by obscuring
the entire application screen during media projection.

## Threads and native interop

Dart runs on the application main thread on Android. Mobile embedders no longer
permit opting out of UI/platform thread merging, so native integration code must not
assume separate Flutter UI and platform task runners. See the embedding reference for
the same contract on other targets.

## Removed and changed tool controls

- The experimental `--fast-start` option is removed.
- Projects using Flutter's framework default target Android SDK 36.
- Tool validation can reject an outdated `minSdk`, Gradle, AGP, Kotlin, Java, or NDK
  combination rather than leaving the failure to the Android build itself.
