# Type System & Patterns

## Record updates can change type parameters (1.7)

Record update syntax now works when the type parameter changes, thanks to monomorphised code generation.

```gleam
pub type Named(element) {
  Named(name: String, value: element)
}

pub fn replace_value(data: Named(a), replacement: b) -> Named(b) {
  Named(..data, value: replacement)
}
```

## Variant deprecation (1.7)

`@deprecated` can now be applied to individual custom type variants, not just functions and types.

```gleam
pub type HashAlgorithm {
  @deprecated("Please upgrade to another algorithm")
  Md5
  Sha224
  Sha512
}
```

## Record update syntax for constants (1.14)

Record update syntax now works in `const` definitions, allowing constant records to be built from other constants.

```gleam
pub const base = HttpConfig(host: "0.0.0.0", port: 8080, tls: False)
pub const dev = HttpConfig(..base, port: 4000)
pub const prod = HttpConfig(..base, port: 80, tls: True)
```

## String concatenation in case guards (1.15)

The `<>` operator can now be used in case expression guard clauses.

```gleam
case message {
  action if version <> ":" <> action == "v1:delete" -> handle_delete()
  _ -> ignore_command()
}
```
