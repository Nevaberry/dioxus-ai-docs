# Dart language

## Collection literals

- Dart 3.8 adds null-aware list, set, and map elements. Prefix an element with `?`
  to omit it when its value is null (`dart-3.8.0`).

```dart
String? middleName;
var names = ['Ada', ?middleName, 'Lovelace'];
```

- In packages using the 3.8 language version, a trailing comma no longer forces a
  construct to split; the formatter chooses layout first and then manages the
  comma. Installing the SDK alone does not opt a package in (`dart-3.8.0`).

## Flow analysis and runtime soundness

- With an SDK lower bound of 3.9 or later, flow analysis assumes null safety when
  calculating promotion, reachability, and definite assignment. Raising the lower
  bound can reveal new `dead_code` diagnostics (`dart-3.9.0`).
- DDC adds runtime checks when directly invoking a getter result whose declared
  type is a generic parameter instantiated as `dynamic` or `Function`. Other Dart
  tools already had the required sound behavior (`dart-3.9.0`).

## Dot shorthands

The `dart-3.10-dot-shorthands` rules let a leading dot omit a type name when an
expected type is available.

- Shorthands select enum values, static fields/getters or methods, named/factory
  constructors, and `.new()`; generic constructor arguments are inferred.
- Typed arguments, assignments, returns, switch cases, and other contextual
  positions can provide the expected type.
- Constant members and const constructors remain valid in constant expressions.
- A chain after a shorthand retains the original context type for checking the
  complete expression.
- On the direct right side of `==` or `!=`, the left operand's static type supplies
  context. The rule is asymmetric and does not apply to a shorthand on the left or
  nested inside a conditional right operand.
- An expression statement cannot begin with `.`, so a standalone
  `.log('message');` is invalid.
- In `T?` context lookup uses `T`, not `Null`; in `FutureOr<T>` it uses `T`, not
  static members from `Future`.

```dart
enum LogLevel { debug, warning }

LogLevel level = .warning;
int port = .parse('8080');
List<int> values = .filled(3, 0);
const List<Duration> delays = [.zero, .new(seconds: 1)];
String lowerH = .fromCharCode(72).toLowerCase();
```

## Deprecation declarations

- `Deprecated.extend()`, `.implement()`, `.subclass()`, `.mixin()`, and
  `.instantiate()` target particular class or mixin uses; `.subclass()` covers
  extending and implementing. `@Deprecated.optional()` marks an optional parameter
  intended to become required (`dart-3.10.0`).

```dart
@Deprecated.extend()
class LegacyBase {}

void connect({@Deprecated.optional() String? token}) {}
```

## Constructor syntax

- Dart permits private field names in named initializing formals. The public call
  label omits the leading underscore (`dart-3.12.0`).

```dart
class Hummingbird {
  final String _petName;
  Hummingbird({required this._petName});
}

final bird = Hummingbird(petName: 'Dash');
```

- The experimental `primary-constructors` feature places constructor parameters
  in the class header, permits a semicolon in place of an empty body, and permits
  body constructors to use `new` or `factory` without repeating the class name.
  Enable it with `--enable-experiment=primary-constructors` (`dart-3.12.0`).

```dart
class Point(final int x, final int y);

class Pet {
  String name;
  new() : name = 'Fluffy';
  new withName(this.name);
}
```

## Metaprogramming direction

Dart cancelled the macro prototype because deep semantic introspection harmed
analysis, completion, and incremental compilation. Do not plan code generation on
that prototype. The stated direction is bespoke data/serialization language
features, standalone augmentations, and `build_runner` improvements; general
metaprogramming remains longer-term exploration (`dart-language-roadmap`).
