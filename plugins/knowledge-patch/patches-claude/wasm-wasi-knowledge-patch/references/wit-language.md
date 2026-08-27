# WIT Language and Composition

Use this reference when declaring interface types, resources, packages, and
worlds. The core syntax guidance comes from `wasi-0.2-guide`; map and interface
instance additions come from `wasi-0.3.1`.

## Identifiers and documentation comments

WIT identifiers are ASCII kebab-case. Every hyphen-delimited word must be
entirely lowercase or entirely uppercase. Prefix a keyword with `%` when using
it as a name.

`///` and `/** ... */` document the item that follows. Ordinary `/* ... */`
comments may be nested.

```wit
/// An interface whose escaped name would otherwise be a keyword.
interface %interface {
    HTTP-request: func();
}
```

## Result shorthands

Either payload in `result<T, E>` may be omitted:

- `result<T>` has no error payload.
- `result<_, E>` has no success payload.
- Bare `result` has neither payload.

```wit
interface results {
    type print-result = result<_, u32>;
    type signal-result = result;
}
```

## Floating-point NaNs

Although `f32` and `f64` otherwise describe IEEE 754 values, WIT logically has
one `nan` value. Do not rely on a NaN's bit-level payload surviving an interface
crossing.

## Generic types

User-defined records and variants cannot declare type parameters. Only WIT's
built-in generic types, including `list<T>`, `option<T>`, and `result<T, E>`,
can be parameterized.

WIT also supports `map<K, V>` for dynamic key-value collections. Use it instead
of encoding a map as `list<tuple<K, V>>` when targeting WASI 0.3.1-compatible
runtimes and toolchains.

```wit
type labels = map<string, string>;
```

## Resources, ownership, and members

A resource may contain at most one `constructor`. An ordinary method receives
an implicit borrowed `self`; a `static func` member has no `self`.

`borrow<resource>` loans the handle only for the duration of the call. Passing
an owned resource handle transfers responsibility for eventually destroying
it.

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
one type. The same form works across `.wit` files in one package.

```wit
interface types { type point = tuple<u32, u32>; }
interface canvas {
    use types.{point};
    draw: func(at: point);
}
```

## Composing worlds

A world may import or export a complete interface or an individual function.
It may declare an interface inline. `include` acquires all imports and exports
from another world.

Name an external interface with `package/interface` syntax. Package resolution
is deliberately delegated to tooling.

```wit
world diagnostics { export report: func(message: string); }
world proxy {
    export wasi:http/incoming-handler;
    import wasi:http/outgoing-handler;
    include diagnostics;
}
```

## Multi-file packages

A package ID has the form `namespace:name`, optionally followed by `@semver`.
A package may span peer `.wit` files in one directory. Only one file needs the
package declaration; any repeated declarations must match.

```wit
package documentation:http@1.0.0;
```

## Multiple instances of one interface

WASI 0.3.1 interfaces may depend on the Component Model's `implements` feature.
It lets a component import or export multiple instances of the same interface
under different names, such as remote and in-memory stores implementing one
key-value interface. Runtimes and toolchains must support `implements` to be
compatible with WASI 0.3.1 or later.
