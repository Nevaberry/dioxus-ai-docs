# C++ runtime and generated APIs

## Language baseline (`30.0-migration`)

The minimum supported language level is C++17 rather than C++14.

## Borrowed descriptor strings (`30.0-migration`)

`MessageLite::GetTypeName`, `UnknownField::length_delimited`, and descriptor name
methods such as `FieldDescriptor::full_name` return `absl::string_view`. Update
callers to retain only a borrowed view, or explicitly copy to `std::string` when
ownership is required. A view's `data()` is not guaranteed to be null-terminated.

## Debug output and redaction (`30.0-migration`)

`AbslStringify`, `proto2::ShortFormat`, `proto2::Utf8Format`, and all
`*DebugString` methods redact fields annotated with `debug_redact`, prepend a
per-process randomized marker, and no longer produce parseable TextFormat.

Use these methods for logs, binary encoding for serialization, or
`TextFormat.printer().printToString(proto)` when parseable unredacted text is an
explicit requirement.

## Removed core APIs (`30.0-migration`)

| Removed API | Migration |
| --- | --- |
| `Arena::CreateMessage` | `Arena::Create` |
| `Arena::GetArena` | `value->GetArena()` |
| `JsonOptions` | `JsonPrintOptions` |
| `RepeatedPtrField::ClearedCount` | No direct replacement; migrate ownership to arenas |
| `FieldDescriptor` access to `ctype` | `FieldDescriptor::cpp_string_type()` |

## Cleared arena oneofs (`30.0-migration`)

In debug builds, clearing an arena-allocated oneof message clears its memory and
ASAN poisons it. Any later access is a diagnosed use-after-free. Never retain or
reuse a pointer to the cleared object.

## Reflection reserve removal (`30.0`)

`MutableRepeatedFieldRef<T>::Reserve()` was removed. Generic repeated-field
reflection code must stop attempting to reserve capacity through that API.

## Edition string and enum views (`edition-2024-announcement`)

Edition 2024 changes the default `features.(pb.cpp).string_type` from `STRING` to
`VIEW`, so generated string-field APIs use view behavior unless the feature is
overridden. The `enum_name_uses_string_view` default similarly makes generated
enum-name helpers return borrowed `absl::string_view` rather than a referenced
`std::string`:

```cpp
absl::string_view Foo_Name(int);
```

## Unconditional future behavior (`34.0-announcement`)

The following rollout macros were removed and their behavior is unconditional:

- `PROTOBUF_FUTURE_RENAME_ADD_UNUSED_IMPORT`
- `PROTOBUF_FUTURE_REMOVE_ADD_IGNORE_CRITERIA`
- `PROTOBUF_FUTURE_STRING_VIEW_DESCRIPTOR_DATABASE`
- `PROTOBUF_FUTURE_NO_RECURSIVE_MESSAGE_COPY`
- `PROTOBUF_FUTURE_REMOVE_REPEATED_PTR_FIELD_ARENA_CONSTRUCTOR`
- `PROTOBUF_FUTURE_REMOVE_MAP_FIELD_ARENA_CONSTRUCTOR`
- `PROTOBUF_FUTURE_REMOVE_REPEATED_FIELD_ARENA_CONSTRUCTOR`

## Arena-taking container constructors (`34.0-announcement`)

`RepeatedField(Arena*)`, `RepeatedPtrField(Arena*)`, and `Map(Arena*)` are
deleted. Callers cannot construct field containers directly from an arena
pointer.

## Removed runtime APIs (`34.0-announcement`)

| Removed or changed API | Migration |
| --- | --- |
| `AddUnusedImportTrackFile()` | `AddDirectInputFile()` |
| `ClearUnusedImportTrackFiles()` | `ClearDirectInputFiles()` |
| `AddIgnoreCriteria(raw_pointer)` | Transfer ownership with `unique_ptr` |
| `FieldDescriptor::has_optional_keyword()` | `has_presence()` |
| `FieldDescriptor::is_optional()` | `!is_required() && !is_repeated()` |
| `UseDeprecatedLegacyJsonFieldConflicts()` | No replacement |

Several logically constant APIs are now `[[nodiscard]]`; callers that ignore
their return values can newly fail warning-as-error builds.

## Repeated-field access hardening (`34.0-announcement`, `34.0`, `35.0`)

`RepeatedField::Get` and `RepeatedPtrField::Get` now perform comprehensive
out-of-bounds checks. `ExtractSubrange` and `DeleteSubrange` validate their
ranges and abort on invalid access. The same hardening later covers
`UnsafeArenaExtractSubrange`, `ReleaseLast`, and `SwapElements`. Validate every
index and count before calling these operations.

## New `RepeatedPtrField` layout (`34.0-migration`)

Elements occupy contiguous chunks of preallocated memory, similar to
`std::deque`. Review code that relies on old copy or move behavior. Some
`UnsafeArena` operations can now be equivalent to arena-safe operations and may
be deprecated.

## Recursive `CopyFrom` safety (`34.0`)

Debug builds check that a `CopyFrom` destination is not a descendant of its
source. Do not copy a parent message into one of its own descendants.

## Binary-to-JSON errors (`34.0`)

`BinaryToJson` reports a parse failure when skipping an unknown field fails.
Inputs that previously appeared to convert successfully can now reach the
caller's error path.

## Field-mask trimming (`34.0`)

`FieldMaskUtil::TrimMessage` now trims repeated message fields, so a mask can be
applied to messages containing repeated submessages.

## Removed compile-time and boundary switches (`34.0`)

`PROTOBUF_CONSTEXPR` was removed; use the C++ `constexpr` keyword. The old
`safe_boundary_check` mechanism is also gone. Source builds select boundary
checking with `--//third_party/protobuf:bounds_check_mode`.

## `unverified_lazy` on extensions (`34.0`)

The C++ implementation rejects `[unverified_lazy = true]` on extension fields.
Remove the option from those schema declarations.

## Arena smart pointers (`35.0`)

`Arena::Ptr` and `Arena::UniquePtr` provide explicit smart-pointer forms for
values associated with an arena. Prefer them where code previously hand-managed
raw arena-backed pointers.

## Native Abseil flags (`35.0`)

Message and enum types can be used directly as Abseil flag values. Enum support
also extends to `std::vector` flag values.

## Edition repeated-field proxy API (`edition-2026-guide`)

Edition 2026 adds `features.(pb.cpp).repeated_type`. Selecting `PROXY` makes
repeated-field accessors return `RepeatedFieldProxy` instead of pointers or
references to `RepeatedField`/`RepeatedPtrField`. The default is `LEGACY`, so
generated APIs change only when `PROXY` is selected at file or field scope.

```proto
edition = "2026";

import option "google/protobuf/cpp_features.proto";

option features.(pb.cpp).repeated_type = PROXY;
```

## Removed Edition options (`edition-2026-guide`)

Edition 2026 schemas must remove `cc_api_version`, `cc_utf8_verification`, and
`cc_enable_arenas`.

## Generated namespace (`edition-2026`)

The file custom option `(pb.file.cpp).namespace` decouples the generated C++
namespace from the proto package:

```proto
import option "google/protobuf/cpp_options.proto";

package clock.time;

option (pb.file.cpp).namespace = "clock_time";
```
