---
name: gleam-knowledge-patch
description: Gleam 1.7.0–1.17.0 compatibility. Use for Gleam work.
license: MIT
version: 1.17.0
metadata:
  author: Nevaberry
---

# Gleam Knowledge Patch

Baseline: Gleam through v1.6.x (core language, types, pattern matching, pipes, `use`, `Result`/`Option`, labelled arguments, generics, opaque types, externals/FFI, BEAM and JavaScript targets, and basic build tooling); coverage: Gleam 1.7.0 through 1.17.0 plus current language, FFI, conventions, configuration, and standard-library guidance.

Included release batches: `1.7.0`, `1.8.0`, `1.9.0`, `1.10.0`, `1.11.0`, `1.12.0`, `1.13.0`, `1.14.0`, `1.15.0`, `1.16.0`, and `1.17.0`.

Included topic batches: `language-tour`, `externals-and-ffi`, `conventions-and-patterns`, `tooling-and-configuration`, and `stdlib-release-history`.

## Reference index

| Reference | Topics |
| --- | --- |
| [language-and-diagnostics.md](references/language-and-diagnostics.md) | Syntax and semantics, assertions, debugging, constants, guards, patterns, bit arrays, formatter behavior, compiler diagnostics |
| [editor-and-refactoring.md](references/editor-and-refactoring.md) | Navigation, rename, generation, refactoring, completion, code actions, language-server operation |
| [packages-build-and-config.md](references/packages-build-and-config.md) | Dependencies, publishing, Hex authentication and ownership, project layout, documentation, exports, CI, `gleam.toml` |
| [targets-and-ffi.md](references/targets-and-ffi.md) | Erlang and JavaScript targets, shipments and escripts, source maps, externals, runtime representations, JavaScript interop |
| [conventions-and-patterns.md](references/conventions-and-patterns.md) | Naming, annotations, imports, shared packages, tool configuration, source boundaries, Sans-I/O, opaque FFI types |
| [stdlib-migrations-and-behavior.md](references/stdlib-migrations-and-behavior.md) | Removed and renamed APIs, package migrations, dynamic decoding, bit arrays, URI behavior, list and string edge cases |

Read the reference matching the work before changing code. Treat the quick reference below as a migration checklist, not as a replacement for the detailed files.

## Breaking changes and deprecations

### Configuration spelling

Use snake case in `gleam.toml`:

```toml
[dev_dependencies]
gleeunit = ">= 1.0.0 and < 2.0.0"

[repository]
tag_prefix = "my_package-v"
```

`dev-dependencies` and `tag-prefix` still parse but are deprecated. New JavaScript options also use snake case, including `source_maps` and `typescript_declarations`.

### Publishing requirements

Before publishing, ensure that:

- The package has an authored README, not the untouched `gleam new` placeholder.
- Every published module exposes at least one public type or function.
- Package modules normally live below the package namespace.
- `licences`, `description`, and `repository` are present.
- No development-only module or dependency leaks into the package.
- Hex authentication can complete the short-lived OAuth2 and MFA flow.

Publishing a `0.*` version or a package using the `gleam_` prefix requires explicit confirmation. See [packages-build-and-config.md](references/packages-build-and-config.md).

### Language migrations

- Replace deprecated discard aliases such as `_ as value` with `value`.
- Keep the returned value from immutable updates; discarded pure calls now warn.
- Replace full-list length checks for emptiness with patterns, `items == []`, or `items != []`.
- Remove meaningless `opaque` from private custom types.
- Use the supported generated JavaScript constructor, predicate, and accessor exports rather than compiler-internal custom-type layouts.

### Standard-library migrations

- Use `int.range`, not removed `list.range`.
- Use `gleam/dynamic/decode`, not the retired decoder API in `gleam/dynamic`.
- Use `list.flatten`, not removed `list.concat`.
- Use `drop_start`, `drop_end`, `pad_start`, `pad_end`, `trim_start`, and `trim_end`, not the old left/right names.
- Use `gleam_deque`, `gleam_yielder`, and `gleam_regexp` instead of the removed queue, iterator, and regex modules.
- Use `gleam/bytes_tree` and `gleam/string_tree` instead of removed builder modules.
- Replace removed helpers such as `result.then`, `result.unwrap_both`, `function.tap`, `int.digits`, and `io.debug` with their current equivalents.

Read [stdlib-migrations-and-behavior.md](references/stdlib-migrations-and-behavior.md) before upgrading old code.

## Language quick reference

### Assertions and debugging

Use Boolean `assert` when failure should panic with test-friendly expression details:

```gleam
assert telecom.is_up(key, strict, 2025) as "internet must be available"
```

Add `as "message"` to `let assert` as well. Use `echo expression` to print the value and source location to standard error without changing the value; add `as "message"` for context. Remove all module `echo` expressions with the language-server action before publishing.

### Constants

Constants now support record updates, list prepending from another constant list, and `todo` placeholders:

```gleam
pub const dev = HttpConfig(..base, port: 4000)
pub const mammals = ["platypus", ..viviparous]
pub const pending = Pokemon(number: 173, name: todo, hp: todo)
```

A program containing a constant `todo` can be analysed but cannot run.

### Guards, pipes, and records

String concatenation with `<>` is valid in `case` guards. For `value |> function(1, 2)`, Gleam first tries `function(value, 1, 2)` and, if the types reject that call, tries `function(1, 2)(value)`.

Record updates can safely change a generic parameter:

```gleam
pub fn replace(data: Named(a), replacement: b) -> Named(b) {
  Named(..data, value: replacement)
}
```

Access a field on a multi-variant custom type only when its label, position, and type agree across every possible variant, or after a pattern narrows the variant.

### Bit arrays

A segment defaults to an 8-bit integer and `size(n)` counts bits unless another unit is supplied. Use `:bits` for any alignment and `:bytes` for byte-aligned data. UTF codepoint segments accept endianness, and pattern sizes can contain calculations.

Check target support before relying on bit-array forms. JavaScript supports unaligned and dynamic segments, 16-bit floats, UTF-16/UTF-32, and unit options, but integer pattern segments wider than 52 bits are truncated and warn.

## Build and package quick reference

### Development and CI

Put development-only modules in `dev/`, give `<package>_dev` a `main`, and run:

```sh
gleam dev
gleam dev --no-print-progress
gleam build --warnings-as-errors
gleam format --check src test
```

`src/` cannot import development dependencies or `dev/`/`test/`; `test/` can import from all dependency scopes and source directories.

### Dependencies

Use Git dependencies with an explicit `ref`, inspect resolution, and audit updates:

```toml
[dependencies]
gleam_stdlib = { git = "https://github.com/gleam-lang/stdlib.git", ref = "957b83b" }
shared = { path = "../shared" }
```

```sh
gleam deps tree
gleam deps tree --package package_c
gleam deps tree --invert package_b
gleam deps outdated
```

Do not combine `--package` and `--invert`. Resolution errors now show the constraint chains that caused conflicts, and update commands report changed packages and available major releases.

### JavaScript output

```toml
[javascript]
runtime = "bun"
source_maps = true
typescript_declarations = true
```

Choose `node`, `deno`, or `bun`; `node` is the default. Serve `.map` files beside generated JavaScript. Configure Deno permissions under `[javascript.deno]`.

### Erlang distribution

Use `gleam export erlang-shipment` for a relocatable directory with cross-platform launchers. Use `gleam export escript` for one executable file that can run on a machine with Erlang installed.

## FFI quick reference

### External declarations

Give an external function a Gleam body to provide a fallback on targets without a matching `@external`. For external types, attach target-specific definitions:

```gleam
@external(erlang, "erlang", "map")
@external(javascript, "../dict.d.mts", "Dict")
pub type Dict(key, value)
```

JavaScript external paths are runtime module specifiers relative to the declaring Gleam file; install bare npm dependencies separately. Source directories can contain `.mjs`, `.js`, `.cjs`, `.mts`, `.cts`, `.jsx`, and `.tsx` external modules.

### Runtime values

Respect exact boundary representations:

- On BEAM, `String` is a UTF-8 binary, `Nil` is `nil`, `Result` is `{ok, Value}` or `{error, Value}`, fieldless variants are snake-case atoms, variants with fields are tagged tuples, and `Dict` is a map.
- In JavaScript, `Nil` is `undefined`, tuples are immutable arrays, and Gleam numeric constraints still apply even though both number types use JavaScript numbers.
- Construct and inspect lists, results, bit arrays, and custom types with the generated prelude or module APIs documented in [targets-and-ffi.md](references/targets-and-ffi.md).

## Editor workflow

Run the bundled server with `gleam lsp` from a project root. It supports multiple projects and unsaved buffers, follows each project's target, does not run project code, and only formats files outside a Gleam project.

Use current actions to generate functions, variants, encoders and decoders; exhaustively match values; add labels and annotations; correct operators; rename symbols or modules; and extract variables, constants, functions, pipeline segments, or assignment values. Read [editor-and-refactoring.md](references/editor-and-refactoring.md) for exact scope and edge cases.
