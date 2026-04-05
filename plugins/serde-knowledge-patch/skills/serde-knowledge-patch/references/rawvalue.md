# RawValue

## Associated Constants (serde_json 1.0.134)

`RawValue` now has associated constants for common JSON literals, avoiding the need to construct them at runtime:

```rust
use serde_json::value::RawValue;

let null: &RawValue = RawValue::NULL;   // raw "null"
let t: &RawValue = RawValue::TRUE;      // raw "true"
let f: &RawValue = RawValue::FALSE;     // raw "false"
```

These are `&'static RawValue` references — no heap allocation, no parsing.

### When to use

- Default values in structs that use `RawValue` fields:

```rust
use serde::{Deserialize, Serialize};
use serde_json::value::RawValue;

#[derive(Serialize, Deserialize)]
struct Response {
    #[serde(default = "default_data")]
    data: Box<RawValue>,
}

fn default_data() -> Box<RawValue> {
    RawValue::NULL.to_owned()
}
```

- Building partial JSON responses where you want to embed literal null/true/false without serialization overhead
- Conditional JSON construction in APIs that pass through raw JSON
