# Python Runtime and Generated APIs

## Runtime and build baseline

The Python package major moves from 5.29.x to 6.30.x at `30.0-migration` and
requires Python 3.9 or newer. The 7.34 runtime raises the interpreter floor to
Python 3.10 (`34.0-migration`).

For Bazel rule and dependency-file moves, see
[Compatibility, Builds, and Releases](compatibility-builds-and-releases.md).

## Removed dynamic-message and service APIs

The following runtime APIs are removed at `30.0-migration`:

- `reflection.ParseMessage` and `reflection.MakeClass`;
- prototype/creation methods on `MessageFactory` and `SymbolDatabase`;
- `GetMessages` methods on those objects;
- legacy `service` RPC interfaces;
- the C++-extension-only `GetDebugString`.

Use `message_factory.GetMessageClass()` or
`GetMessageClassesForFiles()` for dynamic classes. Replace legacy generic RPC
interfaces with RPC-specific generator plugins. `GetDebugString` has no
replacement.

## Assignment, maps, and initialization

### Closed enums

Python and upb setters reject invalid values for closed enums under Edition
2023 (`30.0-migration`).

### Map `setdefault`

`ScalarMap.setdefault` requires both a key and a value. Message-valued maps
reject `setdefault` entirely (`30.0-migration`). Construct a message explicitly
through the map's supported access pattern instead.

### Scalar conversion failures

Assigning `bool` to an enum or integer field is rejected rather than converted
implicitly (`34.0-announcement`). Invalid-type conversion to `Timestamp` or
`Duration` raises `TypeError` instead of `AttributeError`; update exception
handlers accordingly.

### Repeated-field initialization

Keyword-argument message construction no longer swallows some errors involving
repeated fields. Invalid repeated-field initialization can raise an error
(`34.0`).

## Generated class identity

Generated nested classes include their outer message in `__qualname__` while
retaining the short `__name__` (`30.0-migration`). For example,
`Foo.Bar.__qualname__` is `"Foo.Bar"`, while `Foo.Bar.__name__` remains `"Bar"`.
Code that keys on qualified names must allow the nesting.

## Reflection and descriptors

`FieldDescriptor.label` is removed at `34.0-migration`. Use `is_repeated`,
`is_required`, and presence APIs as appropriate; see
[Editions, Schema, and Descriptors](editions-schema-and-descriptors.md) for the
cross-language migration.

upb's stricter `syntax` and `edition` descriptor parsing is also covered there.

## JSON and text formatting

The JSON serializer no longer accepts deprecated `float_precision`, and text
format serialization no longer accepts `float_format` or `double_format`
(`34.0-announcement`). Remove the options rather than silently approximating
their prior formatting.

Python `text_format` adds an optional recursion-depth limit at `35.0`. Set it
when parsing untrusted or deeply nested text-format data. Python and upb also
guard nested-message recursion from `34.0`, so deep data that previously parsed
can be rejected.

## Repeated scalars and free-threaded execution

Python scalar repeated fields gain a NumPy binding in `34.0`, enabling direct
array-oriented interoperability for those containers.

The upb runtime supports free-threaded Python as of `35.0`. The same release
fixes races in lazy message initialization and repeated-field presence handling
that affected free-threaded execution.
