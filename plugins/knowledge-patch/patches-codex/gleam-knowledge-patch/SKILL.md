---
name: gleam-knowledge-patch
description: Gleam
version: "1.17.0"
license: MIT
metadata:
  author: Nevaberry
---


# Gleam Knowledge Patch

Use this skill when writing, reviewing, upgrading, or packaging Gleam code.
Start with the breaking-change checklist, then read the reference file that
matches the work. Prefer the project's compiler, manifest, source, and tests
when they disagree with general guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [language-and-diagnostics.md](references/language-and-diagnostics.md) | Language semantics, assertions, constants, patterns, bit arrays, warnings, documentation, and formatting |
| [editor-and-refactoring.md](references/editor-and-refactoring.md) | Language-server navigation, generation, rename, completion, and refactoring actions |
| [packages-build-and-config.md](references/packages-build-and-config.md) | Dependencies, Hex, publishing, project layout, build behavior, exports, and `gleam.toml` |
| [targets-and-ffi.md](references/targets-and-ffi.md) | Erlang and JavaScript targets, distribution, generated APIs, externals, and runtime representations |
| [conventions-and-patterns.md](references/conventions-and-patterns.md) | Naming, annotations, imports, fallibility, shared types, source boundaries, Sans-I/O, and opaque foreign types |
| [stdlib-migrations-and-behavior.md](references/stdlib-migrations-and-behavior.md) | Removed and renamed standard-library APIs plus current edge behavior |

## Breaking changes and deprecations

### Use canonical configuration keys

Write snake-case keys in `gleam.toml`:

```toml
[dev_dependencies]
gleeunit = ">= 1.0.0 and < 2.0.0"

[repository]
tag_prefix = "my_package-v"
```

The older `dev-dependencies` and `tag-prefix` spellings still parse but are
deprecated. JavaScript settings also use snake case, including `source_maps`
and `typescript_declarations`.

### Migrate retired standard-library APIs

- Use `int.range`, not removed `list.range`.
- Import decoders from `gleam/dynamic/decode`, not `gleam/dynamic`.
- Use `list.flatten`, not removed `list.concat`.
- Use `drop_start`, `drop_end`, `pad_start`, `pad_end`, `trim_start`, and
  `trim_end`, not the removed left/right names.
- Replace the removed queue, iterator, and regex modules with `gleam_deque`,
  `gleam_yielder`, and `gleam_regexp`.
- Use `gleam/bytes_tree` and `gleam/string_tree` instead of the removed builder
  modules.
- Replace `result.then`, `result.unwrap_both`, `function.tap`, `int.digits`,
  `int.undigits`, `io.debug`, and other retired helpers with the current APIs
  described in the standard-library reference.

### Update deprecated language patterns

- Replace `_ as value` with `value`; the formatter performs this rewrite.
- Keep the returned value from immutable updates. Discarding a pure call now
  warns.
- Test list emptiness with patterns or `items == []` / `items != []`, not a
  full `list.length` traversal.
- Do not depend on internal custom-type layouts from generated JavaScript. Use
  the supported constructor, predicate, and accessor exports.

### Satisfy publishing gates

Before `gleam publish`:

- Replace the generated placeholder README and ensure a README exists.
- Remove modules that expose no public type or function.
- Keep package modules beneath the package namespace unless a deliberate
  exception is confirmed.
- Review confirmations for `0.*` packages and names beginning with `gleam_`.
- Ensure Hex OAuth2, MFA for writes, and local token encryption can complete.
- Keep production modules and dependencies free of development-only imports.

## Language quick reference

### Assertions and debugging

Use Boolean `assert` when a false condition should panic with expression and
operand details useful to test frameworks:

```gleam
assert telecom.is_up(key, strict, 2025) as "internet must be available"
```

Add `as "message"` to `let assert` for a custom panic message. Prefix an
expression with `echo` to print its value and source location to standard
error without consuming the value; `echo value as "message"` adds context.
Publishing warns about leftover `echo` expressions.

### Constants

Constants support record updates, list prepending from another constant list,
and incomplete `todo` values:

```gleam
pub const dev = HttpConfig(..base, port: 4000)
pub const mammals = ["platypus", ..other_mammals]
pub const pending = Pokemon(number: 173, name: todo, hp: todo)
```

A constant containing `todo` can be type-checked and analysed, but the program
cannot run.

### Guards, pipelines, and records

String concatenation with `<>` is valid in case guards. Given
`value |> function(1, 2)`, Gleam first tries `function(value, 1, 2)` and, if
that fails to type-check, tries `function(1, 2)(value)`. Use a capture when the
piped value belongs in another argument position.

Record updates can change a generic parameter:

```gleam
pub fn replace(data: Named(a), replacement: b) -> Named(b) {
  Named(..data, value: replacement)
}
```

Direct field access on a multi-variant custom type is valid only when every
possible variant has that field at the same position and with the same type,
or after matching has narrowed the variant.

### Patterns and bit arrays

Alternative case patterns must bind identical names with identical types and
cannot be nested inside another pattern. The compiler diagnoses unreachable
string-prefix clauses, redundant comparisons, impossible integer segments,
truncating bit-array literals, and clauses covered by earlier bit-array
patterns.

A bit-array integer segment defaults to 8 bits; a float segment defaults to
64 bits. `size(n)` uses the selected unit, whose default is one bit. Use
`:bits` for any alignment and `:bytes` to require byte alignment. UTF segments
accept endianness and pattern sizes may contain calculations.

Check the target-specific limits before relying on advanced bit arrays.
JavaScript supports unaligned and dynamic segments, `unit`, 16-bit floats,
UTF-16, and UTF-32, but integer patterns wider than 52 bits truncate and warn.

## Build, dependency, and package workflow

### Development and CI

Put development-only modules in `dev/`, define `main` in `<package>_dev`, and
use:

```sh
gleam dev
gleam dev --no-print-progress
```

`src/` can import only regular dependencies and other `src/` modules. `dev/`
and `test/` can import all dependency scopes and source directories.

### Dependencies

Git dependencies require an explicit `ref`:

```toml
[dependencies]
gleam_stdlib = { git = "https://github.com/gleam-lang/stdlib.git", ref = "957b83b" }
```

Inspect resolution and updates with:

```sh
gleam deps tree
gleam deps tree --package package_c
gleam deps tree --invert package_b
gleam deps outdated
```

Do not combine `--package` and `--invert`. Resolution errors trace constraint
chains, update commands identify changed versions and out-of-range major
releases, and `deps outdated` always reports a summary count.

### JavaScript output

```toml
[javascript]
runtime = "bun"
source_maps = true
typescript_declarations = true
```

The runtime may be `node`, `deno`, or `bun`; Node is the default. Serve `.map`
files beside the generated JavaScript. Configure Deno permissions under
`[javascript.deno]`.

### Erlang distribution

Use `gleam export erlang-shipment` for a relocatable directory with
cross-platform launchers and forwarded POSIX signals. Use
`gleam export escript` for one executable file that can run on a machine with
Erlang installed.

## FFI quick reference

### External declarations

Give an external function a Gleam body when it needs a fallback on targets
without the corresponding external implementation. External types accept
target-specific definitions:

```gleam
@external(erlang, "erlang", "map")
@external(javascript, "../dict.d.mts", "Dict")
pub type Dict(key, value)
```

JavaScript external paths are resolved relative to the declaring Gleam file.
Bare package specifiers are accepted, but Gleam does not install the npm
package. External source files may use `.mjs`, `.cjs`, `.mts`, `.cts`, `.jsx`,
or `.tsx`.

### Runtime representations

- On BEAM, `String` is a UTF-8 binary, `Nil` is `nil`, `Result` is
  `{ok, Value}` or `{error, Value}`, fieldless variants are snake-case atoms,
  variants with fields are tagged tuples, and `Dict` is a map.
- In JavaScript, `Nil` is `undefined`, tuples are immutable arrays, and both
  Gleam number types use JavaScript numbers while retaining Gleam's numeric
  constraints.
- Construct and inspect lists, results, bit arrays, and custom types through
  the generated prelude and module APIs. Use compiled `gleam/dict` functions
  for dictionaries.

## Editor workflow

The language server analyses unsaved buffers for the project's configured
target without generating code or compiling Erlang or Elixir, so analysis
does not execute foreign code. Outside a Gleam project it only formats.

Use its actions to generate functions, variants, encoders, and decoders;
create missing modules; exhaustively match values; add labels, parameters,
and annotations; correct operators; rename symbols and modules; qualify
imports; and extract constants, variables, functions, pipeline segments, or
assignment values. Read the editor reference for the exact scope and edge
cases of each action.
