---
name: flutter-knowledge-patch
description: Flutter/Dart changes since training cutoff (latest: 3.41/Dart 3.11) — dot shorthands, null-aware elements, build hooks, squircle shapes, RadioGroup, UIScene lifecycle, platform-specific assets. Load before working with Flutter.
version: "3.41"
license: MIT
metadata:
  author: Nevaberry
---

# Flutter / Dart Knowledge Patch

Claude Opus 4.6 knows Flutter through 3.29 and Dart through 3.7. It is **unaware** of the features below, covering Flutter 3.32–3.41 / Dart 3.8–3.11.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Dart language | [references/dart-language.md](references/dart-language.md) | Dot shorthands, null-aware elements, cross-compilation, build hooks, analyzer plugins, granular @Deprecated |
| Widgets & UI | [references/widgets-and-ui.md](references/widgets-and-ui.md) | Squircle/RoundedSuperellipseBorder, RadioGroup, DropdownMenuFormField, CupertinoExpansionTile, SensitiveContent, RepeatingAnimationBuilder, Navigator.popUntilWithResult |
| Tooling & config | [references/tooling-and-config.md](references/tooling-and-config.md) | Platform-specific assets, web_dev_config.yaml, web hot reload, widget previews, pub workspace globs, dart pub cache gc, git tag_pattern deps |
| Platform & migration | [references/platform-and-migration.md](references/platform-and-migration.md) | UIScene lifecycle (iOS), Android API 24 minimum, NDK r28, breaking changes by version |

---

## Quick Reference: Dart Language Additions

### Dot shorthands (Dart 3.10)

Omit type names when the compiler can infer:

```dart
// Enums, constructors, static members
Padding(
  padding: .all(8.0),             // EdgeInsets.all(8.0)
  child: Text('Hello'),
)
Column(
  mainAxisAlignment: .start,      // MainAxisAlignment.start
  crossAxisAlignment: .center,    // CrossAxisAlignment.center
  children: [/* ... */],
)

// Default parameter values
void logMessage(String msg, {LogLevel level = .info}) { }
```

### Null-aware elements (Dart 3.8)

Prepend `?` to include a collection element only when non-null:

```dart
var items = [?nullableString, ?nullable.value];
var map = {?'key': nullableValue};
```

### Build hooks stable (Dart 3.10)

Compile native code (C++, Rust, Swift) and bundle with a Dart package — no CMake/Gradle/SPM needed. Previously "native assets".

### Cross-compilation (Dart 3.8+)

```bash
dart compile exe --target-os=linux --target-arch=arm64 bin/server.dart
# Dart 3.9 adds: arm (ARM32), riscv64
```

---

## Quick Reference: Key New Widgets

| Widget | Version | Purpose |
|---|---|---|
| `RoundedSuperellipseBorder` / `ClipRSuperellipse` | 3.32 | iOS-style squircle corners |
| `RawMenuAnchor` | 3.32 | Unstyled menu (widgets layer) |
| `RadioGroup` | 3.35 | Manages radio state (replaces `Radio.groupValue`) |
| `DropdownMenuFormField` | 3.35 | M3 dropdown in Form |
| `CupertinoExpansionTile` | 3.35 | iOS expandable list tile |
| `SensitiveContent` | 3.35 | Obscure during screen share (Android API 35+) |
| `RepeatingAnimationBuilder` | 3.41 | Declarative looping animations |

---

## Quick Reference: Critical Breaking Changes

| Change | Version |
|---|---|
| `Radio.groupValue`/`onChanged` deprecated → use `RadioGroup` | 3.35 |
| Minimum Android SDK → API 24; requires Gradle 8.7.0, AGP 8.6.0, Java 17 | 3.35 |
| Default Android transition → `FadeForwardsPageTransitionsBuilder`; predictive back on by default | 3.38 |
| UIScene lifecycle mandatory for iOS (after iOS 26) | 3.38 |
| UIScene lifecycle is the default (was opt-in) | 3.41 |
| Flutter 3.38+ requires Java 17 minimum for Android | 3.38 |
| NDK r28 default (16KB page size support) | 3.38 |
| `ExpansionTileController` → `ExpansibleController` | 3.32 |
| `CardTheme`/`DialogTheme`/`TabBarTheme` → `CardThemeData`/`DialogThemeData`/`TabBarThemeData` | 3.32 |
| `firebase_vertexai` → `firebase_ai` | 3.32 |
| Do NOT upgrade to AGP 9 — plugin migration not supported | 3.41 |

---

## UIScene Lifecycle (iOS — critical)

Apple mandates UIScene lifecycle for UIKit apps after iOS 26. Migrate:

```bash
flutter config --enable-uiscene-migration  # automatic (experimental in 3.38, default in 3.41)
```

Plugins using app lifecycle events must also update.

---

## Platform-Specific Assets (Flutter 3.41)

```yaml
flutter:
  assets:
    - path: assets/logo.png
    - path: assets/web_worker.js
      platforms: [web]
    - path: assets/desktop_icon.png
      platforms: [windows, linux, macos]
```

---

## Pub Dependency Features

### Git tag_pattern version solving (Dart 3.9)

```yaml
dependencies:
  my_dependency:
    git:
      url: https://github.com/example/my_dependency
      tag_pattern: v{{version}}
    version: ^2.0.1
```

### Workspace globs (Dart 3.11)

```yaml
workspace:
  - pkg/* # adds all packages inside pkg/
```

### Flutter SDK constraint enforcement (Dart 3.9)

From language version 3.9, `flutter` constraint upper bound is enforced in root packages:

```yaml
environment:
  sdk: ^3.9.0
  flutter: 3.33.0 # pub get fails if Flutter SDK isn't exactly 3.33.0
```

---

## Reference Files

| File | Contents |
|---|---|
| [dart-language.md](references/dart-language.md) | Dot shorthands, null-aware elements, cross-compilation, build hooks, analyzer plugins, granular @Deprecated |
| [widgets-and-ui.md](references/widgets-and-ui.md) | Squircle, RadioGroup, DropdownMenuFormField, CupertinoExpansionTile, SensitiveContent, RepeatingAnimationBuilder, popUntilWithResult, content-sized views, shader decoding |
| [tooling-and-config.md](references/tooling-and-config.md) | Platform-specific assets, web dev config, hot reload, widget previews, pub workspace globs, dart pub cache gc, git tag_pattern, Flutter SDK constraint |
| [platform-and-migration.md](references/platform-and-migration.md) | UIScene lifecycle, Android requirements, all breaking changes by version |
