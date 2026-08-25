---
name: serde-knowledge-patch
description: Serde
version: 1.0.220
license: MIT
metadata:
  author: Nevaberry
---


# Serde Knowledge Patch

Use this skill when updating Serde or `serde_json` dependencies, resolving
trait-bound errors, migrating deprecated compatibility code, or working with
JSON object maps and values.

## Reference index

| Reference | Topics |
| --- | --- |
| [Core traits and dependencies](references/core-traits-and-dependencies.md) | `serde` versus `serde_core`, derive support, trait-path diagnostics, deprecated integer compatibility macro |
| [JSON compatibility and values](references/json-compatibility-and-values.md) | Dependency floors, enum object keys, arbitrary-precision output, map parsing and deserialization, borrowed defaults, raw literals, key sorting |

## Quick reference: deprecations and compatibility changes

### Remove `serde_if_integer128!`

Serde 1.0.221 deprecates `serde_if_integer128!`. Remove existing invocations
and do not add new ones; invoking the compatibility wrapper can produce a
deprecation warning.

See [Core traits and dependencies](references/core-traits-and-dependencies.md)
for the batch attribution and migration guidance.

### Convert non-string enum object keys before serialization

As of `serde_json` 1.0.150, JSON object serialization rejects enum keys whose
Serde representation is not a string. Convert data-carrying or otherwise
non-string enum keys into explicit strings before serializing the object.

Do not rely on a non-string enum representation being accepted as an object
key.

### Keep Serde new enough for `serde_json`

`serde_json` 1.0.145 and newer require Serde 1.0.220 or newer. Upgrade the two
dependencies together:

```toml
[dependencies]
serde = "1.0.220"
serde_json = "1.0.145"
```

If Serde must stay below 1.0.220, keep `serde_json` below 1.0.145.

### Recheck exact arbitrary-precision output

With `arbitrary_precision` enabled, `serde_json` 1.0.149 aligns number strings
with `zmij` formatting. Values remain numerically equivalent, but the exact
text can differ. Recheck snapshots, signatures, hashes, and other
byte-for-byte consumers during an upgrade.

## Quick reference: core traits and dependencies

### Choose `serde` when deriving traits

`serde_core` contains the `Serialize`, `Deserialize`, `Serializer`, and
`Deserializer` traits, but it does not support derives. Crates that use
`#[derive(Serialize, Deserialize)]` must continue to depend on `serde`, which
re-exports the same traits:

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

### Use `serde_core` only for trait-only dependencies

Depend directly on `serde_core` when a crate only needs Serde traits for
bounds or handwritten implementations:

```toml
[dependencies]
serde_core = "1.0.220"
```

```rust
fn require_serializable<T: serde_core::Serialize>(_: &T) {}
```

Do not switch a crate that uses derives from `serde` to `serde_core`.

### Treat `serde_core` diagnostic paths as ordinary Serde traits

A format crate can report a failed bound such as:

```text
T: serde_core::ser::Serialize
```

For a local type, derive `serde::Serialize`. For a foreign type, enable the
dependency's existing `serde` feature. The path identifies the ordinary Serde
trait and does not mean the type needs a separate serialization system.

## Quick reference: JSON maps and values

### Parse object text directly into a map

Since `serde_json` 1.0.143, `Map<String, Value>` implements `FromStr`, so an
object can be parsed with `.parse()`:

```rust
use serde_json::{Map, Value};

let object: Map<String, Value> =
    r#"{"enabled":true}"#.parse().unwrap();
assert_eq!(object.get("enabled"), Some(&Value::Bool(true)));
```

There is no need to parse a `Value` first and then extract its object map.

### Deserialize typed data directly from a map

Since `serde_json` 1.0.131, both `Map<String, Value>` and
`&Map<String, Value>` implement `Deserializer` and `IntoDeserializer`.
Decode typed data from the existing map without wrapping it in
`Value::Object` or converting it back to JSON text:

```rust
use serde::Deserialize;
use serde_json::{Map, Value};

#[derive(Deserialize)]
struct Config {
    enabled: bool,
}

let mut map = Map::new();
map.insert("enabled".into(), Value::Bool(true));
let config = Config::deserialize(map).unwrap();
assert!(config.enabled);
```

Use the borrowed map implementation when the caller must retain the map.

### Default a missing borrowed value to JSON null

Since `serde_json` 1.0.142, `&Value` implements `Default`. A missing borrowed
value can therefore fall back to a shared JSON null without allocation or a
source mutation:

```rust
use serde_json::{json, Value};

let document = json!({});
let missing: &Value = document.get("missing").unwrap_or_default();
assert!(missing.is_null());
```

### Reuse static raw JSON literals

Since `serde_json` 1.0.134, `RawValue` provides associated constants for the
JSON literals `null`, `true`, and `false`:

```rust
use serde_json::value::RawValue;

let raw: &'static RawValue = RawValue::NULL;
assert_eq!(raw.get(), "null");
```

Use these constants when one of those raw fragments is needed without
allocation or parsing.

### Sort keys in place when output order must be deterministic

Since `serde_json` 1.0.129, `Map::sort_keys()` sorts one object and
`Value::sort_all_objects()` recursively sorts every object in a JSON tree:

```rust
let mut value = serde_json::json!({
    "z": {"b": 1, "a": 2},
    "a": 0,
});
value.sort_all_objects();
```

Use the recursive method when nested output also needs deterministic key
order.

## Upgrade checklist

1. Remove uses of the deprecated `serde_if_integer128!` wrapper.
2. Convert enum object keys with non-string representations to explicit strings.
3. Pair `serde_json` 1.0.145 or newer with Serde 1.0.220 or newer.
4. Recheck exact number text when `arbitrary_precision` is enabled.
5. Keep `serde` with derive support in crates that derive Serde traits.
6. Use `serde_core` directly only for intentional trait-only dependencies.
7. Resolve `serde_core` trait errors as ordinary Serde implementation errors.
8. Prefer direct map parsing and deserialization over intermediate `Value` or text round trips.
9. Use shared null and raw literal constants where their allocation-free behavior fits.
10. Sort the full value tree when nested deterministic object ordering is required.
