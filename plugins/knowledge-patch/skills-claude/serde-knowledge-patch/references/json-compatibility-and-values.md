# JSON Compatibility and Value APIs

## Dependency and serialization compatibility

### Keep Serde at the required dependency floor

`serde_json` 1.0.145 and newer require Serde 1.0.220 or newer. Upgrade Serde
with it:

```toml
[dependencies]
serde = "1.0.220"
serde_json = "1.0.145"
```

If an older Serde version must remain pinned, keep `serde_json` below 1.0.145.

### Convert non-string enum object keys before serialization

As of `serde_json` 1.0.150, serializing a JSON object rejects enum keys whose
Serde representation is not a string. Convert data-carrying or otherwise
non-string enum keys to explicit strings before serialization.

Do not depend on a non-string enum representation being accepted as a JSON
object key.

### Audit textual output from arbitrary-precision numbers

With `arbitrary_precision` enabled, `serde_json` 1.0.149 aligns number strings
with `zmij` formatting. Numerically equivalent output can have different text.

Recheck every byte-for-byte consumer during an upgrade, including:

- snapshots and golden output;
- signatures;
- hashes;
- other exact-text comparisons.

## Parse and deserialize object maps directly

### Parse JSON object text with `FromStr`

Since `serde_json` 1.0.143, `Map<String, Value>` implements `FromStr`. Parse
object text with `.parse()` instead of parsing a `Value` and then extracting
its object:

```rust
use serde_json::{Map, Value};

let object: Map<String, Value> =
    r#"{"enabled":true}"#.parse().unwrap();
assert_eq!(object.get("enabled"), Some(&Value::Bool(true)));
```

### Decode typed data from an existing object map

Since `serde_json` 1.0.131, both `Map<String, Value>` and
`&Map<String, Value>` implement `Deserializer` and `IntoDeserializer`. Decode
typed data directly from a map without wrapping it in `Value::Object` or
converting it back to JSON text:

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

Pass an owned map when it can be consumed. Use the borrowed implementation
when the caller must retain the map.

## Use value and raw-fragment conveniences

### Default a missing borrowed value to JSON null

Since `serde_json` 1.0.142, `&Value` implements `Default`. This makes
`Option<&Value>::unwrap_or_default()` return a shared JSON null without
allocating or modifying the source value:

```rust
use serde_json::{json, Value};

let document = json!({});
let missing: &Value = document.get("missing").unwrap_or_default();
assert!(missing.is_null());
```

This is a read-only fallback; it does not insert a value into the source
object.

### Reuse static raw JSON literals

Since `serde_json` 1.0.134, `RawValue` provides associated constants for
`null`, `true`, and `false`. Use them to avoid allocation or parsing when one
of those raw fragments is needed:

```rust
use serde_json::value::RawValue;

let raw: &'static RawValue = RawValue::NULL;
assert_eq!(raw.get(), "null");
```

The corresponding associated constants cover all three literal values.

## Sort object keys in place

Since `serde_json` 1.0.129:

- `Map::sort_keys()` sorts one object.
- `Value::sort_all_objects()` recursively sorts every object in a JSON tree.

```rust
let mut value = serde_json::json!({
    "z": {"b": 1, "a": 2},
    "a": 0,
});
value.sort_all_objects();
```

Use the recursive form when deterministic key order is required throughout
nested output.
