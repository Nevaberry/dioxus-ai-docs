# Dart language

## Collections and flow analysis

### Null-aware collection elements (dart-3.8.0)

Prefix a list or set element, or a map key/value entry, with `?` to include it
only when the expression is non-null.

```dart
String? middleName;
var names = ['Ada', ?middleName, 'Lovelace'];
```

### Null-safety-aware flow analysis (dart-3.9.0)

Packages whose SDK lower bound is 3.9 or later use null-safety assumptions for
promotion, reachability, and definite assignment. Raising the constraint opts in
and can expose new `dead_code` diagnostics.

DDC also checks a direct invocation of a getter result whose declared type is a
generic type parameter instantiated as `dynamic` or `Function`. This closes a DDC
soundness gap; other Dart tools already performed the check.

## Dot shorthands (dart-3.10-dot-shorthands)

### Context-inferred members and constructors

When the surrounding context supplies the expected type, a leading dot can omit the
type name for enum values, static fields/getters or methods, named and factory
constructors, and `.new()`. Generic constructor arguments are inferred.

```dart
enum LogLevel { debug, warning }

LogLevel level = .warning;
int port = .parse('8080');
List<int> values = .filled(3, 0);
StringBuffer buffer = .new();
```

Switch cases and typed arguments also supply context. Dot shorthands work in
constant expressions when they select a constant member or const constructor:

```dart
const List<Duration> delays = [.zero, .new(seconds: 1)];
```

### Chains and equality context

A chain may start from a shorthand, but the whole chain is checked against the
original context type.

```dart
String lowerH = .fromCharCode(72).toLowerCase();
```

On the direct right side of `==` or `!=`, the left operand's static type supplies
the shorthand context. This is asymmetric: a shorthand on the left, or inside a
more complex right operand, has no equality context.

```dart
enum Color { red, green, blue }

bool isGreen(Color color) => color == .green;
// .green == color; // Invalid.
```

### Invalid and wrapper contexts

An expression statement cannot begin with a dot, so `.log('message');` is invalid.
In a nullable `T?` context, lookup uses `T` rather than `Null`. In a
`FutureOr<T>` context, lookup likewise uses `T` and does not expose `Future`
static members.

## Deprecation design (dart-3.10.0)

Use `Deprecated.extend()`, `.implement()`, `.subclass()`, `.mixin()`, or
`.instantiate()` when only one use of a class or mixin is deprecated.
`.subclass()` covers both extending and implementing.
`@Deprecated.optional()` marks an optional parameter intended to become required.

```dart
@Deprecated.extend()
class LegacyBase {}

void connect({@Deprecated.optional() String? token}) {}
```

The `remove_deprecations_in_breaking_versions` lint finds deprecated APIs that a
package retained when moving to a breaking version such as `1.0.0` or `0.2.0`.

## Constructors (dart-3.12.0)

### Private named initializing formals

A named initializing formal may name a private field. The field stays private, but
the public argument label omits the underscore.

```dart
class Hummingbird {
  final String _petName;
  Hummingbird({required this._petName});
}

final bird = Hummingbird(petName: 'Dash');
```

### Experimental primary constructors

The `primary-constructors` experiment permits constructor parameters in the class
header and an empty class body ending in a semicolon. Body constructors may use the
shorter `new` or `factory` syntax.

```dart
class Point(final int x, final int y);

class Pet {
  String name;
  new() : name = 'Fluffy';
  new withName(this.name);
}
```

Enable it explicitly:

```sh
dart run --enable-experiment=primary-constructors bin/main.dart
```

Do not ship experiment syntax without checking the project's selected Dart SDK and
experiment flags.

## Metaprogramming direction (dart-language-roadmap)

Dart's macro effort was cancelled because deep semantic introspection made static
analysis, completion, and incremental compilation too slow. Do not plan production
generation around the macro prototype. The stated direction is bespoke language
features for data and serialization, standalone augmentations, and improvements to
`build_runner`; general metaprogramming remains only a longer-term exploration.
