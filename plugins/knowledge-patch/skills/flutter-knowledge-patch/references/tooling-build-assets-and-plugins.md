# Flutter tooling, builds, assets, and plug-ins

## Contents

- [Widget Preview](#widget-preview)
- [Dart and Flutter MCP server](#dart-and-flutter-mcp-server)
- [DevTools and IDE editing](#devtools-and-ide-editing)
- [Assets](#assets)
- [Plug-in scaffolding and metadata](#plug-in-scaffolding-and-metadata)
- [CLI contract changes](#cli-contract-changes)
- [SDK metadata and project creation](#sdk-metadata-and-project-creation)
- [Release channels and archive provenance](#release-channels-and-archive-provenance)

## Widget Preview

Widget Preview is experimental. Annotate a top-level widget-building function with
`@Preview`; the old interim `WidgetPreview` wrapper is removed (`3.32.0`). The preview
scaffold defaults to Flutter Web.

```dart
@Preview(size: Size(320, 640), brightness: Brightness.dark)
Widget preview() => const Example();
```

The annotation uses `size` rather than separate `height` and `width` arguments, and
supports theme, brightness, and localization configuration. `Preview` is not `final`,
so reusable annotations can subclass it. `MultiPreview` produces several variants,
and `group` organizes related previews.

Private constants are valid annotation arguments. Function-valued wrappers and
themes must have public, statically accessible names. Rich custom annotations may
contain collection and record values (`3.44.0`).

### IDE and command integration

VS Code and IntelliJ/Android Studio integrate with the Previewer and initially filter
the environment to the selected source file. The environment can also filter by
group, name, script URI, or package URI (`3.44-guide`). Flutter Inspector is embedded;
if project widgets are absent, add the project package directory in Inspector
settings.

Transitive `dart:ffi` and `dart:io` imports can compile in a preview, but invoking
those platform APIs still fails. Use web-compatible conditional imports on callable
paths.

The preview command supports `--web-server` and `--machine`. Move `--dtd-url` after
`widget-preview start`; it is no longer a global option.

## Dart and Flutter MCP server

The Dart and Flutter MCP server ships on the stable Dart SDK channel (`3.35-guide`).
MCP clients can inspect a running widget tree, manage dependencies, use analyzer
feedback, and call `read_package_uris` to resolve and read project `package:` URIs,
including dependency source (`dart-3.11.0`).

Compatible clients can discover and connect to running applications and request hot
reload after an edit without manual connection setup.

## DevTools and IDE editing

- The redesigned Inspector is enabled by default. On-device widget selection remains
  active across selections until explicitly exited.
- The Logging view filters by severity and shows severity, category, zone, and isolate
  metadata (`3.29.0`).
- The Flutter Property Editor in VS Code and JetBrains IDEs edits widget properties
  and displays their documentation.
- The Flutter IntelliJ plug-in expanded installation support to CLion, GoLand, and
  PyCharm. Do not use that expanded support as a reason to retain a deprecated SDK.

## Assets

### Platform-specific bundles

Limit an asset to named target platforms through its `pubspec.yaml` entry
(`3.41-guide`):

```yaml
flutter:
  assets:
    - path: assets/logo.png
    - path: assets/web_worker.js
      platforms: [web]
    - path: assets/desktop_icon.png
      platforms: [windows, linux, macos]
```

This keeps unrelated platform assets out of the output bundle.

### Manifest and generated packages

`AssetManifest.json` is not emitted by default. Build scripts must use supported
asset APIs rather than assuming that file exists. The synthetic
`package:flutter_gen` package is removed; `flutter: generate: true` remains valid only
with non-synthetic output, which application code imports from its real source path.

### Data, native, and shader assets

Build hooks and code assets are stable, and Flutter tooling supports package-provided
data assets (`3.38.0`). Native assets are a preview feature; their hooks can consume
user-defined values from the workspace `pubspec.yaml`, and assets from development
dependencies are built for `flutter test integration_test`.

Shader declarations support flavors and asset transformers. Do not declare one shader
both as a shader and as an ordinary asset; this is a build error.

## Plug-in scaffolding and metadata

- `.flutter-plugins` is removed. Custom scripts must consume
  `.flutter-plugins-dependencies`.
- Omit `pluginClass` for a platform implementation with no native code; do not write
  `pluginClass: none`.
- Omit `dartPluginClass` when there is no Dart class; `dartPluginClass: 'none'`
  produces a warning.
- The Objective-C Apple plug-in template is deprecated; generate Swift plug-ins.
- The `plugin_ffi` template is deprecated. Use the standard plug-in template with FFI
  support.
- Apple plug-ins must add Swift Package Manager support; see the Apple reference.

## CLI contract changes

### Removed or renamed options

- Use `flutter assemble --dart-define` or `-D`; `--define` and `-d` are deprecated.
- Use `--no-dds` to disable DDS. `--disable-dds` and `--no-disable-dds` are removed.
- Remove `--fast-start`, `--web-hot-reload`, and the selectable
  `--explicit-package-dependencies` mode.
- The web service-worker `--pwa-strategy` option is deprecated.

`flutter assemble` accepts empty Dart defines. `flutter build` without a target exits
with status 1, so scripts must supply the build target.

### Build and run controls

- `flutter run --profile-startup` profiles startup.
- `flutter run --profile-microtasks` profiles `dart:async` microtask scheduling.
- Linux and Windows builds accept `--config-only`.
- `flutter test --ignore-timeouts` leaves time limits to an external harness.
- `flutter test --no-uninstall integration_test` preserves the installed target app.
- Chrome-device launches no longer add `--no-sandbox` automatically.

Web-only controls, including `--static-assets-url`, `--base-href`, Wasm dry runs,
minification, template defines, and cross-origin isolation, are in the web reference.

## SDK metadata and project creation

Read Flutter SDK version metadata from `bin/cache/flutter.version.json`; the SDK-root
`version` file is removed. `flutter create` now emits `pubspec.lock`, pinning the
versions chosen by the initial dependency resolution.

The tool exposes framework version information at runtime, and
`PlatformDispatcher.instance.engineId` distinguishes engines in a multi-engine
process.

## Release channels and archive provenance

A branch cutoff is the deadline for a change to reach Dart's `main` or Flutter's
`master` branch and be guaranteed for the next stable train. The published 2026
targets were February 3.41
(January 6 cutoff), May 3.44 (April 7), August 3.47 (July 7), and November 3.50
(October 6). Treat these as planning windows rather than a substitute for checking an
actual archive.

Roughly every third beta is promoted to stable. Beta normally ships on the first
Wednesday of a month, and a fix commonly reaches beta about two weeks after landing
on main. The main channel has no installation bundles; obtain it from the repository:

```sh
git clone -b main https://github.com/flutter/flutter.git
./flutter/bin/flutter --version
```

Flutter SDK archives use modified calendar versioning. Each Windows, macOS, or Linux
release records architecture, Git ref, release date, bundled Dart version, and JSON
provenance. Archive downloads include SLSA provenance for verifying artifact origin.
