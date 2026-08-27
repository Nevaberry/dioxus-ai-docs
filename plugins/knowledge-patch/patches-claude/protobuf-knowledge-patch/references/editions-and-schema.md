# Editions and schema authoring

## Edition 2024 rollout (`edition-2024-announcement`)

Edition 2024 was provisionally announced for the protobuf 32.x release line in
Q3 2025. The announced behavior could change before release. Select features
explicitly when migration needs to preserve older behavior.

## Naming-style enforcement (`edition-2024-announcement`)

`feature.enforce_naming_style` enables strict naming-style enforcement by
default so schemas remain round-trippable. A file can explicitly choose the
legacy naming-style feature value while names are migrated.

## Symbol visibility (`edition-2024-announcement`, `35.0`)

`default_symbol_visibility` controls whether messages and enums can be referenced
through imports independently of code generation. Edition 2024 defaults to
`EXPORT_TOP_LEVEL`: top-level symbols are exported and nested symbols are local.
Use `export` and `local` to make exceptions explicit.

```proto
local message LocalMessage {
  export enum ExportedNestedEnum {
    UNKNOWN_EXPORTED_NESTED_ENUM_VALUE = 0;
  }
}
```

Visibility checking also applies to service method input and output messages. A
method is rejected when its request or response type is not visible from the
service file.

## Weak declarations and option imports (`edition-2024-announcement`)

Edition 2024 does not allow `import weak` or the `weak` field option. If weak
imports existed only to consume custom options without generating C++ or Go
code, replace them with `import option`. See the build reference for import
ordering and Bazel `option_deps`.

## Removed `ctype` option (`edition-2024-announcement`)

Edition 2024 rejects the `ctype` field option. Select the generated C++ string
representation with `features.(pb.cpp).string_type`.

## Descriptor cardinality and presence (`31.0`, `34.0-migration`)

`FieldDescriptor.label`, `getLabel`, and the `LABEL_*` constants were deprecated
before the C++ `FieldDescriptor::label()`, Python `FieldDescriptor.label`, and
PHP `FieldDescriptor::getLabel()` accessors were removed.

Use semantic queries instead:

- `isRepeated` for repeated cardinality.
- `isRequired` for required proto2 or Editions fields.
- `hasPresence` for singular-field presence.
- For proto3-only questions, use `hasOptionalKeyword` and
  `getRealContainingOneof` to distinguish the optional keyword and true oneofs.

For Editions, the transitional `getLabel` behavior returned `LABEL_OPTIONAL` for
every singular field and `LABEL_REPEATED` for every repeated field, while
`hasOptionalKeyword` always returned false. Proto2 retained declared label
behavior during that transition. Code should not reconstruct semantic presence
from those labels.

## Compiler feature validation (`34.0`)

The compiler validates feature support on custom options and validates both
options and features while parsing. Definitions that use unsupported features
can now be rejected instead of passing unchecked.

## Field-name length limit (`34.0-announcement`)

`protoc` rejects field names longer than 2^16 characters.

## Descriptor parsing and Edition 2024 generators (`34.0`)

upb performs additional validation of `syntax` and `edition` while parsing
descriptors. Malformed dynamic descriptor data accepted by older runtimes can
now fail. upb generators also enable Edition 2024.

## Edition 2026 field-name collisions (`35.0`)

The compiler implements the Edition 2026 `enforce_naming_style` behavior.
Schemas can be rejected when distinct field names collide after a target
language's name conversion. Resolve such collisions before switching editions.

## Custom JSON enum strings (`edition-2026`)

An Edition 2026 enum value can override its JSON spelling with
`(pb.enumvalue.json).string`. This complements field-level `json_name` for
external naming contracts and collision-free migrations.

```proto
enum Foo {
  FOO_UNSPECIFIED = 0;
  FOO_BAR = 5 [(pb.enumvalue.json).string = "custom_string_here"];
}
```
