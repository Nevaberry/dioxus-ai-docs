# Dart Language Features

## Macros Cancelled (Dart 3.7)

Macros development has been stopped. The `@JsonCodable()` experiment from Dart 3.4 is discontinued. Continue using `json_serializable` / `build_runner` for JSON serialization. The team is exploring improvements to `build_runner` performance and new approaches for data serialization.

Legacy web libraries are deprecated in Dart 3.7: `dart:html`, `dart:indexed_db`, `dart:js`, `dart:js_util`, `dart:web_audio`, `dart:web_gl`. Use `dart:js_interop` and `package:web` instead.

## Null-Aware Elements (Dart 3.8)

Prepend `?` to skip null elements in collection literals:

```dart
List<String> names = [
  ?nullableName,      // omitted if null
  ?user?.displayName, // omitted if null
];

Map<String, int> data = {
  ?nullableKey: 1,
  'fixed': ?nullableValue,
};

Set<String> tags = {?maybeTag, 'always'};
```

Replaces verbose `if (x != null) x` patterns in list/map/set literals.

## Cross Compilation (Dart 3.8)

Compile to Linux native binaries from any OS:

```bash
dart compile exe --target-os=linux --target-arch=arm64 bin/server.dart
dart compile aot-snapshot --target-os=linux --target-arch=arm64 bin/server.dart
```

Supported target architectures: `arm64`, `x64`, `arm` (ARM32), `riscv64`.

## Doc Imports (Dart 3.8)

Reference external symbols in doc comments without importing them into the library:

```dart
/// @docImport 'dart:async';
library;

/// Returns a [Future] that completes with the result.
String getData() => 'data';
```

## Dot Shorthands (Dart 3.10)

Omit type names when the compiler can infer them. Works with enums, constructors, static methods, and static fields:

```dart
// Before
Column(
  mainAxisAlignment: MainAxisAlignment.center,
  children: [
    Padding(padding: EdgeInsets.all(8.0), child: Text('Hi')),
  ],
)

// After (Dart 3.10+ / Flutter 3.38+)
Column(
  mainAxisAlignment: .center,
  children: [
    Padding(padding: .all(8.0), child: Text('Hi')),
  ],
)
```

Default parameter values also support shorthands:

```dart
void log(String msg, {LogLevel level = .info}) { ... }
```

Works anywhere the expected type is statically known — named parameters, variable declarations with type annotations, return statements, etc.
