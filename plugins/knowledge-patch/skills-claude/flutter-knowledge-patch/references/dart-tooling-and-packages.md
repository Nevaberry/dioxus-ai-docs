# Dart tooling and packages

## Formatting and package language versions

### Formatter migration (dart-3.7.0)

The formatter reads `package_config.json`: language versions through 3.6 use the
old style and 3.7 or later use the rewritten style. After raising a package SDK
constraint, run `dart pub get` before `dart format`, including in CI. Use
`dart fix` instead of the removed `dart format --fix`.

### Trailing commas (dart-3.8.0)

For packages opted into language version 3.8, a trailing comma no longer forces a
construct to split. The formatter first chooses whether the construct is tall, then
adds or removes the comma. Installing a 3.8 SDK without raising the package language
version does not opt in.

## Dependencies and Pub

### Direct dependencies (3.32.0, 3.35.0)

Every imported package must be declared directly in `pubspec.yaml`. Flutter first
enabled explicit-package-dependency checking by default, then removed its opt-out;
the old `--explicit-package-dependencies` switch is no longer a selectable mode.

The synthetic `package:flutter_gen` package is removed. `flutter: generate: true`
still works for non-synthetic generation; import localization output through its
real generated source.

### Git dependencies and Flutter bounds (dart-3.9.0)

Pub can version-solve Git dependencies from tags when the Git descriptor supplies
`tag_pattern` and the dependency supplies a version constraint.

```yaml
dependencies:
  my_dependency:
    git:
      url: https://github.com/example/my_dependency
      tag_pattern: v{{version}}
    version: ^2.0.1
```

For packages at language version 3.9 or later, Pub respects the root package's upper
`environment.flutter` constraint as it does `environment.sdk`. A narrow Flutter
bound can make `pub get` reject the installed SDK.

### Workspaces and cache maintenance (dart-3.11.0)

With an SDK constraint of 3.11 or later, root workspace members may use globs:

```yaml
environment:
  sdk: ^3.11.0
workspace:
  - packages/*
```

`dart pub cache gc` finds versions used by projects recorded through `pub get` and
interactively removes the rest. A project that was not recognized as active must run
`dart pub get` again.

### Git LFS packages (dart-3.12.0)

Pub resolves Git LFS objects in Git dependencies automatically when `git lfs` is
installed locally. No LFS-specific `pubspec.yaml` configuration is required.

### Package discovery and publishing (dart-3.10.0)

The pub.dev Likes tab supports search, sort, filter, and unlike operations; use
`is:liked-by-me` in general search to restrict results to liked packages. A package
administrator can disable **Enable manual publishing** to block credential-based
`pub publish` updates for automation-only or inactive packages.

### Package migrations

The `firebase_ai` package replaces `firebase_vertexai` for new Firebase AI Logic
work and supports both Gemini API providers plus Imagen (3.32-guide). Existing
`firebase_vertexai` apps continue to work for now but should migrate.

Support was scheduled to end for `ios_platform_images`, `css_colors`,
`palette_generator`, `flutter_image`, `flutter_adaptive_scaffold`, and
`flutter_markdown`; replace them with maintained alternatives or community forks
(3.29.0).

## Documentation imports

Dart doc comments can import external declarations without a normal library import
(3.32-guide):

```dart
/// {@docImport 'package:flutter/material.dart';}
```

Documentation imports do not accept an `as` prefix (3.32.0); refer to imported
declarations without a library qualifier.

## Native compilation

`dart compile exe` and `dart compile aot-snapshot` can cross-compile Linux artifacts
from Windows, macOS, or Linux (dart-3.8.0). The initial targets include Linux
architectures such as ARM64; Dart 3.9 adds `arm` and `riscv64`.

```sh
dart compile exe --target-os=linux --target-arch=riscv64 bin/app.dart
```

The beta preview command shape is `dart build cli --target=<target>`, replacing
`dart build -f exe <target>` (dart-3.9.0).

## Analyzer plugins

### Consumer configuration (dart-3.10.0, dart-3.11-tooling-guide)

Analyzer plugins add diagnostics, fixes, and assists to IDEs, `dart analyze`, and
`flutter analyze`. Configure them at the top level of `analysis_options.yaml`.
The mapping accepts a Pub constraint or a local path. Warnings are enabled by
default; enable plugin lints under that plugin's `diagnostics` and restart the
analysis server after changes.

```yaml
plugins:
  published_plugin: ^1.0.0
  local_plugin:
    path: tools/local_plugin
    diagnostics:
      local_lint: true
      inherited_lint: false
```

Suppress a diagnostic with a qualified code, for example
`// ignore: local_plugin/local_lint` or
`// ignore_for_file: local_plugin/local_lint`.

### Plugin package entry point

An analyzer plugin package depends on `analysis_server_plugin`,
`analyzer_plugin`, and `analyzer`. It must export a top-level `plugin` variable
from `lib/main.dart` whose instance extends `Plugin` and registers diagnostics,
fixes, and assists through `register`.

```dart
final plugin = SimplePlugin();

class SimplePlugin extends Plugin {
  @override
  String get name => 'Simple plugin';

  @override
  void register(PluginRegistry registry) {
    // Register diagnostics, fixes, and assists.
  }
}
```

Plugins run in a separate isolate and their standard output is not connected to the
console, so `print` is ineffective for debugging. Inspect the analyzer diagnostics
**plugins** screen for crashes and stack traces, or write trace output to a log
file.

Use `dart info record-performance` to capture execution traces and CPU profiles
from active analysis-server processes when analysis or completion is slow
(dart-3.12.0).

## Build hooks and native assets (dart-3.11-tooling-guide)

A package hook lives at `hooks/build.dart` and calls `build` from
`package:hooks/hooks.dart` with a `BuildInput` and `BuildOutputBuilder`. It runs
automatically for run, build, and test, alongside compilation and in dependency
order. Hook-bearing dependency cycles are unsupported.

Use `hooks` and `code_assets` dependencies, plus `native_toolchain_c` for C
compilation. Put downloaded or generated intermediates in
`input.sharedOutputDirectory`.

Hook processes are semi-hermetic: they receive only documented path/home/system
root, temporary directory, proxy, Clang, Android NDK, and `NIX_*` variables.
Changing a forwarded value invalidates the hook cache.

A hook may emit a `CodeAsset` native dynamic library only for its own package. Its
identity is `package:<package-name>/<asset-name>`. Name that ID from `@Native`, or
omit `assetId` when the Dart library URI already matches it.

```dart
@Native<Int32 Function(Int32, Int32)>(
  assetId: 'package:native_add_library/native_add_library.dart',
)
external int add(int a, int b);
```

## Tool integrations and server-side Dart

The stable Dart SDK includes the Dart and Flutter MCP server, which can inspect a
running widget tree, dependencies, and analyzer feedback (3.35-guide). Its
`read_package_uris` tool resolves and reads project `package:` URIs, including
dependency source (dart-3.11.0).

The Dart Genkit preview supplies structured output, tool calls, multi-step flows,
plugins for Google, Anthropic, OpenAI, and OpenAI-compatible models, and a local UI
for prompt testing and trace inspection (dart-3.12.0). Experimental Cloud Functions
for Firebase support can AOT-compile Dart without an application-provided
Dockerfile, letting frontend and backend share models, validation, and business
logic.
