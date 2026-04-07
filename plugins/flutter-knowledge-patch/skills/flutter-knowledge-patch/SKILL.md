---
name: flutter-knowledge-patch
description: "Flutter 3.29-3.41 + Dart 3.7-3.11 changes since training cutoff — dot shorthands, squircles, null-aware elements, predictive back, platform assets. Load before working with Flutter/Dart."
license: MIT
version: "3.41.0"
metadata:
  author: Nevaberry
---

# Flutter 3.29–3.41 / Dart 3.7–3.11 Knowledge Patch

Claude's baseline knowledge covers Flutter through ~3.19 and Dart through ~3.3. This skill provides features from Flutter 3.29 (Feb 2025) and Dart 3.7 (Feb 2025) onwards.

## Quick Reference — Dart Language

| Feature | Version | Example |
|---------|---------|---------|
| Null-aware elements | Dart 3.8 | `[?nullableValue]` — omits if null |
| Dot shorthands | Dart 3.10 | `.center` instead of `MainAxisAlignment.center` |
| Doc imports | Dart 3.8 | `/// @docImport 'dart:async';` |
| Cross compilation | Dart 3.8 | `dart compile exe --target-os=linux --target-arch=arm64` |
| Macros cancelled | Dart 3.7 | `@JsonCodable()` discontinued; use `json_serializable` |

See `references/dart-language.md` for syntax details and examples.

## Quick Reference — Dart Tooling

| Feature | Version | Detail |
|---------|---------|--------|
| Pub git tags | Dart 3.9 | `tag_pattern: v{{version}}` in pubspec |
| Pub workspace globs | Dart 3.11 | `workspace: [pkg/*]` |
| `dart pub cache gc` | Dart 3.11 | Clean unused cached packages |
| Build hooks (stable) | Dart 3.10 | Bundle native C++/Rust/Swift code |
| Analyzer plugins | Dart 3.10 | Custom lint rules in `analysis_options.yaml` |
| Flutter SDK upper bound | Dart 3.9 | `flutter: 3.33.0` enforced in root packages |

See `references/dart-tooling.md` for configuration details.

## Quick Reference — New & Changed Widgets

| Widget | Version | Purpose |
|--------|---------|---------|
| `CupertinoSheetRoute` | 3.29 | iOS draggable modal sheet |
| `RoundedSuperellipseBorder` | 3.32 | Squircle (iOS-style) corners |
| `ClipRSuperellipse` | 3.32 | Clip child to squircle shape |
| `Expansible` | 3.32 | Unstyled expand/collapse |
| `RawMenuAnchor` | 3.32 | Unstyled menu with keyboard nav |
| `DropdownMenuFormField` | 3.35 | M3 dropdown for forms |
| `CupertinoExpansionTile` | 3.35 | iOS expandable list tile |
| `RadioGroup` | 3.35 | Replaces `Radio.groupValue` (breaking) |
| `CarouselView.builder` | 3.41 | Dynamic carousel content |
| `RepeatingAnimationBuilder` | 3.41 | Declarative continuous animations |
| `Badge.count(maxCount:)` | 3.38 | Capped badge count ("99+") |

See `references/widgets.md` for code examples.

## Quick Reference — Platform, Web & Native

| Feature | Version | Detail |
|---------|---------|--------|
| Wasm without headers | 3.29 | Single-threaded by default, headers for multi-thread |
| Hot reload web | 3.32→3.35 | Experimental in 3.32, stable in 3.35 |
| Web dev config | 3.38 | `web_dev_config.yaml` for host/port/proxy/headers |
| Predictive back (default) | 3.38 | Android back gesture with home preview |
| Platform-specific assets | 3.41 | `platforms: [web]` in pubspec assets |
| Content-sized views | 3.41 | Add-to-App auto-resize (`isAutoResizable`) |
| Multi-window (experimental) | 3.41 | Desktop popup/tooltip/dialog windows |
| UISceneDelegate (iOS) | 3.38 | Default on iOS; migration guide available |
| AGP 9 warning | 3.41 | Do NOT upgrade — plugin migration unsupported |

See `references/platform-web.md` for configuration and migration details.

## Quick Reference — Navigation & Animation

| Feature | Version | Detail |
|---------|---------|--------|
| `FadeForwardsPageTransitionsBuilder` | 3.29 | New M3 transition; default in 3.38 |
| `PredictiveBackPageTransitionBuilder` | 3.38 | Default Android back transition |
| `Navigator.popUntilWithResult` | 3.41 | Pop multiple screens, return value |
| `OverlayPortal.overlayChildLayoutBuilder` | 3.38 | Render overlay in any ancestor `Overlay` |
| Fragment shader improvements | 3.41 | `decodeImageFromPixelsSync`, 128-bit textures |

See `references/navigation-animation.md` for code examples.

## Quick Reference — Accessibility

| Feature | Version | Detail |
|---------|---------|--------|
| `SelectionListener` | 3.29 | Get selection text from `SelectionArea` |
| `SemanticsRole` | 3.32 | Assign roles for screen readers (web) |
| `SensitiveContent` | 3.35 | Obscure during screen sharing (Android 15+) |
| `SliverEnsureSemantics` | 3.35 | Keep slivers in semantics tree when scrolled |
| `SemanticsLabelBuilder` | 3.35 | Combine data into single announcement |
| `SliverSemantics` | 3.38 | Annotate slivers for screen readers |
| `CalendarDatePicker.calendarDelegate` | 3.32 | Non-Gregorian calendar support |

See `references/accessibility.md` for code examples.

## Breaking Changes

| Change | Version | Migration |
|--------|---------|-----------|
| `Radio.groupValue` deprecated | 3.35 | Use `RadioGroup` wrapper |
| SnackBar no auto-dismiss with action | 3.38 | User must dismiss manually |
| Default Android transition changed | 3.38 | Now `FadeForwardsPageTransitionsBuilder` |
| `UISceneDelegate` default on iOS | 3.38 | See migration guide |
| Min Android SDK → API 24 | 3.35 | Android 7+ required |
| Gradle 8.7.0, AGP 8.6.0, Java 17 | 3.35 | Update build tools |
| Legacy web libs deprecated | Dart 3.7 | Use `dart:js_interop` + `package:web` |
| Merged threads on Linux desktop | 3.41 | UI + platform threads merged by default |

## Reference Files

| File | Contents |
|------|----------|
| `dart-language.md` | Null-aware elements, dot shorthands, doc imports, cross compilation |
| `dart-tooling.md` | Pub git tags, workspace globs, build hooks, analyzer plugins |
| `widgets.md` | CupertinoSheet, squircles, Expansible, RadioGroup, CarouselView |
| `platform-web.md` | Hot reload web, predictive back, platform assets, multi-window |
| `navigation-animation.md` | Page transitions, popUntilWithResult, RepeatingAnimationBuilder |
| `accessibility.md` | SemanticsRole, SliverSemantics, SensitiveContent, SelectionListener |

## Critical Examples

### Dot Shorthands (Dart 3.10+ / Flutter 3.38+)

```dart
Column(
  mainAxisAlignment: .center,
  children: [
    Padding(padding: .all(8.0), child: Text('Hi')),
  ],
)
```

### Null-Aware Elements (Dart 3.8+)

```dart
List<String> names = [?nullableName, ?user?.displayName];
```

### Squircle Container

```dart
Container(
  decoration: ShapeDecoration(shape: RoundedSuperellipseBorder(
    borderRadius: BorderRadius.circular(20),
  )),
)
```

### RadioGroup (Flutter 3.35+, Breaking)

```dart
RadioGroup<String>(
  groupValue: selected,
  onChanged: (value) => setState(() => selected = value),
  children: [Radio<String>(value: 'a'), Radio<String>(value: 'b')],
)
```

### Platform-Specific Assets

```yaml
flutter:
  assets:
    - path: assets/logo.png
    - path: assets/web_worker.js
      platforms: [web]
```
