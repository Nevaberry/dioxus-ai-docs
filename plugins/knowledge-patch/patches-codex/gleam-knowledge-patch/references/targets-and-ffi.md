# Targets and FFI

## External declarations and source files

### Fallback function bodies

An external function may also have a Gleam body. The external implementation
is used when one exists for the current target; otherwise the Gleam body runs:

```gleam
import gleam/list

@external(erlang, "lists", "reverse")
pub fn reverse(items: List(a)) -> List(a) {
  list.reverse(items)
}
```

### Target definitions for external types

External types accept target-specific `@external` definitions (since 1.14.0),
so Erlang type specifications and TypeScript declarations can use a precise
foreign type instead of `any`:

```gleam
@external(erlang, "erlang", "map")
@external(javascript, "../dict.d.mts", "Dict")
pub type Dict(key, value)
```

### Source locations and extensions

External Erlang, Elixir, JavaScript, and other source files may live in
subdirectories of `src/` or `test/` (since 1.7.0), not just at their roots.

JavaScript external files may use `.mjs`, `.cjs`, `.mts`, `.cts`, `.jsx`, and
`.tsx`. CommonJS `.cjs` support arrived in 1.12.0; the TypeScript
and JSX extensions were added in 1.16.0 for runtimes that consume them
directly.

## Erlang and Elixir interop

### Call Elixir through the Erlang target

Use `@external(erlang, ...)` for an Elixir function and include the VM's
implicit `Elixir.` module prefix. Public functions are callable; macros are
not.

```gleam
@external(erlang, "Elixir.Pokemon", "badge_count")
pub fn pokemon_badge_count() -> Int
```

### Match BEAM runtime representations

Foreign code must produce the exact representation Gleam expects:

- `String` is a UTF-8 binary, not a character list.
- Lists must be proper lists.
- `Nil` is the atom `nil`.
- `Result` is `{ok, Value}` or `{error, Value}`, not a bare atom.
- A fieldless custom-type variant is a snake-case atom.
- A variant with fields is a tagged tuple.
- `Dict` is an Erlang map.

```erlang
guest
{super_user, 11}
{ok, 2}
#{<<"a"/utf8>> => 1}
```

The compiler emits an Erlang header with record definitions for custom-type
variants. Erlang can include it directly; Elixir can consume it through
`Record`.

### Generated Erlang documentation

Generated Erlang includes OTP 27 `-doc` attributes (since 1.8.0), exposing
Gleam function documentation to BEAM tooling and Erlang/Elixir REPL helpers.
The generated code remains compatible with older OTP versions.

### OTP application startup

`erlang.application_start_module` names an OTP application-behaviour module.
Use Erlang atom notation, where a slash in a Gleam module becomes `@`.
`erlang.extra_applications` lists OTP applications that must start in addition
to those supplied by dependencies.

```toml
[erlang]
application_start_module = "my_project@application"
extra_applications = ["inets", "ssl"]
```

## Erlang distribution

### Relocatable shipments

`gleam export erlang-shipment` creates a relocatable directory. Shipments
contain entrypoint scripts for every platform regardless of the build host
(since 1.10.0). Their launchers forward POSIX exit signals to the program
(since 1.11.0), allowing clean termination handling.

### Single-file escripts

`gleam export escript` builds an Erlang-target project, verifies its `main`,
and writes one runnable escript (since 1.17.0):

```sh
gleam export escript
./my_project
```

The output can move to any machine with Erlang installed.

## JavaScript module paths and representations

### Resolve external paths from the declaring source

A local JavaScript external module path is resolved relative to the Gleam file
containing the declaration. Bare package specifiers are accepted, but Gleam
does not install or manage their npm dependencies.

```gleam
// src/my_app.gleam loads src/my_app/pokemon.mjs
@external(javascript, "./my_app/pokemon.mjs", "badge_count")
pub fn pokemon_badge_count() -> Int
```

### Import compiled Gleam by generated path

Each compiled Gleam module is an ES module at its source-shaped path with an
`.mjs` extension. Output packages sit beside one another, so an external module
that imports a dependency ascends out of its own package directory and enters
the dependency directory:

```javascript
// From src/wibble/wobble.mjs
import * as option from "../../gleam_stdlib/gleam/option.mjs";
```

### Match JavaScript runtime values

- A Gleam `Int` is a whole JavaScript number; both numeric types use JS
  numbers, but Gleam's numeric constraints still apply.
- `Nil` is `undefined`.
- A tuple is represented as a JavaScript array but is an immutable Gleam
  value. Do not mutate it through indexing or array methods.

### Construct prelude values through generated APIs

Import the virtual prelude from `src/gleam.mjs`. Build and inspect lists,
results, and bit arrays with its supported constructors, predicates, and
accessors:

```javascript
import {
  BitArray$BitArray,
  List$Empty,
  List$NonEmpty,
  Result$Ok,
} from "../gleam.mjs";

const bytes = BitArray$BitArray(new Uint8Array([30, 56, 10]));
const one = List$NonEmpty(1, List$Empty());
const ok = Result$Ok(2);
```

Use `List$isEmpty`, `List$isNonEmpty`, `List$NonEmpty$first`, and
`List$NonEmpty$rest` for lists. Results use `Result$isOk`, `Result$isError`,
`Result$Ok$0`, and `Result$Error$0`.

### Use compiled functions for dictionaries

`Dict` has no special JavaScript construction API. Convert a JavaScript array
to a Gleam list and call compiled `gleam/dict.from_list`:

```javascript
import { from_list as list_to_dict } from "../gleam_stdlib/gleam/dict.mjs";
import { to_list as array_to_list } from "../gleam_stdlib/gleam/javascript/array.mjs";

const ages = list_to_dict(array_to_list([["Ada", 1]]));
```

## Generated JavaScript APIs

### Custom-type constructors and accessors

Generated modules export supported custom-type constructor, predicate, and
field-access functions (since 1.13.0). Use them instead of compiler-internal
object layouts:

```javascript
const teacher = Person$Teacher("Joe Armstrong", "Computer Science");
const isTeacher = Person$isTeacher(teacher);
const subject = Person$Teacher$subject(teacher);
const name = Person$name(teacher);
```

### Bit-array predicates and data access

Generated JavaScript exposes `BitArray$isBitArray` and
`BitArray$BitArray$data` (since 1.15.0). Generated TypeScript predicates return
`value is TypeName`, enabling control-flow narrowing.

```javascript
if (BitArray$isBitArray(value)) {
  return BitArray$BitArray$data(value);
}
```

### JSDoc and declarations

Gleam documentation comments compile to JSDoc in JavaScript output (since
1.12.0), allowing JavaScript editors to display them. Enable TypeScript
declarations with `javascript.typescript_declarations`.

## JavaScript configuration and debugging

### Runtime and Deno permissions

`javascript.runtime` accepts `node`, `deno`, or `bun` and defaults to Node.
Deno's `allow_env`, `allow_net`, `allow_read`, `allow_run`, and `allow_write`
accept booleans or allowlists. `allow_all`, `allow_ffi`, `allow_hrtime`, and
`allow_sys` are booleans.

```toml
[javascript]
typescript_declarations = true
runtime = "deno"

[javascript.deno]
allow_env = ["DATABASE_URL"]
allow_net = ["example.com:443"]
allow_read = ["./database.sqlite"]
```

### Source maps

Set `javascript.source_maps = true` to emit maps for generated JavaScript
(since 1.16.0). Browser and runtime debuggers then report original Gleam source
locations in stack traces and breakpoints. Serve each `.map` file beside its
generated JavaScript.

## Numeric and bit-array target differences

### Float edge behavior

Both targets use 64-bit floats. JavaScript overflow yields `Infinity` or
`-Infinity` and can produce `NaN`; BEAM overflow raises and has neither
infinities nor NaN. Gleam defines float division by zero to return zero rather
than overflow.

### JavaScript bit-array capabilities

JavaScript bit arrays support unaligned segments and dynamic sizes (since
1.9.0), the `unit` option and 16-bit floats (since 1.10.0), and UTF-16/UTF-32
segments (since 1.11.0). A float literal implies a float segment:

```gleam
<<1.11>>
<<1.11:float>>
```

Extracting an integer wider than 52 bits in a JavaScript bit-array pattern
warns that only the first 52 bits are retained (since 1.16.0). Use a `bytes`
segment when all bits are required.

In 1.18.0, JavaScript 16-bit floats correctly handle fractional carry and
round exact halfway cases to even. A zero-sized segment contributes nothing
instead of a zero byte, which is essential for exact protocol output.
