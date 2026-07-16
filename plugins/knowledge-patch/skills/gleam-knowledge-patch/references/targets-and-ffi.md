# Targets and FFI

## Contents

- [Target build and distribution](#target-build-and-distribution)
- [External declarations and source files](#external-declarations-and-source-files)
- [Erlang and Elixir interop](#erlang-and-elixir-interop)
- [JavaScript output and runtime selection](#javascript-output-and-runtime-selection)
- [JavaScript value interop](#javascript-value-interop)
- [JavaScript bit arrays and custom types](#javascript-bit-arrays-and-custom-types)

## Target build and distribution

### External-source layout

Since 1.7.0, Erlang, Elixir, JavaScript, and other external-module files may live in subdirectories of `src/` or `test/`; they no longer have to be at the source root.

Since 1.16.0, the build includes `.mts`, `.cts`, `.jsx`, and `.tsx` files in source directories, in addition to the previously supported JavaScript external-source extensions.

### Erlang shipments

Since 1.10.0, `gleam export erlang-shipment` includes all entrypoint scripts regardless of the operating system used to build it. Build an artefact on one platform and run it on another.

Since 1.11.0, programs started by the shipment launcher receive POSIX exit signals, enabling normal process-manager shutdown behavior.

### Escript executables

Since 1.17.0, `gleam export escript` compiles an Erlang-target project, verifies that it has a valid `main`, and produces one executable file containing the compiled modules. Copy it to any machine with Erlang installed and run it directly.

```sh
gleam export escript
./my_project
```

### Erlang documentation metadata

Since 1.8.0, generated Erlang carries OTP 27 `-doc` data, exposing Gleam function documentation to BEAM tools such as `h(gleam@list, map)` while remaining compatible with older OTP releases.

## External declarations and source files

### Gleam fallbacks

An external declaration with no implementation for the selected target is a compile error. Give an external function a Gleam body to use that body on targets without a matching `@external`; the foreign implementation still wins where supplied.

```gleam
import gleam/list

@external(erlang, "lists", "reverse")
pub fn reverse(items: List(item)) -> List(item) {
  list.fold(items, [], fn(reversed, item) { [item, ..reversed] })
}
```

### Target definitions for external types

Since 1.14.0, an external type can declare target-specific Erlang and JavaScript definitions. Generated Erlang specs and TypeScript declarations then use the precise foreign type instead of `any`.

```gleam
@external(erlang, "erlang", "map")
@external(javascript, "../dict.d.mts", "Dict")
pub type Dict(key, value)
```

## Erlang and Elixir interop

### Exact BEAM representations

Foreign code must return Gleam's exact runtime representation:

- `String` is a UTF-8 binary, not an Erlang character list.
- `List` is a proper homogeneous Erlang list.
- `Nil` is the atom `nil`.
- `Result` values are `{ok, Value}` and `{error, Value}`, not bare `ok` or `error`.
- A fieldless custom-type variant is a snake-case atom.
- A custom-type variant with fields is a tagged tuple.
- `Dict` is an Erlang map.

```erlang
guest
{super_user, 11}
{ok, 2}
#{<<"a"/utf8>> => 1}
```

### Generated record definitions

The compiler generates an Erlang header with a record definition for each custom-type variant. Erlang code can include that header for record syntax; Elixir can consume it through the `Record` module.

### Calling Elixir

Declare an Elixir function with the `erlang` target and the VM module name, including Elixir's implicit `Elixir.` prefix. Elixir macros cannot be called as externals.

```gleam
@external(erlang, "Elixir.Pokemon", "badge_count")
pub fn pokemon_badge_count() -> Int
```

### OTP application startup

`erlang.application_start_module` names a module implementing the OTP application behaviour. Use the compiled Erlang atom form, replacing a Gleam `/` with `@`. `erlang.extra_applications` lists OTP applications to start beyond those supplied by dependencies.

```toml
[erlang]
application_start_module = "my_project@application"
extra_applications = ["inets", "ssl"]
```

## JavaScript output and runtime selection

### JavaScript source maps

Since 1.16.0, enable source maps to map generated JavaScript, stack traces, breakpoints, and debugger positions back to Gleam source.

```toml
[javascript]
source_maps = true
```

Serve each map beside its JavaScript. Serving the build directory or using Lustre development tooling already does this.

### TypeScript declarations and JSDoc

Set `typescript_declarations` to emit `.d.ts` files for compiled modules; it defaults to `false`.

```toml
[javascript]
typescript_declarations = true
```

Since 1.12.0, Gleam documentation comments are also emitted as JSDoc in JavaScript output for editors and documentation tools.

Since 1.15.0, generated `is` declarations are TypeScript predicates such as `value is TypeName`, enabling control-flow narrowing.

### Runtime selection

`javascript.runtime` selects `node`, `deno`, or `bun` for `gleam run`, `gleam test`, and related commands. The default is `node`, and `--runtime` overrides it for one invocation.

```toml
[javascript]
runtime = "bun"
```

### Deno permissions

`[javascript.deno]` maps Deno permissions into project configuration. `allow_all`, `allow_ffi`, `allow_hrtime`, and `allow_sys` are Boolean. `allow_env`, `allow_net`, `allow_read`, `allow_run`, and `allow_write` accept either a Boolean or a scoped list.

```toml
[javascript.deno]
allow_env = ["DATABASE_URL"]
allow_net = ["example.com:443"]
allow_read = ["./database.sqlite"]
```

## JavaScript value interop

### External module specifiers

A local JavaScript external path resolves relative to the Gleam file containing the declaration. Bare Node module specifiers work, but Gleam neither installs nor manages npm dependencies; install them in the application separately.

```gleam
@external(javascript, "has-flag", "hasFlag")
pub fn argv_has_flag(name: String) -> Bool
```

Since 1.12.0, an external module may use `.cjs` and CommonJS.

### Importing compiled Gleam modules

Each compiled Gleam module is an ES module at its source-shaped path with an `.mjs` extension. Build output places packages beside each other, so JavaScript reaches a dependency by ascending out of its package root and entering the dependency directory.

```javascript
// From src/wibble/wobble.mjs:
import * as option from "../../gleam_stdlib/gleam/option.mjs";
```

### Primitive and tuple boundaries

Gleam `Int` values are whole JavaScript numbers. `Float` values are JavaScript numbers but should not receive `NaN` or infinities. `Nil` is `undefined`. Tuples are JavaScript arrays representing immutable values and must not be mutated.

### Lists

Use `List$Empty()` and `List$NonEmpty(first, rest)` to construct a Gleam list. Test variants with `List$isEmpty` and `List$isNonEmpty`, and read a non-empty node through `List$NonEmpty$first` and `List$NonEmpty$rest`. Every tail must itself be a correctly typed Gleam list.

```javascript
import { List$Empty, List$NonEmpty } from "../gleam.mjs";

const one = List$NonEmpty(1, List$Empty());
```

### Results

Construct results with `Result$Ok(value)` and `Result$Error(value)`, test with `Result$isOk` and `Result$isError`, and unwrap the matching variant through `Result$Ok$0` or `Result$Error$0`.

```javascript
import { Result$Ok, Result$Ok$0 } from "../gleam.mjs";

Result$Ok$0(Result$Ok(2));
```

### Dictionaries

`Dict` has no special JavaScript representation API. Import the regular compiled `gleam/dict` functions, converting a JavaScript array to a Gleam list first when calling `dict.from_list`.

```javascript
import { from_list as list_to_dict } from "../gleam_stdlib/gleam/dict.mjs";
import { to_list as array_to_list } from "../gleam_stdlib/gleam/javascript/array.mjs";

const ages = list_to_dict(array_to_list([["Ada", 1]]));
```

## JavaScript bit arrays and custom types

### Bit-array compiler support

JavaScript bit-array support expanded in several releases:

- Since 1.9.0, unaligned values and dynamically sized pattern segments work.
- Since 1.10.0, segment `unit` options and 16-bit float segments work. A float literal infers a float segment, so `<<1.11>>` equals `<<1.11:float>>`.
- Since 1.11.0, UTF-16 and UTF-32 segments work.
- Since 1.16.0, an integer pattern segment wider than 52 bits warns that JavaScript truncates it to the first 52 bits and suggests a `bytes` segment.

```gleam
let <<_, number:152>> = sha
```

### Prelude bit-array API

The build tool exposes the virtual prelude as if it were `src/gleam.mjs`. Construct a bit array with `BitArray$BitArray` and a `Uint8Array`.

```javascript
import { BitArray$BitArray } from "../gleam.mjs";

const bytes = BitArray$BitArray(new Uint8Array([30, 56, 10]));
```

Since 1.15.0, use `BitArray$isBitArray` to test a value and `BitArray$BitArray$data` to unpack its bytes.

### Supported custom-type API

Since 1.13.0, generated modules export supported functions for constructing variants, testing variants, and reading fields. Migrate JavaScript externals away from compiler-internal representations. A shared accessor such as `Person$name` exists for a field present in every variant.

```javascript
import {
  Person$Teacher,
  Person$isTeacher,
  Person$Teacher$subject,
  Person$name,
} from "./person.mjs";

const teacher = Person$Teacher("Joe Armstrong", "Computer Science");
Person$isTeacher(teacher);
Person$Teacher$subject(teacher);
Person$name(teacher);
```
