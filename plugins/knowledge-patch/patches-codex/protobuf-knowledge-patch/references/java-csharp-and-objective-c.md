# Java, C#, and Objective-C

## Java generation and reflection

### Edition 2024 files and outer classes (`edition-2024-announcement`)

`nest_in_file_class` replaces the removed `java_multiple_files` option. Edition
2024 generates classes in their own files by default. The default outer class
name is always the camel-cased proto filename plus `Proto`; for example,
`foo/bar_baz.proto` becomes `BarBazProto`. Set `java_outer_classname` to
override it.

### Large enums

The opt-in `large_enum` feature permits generated Java enums beyond Java's
normal enum-constant limit. The generated types emulate enums but do not
support every enum operation, including `switch`. The Java lite runtime honors
`large_enum` and correctly handles large enums with aliased values as of
`34.0`.

### Initialization

Generated `isInitialized()` accessors are deprecated for message types without
required fields (`34.0`). Calls for those types can newly produce deprecation
diagnostics.

## Recursion limits in Java and C#

Recursion-limit enforcement expands in `34.0` to Java JSON `Any` nested within
`Any` and to C# JSON well-known types containing deep arrays. Inputs that
previously bypassed recursion checks can now be rejected.

## C# generated-code packaging and validation

The `Google.Protobuf.Tools` NuGet package includes an `include` directory with
the well-known-type `.proto` files as of `35.0`. Compiler invocations installed
through that package can resolve those imports from the package itself.

C# now surfaces UTF-8 enforcement errors earlier when invalid UTF-8 reaches a
protobuf `string` field (`30.0-migration`). Do not depend on delayed failure.

## Objective-C breaking runtime migration

### Unknown fields (`30.0-migration`)

Objective-C's first breaking runtime release moves from 3.x to 4.30.x and
replaces `GPBUnknownFieldSet` with the ordering-preserving
`GPBUnknownFields`. A `GPBUnknownField` represents one value instead of grouping
values by field number.

- Extract unknown fields with `initFromMessage:`.
- Update with `mergeUnknownFields:extensionRegistry:error:`.
- Remove them with `clearUnknownFields`.

### Removed APIs and old generated code

- Use `mergeFrom:extensionRegistry:error:` instead of
  `mergeFrom:extensionRegistry:`.
- Use `GPBDuration.timeInterval` instead of `timeIntervalSince1970`.
- Use `GPBTextFormatForMessage()` instead of
  `GPBTextFormatForUnknownFieldSet()`.
- Treat `GPBFileDescriptor.syntax` as obsolete.

Runtime entry points for generated code older than 3.22 are removed. Regenerate
those sources with a current compiler before upgrading the runtime.

### Nullability and descriptors (`34.0-announcement`)

Corrected `GPB*Dictionary` nullability makes affected Swift return values
`Optional<T>`. Audit Swift call sites that assumed a nonoptional value.

`-[GPBFieldDescriptor optional]` is removed. Test
`!required && fieldType == GPBFieldTypeSingle` instead.

### Generated extensions and oneofs (`34.0`)

Objective-C generation supports three modes for proto extension generation and
emits presence-checking accessors for oneofs.
