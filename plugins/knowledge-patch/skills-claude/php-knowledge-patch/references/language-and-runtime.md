# Language and Runtime

## Deprecations and migration work

### Arithmetic, identifiers, and fatal signaling (8.4-migration)

`0 ** $negative` and `pow(0, $negative)` are deprecated because they imply
division by zero; use `fpow()` when IEEE 754 behavior is intended. A class whose
complete name is `_` is deprecated, though names beginning with `_` remain
valid. Replace `trigger_error($message, E_USER_ERROR)` with an exception for a
recoverable failure or `exit()` for an unrecoverable one.

### Named entry points (8.4-migration)

Replace the ISO-string `DatePeriod` constructor with
`DatePeriod::createFromISO8601String()`. Replace one-argument
`ReflectionMethod::__construct()` with
`ReflectionMethod::createFromMethodName()`. The corresponding Intl, LDAP, and
stream-context overload migrations are covered in their topical references.

### Core syntax and execution forms (8.5-migration)

The casts `(boolean)`, `(integer)`, `(double)`, and `(binary)` are deprecated;
use `(bool)`, `(int)`, `(float)`, and `(string)`. End a `case` with `:` rather
than `;`. Backticks as an alias for `shell_exec()` are deprecated, so call the
chosen process API explicitly.

### Output and magic methods (8.5-migration)

Producing output inside a user output handler is deprecated. Its deprecation
message bypasses that handler so it remains visible. `__debugInfo()` must return
an array, while `__sleep()` and `__wakeup()` are soft-deprecated in favor of
`__serialize()` and `__unserialize()`.

### Closure rebinding (8.5-migration)

The following are deprecated: binding an instance to a static closure, binding
a method to an unrelated object, unbinding `$this`, binding to an internal-class
scope, and rebinding the scope of a closure created from a function or method.

### Null keys and string increments (8.5-migration)

Using `null` as an array offset or as the key for `array_key_exists()` is
deprecated. Use `''` explicitly only when the empty-string key is intended.
Incrementing a non-numeric string with `++` is deprecated; use
`str_increment()`.

### Non-CLI arguments and diagnostics (8.5-migration)

Deriving `$_SERVER['argc']` and `$_SERVER['argv']` from a query string in a
non-CLI SAPI is deprecated. Set `register_argc_argv=0`, validate the request,
and read `$_GET` or `$_SERVER['QUERY_STRING']`. Redeclaring a constant is now
deprecated as well as warned, and `report_memleaks` is deprecated.

### Reflection access and missing values (8.5-migration)

The no-op Reflection `setAccessible()` methods are deprecated. Do not request a
missing constant with `ReflectionClass::getConstant()` or request a default
value from a `ReflectionProperty` that has none.

## Object, type, and comparison behavior

### Readonly properties during cloning (8.4-migration)

`__clone()` may reinitialize a readonly property, but it may not take an
indirect reference to that property, such as
`$ref = &$this->readonlyProperty`.

### Recursive comparisons (8.4-migration)

Recursion encountered while comparing values throws an `Error` instead of
ending with an `E_ERROR` fatal error. Code intentionally comparing cyclic
structures can catch this failure.

### Core values, filenames, and internal constants (8.4-migration)

`PHP_DEBUG` and `PHP_ZTS` contain booleans rather than integers. Upload and
`tempnam()` names are 13 bytes longer, so revisit path-length assumptions.
Internal class constants supplied by Date, Intl, PDO, Reflection, SPL, SQLite,
and XMLReader now declare types; Reflection and tooling must account for that
metadata.

### Core types and comparisons (8.5-migration)

`class_alias()` no longer permits `array` or `callable` as alias names. Loose
comparisons between otherwise uncomparable objects and booleans consistently
follow `(bool)$object`. Final subclasses may substitute `static` with `self` or
their concrete class name. `gc_collect_cycles()` no longer counts strings or
resources collected only indirectly through cycles.

### New warnings and removed configuration (8.5-migration)

`disable_classes` has been removed. Destructuring a non-array other than `null`
warns. Casting `NAN` to `int` warns, as does casting a float or float-like string
to `int` when its value cannot be represented.

## Compilation, linking, and shutdown

### Shutdown sequencing and delayed linking errors (8.5-migration)

Tick handlers remain active until shutdown functions, destructors, and output
handler cleanup finish. Traits bind before the parent class. Compilation and
linking errors are delayed until their phases finish; a fatal error flushes
delayed errors without user error handlers, and an exception raised while a
handler processes a linking error no longer prevents linking.

### Attribute target validation (8.5-migration)

Applying `#[\Attribute]` to an abstract class, enum, interface, or trait fails
during compilation. `#[\DelayedTargetValidation]` defers the check until
runtime, where `ReflectionAttribute::newInstance()` can throw.

### Namespace-block symbol reuse (8.4.0)

Leaving a namespace block clears its seen symbols. A later namespace block may
therefore use a symbol name declared by an earlier block without the former
cross-block conflict.

## New language and runtime capabilities

### Constant expressions (8.5.0)

Closures and first-class callables may appear in attribute arguments, property
or parameter defaults, constants, and class constants. Casts are valid in
constant expressions too.

```php
const LENGTH = strlen(...);
const ZERO = (int) 0.3;
```

### Attributes on constants (8.5.0)

Attributes may decorate compile-time non-class constants declared with
`const`; `#[\Deprecated]` can mark these constants.

```php
#[\Deprecated]
const LEGACY_MODE = 1;
```

### Property declarations (8.5.0)

`#[\Override]` may be applied to properties, asymmetric visibility is available
for static properties, and constructor property promotion may declare final
properties.

### Clone-time property replacement (8.5.0)

`clone` has function syntax and accepts a `$withProperties` argument that can
replace properties, including readonly properties, while copying.

```php
$copy = clone($original, ['id' => $newId]);
```

### Fatal-error backtraces (8.5.0)

Fatal errors, including maximum-execution-time failures, now include a
backtrace.
