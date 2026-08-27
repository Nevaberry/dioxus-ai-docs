# Targets and FFI

## Generated Erlang and deployments

Since 1.8.0, generated Erlang includes OTP 27 `-doc` attributes, making Gleam
function documentation available to BEAM tooling such as Erlang and Elixir REPL
documentation helpers. Generated code remains compatible with older Erlang/OTP.

Since 1.10.0, `gleam export erlang-shipment` includes entrypoint scripts for
every platform regardless of the build host, allowing a shipment made on one
operating system to launch on another.

Since 1.11.0, programs launched from an Erlang shipment receive POSIX exit
signals and can respond to process termination.

Precompiled Gleam executables are available for ARM64 Windows (since 1.11.0).

Since 1.17.0, `gleam export escript` compiles an Erlang-target project, verifies
a valid `main`, and writes one runnable escript. It can be copied to a machine
with Erlang installed.

```sh
gleam export escript
./my_project
```

## Generated JavaScript and TypeScript

### Documentation and source maps

Since 1.12.0, Gleam documentation comments compile to JSDoc syntax so
JavaScript editors and tools can expose them.

Enable JavaScript source maps with `javascript.source_maps` (since 1.16.0).
They provide original Gleam locations, stack traces, and breakpoints in browser
and runtime debuggers. Serve map files with the generated JavaScript.

```toml
[javascript]
source_maps = true
```

### Custom types and bit arrays

Since 1.13.0, generated JavaScript exports supported functions for constructing
custom-type variants, testing variants, and accessing fields. JavaScript
externals should migrate from compiler-internal representations to these
exports.

```javascript
let teacher = Person$Teacher("Joe Armstrong", "Computer Science");
let is_teacher = Person$isTeacher(teacher);
let subject = Person$Teacher$subject(teacher);
let name = Person$name(teacher);
```

Since 1.15.0, generated JavaScript exposes `BitArray$isBitArray` and
`BitArray$BitArray$data` for recognising and consuming Gleam bit arrays.
Generated TypeScript declarations give type-checking functions a
`value is TypeName` return type, so successful checks narrow the value.

```javascript
import { BitArray$isBitArray, BitArray$BitArray$data } from "../gleam.mjs";

export function bytes(value) {
  if (BitArray$isBitArray(value)) {
    return BitArray$BitArray$data(value);
  }
}
```

### Bit-array capabilities and warnings

- Since 1.9.0, JavaScript bit arrays need not be byte-aligned, and patterns may
  contain dynamically sized segments.
- Since 1.10.0, JavaScript supports the bit-array `unit` option and 16-bit
  floats. A float literal implies a float segment, so `<<1.11>>` and
  `<<1.11:float>>` are equivalent.
- Since 1.11.0, JavaScript supports UTF-16 and UTF-32 bit-array segments.
- Since 1.16.0, extracting an integer wider than 52 bits in a JavaScript
  bit-array pattern warns that only its first 52 bits are retained. Use a
  `bytes` segment when all data is required.

Since 1.18.0, JavaScript 16-bit float segments handle fractional carry and exact
halfway cases correctly, rounding ties to even. A zero-size bit-array segment
contributes nothing rather than adding a zero byte, which matters for exact
protocol output.

## Generated-code compatibility fixes

Gleam 1.18.0 fixes invalid generated code for constant strings used in
bit-array segments. Use 1.18.1 or newer when a referenced constant aliases
another constant inside a bit-array segment, string concatenation, or a clause
guard; 1.18.0 can generate incorrect Erlang for those cases.

## External source files

JavaScript external modules may use `.cjs` for CommonJS (since 1.12.0).
Since 1.16.0, `.mts`, `.cts`, `.jsx`, and `.tsx` are also supported, allowing
runtimes with built-in TypeScript or JSX support to consume them.

## Target-specific external types

Since 1.14.0, external types accept target-specific `@external` annotations.
Generated Erlang type specifications and TypeScript declarations can therefore
use a precise foreign type instead of `any`.

```gleam
@external(erlang, "erlang", "map")
@external(javascript, "../dict.d.mts", "Dict")
pub type Dict(key, value)
```

## Gleam fallback implementations

A function containing both `@external` and a Gleam body uses the external
implementation for a target that provides one and otherwise runs its body.

```gleam
import gleam/list

@external(erlang, "lists", "reverse")
pub fn reverse(items: List(a)) -> List(a) {
  list.reverse(items)
}
```

## Elixir calls from Gleam

Elixir functions use `@external(erlang, ...)`. Include Elixir's implicit
`Elixir.` prefix in the VM module name. Public functions can be called, but
Elixir macros cannot.

```gleam
@external(erlang, "Elixir.Pokemon", "badge_count")
pub fn pokemon_badge_count() -> Int
```

## BEAM runtime representations

Foreign BEAM code must use Gleam's exact representations:

- strings are UTF-8 binaries, not character lists;
- lists must be proper;
- `Nil` is `nil`;
- results are `{ok, Value}` or `{error, Value}`, not bare atoms;
- fieldless custom-type variants are snake-case atoms;
- variants with fields are tagged tuples;
- `Dict` is an Erlang map.

```erlang
guest
{super_user, 11}
{ok, 2}
#{<<"a"/utf8>> => 1}
```

The compiler generates an Erlang header with record definitions for custom-type
variants. Erlang can include the header directly; Elixir can consume it through
`Record`.

## JavaScript external paths

A local external-module path is relative to the Gleam file containing the
declaration. Bare Node module specifiers are accepted, but Gleam does not
install or manage their npm packages.

```gleam
// src/my_app.gleam loads src/my_app/pokemon.mjs
@external(javascript, "./my_app/pokemon.mjs", "badge_count")
pub fn pokemon_badge_count() -> Int
```

## Importing generated modules

Each compiled Gleam module is an ES module at its source-shaped path with a
`.mjs` extension. Build output places packages beside one another, so an import
from a dependency ascends out of the current package directory and enters the
dependency directory.

```javascript
// From src/wibble/wobble.mjs
import * as option from "../../gleam_stdlib/gleam/option.mjs";
```

## JavaScript runtime representations

A Gleam `Int` is a whole JavaScript number. `Nil` is `undefined`. A tuple is a
JavaScript array representing an immutable value; do not mutate it through
indexed assignment or array methods.

Import the virtual prelude as `src/gleam.mjs`. Construct lists and results with
generated constructors and inspect them with generated predicates and
accessors. Construct bit arrays from `Uint8Array`.

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

Inspect lists with `List$isEmpty`, `List$isNonEmpty`,
`List$NonEmpty$first`, and `List$NonEmpty$rest`. Inspect results with
`Result$isOk`, `Result$isError`, `Result$Ok$0`, and `Result$Error$0`.

`Dict` has no special JavaScript construction API. Convert a JavaScript array
to a Gleam list and pass it to the compiled `gleam/dict.from_list` function.

```javascript
import { from_list as list_to_dict } from "../gleam_stdlib/gleam/dict.mjs";
import { to_list as array_to_list } from "../gleam_stdlib/gleam/javascript/array.mjs";

const ages = list_to_dict(array_to_list([["Ada", 1]]));
```

## Generated documentation precision

Since 1.11.0, generated package documentation preserves source type-variable
names. Imported types retain their qualifier, link to their documentation, and
show the full module name on hover.

Since 1.13.0, HexDocs, language-server hovers, and actions such as add
annotations prefer an accessible public type alias rather than revealing the
aliased internal type.
