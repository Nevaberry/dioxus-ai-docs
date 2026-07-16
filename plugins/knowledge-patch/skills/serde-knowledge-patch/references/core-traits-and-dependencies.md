# Core Traits and Dependencies

## The trait-only `serde_core` crate

The `serde_core` crate introduced in the `1.0.220-serde-core` coverage batch
contains Serde's core traits and their supporting APIs:

- `Serialize` and `Serializer`
- `Deserialize` and `Deserializer`
- the `ser` and `de` modules used by handwritten implementations

It deliberately contains no derive-macro support. This separation lets a
crate depend on the trait layer without pulling in the rest of `serde`, but
it changes neither the meaning of the traits nor the implementation that a
format crate expects.

### Suitable direct dependencies

Use `serde_core` directly for libraries that only mention traits in generic
bounds:

```toml
[dependencies]
serde_core = "1.0.220"
```

```rust
pub fn require_serializable<T: serde_core::Serialize>(_: &T) {}
```

It is also suitable when all required `Serialize` or `Deserialize`
implementations are handwritten with the `ser` and `de` APIs.

### When to retain `serde`

Any crate using `#[derive(Serialize)]` or `#[derive(Deserialize)]` must
continue to depend on `serde` with derive support:

```toml
[dependencies]
serde = { version = "1.0.220", features = ["derive"] }
```

```rust
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct Message {
    body: String,
}
```

`serde` re-exports the same core traits and remains the safe default for
applications and libraries that do not specifically need a trait-only
dependency.

## Understanding diagnostic paths

Because the traits originate in `serde_core`, an unsatisfied trait bound can
be rendered with a path such as:

```text
T: serde_core::ser::Serialize
```

This is the ordinary Serde serialization trait. The path does not imply that
the affected dependency has a distinct `serde_core` integration or that the
type needs a second serialization implementation.

Use the same remedies as for any missing Serde implementation:

- Derive `serde::Serialize` or `serde::Deserialize` for a local type.
- Enable the `derive` feature on `serde` if the derive macro is unavailable.
- Enable a dependency's `serde` feature when its Serde implementations are
  feature-gated.
- Write the corresponding trait implementation by hand when deriving is not
  appropriate.

Do not search for a separate “serde_core support” switch solely because the
diagnostic prints a `serde_core` path.

