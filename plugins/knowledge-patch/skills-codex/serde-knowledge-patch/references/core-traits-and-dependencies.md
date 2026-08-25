# Core Traits and Dependencies

## Choose the dependency boundary

### Trait-only serde_core crate (`1.0.220-serde-core`)

`serde_core` contains Serde's `Serialize`, `Deserialize`, `Serializer`, and
`Deserializer` traits. Use it directly only when a crate needs those traits as
bounds or provides handwritten implementations without derive macros.

```toml
[dependencies]
serde_core = "1.0.220"
```

```rust
fn require_serializable<T: serde_core::Serialize>(_: &T) {}
```

The direct dependency communicates that the crate needs Serde's trait layer,
not its derive support.

### Keep serde for derives

`serde_core` does not support `#[derive(Serialize)]` or
`#[derive(Deserialize)]`. A crate that derives either trait must continue to
depend on `serde`, which re-exports the same traits.

```rust
#[derive(serde::Serialize, serde::Deserialize)]
struct Record {
    id: u64,
}
```

Do not replace `serde` with `serde_core` merely because dependency resolution
or a compiler diagnostic begins showing `serde_core` paths.

## Diagnose exposed serde_core paths

Format crates that use `serde_core` can report an error such as:

```text
T: serde_core::ser::Serialize
```

Read this as the ordinary Serde `Serialize` bound. The path identifies where
the shared trait is defined; it does not describe a different serialization
contract.

For a local type, derive or manually implement `serde::Serialize`:

```rust
#[derive(serde::Serialize)]
struct Event {
    sequence: u64,
}
```

For a type owned by another crate, enable that crate's existing `serde`
feature when it provides one.

Do not look for a special `serde_core` compatibility feature unless the
dependency documents one. Fix the same missing implementation or feature that
would have caused an unsatisfied `serde::Serialize` bound.

## Remove the integer-128 compatibility wrapper

### serde_if_integer128! is deprecated (since 1.0.221)

Serde 1.0.221 deprecates `serde_if_integer128!`. Invoking the macro can produce
deprecation warnings, so remove existing calls and avoid new ones.

Search compatibility modules, macro definitions, and generated sources if the
warning is not emitted directly from handwritten code:

```text
serde_if_integer128!
```

The macro is an obsolete compatibility wrapper. Remove the wrapper rather than
suppressing its deprecation warning.

## Dependency review checklist

- Does the crate derive `Serialize` or `Deserialize`? Keep `serde`.
- Does it only name traits in bounds or handwritten implementations?
  `serde_core` may be appropriate.
- Does an error mention `serde_core::ser::Serialize`? Fix the ordinary Serde
  implementation or the foreign dependency's `serde` feature.
- Does the source invoke `serde_if_integer128!`? Remove the deprecated wrapper.
