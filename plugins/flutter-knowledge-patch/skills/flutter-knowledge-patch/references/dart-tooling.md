# Dart Tooling

## Pub Git Tag-Based Version Solving (Dart 3.9)

Git dependencies can resolve versions from tags instead of pinning to a branch or commit:

```yaml
dependencies:
  my_dep:
    git:
      url: https://github.com/example/my_dep
      tag_pattern: v{{version}}
    version: ^2.0.1
```

## Flutter SDK Upper Bound Enforced (Dart 3.9)

From language version 3.9, the `flutter` constraint upper bound is respected in root packages. Useful for pinning team SDK versions:

```yaml
environment:
  sdk: ^3.9.0
  flutter: 3.33.0 # pub get fails if SDK doesn't match
```

## Build Hooks — Stable (Dart 3.10)

Native code (C++, Rust, Swift) can be compiled and bundled directly with Dart packages without separate CMake/Gradle/SPM files. Configuration via `dart.dev/tools/hooks`.

## Analyzer Plugins (Dart 3.10)

Custom static analysis rules that integrate into IDEs. Enable in `analysis_options.yaml`:

```yaml
analyzer:
  plugins:
    - some_plugin
```

## Glob Patterns in Pub Workspaces (Dart 3.11)

```yaml
workspace:
  - pkg/* # includes all packages inside pkg/
```

Requires SDK constraint `^3.11.0`.

## Pub Cache GC (Dart 3.11)

Clean unused cached packages:

```bash
dart pub cache gc
```

Tracks which projects use the cache (since Dart 3.9) and removes unreferenced package versions.
