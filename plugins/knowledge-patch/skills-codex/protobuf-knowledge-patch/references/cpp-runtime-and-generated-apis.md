# C++ Runtime and Generated APIs

## Language and ownership baseline

C++17 is the minimum language level from `30.0-migration` onward.

### Borrowed descriptor strings

`MessageLite::GetTypeName`, `UnknownField::length_delimited`, and descriptor
name accessors such as `FieldDescriptor::full_name` return
`absl::string_view`. Update callers to preserve the source lifetime or make an
explicit `std::string` copy. A view's `data()` is not guaranteed to be
null-terminated.

Edition-driven string and enum-name view defaults are covered in
[Editions, Schema, and Descriptors](editions-schema-and-descriptors.md).

## Removed and changed APIs

### Runtime replacements (`30.0-migration`)

- Replace `Arena::CreateMessage` with `Arena::Create`.
- Replace `Arena::GetArena` with `value->GetArena()`.
- Replace `JsonOptions` with `JsonPrintOptions`.
- `RepeatedPtrField::ClearedCount` has no direct replacement; migrate to arenas.
- The `ctype` descriptor option is no longer exposed; use
  `FieldDescriptor::cpp_string_type()`.

### Unconditional behavior and removals (`34.0-announcement`)

These rollout macros are removed and their behavior is unconditional:

- `PROTOBUF_FUTURE_RENAME_ADD_UNUSED_IMPORT`
- `PROTOBUF_FUTURE_REMOVE_ADD_IGNORE_CRITERIA`
- `PROTOBUF_FUTURE_STRING_VIEW_DESCRIPTOR_DATABASE`
- `PROTOBUF_FUTURE_NO_RECURSIVE_MESSAGE_COPY`
- `PROTOBUF_FUTURE_REMOVE_REPEATED_PTR_FIELD_ARENA_CONSTRUCTOR`
- `PROTOBUF_FUTURE_REMOVE_MAP_FIELD_ARENA_CONSTRUCTOR`
- `PROTOBUF_FUTURE_REMOVE_REPEATED_FIELD_ARENA_CONSTRUCTOR`

The arena-taking constructors `RepeatedField(Arena*)`,
`RepeatedPtrField(Arena*)`, and `Map(Arena*)` are deleted. Also:

- replace `AddUnusedImportTrackFile()` / `ClearUnusedImportTrackFiles()` with
  `AddDirectInputFile()` / `ClearDirectInputFiles()`;
- pass `AddIgnoreCriteria()` a `unique_ptr` to transfer ownership;
- replace `FieldDescriptor::has_optional_keyword()` with `has_presence()`;
- express `FieldDescriptor::is_optional()` as
  `!is_required() && !is_repeated()`;
- `UseDeprecatedLegacyJsonFieldConflicts()` has no replacement.

In `34.0`, `PROTOBUF_CONSTEXPR` is removed; use `constexpr` directly.

## Repeated fields and bounds

`MutableRepeatedFieldRef<T>::Reserve()` is removed (`30.0`). Generic reflection
over repeated fields must not reserve capacity through that API.

The `34.0-migration` `RepeatedPtrField` layout stores elements in contiguous
chunks of preallocated memory, similarly to `std::deque`. Review code that
depends on earlier copy/move behavior. Some `UnsafeArena` operations can become
equivalent to arena-safe counterparts and may later be deprecated.

Bounds validation is progressively comprehensive:

- `RepeatedField::Get` and `RepeatedPtrField::Get` check out-of-bounds access
  (`34.0-announcement`).
- `ExtractSubrange` and `DeleteSubrange` validate ranges and abort on invalid
  access (`34.0`).
- `UnsafeArenaExtractSubrange`, `ReleaseLast`, and `SwapElements` also validate
  their bounds (`35.0`).

Validate indices, counts, and nonempty preconditions before these calls.

## Arenas and recursive messages

In debug builds, clearing an arena-allocated oneof message clears its memory;
ASAN poisons it. Accessing the old object after the clear is diagnosed as a
use-after-free (`30.0-migration`).

Debug builds also verify that a `CopyFrom` destination is not a descendant of
the source (`34.0`). Never copy a parent recursive message into one of its own
descendants.

`Arena::Ptr` and `Arena::UniquePtr` (`35.0`) provide explicit smart-pointer
forms for values associated with an arena.

## Debug output and parsing

`AbslStringify`, `proto2::ShortFormat`, `proto2::Utf8Format`, and
`*DebugString` redact `debug_redact` fields, prepend a randomized per-process
prefix, and do not produce parseable TextFormat (`30.0-migration`). Use them
for logs, binary encoding for serialization, or an explicit
`TextFormat.printer().printToString(proto)` call when parseable unredacted text
is deliberately required.

`BinaryToJson` now propagates a parse failure when skipping an unknown field
fails (`34.0`). Code can receive an error for malformed input that previously
appeared to succeed.

## Generated APIs and utilities

`FieldMaskUtil::TrimMessage` handles repeated message fields (`34.0`), allowing
field-mask trimming of messages that contain repeated submessages.

Several logically constant APIs became `[[nodiscard]]` at
`34.0-announcement`; callers that ignore results can newly fail warning-as-error
builds.

Protobuf message and enum types can be used directly as native Abseil flag
values (`35.0`); enum support also includes `std::vector` values.
