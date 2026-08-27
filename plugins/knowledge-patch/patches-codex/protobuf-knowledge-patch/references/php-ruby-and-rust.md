# PHP, Ruby, and Rust

## Shared JSON and UTF-8 hardening

Ruby and PHP JSON parsers reject nonnumeric strings such as `""`, `"12abc"`,
and `"abc"` for numeric fields from `30.0-migration` onward. The same inputs
only warned in the 29.x line.

Ruby also surfaces UTF-8 enforcement failures earlier when invalid UTF-8 data
is assigned to a protobuf `string` field (`30.0-migration`).

## PHP

### Runtime baseline and renamed types

The PHP runtime requires PHP 8.2 or newer from `34.0-migration`.

At `34.0-announcement`, replace removed runtime types as follows:

| Removed | Replacement |
| --- | --- |
| `Google\Protobuf\Field_Kind` | `Google\Protobuf\Field\Kind` |
| `Google\Protobuf\Field_Cardinality` | `Google\Protobuf\Field\Cardinality` |
| `Google\Protobuf\Internal\RepeatedField` | `Google\Protobuf\RepeatedField` |

### Strict JSON behavior

PHP JSON parsing rejects out-of-range values, noninteger numeric values for
integer fields, duplicate oneof fields, and non-string values for string fields
(`34.0-announcement`). JSON serialization also rejects `Infinity` and `NaN` as
number values.

The runtime now honors proto2 and Editions scalar defaults instead of ignoring
them. Pure-PHP type checks align with upb-PHP, including rejection of `null` for
string fields.

At `34.0`, JSON serialization gains an option to emit fields whose values equal
their defaults.

### Generated setters and reflection

Generated PHP setters carry type hints at `34.0`, and redundant `GPBUtil`
checks are removed. Reflection, subclasses, and callers that depended on
untyped signatures may require updates.

PHP field descriptors implement `hasPresence()`. The broken
`hasOptionalKeyword()` helper is removed; reflection code should ask about
presence rather than optional-keyword syntax (`34.0`). The older `getLabel()`
removal is detailed in the descriptors reference.

## Ruby and JRuby

JRuby switches to its FFI implementation by default in `30.0`. Applications
that relied on the prior implementation can break. This did not trigger a Ruby
major bump because JRuby support is best-effort rather than official.

Ruby 3.0 support is removed in `31.0`; use Ruby 3.1 or newer. The runtime adds
Ruby 4.0 support in `34.0`.

Ruby code generation can emit RBS files as of `34.0`, allowing generated
protobuf types to participate in RBS-based type checking.

## Rust

### Sendable mutations (`34.0`)

`MessageMut` includes a `Send` bound. Implementations and generic code using
the trait must meet cross-thread sendability requirements.

### Standard optional accessors (`35.0`)

Generated `_opt()` accessors return the standard `Option` type instead of
`protobuf::Optional`. Update code that names, converts, or implements against
the old wrapper.

### Generated-name collisions

When direct siblings named `Xyz` and `XyzView` occur in one generated scope,
the Rust generator mangles the `XyzView` type (`35.0`). Code that refers to the
old generated identifier must follow the regenerated name.

### Field and map traits

Rust adds a `Singular` trait for types allowed as simple fields and revises map
traits (`35.0`). `ProxiedInMapValue` is replaced by `MapValue`; `f32` and `f64`
no longer incorrectly satisfy the map-key trait.

### View usability

`ProtoStr` works in const contexts, and `&T` implements `AsView` whenever `T`
does (`35.0`). Generic view-taking code can accept references without custom
adapters or conversion to byte slices.
