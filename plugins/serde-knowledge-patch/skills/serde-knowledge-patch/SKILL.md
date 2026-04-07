---
name: serde-knowledge-patch
description: "Serde/serde_json changes since training cutoff (latest: serde 1.0.228 / serde_json 1.0.149) — Map sorting, Map as Deserializer, RawValue constants, Map FromStr. Load before working with serde or serde_json."
version: "1.0.228"
license: MIT
metadata:
  author: Nevaberry
---

# Serde Knowledge Patch

Covers serde_json 1.0.129–1.0.143 (Nov 2024 – Aug 2025). Claude Opus 4.6 knows serde through 1.0.200 and serde_json through 1.0.128.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Map operations | [references/map-operations.md](references/map-operations.md) | `sort_keys`, `sort_all_objects`, `Map` as `Deserializer`, `FromStr` for `Map` |
| RawValue | [references/rawvalue.md](references/rawvalue.md) | `NULL`, `TRUE`, `FALSE` associated constants |

---

## Quick Reference — New serde_json APIs

| API | Version | What it does |
|---|---|---|
| `Map::sort_keys()` | 1.0.129 | Sort map keys alphabetically in place |
| `Value::sort_all_objects()` | 1.0.129 | Recursively sort all nested object keys |
| `Map<String, Value>: Deserializer` | 1.0.131 | Deserialize structs directly from a map |
| `&Map<String, Value>: IntoDeserializer` | 1.0.131 | Use `&map` with `Deserialize::deserialize` |
| `RawValue::NULL` | 1.0.134 | Associated constant for raw `"null"` |
| `RawValue::TRUE` | 1.0.134 | Associated constant for raw `"true"` |
| `RawValue::FALSE` | 1.0.134 | Associated constant for raw `"false"` |
| `Map<String, Value>: FromStr` | 1.0.143 | Parse JSON string into a `Map` via `.parse()` |

---

## Essential Patterns (inline)

### Sort JSON keys — deterministic output

```rust
use serde_json::{Map, Value, json};

// Sort a single map's keys
let mut map: Map<String, Value> = serde_json::from_str(r#"{"z":1,"a":2}"#)?;
map.sort_keys();
// map is now {"a":2,"z":1}

// Recursively sort all nested objects
let mut value = json!({"z": {"c": 1, "a": 2}, "a": 3});
value.sort_all_objects();
// {"a":3,"z":{"a":2,"c":1}}
```

Use `sort_all_objects()` before serializing when you need deterministic JSON output (e.g., for hashing, diffing, or snapshot tests).

### Deserialize struct directly from a Map

```rust
use serde::Deserialize;
use serde_json::{Map, Value};

#[derive(Deserialize)]
struct Config { name: String, count: u32 }

let map: Map<String, Value> = serde_json::from_str(r#"{"name":"x","count":5}"#)?;
let config = Config::deserialize(&map)?;
```

Avoids the round-trip through `Value` when you already have a `Map`. Works with both owned `Map` and `&Map`.

### RawValue associated constants

```rust
use serde_json::value::RawValue;

let null: &RawValue = RawValue::NULL;   // raw "null"
let t: &RawValue = RawValue::TRUE;      // raw "true"
let f: &RawValue = RawValue::FALSE;     // raw "false"
```

Useful when constructing partial JSON responses or default values without allocation.

### Parse JSON string directly into a Map

```rust
use serde_json::Map;

let map: Map<String, serde_json::Value> = r#"{"a":1}"#.parse()?;
```

Shorthand for `serde_json::from_str` when you know the top-level value is an object.
