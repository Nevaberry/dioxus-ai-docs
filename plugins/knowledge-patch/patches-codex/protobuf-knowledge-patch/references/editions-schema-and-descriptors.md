# Editions, Schema, and Descriptors

## Edition 2024 schema behavior

The `edition-2024-announcement` targeted Edition 2024 for Protobuf 32.x in Q3
2025 and described its behavior as provisional at announcement time. When
maintaining an implementation pinned to that announcement boundary, account
for the following feature changes.

### C++ strings and enum names

The default for `features.(pb.cpp).string_type` changes from `STRING` to `VIEW`.
Generated C++ string-field APIs therefore use view behavior unless explicitly
overridden.

The default for `enum_name_uses_string_view` makes generated enum-name helpers
return a borrowed `absl::string_view` instead of a referenced `std::string`:

```cpp
absl::string_view Foo_Name(int);
```

Update callers that store the result or require a null-terminated string.

### Naming style

`feature.enforce_naming_style` enables strict naming enforcement by default so
schemas remain round-trippable. A feature value can opt a file back into the
legacy naming style.

### Symbol visibility

`default_symbol_visibility` controls whether messages and enums can be
referenced through imports without changing code generation. Edition 2024
defaults to `EXPORT_TOP_LEVEL`: top-level symbols are exported and nested
symbols are local. Use `export` and `local` to override visibility explicitly:

```proto
local message LocalMessage {
  export enum ExportedNestedEnum {
    UNKNOWN_EXPORTED_NESTED_ENUM_VALUE = 0;
  }
}
```

As of `35.0`, this visibility checking also covers service method request and
response messages. The compiler rejects a service method whose input or output
type is not visible from the service file.

### Option-only imports

`import option` loads custom options without exposing the imported file's
messages or enums as ordinary symbols. It must follow normal imports. Bazel
targets put such imports in `option_deps`, not `deps`; `option_deps` requires
Bazel 8 or later.

```proto
edition = "2024";
import option "bar.proto";

option (file_opt1) = true;
option (file_opt2) = {bar: true};
```

```build
proto_library(
  name = "foo",
  srcs = ["foo.proto"],
  option_deps = [":custom_option"],
)
```

Edition 2024 removes `import weak` and the `weak` field option. Code that used
weak imports to consume custom options without producing C++ or Go output
should migrate to `import option`.

The `ctype` field option is also forbidden. Choose C++ string representation
through `features.(pb.cpp).string_type`.

## Edition 2026 schema features

### Go generated API (`edition-2026-guide`)

The default for `features.(pb.go).api_level` changes from `API_OPEN` in Edition
2023 to `API_OPAQUE` in Editions 2024 and 2026. Opaque output hides generated
struct fields behind accessors. Select `API_OPEN` to retain fields or
`API_HYBRID` to expose fields and accessors during migration.

```proto
edition = "2026";

import option "google/protobuf/go_features.proto";

option features.(pb.go).api_level = API_HYBRID;
```

### C++ repeated-field proxies

`features.(pb.cpp).repeated_type = PROXY` makes repeated-field accessors return
`RepeatedFieldProxy` instead of `RepeatedField` or `RepeatedPtrField` pointers
and references. The default remains `LEGACY`, so generation changes only when
the feature is selected at file or field scope.

```proto
edition = "2026";

import option "google/protobuf/cpp_features.proto";

option features.(pb.cpp).repeated_type = PROXY;
```

### Go enum-prefix stripping

Edition 2024 and newer allow `features.(pb.go).strip_enum_prefix` at file, enum,
or enum-value scope. `STRIP_ENUM_PREFIX_KEEP` preserves generated names,
`STRIP_ENUM_PREFIX_GENERATE_BOTH` supports migration, and
`STRIP_ENUM_PREFIX_STRIP` removes the repeated enum-name prefix.

```proto
edition = "2026";

import option "google/protobuf/go_features.proto";

option features.(pb.go).strip_enum_prefix = STRIP_ENUM_PREFIX_STRIP;
```

### Removed C++ options

Edition 2026 schemas must remove `cc_api_version`, `cc_utf8_verification`, and
`cc_enable_arenas`.

### Enum JSON strings (`edition-2026`)

An enum value can override its JSON spelling with
`(pb.enumvalue.json).string`. This complements field-level `json_name` for
conflict avoidance, migrations, and external naming requirements.

```proto
enum Foo {
  FOO_UNSPECIFIED = 0;
  FOO_BAR = 5 [(pb.enumvalue.json).string = "custom_string_here"];
}
```

### C++ generated namespace

The `(pb.file.cpp).namespace` file option decouples the generated C++ namespace
from the proto package:

```proto
import option "google/protobuf/cpp_options.proto";

package clock.time;

option (pb.file.cpp).namespace = "clock_time";
```

### Field-name collisions (`35.0`)

The compiler implements Edition 2026 naming enforcement and its
`enforce_naming_style` feature value. Schemas whose field names collide after
language-specific name conversion can now be rejected.

## Descriptor cardinality and presence

At `31.0`, `FieldDescriptor.label`, `getLabel`, and `LABEL_*` constants became
deprecated. Migrate reflection, generators, and dynamic-message code to:

- `isRepeated` for cardinality;
- `isRequired` for required proto2 or Editions fields;
- `hasPresence` for singular presence;
- `hasOptionalKeyword` and `getRealContainingOneof` only when proto3
  optional-keyword or real-oneof detail is specifically needed.

For Editions, `getLabel` simplifies to `LABEL_OPTIONAL` for every singular field
and `LABEL_REPEATED` for every repeated field, while `hasOptionalKeyword` is
always false. Proto2 labels continue to expose declared `optional`, `required`,
or `repeated` keywords at that boundary.

The deprecated C++ `FieldDescriptor::label()`, Python `FieldDescriptor.label`,
and PHP `FieldDescriptor::getLabel()` accessors are removed at
`34.0-migration`. Use the semantic queries rather than emulating labels.

## Compiler and descriptor validation

The compiler rejects field names longer than 2^16 characters
(`34.0-announcement`).

Feature support on custom options is validated as of `34.0`, and both options
and features are validated during parsing. Definitions that use unsupported
features can now fail instead of passing unchecked.

The C++ implementation rejects `[unverified_lazy = true]` on extensions
(`34.0`); remove it from extension fields.

upb performs additional `syntax` and `edition` validation while parsing
descriptors, so malformed dynamic descriptor data can now fail. Its generators
also enable Edition 2024 (`34.0`).
