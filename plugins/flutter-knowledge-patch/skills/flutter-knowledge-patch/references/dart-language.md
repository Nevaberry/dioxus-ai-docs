# Dart Language Features (3.8–3.11)

## Null-aware elements in collections (Dart 3.8)

Prepend `?` to a collection element to include it only when non-null. Works in list, set, and map literals.

```dart
var items = [
  ?nullableString,
  ?nullable.value,  // no need for null-check or `!`
];

var map = {
  ?'key': nullableValue,  // null-aware map entry
};
```

## Cross compilation (Dart 3.8+)

Compile to native Linux binaries from any OS with `--target-os` and `--target-arch`:

```bash
dart compile exe --target-os=linux --target-arch=arm64 bin/server.dart
dart compile aot-snapshot --target-os=linux --target-arch=arm64 bin/server.dart
```

Dart 3.9 added `arm` (ARM32) and `riscv64` (RV64GC) as additional cross-compilation targets for Linux.

## Dot shorthands (Dart 3.10)

Omit redundant type names when the compiler can infer the type. Works with enums, constructors, static methods, and static fields.

```dart
// Enum values
logMessage('error', level: .error);  // instead of LogLevel.error

// Named constructors
Padding(
  padding: .all(8.0),  // instead of EdgeInsets.all(8.0)
  child: Text('Hello'),
)

// Static methods and fields
Column(
  mainAxisAlignment: .start,    // MainAxisAlignment.start
  crossAxisAlignment: .center,  // CrossAxisAlignment.center
  children: [/* ... */],
)

// Default parameter values
void logMessage(String msg, {LogLevel level = .info}) { }
```

## Build hooks stable (Dart 3.10)

Compile native code (C++, Rust, Swift) or download native libraries and bundle them directly with a Dart package — no CMake/Gradle/SPM build files needed. Previously called "native assets".

## Analyzer plugins (Dart 3.10)

Custom static analysis rules that integrate into IDEs and `dart analyze`. Enable in `analysis_options.yaml`:

```yaml
plugins:
  - some_plugin
```

Note: uses top-level `plugins:` key, not `analyzer: plugins:`.

## Granular @Deprecated annotations (Dart 3.10)

Deprecate specific capabilities of a class instead of the whole API:

```dart
@Deprecated.extend('Use composition instead')   // extending deprecated
@Deprecated.implement('Use the concrete class')  // implementing deprecated
@Deprecated.subclass('Sealed in next major')     // extend or implement
@Deprecated.mixin('Use a mixin instead')         // mixing in deprecated
@Deprecated.instantiate('Use factory method')    // instantiation deprecated
@Deprecated.optional('Will become required in 2.0')  // optional→required param
```

## `dart build cli` (Dart 3.9, preview)

`dart build` replaces `dart compile` syntax on beta channel: `dart build cli --target=<target>`.

## Glob support in pub workspaces (Dart 3.11)

Declare workspace packages using globs (requires SDK `^3.11.0`):

```yaml
workspace:
  - pkg/* # adds all packages inside pkg/
```

## `dart pub cache gc` (Dart 3.11)

New command to clean unused packages from the global pub cache. Scans active projects and deletes package versions no longer referenced.
