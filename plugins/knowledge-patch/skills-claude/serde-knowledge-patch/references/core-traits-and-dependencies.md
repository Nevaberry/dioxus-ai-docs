# Core Traits and Dependencies

## Choose the dependency by how the crate uses Serde

Batch attribution: `1.0.220-serde-core`.

`serde_core` contains Serde's `Serialize`, `Deserialize`, `Serializer`, and
`Deserializer` traits. It does not support `#[derive(Serialize)]` or
`#[derive(Deserialize)]`.

Use `serde_core` directly only when the crate needs trait bounds or handwritten
implementations:

```toml
[dependencies]
serde_core = "1.0.220"
```

```rust
fn require_serializable<T: serde_core::Serialize>(_: &T) {}
```

Continue to depend on `serde` when the crate derives either trait. `serde`
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

Do not replace `serde` with `serde_core` in a crate that uses Serde derives.

## Diagnose trait bounds that expose `serde_core` paths

Batch attribution: `1.0.220-serde-core`.

Format crates that depend on `serde_core` can produce an error like:

```text
T: serde_core::ser::Serialize
```

This is the ordinary Serde trait. Resolve the missing implementation according
to who owns the type:

- For a local type, derive `serde::Serialize`.
- For a foreign type, enable the dependency's existing `serde` feature.

The `serde_core` path in the diagnostic does not indicate that another
compatibility layer is required.

## Remove the deprecated integer compatibility macro

Batch attribution: `1.0.221`.

Serde 1.0.221 deprecates `serde_if_integer128!`. Remove existing uses of this
compatibility wrapper and avoid introducing new uses, because invoking it can
now produce deprecation warnings.

When reviewing an upgrade, search the crate and its local macros for
`serde_if_integer128!` so invocations are not left behind.
