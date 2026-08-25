# WIT Language and Composition

## Identifiers and documentation (`wasi-0.2-guide`)

WIT identifiers use ASCII kebab-case. Each hyphen-delimited word must be
entirely lowercase or entirely uppercase. Escape a keyword used as a name by
prefixing it with `%`.

`///` and `/** ... */` document the following item. Ordinary `/* ... */`
comments may be nested.

```wit
/// An interface whose escaped name would otherwise be a keyword.
interface %interface {
    HTTP-request: func();
}
```

## Result shorthands

Either payload in `result<T, E>` may be omitted:

- `result<T>` has no error payload;
- `result<_, E>` has no success payload; and
- bare `result` has neither payload.

```wit
interface results {
    type print-result = result<_, u32>;
    type signal-result = result;
}
```

## Floating-point NaNs

Although `f32` and `f64` otherwise represent IEEE 754 values, WIT has one
logical `nan` value. Never depend on the bit-level payload of a NaN surviving
an interface crossing.

## Generic type boundary

User-defined records and variants cannot declare type parameters. Only WIT's
built-in generic types, including `list<T>`, `option<T>`, and `result<T, E>`,
may be parameterized.

## Resource ownership and members

A resource can have at most one `constructor`. An ordinary method receives an
implicit borrowed `self`; a `static func` has no `self`.

`borrow<resource>` loans a handle for the duration of a call. Passing an owned
resource handle instead transfers responsibility for eventually destroying
the resource.

```wit
interface storage {
    resource blob {
        constructor(init: list<u8>);
        read: func(n: u32) -> list<u8>;
        merge: static func(lhs: blob, rhs: blob) -> blob;
    }
}
```

## Reusing interface types

Import types from another interface with
`use interface-name.{type-name, ...}`. Braces are mandatory even when importing
one type. The syntax also works between `.wit` files in the same package.

```wit
interface types { type point = tuple<u32, u32>; }
interface canvas {
    use types.{point};
    draw: func(at: point);
}
```

## World composition

A world may import or export entire interfaces or individual functions,
declare an interface inline, and `include` another world to inherit all its
imports and exports. Refer to an external interface with `package/interface`;
the tooling decides how that package is resolved.

```wit
world diagnostics { export report: func(message: string); }
world proxy {
    export wasi:http/incoming-handler;
    import wasi:http/outgoing-handler;
    include diagnostics;
}
```

## Multi-file packages

A package ID has the form `namespace:name` with an optional `@semver`. A
package can span peer `.wit` files in one directory. Only one file must contain
the declaration; if several files repeat it, every declaration must match.

```wit
package documentation:http@1.0.0;
```

## Multiple instances with `implements` (`wasi-0.3.1`)

The Component Model's `implements` feature lets a component import or export
multiple instances of the same interface under distinct names. For example,
remote and in-memory stores may both implement one key-value interface. A
runtime and toolchain must support this feature to accept WASI 0.3.1 or later.

## First-class maps

Use `map<K, V>` for a dynamic key-value collection instead of encoding it as
`list<tuple<K, V>>`. This type also requires WASI 0.3.1-or-later runtime and
toolchain support.

```wit
type labels = map<string, string>;
```
