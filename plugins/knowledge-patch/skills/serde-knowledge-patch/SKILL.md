---
name: serde-knowledge-patch
description: Serde 1.0.220 compatibility. Use for Serde work.
license: MIT
version: "1.0.220"
metadata:
  author: Nevaberry
---

# Serde Knowledge Patch

Baseline: Serde through 1.0.209. Covers later Serde and serde_json changes represented by `1.0.220-serde-core`, including serde_json releases through 1.0.150.

## Reference index

| Reference | Topics |
| --- | --- |
| [Core traits and dependencies](references/core-traits-and-dependencies.md) | Choosing `serde` or `serde_core`; derive support; trait-path diagnostics |
| [JSON compatibility and values](references/json-compatibility-and-values.md) | Version floors; enum object keys; arbitrary-precision numbers; `Map` parsing and deserialization; `Value` defaults; `RawValue`; deterministic key ordering |

## Dependency and compatibility changes

### Choose `serde` unless a trait-only dependency is intentional

`serde_core` 1.0.220 contains the core traits and supporting APIs:

- `Serialize`
- `Deserialize`
- `Serializer`
- `Deserializer`
- the supporting `ser` and `de` modules

It deliberately does not provide `#[derive(Serialize)]` or
`#[derive(Deserialize)]`.

Depend directly on `serde_core` only when a crate uses traits as bounds or
writes implementations by hand:

```toml
[dependencies]
serde_core = "1.0.220"
```

```rust
pub fn require_serializable<T: serde_core::Serialize>(_: &T) {}
```

Keep depending on `serde` when the crate derives either trait. `serde`
re-exports the same traits and remains the general-purpose default:

```toml
[dependencies]
serde = { version = "1.0.220", features = ["derive"] }
```

```rust
#[derive(serde::Serialize, serde::Deserialize)]
struct Record {
    id: u64,
}
```

### Read `serde_core` paths in errors as ordinary Serde traits

After the traits moved to `serde_core`, an unsatisfied bound from a format
crate can appear as:

```text
T: serde_core::ser::Serialize
```

This does not normally call for a separate compatibility feature. Fix the
underlying Serde implementation by deriving `serde::Serialize`, enabling
`serde`'s `derive` feature, or enabling the dependency's existing `serde`
feature.

### Respect serde_json's Serde version floor

`serde_json` 1.0.145 requires Serde 1.0.220 or newer. If a dependency graph
pins Serde below 1.0.220, either update Serde or keep `serde_json` below
1.0.145.

### Do not serialize non-string enum representations as object keys

As of `serde_json` 1.0.150, enum keys whose Serde representation is not a
string are rejected during JSON object serialization. Give data-carrying
variants an explicit string-key representation instead of relying on a
non-string enum representation.

### Expect arbitrary-precision spelling changes

In `serde_json` 1.0.149, number strings emitted with the
`arbitrary_precision` feature were aligned with `zmij` formatting. Numeric
values remain equivalent, but their exact serialized spelling can change.
Review snapshots, hashes, signatures, golden files, and byte-for-byte tests
when upgrading.

## Common serde_json value operations

### Deserialize directly from an object map

Since `serde_json` 1.0.131, owned and borrowed object maps implement both
Serde `Deserializer` and `IntoDeserializer`:

```rust
use serde::Deserialize;
use serde_json::{Map, Value};

#[derive(Deserialize)]
struct Config {
    enabled: bool,
}

let map: Map<String, Value> =
    serde_json::from_str(r#"{"enabled":true}"#).unwrap();
let config = Config::deserialize(map).unwrap();
assert!(config.enabled);
```

There is no need to wrap the map in `Value::Object` or serialize it back to
text first. Use a borrowed `&Map<String, Value>` when the caller must retain
the map.

### Parse an object map with `FromStr`

Since `serde_json` 1.0.143, `Map<String, Value>` supports `.parse()`:

```rust
let object: serde_json::Map<String, serde_json::Value> =
    r#"{"answer":42}"#.parse().unwrap();
assert_eq!(object["answer"], serde_json::json!(42));
```

### Default a missing shared value to JSON null

Since `serde_json` 1.0.142, `&Value` implements `Default`. This makes a
missing optional shared reference default to a shared JSON `null` value:

```rust
let value = serde_json::json!({});
let missing: &serde_json::Value =
    value.get("missing").unwrap_or_default();
assert!(missing.is_null());
```

This is useful for read-only fallback behavior. It does not insert a value
into the source object.

### Reuse static raw JSON literals

With the `raw_value` feature enabled, `RawValue::NULL`, `RawValue::TRUE`, and
`RawValue::FALSE` provide static raw fragments (since `serde_json` 1.0.134):

```rust
use serde_json::value::RawValue;

let raw: &'static RawValue = RawValue::NULL;
assert_eq!(raw.get(), "null");
```

Use these constants instead of allocating or parsing a boxed `RawValue` for
one of the three JSON literals.

### Sort object keys deterministically

Since `serde_json` 1.0.129:

- `Map::sort_keys()` sorts one object.
- `Value::sort_all_objects()` recursively sorts all objects in a tree.

```rust
let mut value = serde_json::json!({
    "z": {"second": 2, "first": 1},
    "a": 0,
});
value.sort_all_objects();
assert_eq!(
    value.to_string(),
    r#"{"a":0,"z":{"first":1,"second":2}}"#,
);
```

These methods matter when the `preserve_order` feature is enabled. Without
that feature, object maps are already maintained in sorted order and
`sort_keys()` does no work.

## Upgrade checklist

1. Keep `serde` with `derive` enabled anywhere derives are used.
2. Use `serde_core` directly only for intentionally trait-only crates.
3. Treat diagnostic paths through `serde_core` as the regular Serde traits.
4. Pair `serde_json` 1.0.145 or newer with Serde 1.0.220 or newer.
5. Convert enum object keys to explicit string representations.
6. Recheck exact-number snapshots when `arbitrary_precision` is enabled.
7. Prefer direct `Map` deserialization over JSON text round trips.
8. Sort objects before deterministic output when `preserve_order` is used.

