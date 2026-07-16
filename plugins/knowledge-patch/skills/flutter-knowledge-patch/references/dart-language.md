# Dart language

## Contents

- [Null-aware collection elements](#null-aware-collection-elements)
- [Null-safety-aware flow analysis](#null-safety-aware-flow-analysis)
- [Dot shorthands](#dot-shorthands)
- [Private named initializing formals](#private-named-initializing-formals)
- [Experimental primary constructors](#experimental-primary-constructors)
- [Use-specific deprecation annotations](#use-specific-deprecation-annotations)
- [Documentation imports](#documentation-imports)
- [Metaprogramming direction](#metaprogramming-direction)

## Null-aware collection elements

In a list, set, or map literal, prefix an element with `?` to include the evaluated
value only when it is non-null (`dart-3.8.0`). This is an element-level conditional,
not a null check applied to the whole collection.

```dart
String? middleName;
var names = ['Ada', ?middleName, 'Lovelace'];
```

## Null-safety-aware flow analysis

Packages whose SDK lower bound is 3.9 or later opt into flow analysis that assumes
null safety while computing promotion, reachability, and definite assignment
(`dart-3.9.0`). Raising the lower bound can reveal new `dead_code` diagnostics.

```yaml
environment:
  sdk: ^3.9.0
```

DDC also adds a runtime soundness check when code directly invokes a getter result
whose declared type is a generic type parameter instantiated as `dynamic` or
`Function`. This missing check affected DDC, not the other Dart execution tools.

## Dot shorthands

Dot shorthands omit a type name when the surrounding context supplies the expected
type (`dart-3.10-dot-shorthands`). They can resolve:

- enum values;
- static fields, getters, and methods;
- named and factory constructors;
- `.new()` for an unnamed constructor;
- generic constructor arguments inferred from context.

```dart
enum LogLevel { debug, warning }

LogLevel level = .warning;
int port = .parse('8080');
List<int> values = .filled(3, 0);
StringBuffer buffer = .new();
```

Typed arguments and switch cases supply context. Constant contexts also accept a
shorthand when it selects a constant member or const constructor:

```dart
const List<Duration> delays = [.zero, .new(seconds: 1)];
```

### Chaining and equality

A chain that starts from a shorthand is checked against the original context type
used to resolve the leading member:

```dart
String lowerH = .fromCharCode(72).toLowerCase();
```

On the right side of `==` or `!=`, a direct shorthand receives context from the
static type of the left operand. This is asymmetric: a shorthand on the left, or
inside a conditional or other complex right operand, does not receive equality
context.

```dart
enum Color { red, green, blue }

bool isGreen(Color color) => color == .green;
Color next(bool condition) => condition ? .green : .blue;
```

An expression statement cannot begin with `.`, so a standalone `.log('message');`
is invalid. In a nullable `T?` context, lookup uses `T`, not `Null`; in a
`FutureOr<T>` context, lookup also uses `T` and does not expose `Future` members.

## Private named initializing formals

A private field may be initialized by a named initializing formal
(`dart-3.12.0`). The field stays private, but the call-site label is public and drops
the leading underscore.

```dart
class Hummingbird {
  final String _petName;

  Hummingbird({required this._petName});
}

final bird = Hummingbird(petName: 'Dash');
```

## Experimental primary constructors

The `primary-constructors` experiment permits constructor parameters in a class
header and permits an empty body to end with a semicolon. Constructors in the body
can use the shorter `new` or `factory` syntax.

```dart
class Point(final int x, final int y);

class Pet {
  String name;

  new() : name = 'Fluffy';
  new withName(this.name);
}
```

Enable the experiment explicitly for a run; do not expose experimental syntax from a
package that must compile without the same experiment.

```sh
dart run --enable-experiment=primary-constructors bin/main.dart
```

## Use-specific deprecation annotations

`Deprecated` has `.extend()`, `.implement()`, `.subclass()`, `.mixin()`, and
`.instantiate()` constructors (`dart-3.10.0`). Use them when only one operation on a
class or mixin is being phased out; `.subclass()` covers both extending and
implementing. `@Deprecated.optional()` marks an optional parameter intended to become
required later.

```dart
@Deprecated.extend()
class LegacyBase {}

void connect({@Deprecated.optional() String? token}) {}
```

## Documentation imports

A documentation comment can reference declarations from another library without a
normal import:

```dart
/// {@docImport 'package:flutter/material.dart';}
```

Documentation imports do not accept an `as` clause. Refer to imported declarations
without a prefix.

## Metaprogramming direction

Dart stopped work on macros because deep semantic introspection made static analysis,
completion, and incremental compilation too slow. Do not plan production generation
around the prototype. The stated replacement direction is bespoke language support
for data and serialization, standalone augmentations, and improvements to
`build_runner`; general metaprogramming remains only a longer-term exploration.
