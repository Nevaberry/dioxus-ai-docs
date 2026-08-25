---
name: serde-knowledge-patch
description: Serde
version: 1.0.220
license: MIT
metadata:
  author: Nevaberry
---


# Serde Knowledge Patch

Use this skill when choosing between `serde` and `serde_core`, diagnosing
Serde trait bounds, upgrading `serde_json`, serializing JSON object keys, or
working with `serde_json::Map`, `Value`, and `RawValue`.

## Reference index

| Reference | Topics |
| --- | --- |
| [Core traits and dependencies](references/core-traits-and-dependencies.md) | `serde` versus `serde_core`, derive support, trait diagnostics, deprecated integer-128 compatibility macro |
| [JSON compatibility and values](references/json-compatibility-and-values.md) | Dependency floor, object keys, arbitrary-precision output, maps, borrowed defaults, raw literals, deterministic sorting |

## Apply this patch

1. Inspect `Cargo.toml` and `Cargo.lock` to establish the selected `serde` and
   `serde_json` versions and enabled features.
2. Keep `serde` as the dependency when code derives `Serialize` or
   `Deserialize`; choose `serde_core` only for deliberately trait-only use.
3. Check the compatibility items before changing either dependency version.
4. Review exact-output consumers when arbitrary-precision numbers are enabled.
5. Prefer direct `Map` and `Value` operations over avoidable JSON text round
   trips.
6. Trust the crate's manifests, code, tests, and observed behavior if they
   conflict with this guidance.

## Critical compatibility actions

### Convert non-string enum object keys to strings

As of `serde_json` 1.0.150, JSON object serialization rejects enum keys whose
Serde representation is not a string. This especially affects data-carrying
or otherwise non-string enum representations.

Convert such keys to explicit strings before serializing the object. Do not
depend on a non-string enum representation being accepted as a JSON property
name.

```rust
use serde::Serialize;
use std::collections::BTreeMap;

#[derive(Serialize)]
enum Key {
    Item(u64),
}

let source = [("item-7".to_owned(), 7)].into_iter().collect::<BTreeMap<_, _>>();
let json = serde_json::to_string(&source).unwrap();
assert_eq!(json, r#"{"item-7":7}"#);
```

See [JSON compatibility and values](references/json-compatibility-and-values.md)
for the affected representation and migration guidance.

### Remove `serde_if_integer128!`

Serde 1.0.221 deprecates `serde_if_integer128!`. Remove existing uses of this
compatibility wrapper and do not introduce new ones, because invoking it can
now emit deprecation warnings.

Search macro definitions, generated code, and compatibility modules when
warnings appear after an update. See
[Core traits and dependencies](references/core-traits-and-dependencies.md).

### Pair recent serde_json with Serde 1.0.220 or newer

`serde_json` 1.0.145 and newer require Serde 1.0.220 or newer. Upgrade the two
dependencies together, or keep `serde_json` below 1.0.145 if the graph must
retain an older Serde.

```toml
[dependencies]
serde = "1.0.220"
serde_json = "1.0.145"
```

After editing the manifest, inspect the lockfile to verify that dependency
resolution did not retain an incompatible Serde version.

## Choose the correct trait crate

### Use serde_core only for trait-only dependencies

`serde_core` contains `Serialize`, `Deserialize`, `Serializer`, and
`Deserializer`. It does not provide
`#[derive(Serialize)]` or `#[derive(Deserialize)]`.

Use it directly when a crate only names traits in bounds or writes
implementations by hand:

```toml
[dependencies]
serde_core = "1.0.220"
```

```rust
fn require_serializable<T: serde_core::Serialize>(_: &T) {}
```

Keep depending on `serde` when the crate derives either trait. `serde`
re-exports the same traits and remains the dependency boundary for derive
users.

### Interpret serde_core diagnostic paths as Serde bounds

A format crate may report an unsatisfied bound such as:

```text
T: serde_core::ser::Serialize
```

This is the ordinary Serde serialization trait. For a local type, derive or
implement `serde::Serialize`. For a foreign type, enable that dependency's
existing `serde` integration feature. A `serde_core` path in the error does
not by itself require adding a second compatibility feature.

## Handle exact JSON output carefully

### Recheck arbitrary-precision number text

With `arbitrary_precision` enabled, `serde_json` 1.0.149 aligns emitted number
strings with `zmij` formatting. Values remain numerically equivalent, but the
serialized spelling can differ.

Revalidate every consumer that compares bytes rather than numeric meaning:

- snapshot and golden-file tests;
- hashes and cache keys;
- signatures and signed payloads;
- byte-for-byte protocol fixtures.

Regenerate expected output only after confirming that the textual change is
acceptable to all consumers.

## Use direct JSON value operations

### Parse object text directly into Map

Since `serde_json` 1.0.143, `Map<String, Value>` implements `FromStr`. Parse an
object with `.parse()` instead of first parsing a `Value` and extracting its
object:

```rust
use serde_json::{Map, Value};

let object: Map<String, Value> =
    r#"{"enabled":true}"#.parse().unwrap();
assert_eq!(object.get("enabled"), Some(&Value::Bool(true)));
```

### Deserialize typed data directly from Map

Since `serde_json` 1.0.131, owned and borrowed object maps implement both
`Deserializer` and `IntoDeserializer`. Decode typed data from the map without
wrapping it in `Value::Object` or serializing it back to text.

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

Pass a borrowed map when the caller needs to retain it.

### Use a shared null for a missing borrowed value

Since `serde_json` 1.0.142, `&Value` implements `Default`. Therefore
`Option<&Value>::unwrap_or_default()` returns a shared JSON null without
allocating or modifying the source document.

```rust
use serde_json::{json, Value};

let document = json!({});
let missing: &Value = document.get("missing").unwrap_or_default();
assert!(missing.is_null());
```

Use this for read-only fallback behavior, not when a missing member must be
inserted into the object.

### Reuse static raw JSON literals

`RawValue::NULL`, `RawValue::TRUE`, and `RawValue::FALSE` provide static raw
fragments. Use them instead of allocating or parsing one of those literals.

```rust
use serde_json::value::RawValue;

let raw: &'static RawValue = RawValue::NULL;
assert_eq!(raw.get(), "null");
```

### Sort keys at the required depth

Since `serde_json` 1.0.129, `Map::sort_keys()` sorts one object and
`Value::sort_all_objects()` recursively sorts every object in a JSON tree.
Choose the recursive operation when deterministic order is required
throughout nested output.

```rust
let mut value = serde_json::json!({"z": {"b": 1, "a": 2}, "a": 0});
value.sort_all_objects();
assert_eq!(value.to_string(), r#"{"a":0,"z":{"a":2,"b":1}}"#);
```

## Upgrade checklist

1. Keep `serde` wherever derive macros are used.
2. Use `serde_core` directly only for intentional trait-only dependencies.
3. Treat trait paths through `serde_core` as ordinary Serde bounds.
4. Remove `serde_if_integer128!` uses.
5. Match `serde_json` 1.0.145 or newer with Serde 1.0.220 or newer.
6. Convert non-string enum object keys to explicit strings.
7. Recheck exact number output with `arbitrary_precision` enabled.
8. Prefer direct parsing and deserialization through `Map`.
9. Use borrowed defaults and raw literal constants when their fallback
   semantics fit.
10. Sort one object or the whole tree according to the required output scope.
