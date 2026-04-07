# Platform, Web & Native Integration

## Wasm Without Special Headers (Flutter 3.29)

Flutter web wasm apps no longer require special HTTP headers. Default headers run wasm single-threaded; special headers enable multi-threading.

## Hot Reload on Web

- **Flutter 3.32**: Experimental. Enable with `flutter run -d chrome --web-experimental-hot-reload`
- **Flutter 3.35**: Stable. Enabled by default with `-d chrome`. No flags needed.
- **Flutter 3.38**: Also works with `-d web-server` (multiple browsers simultaneously).

## Web Dev Config File (Flutter 3.38)

Configure host, port, certificates, proxy, and headers in `web_dev_config.yaml` at project root. Checked into source control.

## Predictive Back — Default on Android (Flutter 3.38)

`PredictiveBackPageTransitionBuilder` is the default Android page transition in `MaterialApp`. Users see a home screen preview during back gesture.

## Default Transition Changed (Flutter 3.38)

Default Android page transition is now `FadeForwardsPageTransitionsBuilder` (changed from `ZoomPageTransitionsBuilder`).

## Platform-Specific Assets (Flutter 3.41)

Specify which platforms an asset should be bundled for:

```yaml
flutter:
  assets:
    - path: assets/logo.png
    - path: assets/web_worker.js
      platforms: [web]
    - path: assets/desktop_icon.png
      platforms: [windows, linux, macos]
```

## Content-Sized Flutter Views — Add-to-App (Flutter 3.41)

Flutter views in native apps can auto-resize based on content:

- **iOS**: `FlutterViewController.isAutoResizable = true`
- **Android**: Set width/height to `content_wrap` in manifest

Root widget must support unbounded constraints (avoid `ListView`, `LayoutBuilder` at top level).

## Multi-Window APIs — Experimental (Flutter 3.41)

Desktop popup, tooltip, and dialog windows on Linux/macOS/Windows. See `examples/multiple_windows` in the Flutter repo.

## UISceneDelegate Adoption (Flutter 3.38)

Flutter now uses `UISceneDelegate` on iOS by default. Migration guide at `docs.flutter.dev/release/breaking-changes/uiscenedelegate`.

## AGP 9 Warning (Flutter 3.41)

Do NOT update to AGP 9 yet — plugin migration not supported. Track `flutter/flutter#181383`.

## Merged Threads on Linux Desktop (Flutter 3.41)

UI and platform threads merged by default on Flutter Linux desktop.

## Minimum Android Requirements (Flutter 3.35)

- Min Android SDK: API 24 (Android 7)
- Gradle: 8.7.0
- AGP: 8.6.0
- Java: 17

## SnackBar Breaking Change (Flutter 3.38)

SnackBars with an action button no longer auto-dismiss. Must be dismissed by user.
