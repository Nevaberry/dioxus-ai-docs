# Tooling & Configuration (Flutter 3.32–3.41)

## Platform-specific assets (Flutter 3.41)

Restrict which platforms an asset is bundled for in `pubspec.yaml`:

```yaml
flutter:
  assets:
    - path: assets/logo.png
    - path: assets/web_worker.js
      platforms: [web]
    - path: assets/desktop_icon.png
      platforms: [windows, linux, macos]
```

## Git dependency version solving with tag_pattern (Dart 3.9)

Git dependencies can now be version-solved based on git tags using `tag_pattern`:

```yaml
dependencies:
  my_dependency:
    git:
      url: https://github.com/example/my_dependency
      tag_pattern: v{{version}}
    version: ^2.0.1
```

Only commits matching the pattern with satisfying versions are considered during resolution.

## Flutter SDK constraint upper bound (Dart 3.9)

From language version 3.9, `flutter` constraint upper bound is enforced in root packages (like `dart` already was). Useful for locking team SDK versions:

```yaml
environment:
  sdk: ^3.9.0
  flutter: 3.33.0 # pub get fails if Flutter SDK isn't exactly 3.33.0
```

## Web dev config file (Flutter 3.38)

`web_dev_config.yaml` at project root configures `flutter run` for web — host, port, TLS certificates, headers, and proxy settings. Check it in for consistent team settings.

## Web hot reload default (Flutter 3.38)

Stateful hot reload enabled by default with `-d web-server` (multiple browsers supported). Disable with `--no-web-experimental-hot-reload`.

## Widget Previews (Flutter 3.35–3.38, experimental)

Preview widgets in isolation without running the full app. Annotate preview functions and view them in a sandboxed environment.

### Flutter 3.35
Currently opens in a browser window; IDE-embedded panes planned.

### Flutter 3.38
- Integrated in VS Code and IntelliJ/Android Studio (previews in IDE pane)
- `Preview` annotation is no longer `final` — extend it for custom preview types
- `MultiPreview` base class for multiple variations from one annotation
- `group` parameter in `Preview` for grouping related previews

## Wasm dry runs (Flutter 3.35)

JS web builds now perform a Wasm "dry run" to check readiness, emitting warnings. Toggle with `--no-wasm-dry-run`.

## Glob support in pub workspaces (Dart 3.11)

Declare workspace packages using globs (requires SDK `^3.11.0`):

```yaml
workspace:
  - pkg/* # adds all packages inside pkg/
```

## `dart pub cache gc` (Dart 3.11)

New command to clean unused packages from the global pub cache. Scans active projects and deletes package versions no longer referenced.

## New plugin project defaults (Flutter 3.41)

New plugin projects default to Kotlin DSL for Gradle.
