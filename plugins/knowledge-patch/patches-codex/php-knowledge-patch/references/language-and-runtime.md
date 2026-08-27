# Language and Runtime

## Syntax and name deprecations

Source batch: `8.5-migration`.

- Replace the non-canonical casts `(boolean)`, `(integer)`, `(double)`, and
  `(binary)` with `(bool)`, `(int)`, `(float)`, and `(string)`.
- Terminate `case` labels with `:` rather than `;`.
- Replace backticks used as an alias for `shell_exec()` with an explicit
  `shell_exec()` call.
- Incrementing a non-numeric string with `++` is deprecated; use
  `str_increment()`.
- A `null` array offset and a `null` key passed to `array_key_exists()` are
  deprecated. Use the empty string explicitly when that is the intended key.

Declaring a class whose complete name is `_` is deprecated (source batch
`8.4-migration`). Class names that merely start with an underscore remain
valid.

## Errors, diagnostics, and output lifecycle

### User-generated fatal errors

Source batch: `8.4-migration`.

`trigger_error($message, E_USER_ERROR)` is deprecated. Throw an exception when
the failure should be recoverable, or call `exit()` when it should not be.

### Output and magic methods

Source batch: `8.5-migration`.

Producing output from inside a user output handler is deprecated. Its
deprecation bypasses that handler, so the message remains visible.

`__debugInfo()` must return an array rather than `null`. `__sleep()` and
`__wakeup()` are soft-deprecated in favor of `__serialize()` and
`__unserialize()`.

For `SplFixedArray` subclasses, `SplFixedArray::__wakeup()` is deprecated; use
`__serialize()` and `__unserialize()` instead (source batch `8.4-migration`).
The nonstandard uppercase `S` tag in serialized strings is also deprecated.

### Fatal errors and shutdown

Fatal errors, including maximum-execution-time failures, now include a
backtrace (source batch `8.5.0`).

Tick handlers remain active until shutdown functions, destructors, and
output-handler cleanup have all completed (source batch `8.5-migration`).

Traits now bind before the parent class. Compilation and linking errors are
delayed until those phases finish. A fatal error flushes delayed errors without
user error handlers, and an exception from a handler processing a linking error
no longer prevents linking.

## Numeric, comparison, and destructuring behavior

### Zero to a negative power

Source batch: `8.4-migration`.

`0 ** $negative` and `pow(0, $negative)` are deprecated because they imply
division by zero. Use `fpow()` when IEEE 754 behavior is wanted.

### Recursive and loose comparisons

Encountering recursion while comparing values now throws `Error` rather than
ending with an `E_ERROR` fatal error, allowing deliberate comparisons of cyclic
structures to catch the failure (source batch `8.4-migration`).

Loose comparisons between otherwise uncomparable objects and booleans now
consistently follow `(bool)$object` (source batch `8.5-migration`).

### Cast and destructuring warnings

Source batch: `8.5-migration`.

Destructuring a non-array value other than `null` now warns. Casting `NAN` to
`int` warns, as does casting a float or float-like string to `int` when the
value cannot be represented as an integer.

`class_alias()` no longer permits `array` or `callable` as alias names. Final
subclasses may substitute `static` with `self` or with their concrete class
name. `gc_collect_cycles()` no longer counts strings or resources collected
only indirectly through cycles.

## Constants, properties, and constant expressions

### Internal constant metadata

Source batch: `8.4-migration`.

Class constants supplied by Date, Intl, PDO, Reflection, SPL, SQLite, and
XMLReader now declare types. Reflection and tooling that assumed these internal
constants were untyped must account for the type metadata.

Redeclaring a constant is deprecated in addition to continuing to emit a
warning (source batch `8.5-migration`). The `report_memleaks` INI directive is
also deprecated.

### Closures and casts in constant expressions

Source batch: `8.5.0`.

Closures and first-class callables may appear in attribute arguments, property
or parameter defaults, constants, and class constants. Casts are also valid in
constant expressions.

```php
const LENGTH = strlen(...);
const ZERO = (int) 0.3;
```

### Attributes and property declarations

Source batch: `8.5.0`.

Attributes may decorate compile-time non-class constants declared with
`const`, and `#[\Deprecated]` can mark those constants.

```php
#[\Deprecated]
const LEGACY_MODE = 1;
```

`#[\Override]` may be applied to properties. Static properties support
asymmetric visibility, and constructor property promotion may declare final
properties.

### Attribute target validation

Source batch: `8.5-migration`.

Applying `#[\Attribute]` to an abstract class, enum, interface, or trait now
fails during compilation. Adding `#[\DelayedTargetValidation]` defers the check
until runtime, where `ReflectionAttribute::newInstance()` can throw.

## Cloning and readonly properties

In `__clone()`, a readonly property may be reinitialized, but code may no longer
take an indirect reference such as `$ref = &$this->readonlyProperty` (source
batch `8.4-migration`).

The `clone` operation also has function syntax with a `$withProperties`
argument. It may replace properties, including readonly properties, while
cloning (source batch `8.5.0`).

```php
$copy = clone($original, ['id' => $newId]);
```

## Closures and reflection

Source batch: `8.5-migration`.

The following closure operations are deprecated:

- Binding an instance to a static closure.
- Binding a method to an unrelated object.
- Unbinding `$this`.
- Binding to the scope of an internal class.
- Rebinding the scope of a closure created from a function or method.

The no-op Reflection `setAccessible()` methods are deprecated. Do not request a
missing constant with `ReflectionClass::getConstant()` or request a default
value from a `ReflectionProperty` that has none.

The one-argument `ReflectionMethod::__construct()` is deprecated; use
`ReflectionMethod::createFromMethodName()` instead (source batch
`8.4-migration`).

## SPL collections and autoloading

Source batch: `8.5-migration`.

- To unregister every autoloader, iterate over `spl_autoload_functions()`
  instead of passing `spl_autoload_call` to `spl_autoload_unregister()`.
- Prefer `SplObjectStorage::offsetExists()`, `offsetSet()`, and `offsetUnset()`
  over `contains()`, `attach()`, and `detach()`.
- Stop constructing `ArrayObject` or `ArrayIterator` over objects.
- `ArrayObject` no longer accepts enums.
- `SplFileObject::fwrite()` has a nullable `length` parameter whose default is
  `null` rather than `0`.

## Namespaces, values, and generated filenames

Leaving a namespace block now clears its seen symbols, so a later namespace
block may reuse a symbol name declared by an earlier block without the prior
cross-block conflict (source batch `8.4.0`).

`PHP_DEBUG` and `PHP_ZTS` contain booleans rather than integers (source batch
`8.4-migration`). Names generated for uploads and by `tempnam()` are 13 bytes
longer, so revisit path-length assumptions.

## Non-CLI argument derivation

Source batch: `8.5-migration`.

Deriving `$_SERVER['argc']` and `$_SERVER['argv']` from a query string in
non-CLI SAPIs is deprecated. Set `register_argc_argv=0`; after validating the
input, read `$_GET` or `$_SERVER['QUERY_STRING']` instead.
