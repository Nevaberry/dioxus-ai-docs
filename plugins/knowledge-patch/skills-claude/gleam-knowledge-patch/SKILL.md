---
name: gleam-knowledge-patch
description: Gleam
version: 1.17.0
license: MIT
metadata:
  author: Nevaberry
---


# Gleam Knowledge Patch

Use this skill for Gleam language, compiler, build-tool, package, standard-library,
editor, target, and foreign-function-interface work where current compatibility
details matter.

## How to use this skill

1. Identify whether the task concerns language behavior, editor actions, packaging,
   conventions, standard-library migration, or target interoperation.
2. Read the matching reference before proposing syntax, configuration, commands,
   migrations, or foreign value representations.
3. Apply only the guidance relevant to the requested target and workflow.
4. Preserve explicit qualifications such as deprecation, target differences,
   publication-only failures, and warnings versus errors.

## Reference index

| Reference | Topics |
| --- | --- |
| [Language and diagnostics](references/language-and-diagnostics.md) | Language syntax and semantics, assertions, constants, patterns, guards, bit arrays, compiler warnings |
| [Editor and refactoring](references/editor-and-refactoring.md) | Language-server navigation, generation, completion, rename, extraction, and pattern actions |
| [Packages, build, and configuration](references/packages-build-and-config.md) | Dependencies, Hex, publishing, exports, project configuration, documentation, and build behavior |
| [Targets and FFI](references/targets-and-ffi.md) | Erlang and JavaScript generation, deployments, source maps, external modules, and runtime representations |
| [Standard-library migrations and behavior](references/stdlib-migrations-and-behavior.md) | Removed and replacement APIs, decoder changes, collections, strings, URI handling, sorting, and version requirements |
| [Conventions and patterns](references/conventions-and-patterns.md) | Naming, annotations, errors, imports, shared types, configuration placement, Sans-I/O, and FFI boundaries |

## Breaking changes and migrations

### Hex authentication

- Hex authentication uses OAuth2 exclusively, with MFA for write operations and
  short-lived access tokens.
- The first Hex use revokes legacy tokens stored by Gleam.
- The password that encrypts local tokens must contain at least eight characters.

### Configuration spellings

- Use `dev_dependencies` and `tag_prefix` in `gleam.toml`.
- The hyphenated `dev-dependencies` and `tag-prefix` forms still work but are
  deprecated.
- Use `gleam fix` to rewrite deprecated Gleam syntax across a project.

### Dynamic decoding

- Import decoder combinators from `gleam/dynamic/decode`, not `gleam/dynamic`.
- The decoder module has its own error type and a revised
  `new_primitive_decoder` API.
- `dynamic.optional_field` makes the key optional; a present value must still
  satisfy its decoder.

### Retired standard-library APIs

- Replace `list.range` with `int.range` and `result.then` with `result.try`.
- Use `list.flatten`, not the removed `list.concat`, for concatenating lists.
- Use string APIs ending in `_start` and `_end`; the `_left` and `_right`
  variants were removed.
- Use `gleam_deque`, `gleam_yielder`, and `gleam_regexp` instead of the removed
  queue, iterator, and regex standard-library modules.
- `io.debug` was replaced by `echo`; `result.nil_error` was replaced by
  `result.replace_error`.

### JavaScript FFI representations

- Use the generated custom-type constructor, predicate, and accessor exports,
  rather than compiler-internal custom-type representations.
- Construct and inspect lists, results, and bit arrays through the generated
  prelude API.
- `Nil` is JavaScript `undefined`; tuples are JavaScript arrays representing
  immutable values and must not be mutated.
- Use regular compiled Gleam functions to construct `Dict` values.

### Publishing checks

- Package modules should normally live below the package namespace.
- Publishing warns and asks for confirmation about namespace collisions,
  unofficial names beginning with `gleam_`, and `0.*` package versions.
- Modules without public definitions block publishing.
- A missing README or the default README from `gleam new` blocks publishing.

## High-use language features

### Debugging and assertions

```gleam
echo 11 as "lucky number"
assert telecom.is_up(key, strict, 2025) as "My internet must always be up!"
let assert Ok(regex) = regex.compile("ab?c+") as "This regex is always valid"
```

- `echo` prints the value and source location to standard error, can appear in
  a pipeline without consuming the value, and triggers a publish warning when
  left in the project.
- `assert` panics on `False` and records the source expression and relevant
  values for test frameworks.
- Both `echo` and assertions accept custom messages with `as`.

### Records and constants

- Updating a field may change a generic record's type parameter.
- Record-update syntax and list prepending with spread syntax are valid in
  constant expressions.
- Constants may contain `todo` and remain analysable, but a program containing
  such a constant cannot run because constants are evaluated at compile time.

### Guards and patterns

- String concatenation with `<>` is valid in case guards.
- Alternative patterns must bind identical names with identical types and may
  not be nested inside another pattern.
- A record field accessor on a multi-variant type works without refinement only
  when every variant has that field in the same position and with the same type.
- Empty blocks are accepted as incomplete placeholders with a warning.

### Bit arrays

- Segment `size(n)` counts units and `unit` defaults to one bit.
- Integer segments default to 8 bits and float segments to 64 bits.
- Use `bits` for any-sized bit arrays and `bytes` when byte alignment is required.
- UTF codepoint segments can specify endianness, and pattern sizes may contain
  calculations.

## High-use editor actions

The language server can:

- find references and rename types and values project-wide;
- rename local variables, function arguments, modules, constructors in
  constants, and variables bound in string-prefix patterns;
- generate missing local or qualified functions with inferred annotations;
- generate custom-type variants, exhaustive matches, dynamic decoders, and JSON
  encoders;
- convert calls to pipelines and `use` expressions to callback calls and back;
- add or fill labels in calls and record patterns, using matching in-scope
  variables where possible;
- add annotations to every top-level definition or replace type holes with
  inferred types;
- extract constants, expressions, anonymous-function bodies, assignment values,
  and consecutive pipeline segments;
- merge equal case branches, collapse nested cases, expand discards and ignored
  fields, remove unreachable clauses, and remove redundant record updates;
- create a missing imported module's source file;
- provide folding ranges and document highlights.

Read [Editor and refactoring](references/editor-and-refactoring.md) before relying
on the exact scope or output of any action.

## High-use package and build commands

```sh
gleam deps tree
gleam deps outdated
gleam update
gleam dev --no-print-progress
gleam export package-information
gleam export package-interface --out build/package-interface.json
gleam export escript
```

- `gleam deps tree` accepts either `--package` or `--invert`, but not both.
- `gleam deps outdated` shows current and latest versions and prints a summary
  count even when no package is outdated.
- Development tooling may live in `dev/` and run through `gleam dev` without
  entering production output.
- An exported escript is a single runnable Erlang-target file for machines with
  Erlang installed.

## Target reminders

- JavaScript and BEAM have different float overflow behavior; float division by
  zero produces zero on both targets.
- JavaScript source maps require `javascript.source_maps = true`, and map files
  must be served with the generated JavaScript.
- External functions may combine an `@external` annotation with a Gleam fallback
  body for targets without that external implementation.
- Elixir calls use `@external(erlang, ...)` with the VM module's `Elixir.` prefix;
  macros cannot be called this way.
- Local JavaScript external paths are relative to the Gleam source file.

Read [Targets and FFI](references/targets-and-ffi.md) before writing external
declarations or manually constructing foreign runtime values.
