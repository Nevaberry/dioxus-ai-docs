# JSON Compatibility and Value APIs

## Dependency compatibility

### Serde version floor

`serde_json` 1.0.145 requires Serde 1.0.220 or newer. A dependency graph
pinned to an older Serde release has two valid upgrade paths:

- update Serde to at least 1.0.220; or
- keep `serde_json` below 1.0.145.

Check lockfiles and workspace-wide version constraints when an apparently
isolated `serde_json` update fails dependency resolution.

## Serialization behavior

### JSON object keys from enums

As of `serde_json` 1.0.150, enum keys whose Serde representation is not a
string are rejected during JSON object serialization. JSON object keys are
strings, so do not rely on a data-carrying or otherwise non-string enum
representation being accepted as a key.

Give such variants an explicit representation that produces the intended
string key. This is especially important for maps keyed by enums with tuple
or struct variants.

### Arbitrary-precision number spelling

In `serde_json` 1.0.149, number strings produced with the
`arbitrary_precision` feature were aligned with `zmij` formatting. An
upgrade can therefore alter the exact serialized spelling without altering
the numeric value.

Audit consumers that compare bytes rather than values, including:

- snapshot and golden-file tests;
- content hashes and signatures;
- caches keyed by serialized bytes; and
- protocols that incorrectly require one numeric spelling.

Prefer semantic numeric comparisons when the spelling is not part of the
actual contract.

## Parsing and deserializing object maps

### `Map<String, Value>` implements `FromStr`

Since `serde_json` 1.0.143, a JSON object can be parsed directly into its map
type with Rust's `.parse()`:

```rust
let object: serde_json::Map<String, serde_json::Value> =
    r#"{"answer":42}"#.parse().unwrap();
assert_eq!(object["answer"], serde_json::json!(42));
```

The target type must be clear from an annotation or surrounding context.

### Object maps are deserializers

Since `serde_json` 1.0.131, both of these types implement Serde's
`Deserializer` and `IntoDeserializer`:

- `serde_json::Map<String, Value>`
- `&serde_json::Map<String, Value>`

Feed a parsed map directly to `Deserialize` without wrapping it in
`Value::Object` and without round-tripping through JSON text:

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

Pass the map by value when it can be consumed. Pass `&map` when it must
remain available to the caller.

## Shared values and raw literals

### Default shared `Value` references

Since `serde_json` 1.0.142, `&serde_json::Value` implements `Default`.
Consequently, `Option<&Value>::unwrap_or_default()` yields a shared JSON
`null` value:

```rust
let value = serde_json::json!({});
let missing: &serde_json::Value = value.get("missing").unwrap_or_default();
assert!(missing.is_null());
```

The fallback is a reference to a default null value; this operation does not
mutate the object or insert a key.

### Static `RawValue` literals

Since `serde_json` 1.0.134, the following associated constants provide
static raw JSON fragments:

- `RawValue::NULL`
- `RawValue::TRUE`
- `RawValue::FALSE`

They require serde_json's `raw_value` feature:

```toml
[dependencies]
serde_json = { version = "1", features = ["raw_value"] }
```

```rust
use serde_json::value::RawValue;

let raw: &'static RawValue = RawValue::NULL;
assert_eq!(raw.get(), "null");
```

Use the constants to avoid allocating or parsing a boxed `RawValue` when a
literal null, true, or false fragment is needed.

## Deterministic object ordering

Since `serde_json` 1.0.129, `Map::sort_keys()` sorts the keys of one object,
while `Value::sort_all_objects()` recursively sorts every object in a JSON
tree:

```rust
let mut value = serde_json::json!({
    "z": {"second": 2, "first": 1},
    "a": 0,
});
value.sort_all_objects();
assert_eq!(value.to_string(), r#"{"a":0,"z":{"first":1,"second":2}}"#);
```

These APIs provide deterministic order when the `preserve_order` feature is
enabled. Without `preserve_order`, object maps are already kept sorted and
`sort_keys()` does no work.
