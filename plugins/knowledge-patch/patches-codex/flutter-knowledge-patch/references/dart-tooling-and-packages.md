# Dart tooling and packages

## Formatter and documentation

- The rewritten formatter uses legacy style through language 3.6 and new style at
  3.7+, determined from `package_config.json`. After raising an SDK constraint, run
  `dart pub get` before `dart format`, including in CI. Replace removed
  `dart format --fix` with `dart fix` (`dart-3.7.0`).
- Doc imports can reference external declarations from documentation comments:
  `/// {@docImport 'package:flutter/material.dart';}` (`3.32-guide`). They do not
  accept an `as` prefix in 3.32.0.

## Browser interop

`dart:html`, `dart:indexed_db`, `dart:js`, `dart:js_util`, `dart:web_audio`, and
`dart:web_gl` were deprecated in `dart-3.7.0`, with removal planned for the end of
2025. Use `dart:js_interop` and `package:web`. Legacy `dart:html` and `package:js`
also prevent Flutter Wasm compilation.

## Analyzer plug-ins

- Analyzer plug-ins add diagnostics, fixes, and assists to IDEs, `dart analyze`,
  and `flutter analyze`. The early `dart-3.10.0` list syntax evolved into the
  top-level mapping described by `dart-3.11-tooling-guide`.
- A mapping entry accepts a Pub version constraint or local path. Warnings are on
  by default; enable plug-in lints under its `diagnostics`. Restart analysis after
  editing the configuration.
- Qualify suppression codes, for example
  `// ignore: local_plugin/local_lint` or
  `// ignore_for_file: local_plugin/local_lint`.
- A plug-in depends on `analysis_server_plugin`, `analyzer_plugin`, and `analyzer`,
  exposes a top-level `plugin` variable from `lib/main.dart`, extends `Plugin`, and
  registers diagnostics, fixes, and assists through `register`.
- Plug-ins run in an isolate without console-connected stdout, so `print` is not a
  debugging channel. Inspect the analyzer diagnostics **plugins** screen for
  crashes or write trace output to a file.

```yaml
plugins:
  published_plugin: ^1.0.0
  local_plugin:
    path: tools/local_plugin
    diagnostics:
      local_lint: true
```

The `remove_deprecations_in_breaking_versions` lint flags deprecated APIs that
remain when a package advances to a breaking version such as `1.0.0` or `0.2.0`
(`dart-3.10.0`).

## Build hooks and native code assets

- A hook at `hooks/build.dart` invokes `build` from `package:hooks/hooks.dart` and
  receives `BuildInput` plus `BuildOutputBuilder`. It runs automatically for run,
  build, and test in dependency order; cycles between hook-bearing packages are
  unsupported (`dart-3.11-tooling-guide`).
- Depend on `hooks` and `code_assets`, plus `native_toolchain_c` when compiling C.
  Put downloaded/generated files in `input.sharedOutputDirectory`.
- Hook processes receive only documented path/home/system-root, temporary, proxy,
  Clang, Android NDK, and `NIX_*` variables. A forwarded-value change invalidates
  the cache.
- A hook can emit a bundled `CodeAsset` only for its own package. Its identity is
  `package:<package-name>/<asset-name>`; use that ID from `@Native`, or omit
  `assetId` when the Dart library URI already matches it.

## Pub dependencies and workspaces

- Imports must name direct `pubspec.yaml` dependencies. Flutter enabled
  `--explicit-package-dependencies` by default in 3.32.0 and removed the switch
  and its opt-out in 3.35.0.
- Pub can version-solve a Git dependency through tags by combining `tag_pattern`
  containing `{{version}}` with a `version` constraint (`dart-3.9.0`).
- From language 3.9, Pub enforces the root package's upper `environment.flutter`
  constraint as well as `environment.sdk` (`dart-3.9.0`).
- Workspace members can use globs such as `packages/*` when the root SDK constraint
  is 3.11+ (`dart-3.11.0`).
- `dart pub cache gc` identifies versions used by projects observed through
  `pub get`, then asks before deleting other versions. Unrecognized projects need
  another `pub get` (`dart-3.11.0`).
- Git package dependencies transparently fetch Git LFS objects when `git lfs` is
  installed; no special dependency YAML is needed (`dart-3.12.0`).

## Native compilation

- `dart compile exe` and `dart compile aot-snapshot` cross-compile Linux artifacts
  from Windows, macOS, or Linux with `--target-os` and `--target-arch`
  (`dart-3.8.0`). Linux ARM32 and RISC-V 64 were added in `dart-3.9.0`.
- The beta preview command changed from `dart build -f exe <target>` to
  `dart build cli --target=<target>` (`dart-3.9.0`).

## Package and service tooling

- Search the pub.dev Likes tab or use `is:liked-by-me`; disable personal-credential
  `pub publish` with the Admin tab's **Enable manual publishing** control
  (`dart-3.10.0`).
- The Dart/Flutter MCP server can resolve dependency source with
  `read_package_uris` (`dart-3.11.0`).
- `dart info record-performance` captures traces and CPU profiles from active
  analysis-server processes (`dart-3.12.0`).
- The Genkit Dart preview supports structured output, tool calls, multistep flows,
  a local prompt/trace UI, and plug-ins for Google, Anthropic, OpenAI, and
  compatible endpoints. Cloud Functions for Firebase can experimentally deploy
  AOT-compiled Dart without an app-supplied container, allowing shared models and
  validation packages (`dart-3.12.0`).
