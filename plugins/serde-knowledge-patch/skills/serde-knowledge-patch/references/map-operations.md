# Map Operations

## `Map::sort_keys` and `Value::sort_all_objects` (serde_json 1.0.129)

Sort JSON map keys alphabetically in place. `sort_all_objects` recurses into all nested objects within a `Value`.

```rust
use serde_json::{Map, Value, json};

// Sort top-level keys
let mut map: Map<String, Value> = serde_json::from_str(r#"{"z":1,"a":2}"#)?;
map.sort_keys();
// map is now {"a":2,"z":1}

// Recursively sort all nested objects
let mut value = json!({"z": {"c": 1, "a": 2}, "a": 3});
value.sort_all_objects();
// {"a":3,"z":{"a":2,"c":1}}
```

Key details:
- `sort_keys()` is on `Map<String, Value>` — sorts only the top-level keys
- `sort_all_objects()` is on `Value` — recursively sorts keys in all nested objects
- Both sort alphabetically (lexicographic order)
- Sorting is in-place; no new allocation

Common use cases:
- Deterministic JSON output for hashing or content-addressing
- Snapshot testing where key order must be stable
- Diffing JSON documents

---

## `Map<String, Value>` as `Deserializer` (serde_json 1.0.131)

Both `Map<String, Value>` and `&Map<String, Value>` implement `Deserializer` and `IntoDeserializer`. This lets you deserialize a struct directly from a map without first converting to `Value`.

```rust
use serde::Deserialize;
use serde_json::{Map, Value};

#[derive(Deserialize)]
struct Config {
    name: String,
    count: u32,
}

let map: Map<String, Value> = serde_json::from_str(r#"{"name":"x","count":5}"#)?;

// Deserialize from owned map (consumes the map)
let config = Config::deserialize(map)?;

// Or from a reference (borrows the map)
let map2: Map<String, Value> = serde_json::from_str(r#"{"name":"y","count":10}"#)?;
let config2 = Config::deserialize(&map2)?;
// map2 is still usable here
```

This is useful when:
- You've already parsed JSON into a `Map` and want to extract typed structs
- You're processing dynamic JSON where some fields are known structs and others are arbitrary
- You want to avoid the overhead of serializing back to `Value` then deserializing

---

## `FromStr` for `Map<String, Value>` (serde_json 1.0.143)

`Map<String, Value>` implements `FromStr`, so you can parse a JSON object string directly into a map using `.parse()`.

```rust
use serde_json::{Map, Value};

let map: Map<String, Value> = r#"{"a":1,"b":"hello"}"#.parse()?;
assert_eq!(map["a"], json!(1));
```

This is equivalent to `serde_json::from_str::<Map<String, Value>>(s)` but more ergonomic. Returns an error if the JSON is not an object at the top level.
