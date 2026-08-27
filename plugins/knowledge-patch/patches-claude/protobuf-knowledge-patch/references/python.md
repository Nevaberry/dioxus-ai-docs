# Python and upb runtime

## Interpreter and package baselines (`30.0-migration`, `34.0-migration`)

The Python package first moved from 5.29.x to 6.30.x with a Python 3.9 minimum.
The later v34 runtime raises the interpreter requirement to Python 3.10 or
newer. Check both the protobuf package coordinate and interpreter before
upgrading.

## Removed reflection and factory APIs (`30.0-migration`)

The runtime removed `reflection.ParseMessage`, `reflection.MakeClass`, prototype
and creation methods on `MessageFactory` and `SymbolDatabase`, and the
`GetMessages` methods on those classes. Use:

- `message_factory.GetMessageClass()` for one descriptor;
- `message_factory.GetMessageClassesForFiles()` for files.

The legacy `service` RPC interfaces must be replaced with RPC-specific generator
plugins. The C++-extension-only `GetDebugString` has no replacement.

## Closed enums and scalar assignment (`30.0-migration`, `34.0-announcement`)

Python and upb setters reject values outside a closed enum under Edition 2023.
They also reject `bool` assigned to an integer or enum field instead of
implicitly converting it. Invalid-type conversion to `Timestamp` or `Duration`
raises `TypeError`, not `AttributeError`; update exception handling accordingly.

## Map `setdefault` (`30.0-migration`)

`ScalarMap.setdefault` requires both a key and a value. Message-valued maps
reject `setdefault` entirely because synthesizing a message value through that
mapping method is unsupported.

## Nested generated names (`30.0-migration`)

A nested generated message class includes its outer message in `__qualname__`
while retaining the short `__name__`. For example, `Foo.Bar.__qualname__` is
`"Foo.Bar"`, while `Foo.Bar.__name__` remains `"Bar"`.

## Removed formatting controls (`34.0-announcement`)

JSON serialization no longer accepts the deprecated `float_precision` option.
Text-format serialization no longer accepts `float_format` or `double_format`.
Remove those keyword arguments rather than attempting to preserve the old
formatting behavior.

## Repeated-field initialization errors (`34.0`)

Message construction through keyword arguments no longer silently swallows some
errors involving repeated fields. Invalid repeated-field initialization can now
raise an exception; do not assume partially accepted input.

## NumPy repeated-scalar binding (`34.0`)

Scalar repeated fields provide a NumPy binding for direct array-oriented
interoperability. Prefer the binding when transferring compatible scalar arrays
instead of manually iterating values.

## Recursion limits (`34.0`, `35.0`)

Python and upb guard recursive nesting in message processing. Python
`text_format` also accepts an optional recursion-depth limit. Set the limit when
parsing untrusted or deeply nested text-format input, and test rejection at the
boundary.

## Strict descriptor parsing (`34.0`)

upb validates `syntax` and `edition` more thoroughly when parsing descriptors.
Malformed dynamic descriptor data that older releases accepted can be rejected.

## Free-threaded Python (`35.0`)

The upb runtime supports free-threaded Python. The same release fixes races in
lazy message initialization and repeated-field presence handling that affected
that mode. Test native extensions and concurrency-sensitive message paths in the
free-threaded build rather than assuming ordinary-CPython behavior.
