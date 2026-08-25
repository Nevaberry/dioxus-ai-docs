# Java, C#, and Objective-C runtimes

## Java file layout and outer class names (`edition-2024-announcement`)

The `nest_in_file_class` feature replaces the removed `java_multiple_files`
option. Edition 2024 generates classes in separate files by default. Its default
outer class name is always the camel-cased proto filename plus `Proto`; for
example, `foo/bar_baz.proto` becomes `BarBazProto`. Use
`java_outer_classname` to override that derived name.

## Large Java enums (`edition-2024-announcement`, `34.0`)

The opt-in `large_enum` feature permits Java enums beyond the language's normal
enum-constant limit. Generated large-enum types emulate enums but do not support
every enum operation, including `switch`. The Java lite runtime now honors the
feature and correctly handles aliased values in large enums.

## Java initialization checks (`34.0`)

Generated `isInitialized()` accessors are deprecated for message types that have
no required fields. Calls on those types can newly produce deprecation
diagnostics; remove redundant checks or scope them to messages that can contain
required fields.

## JSON and deep recursion (`34.0`)

Recursion-limit enforcement now includes Java JSON `Any` nested within `Any`
and C# JSON well-known types containing deep arrays. Deep inputs that previously
bypassed the limit can be rejected. Test parsers at and beyond the configured
limit, especially when handling untrusted JSON.

## C# UTF-8 timing (`30.0-migration`)

C# surfaces UTF-8 enforcement failures earlier when a protobuf `string` field
contains invalid UTF-8. Do not rely on a later serialization or conversion step
to be the first point of failure.

## C# well-known type includes (`35.0`)

The `Google.Protobuf.Tools` NuGet package contains an `include` directory with
the well-known-type `.proto` files. Packaged compiler invocations can resolve
those imports from the package itself.

## Objective-C unknown fields (`30.0-migration`)

Objective-C's first breaking runtime line is 4.30.x. It replaces
`GPBUnknownFieldSet` with ordering-preserving `GPBUnknownFields`. Each
`GPBUnknownField` represents one value rather than grouping all values for a
field number.

- Extract unknowns with `initFromMessage:`.
- Update them with `mergeUnknownFields:extensionRegistry:error:`.
- Remove them with `clearUnknownFields`.

## Objective-C removed APIs and old gencode (`30.0-migration`)

| Removed or obsolete API | Migration |
| --- | --- |
| `mergeFrom:extensionRegistry:` | `mergeFrom:extensionRegistry:error:` |
| `GPBDuration.timeIntervalSince1970` | `GPBDuration.timeInterval` |
| `GPBTextFormatForUnknownFieldSet()` | `GPBTextFormatForMessage()` |
| `GPBFileDescriptor.syntax` | Remove the obsolete query |

Runtime entry points for generated code older than 3.22 were removed. Regenerate
that code with a current compiler before updating the runtime.

## Objective-C nullability and descriptors (`34.0-announcement`)

Corrected `GPB*Dictionary` nullability makes affected Swift return values
`Optional<T>`. Handle the optional at Swift call sites. The
`-[GPBFieldDescriptor optional]` accessor was removed; use
`!required && fieldType == GPBFieldTypeSingle`.

## Objective-C generated extension and oneof APIs (`34.0`)

The generator supports three modes for proto extension generation. It also emits
presence-checking accessors for oneofs; prefer those generated checks over
inferring presence from values.
