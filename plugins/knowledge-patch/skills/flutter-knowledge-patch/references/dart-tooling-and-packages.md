# Dart tooling and packages

## Contents

- [Formatter migrations](#formatter-migrations)
- [Dependency declarations and SDK constraints](#dependency-declarations-and-sdk-constraints)
- [Analyzer plug-ins](#analyzer-plug-ins)
- [Build hooks](#build-hooks)
- [Pub workspaces and cache](#pub-workspaces-and-cache)
- [Git dependencies](#git-dependencies)
- [Native compilation and dart build](#native-compilation-and-dart-build)
- [Package publishing and discovery](#package-publishing-and-discovery)
- [Analysis performance recordings](#analysis-performance-recordings)
- [Server-side Dart previews](#server-side-dart-previews)

## Formatter migrations

The rewritten formatter selects the prior style through language version 3.6 and its
new style for 3.7 or later, using the package language version recorded in
`package_config.json` (`dart-3.7.0`). After raising a package SDK constraint, run
`dart pub get` before `dart format`, including in CI. Otherwise the formatter can keep
using the prior language style.

`dart format --fix` is removed; use `dart fix` for automated source migrations.

For packages opted into language version 3.8, a trailing comma no longer forces a
construct into the tall layout. The formatter first decides whether the construct is
tall, then adds or removes its trailing comma. Installing a newer SDK without raising
the package language version does not opt into this behavior (`dart-3.8.0`).

## Dependency declarations and SDK constraints

Flutter requires every package imported by application code to be declared directly
in `pubspec.yaml`. The explicit-dependency check became unconditional; the former
`--explicit-package-dependencies` switch cannot restore transitive-only imports.

Starting with language version 3.9, Pub honors the root package's upper
`environment.flutter` bound as well as its Dart SDK range (`dart-3.9.0`). A narrow
upper bound can make `pub get` reject the active Flutter SDK.

```yaml
environment:
  sdk: ^3.9.0
  flutter: 3.33.0
```

## Analyzer plug-ins

Analyzer plug-ins can add project diagnostics, quick fixes, and assists to IDEs,
`dart analyze`, and `flutter analyze` (`dart-3.10.0`). The top-level `plugins` mapping
accepts either a Pub version constraint or a local path. Plug-in warnings are enabled
by default; explicitly enable individual plug-in lints below that plug-in's
`diagnostics` mapping (`dart-3.11-tooling-guide`). Restart the analysis server after
changing the configuration.

```yaml
plugins:
  published_plugin: ^1.0.0
  local_plugin:
    path: /path/to/local_plugin
    diagnostics:
      local_lint: true
      inherited_lint: false
```

Qualify a suppressed diagnostic with its plug-in name:

```dart
// ignore: local_plugin/local_lint
// ignore_for_file: local_plugin/another_lint
```

### Implement a plug-in

The package depends on `analysis_server_plugin`, `analyzer_plugin`, and `analyzer`.
Export a top-level variable named `plugin` from `lib/main.dart`; its value extends
`Plugin` and registers diagnostics, fixes, and assists through `register`.

```dart
import 'package:analysis_server_plugin/plugin.dart';
import 'package:analysis_server_plugin/registry.dart';

final plugin = SimplePlugin();

class SimplePlugin extends Plugin {
  @override
  String get name => 'Simple plug-in';

  @override
  void register(PluginRegistry registry) {
    // Register diagnostics, fixes, and assists.
  }
}
```

Plug-ins run in a separate isolate whose standard output is not attached to the
console. `print` is ineffective for debugging. Inspect crashes and stack traces in
the analyzer diagnostics plug-ins screen or write traces to a log file.

Use `remove_deprecations_in_breaking_versions` to detect deprecated APIs left behind
when a package moves to a breaking version such as `1.0.0` or `0.2.0`:

```yaml
linter:
  rules:
    - remove_deprecations_in_breaking_versions
```

## Build hooks

A package build hook lives at `hooks/build.dart`, calls `build` from
`package:hooks/hooks.dart`, and receives `BuildInput` plus `BuildOutputBuilder`.
Hooks run automatically for run, build, and test alongside Dart compilation. They run
in dependency order, so a hook can consume direct-dependency assets or metadata;
cycles among hook-bearing packages are unsupported.

```dart
import 'package:hooks/hooks.dart';
import 'package:logging/logging.dart';
import 'package:native_toolchain_c/native_toolchain_c.dart';

void main(List<String> args) async {
  await build(args, (input, output) async {
    await CBuilder.library(
      name: input.packageName,
      assetName: '${input.packageName}.dart',
      sources: ['src/${input.packageName}.c'],
    ).run(
      input: input,
      output: output,
      logger: Logger('build'),
    );
  });
}
```

Depend on `hooks` and `code_assets`, adding `native_toolchain_c` when compiling C.
Put downloaded and generated intermediates in `input.sharedOutputDirectory`.

### Hook environment and caching

Hook processes are semi-hermetic. They do not inherit arbitrary environment
variables; only documented path, home, system-root, temporary-directory, proxy,
Clang, Android NDK, and `NIX_*` variables are forwarded. A change to any forwarded
value invalidates the hook cache.

### Native code asset identity

A hook may emit a native dynamic library as a `CodeAsset`, and the SDK bundles it
automatically, but only for the hook's own package. The ID is
`package:<package-name>/<asset-name>`. Name that ID in `@Native`, or omit `assetId`
when the Dart library URI already matches it.

```dart
import 'dart:ffi';

@Native<Int32 Function(Int32, Int32)>(
  assetId: 'package:native_add_library/native_add_library.dart',
)
external int add(int a, int b);
```

## Pub workspaces and cache

The root `pubspec.yaml` can declare workspace members with globs when its Dart SDK
constraint is 3.11 or later (`dart-3.11.0`):

```yaml
environment:
  sdk: ^3.11.0
workspace:
  - packages/*
```

`dart pub cache gc` finds cached versions used by projects recorded through
`pub get`, then interactively deletes the rest. A project not recognized as active
must run `dart pub get` before it works again.

```sh
dart pub cache gc
```

## Git dependencies

Pub can version-solve a Git dependency from tags when the Git descriptor supplies
`tag_pattern` and the dependency supplies a `version` constraint. Pub replaces
`{{version}}` with candidate versions during resolution.

```yaml
dependencies:
  my_dependency:
    git:
      url: https://github.com/example/my_dependency
      tag_pattern: v{{version}}
    version: ^2.0.1
```

Pub also retrieves Git LFS objects in Git dependencies automatically
(`dart-3.12.0`). The local machine must have `git lfs`, but the dependency needs no
LFS-specific `pubspec.yaml` configuration.

## Native compilation and `dart build`

`dart compile exe` and `dart compile aot-snapshot` can create Linux artifacts from
Windows, macOS, or Linux with `--target-os` and `--target-arch`. Linux targets include
`arm64`, `arm` (ARM32), and `riscv64` (RV64GC):

```sh
dart compile exe --target-os=linux --target-arch=riscv64 bin/app.dart
```

The preview `dart build` command uses a `cli` subcommand and `--target`; it no longer
uses the preview form `dart build -f exe <target>`.

```sh
dart build cli --target=<target>
```

## Package publishing and discovery

- The pub.dev Likes view supports searching, sorting, filtering, and unliking saved
  packages. Use `is:liked-by-me` in general search to restrict results to liked
  packages.
- A package administrator can clear **Enable manual publishing** on the pub.dev Admin
  tab, blocking `pub publish` updates made with personal credentials for
  automation-only or inactive packages.

## Analysis performance recordings

Capture execution traces and CPU profiles from active Dart Analysis Server processes
with:

```sh
dart info record-performance
```

Use this when analysis or completion becomes slow or unresponsive.

## Server-side Dart previews

The Genkit for Dart preview supplies structured output, tool calls, multi-step AI
flows, provider plug-ins, and a local developer UI for prompt testing and trace
inspection. Keep preview dependencies isolated from stable application contracts.

Firebase Cloud Functions can experimentally run Dart. Deployment uses AOT
compilation without an application-supplied Dockerfile or container, allowing shared
Dart packages for data classes, validation, and business logic across frontend and
backend.
