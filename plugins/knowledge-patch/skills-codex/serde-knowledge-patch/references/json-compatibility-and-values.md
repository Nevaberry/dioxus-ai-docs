# JSON Compatibility and Value APIs

## Check dependency compatibility

### Respect the Serde dependency floor

`serde_json` 1.0.145 and newer require Serde 1.0.220 or newer. When upgrading,
allow both packages to resolve to compatible versions:

```toml
[dependencies]
serde = "1.0.220"
serde_json = "1.0.145"
```

If the application must keep Serde below 1.0.220, keep `serde_json` below
1.0.145 as well. Inspect `Cargo.lock` after resolution rather than assuming a
manifest edit selected the intended pair.

## Migrate incompatible JSON output

### Convert non-string enum object keys

As of `serde_json` 1.0.150, serializing a JSON object rejects enum keys whose
Serde representation is not a string. Data-carrying variants are a common
source of non-string representations.

Convert the key into the exact string representation required by the wire
format before inserting it into a map:

```rust
use std::collections::BTreeMap;

let object = [("item-42".to_owned(), "ready")]
    .into_iter()
    .collect::<BTreeMap<_, _>>();
let json = serde_json::to_string(&object).unwrap();
assert_eq!(json, r#"{"item-42":"ready"}"#);
```

Do not rely on a non-string enum representation being coerced into a JSON
property name.

### Recheck arbitrary-precision number spelling

With `arbitrary_precision` enabled, `serde_json` 1.0.149 aligns serialized
number strings with `zmij` formatting. The values remain numerically
equivalent, but exact text can change across the upgrade.

Audit consumers that treat serialized JSON as bytes rather than as data:

- snapshots and golden files;
- hashes, fingerprints, and cache keys;
- digital signatures;
- protocol fixtures and exact-output assertions.

Confirm that the new spelling is acceptable before updating expected bytes.

## Work directly with object maps

### Parse an object with FromStr

Since `serde_json` 1.0.143, `Map<String, Value>` implements `FromStr`. Parse
object text directly with `.parse()`:

```rust
use serde_json::{Map, Value};

let object: Map<String, Value> =
    r#"{"enabled":true}"#.parse().unwrap();
assert_eq!(object.get("enabled"), Some(&Value::Bool(true)));
```

This avoids parsing a general `Value` and then extracting its object.

### Deserialize typed data from an owned map

Since `serde_json` 1.0.131, `Map<String, Value>` implements `Deserializer` and
`IntoDeserializer`. Pass an owned map directly to `Deserialize`:

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

There is no need to wrap the map in `Value::Object` or serialize it back to
JSON text.

### Deserialize without consuming a map

`&Map<String, Value>` also implements `Deserializer` and `IntoDeserializer`.
Use a borrowed map when the caller must retain the object after decoding:

```rust
use serde::Deserialize;
use serde_json::{Map, Value};

#[derive(Deserialize)]
struct Config {
    enabled: bool,
}

let mut map = Map::new();
map.insert("enabled".into(), Value::Bool(true));
let config = Config::deserialize(&map).unwrap();
assert!(config.enabled);
assert_eq!(map.get("enabled"), Some(&Value::Bool(true)));
```

## Use value-level conveniences

### Default a missing borrowed value to JSON null

Since `serde_json` 1.0.142, `&Value` implements `Default`. A missing optional
reference can therefore fall back to a shared JSON null:

```rust
use serde_json::{json, Value};

let document = json!({});
let missing: &Value = document.get("missing").unwrap_or_default();
assert!(missing.is_null());
```

This does not allocate and does not insert a member into `document`. Use it
only when a read-only null fallback has the intended semantics.

### Reuse static raw literals

Since `serde_json` 1.0.134, `RawValue` exposes constants for the JSON literals
`null`, `true`, and `false`:

```rust
use serde_json::value::RawValue;

let null: &'static RawValue = RawValue::NULL;
let yes: &'static RawValue = RawValue::TRUE;
let no: &'static RawValue = RawValue::FALSE;
assert_eq!((null.get(), yes.get(), no.get()), ("null", "true", "false"));
```

Use these constants instead of parsing or allocating one of the three raw
fragments.

### Sort object keys in place

Since `serde_json` 1.0.129, `Map::sort_keys()` sorts one object in place. Use it
when only a specific map needs deterministic key order:

```rust
use serde_json::{Map, Value};

let mut map = Map::new();
map.insert("z".into(), Value::Null);
map.insert("a".into(), Value::Null);
map.sort_keys();
```

`Value::sort_all_objects()` recursively sorts every object in an entire JSON
tree. Use the recursive operation when nested objects are also part of the
deterministic output contract:

```rust
let mut value = serde_json::json!({"z": {"b": 1, "a": 2}, "a": 0});
value.sort_all_objects();
assert_eq!(value.to_string(), r#"{"a":0,"z":{"a":2,"b":1}}"#);
```

## JSON upgrade checklist

- Match `serde_json` 1.0.145 or newer with Serde 1.0.220 or newer.
- Convert non-string enum object keys to explicit strings.
- Revalidate byte-sensitive consumers with `arbitrary_precision` enabled.
- Parse object text directly into `Map<String, Value>` when appropriate.
- Deserialize from owned or borrowed maps without a JSON text round trip.
- Use a shared null default only for read-only missing-value behavior.
- Reuse the three `RawValue` constants for static literal fragments.
- Choose `sort_keys()` for one map or `sort_all_objects()` for a full tree.
