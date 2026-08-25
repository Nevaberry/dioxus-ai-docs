# Rust and Go generated APIs

## Rust exact-version compatibility

Rust generated code and its runtime must use the exact same protobuf release.
Regenerate whenever the runtime changes.

## `MessageMut` sendability (`34.0`)

The Rust `MessageMut` trait includes a `Send` bound. Custom implementations and
generic code using the trait must satisfy cross-thread sendability.

## Standard optional type (`35.0`)

Generated `_opt()` accessors return the standard `Option` type instead of
`protobuf::Optional`. Update explicit type names, conversions, trait bounds, and
wrappers that mentioned the old protobuf-specific type.

## Generated `XyzView` collisions (`35.0`)

When one generated scope contains direct siblings named `Xyz` and `XyzView`,
the generator mangles the `XyzView` type. Code referring to the former generated
identifier must be updated after regeneration.

## Generic field traits (`35.0`)

The runtime adds `Singular` for types allowed as simple fields and revises map
traits. Replace the removed `ProxiedInMapValue` alias with `MapValue`. Do not
treat `f32` or `f64` as satisfying the map-key trait; their prior conformance was
incorrect.

## View ergonomics (`35.0`)

`ProtoStr` is usable in const contexts. In addition, `&T` implements `AsView`
whenever `T` implements it, so generic view-taking code can accept references
without converting to byte slices or adding an adapter.

## Go Editions API level (`edition-2026-guide`)

`features.(pb.go).api_level` defaults to `API_OPEN` in Edition 2023 and to
`API_OPAQUE` in Editions 2024 and 2026. Opaque generated APIs hide struct fields
behind accessors. Select `API_OPEN` to preserve direct field access, or
`API_HYBRID` to expose both fields and accessors during migration.

```proto
edition = "2026";

import option "google/protobuf/go_features.proto";

option features.(pb.go).api_level = API_HYBRID;
```

## Go enum-prefix stripping (`edition-2026-guide`)

Edition 2024 and later support `features.(pb.go).strip_enum_prefix` at file,
enum, and enum-value scopes:

- `STRIP_ENUM_PREFIX_KEEP` is the default and preserves generated names.
- `STRIP_ENUM_PREFIX_GENERATE_BOTH` produces both spellings for migration.
- `STRIP_ENUM_PREFIX_STRIP` removes the repeated enum-name prefix.

```proto
edition = "2026";

import option "google/protobuf/go_features.proto";

option features.(pb.go).strip_enum_prefix = STRIP_ENUM_PREFIX_STRIP;
```
