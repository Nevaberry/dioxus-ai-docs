---
name: gleam-knowledge-patch
description: "Gleam changes since training cutoff (latest: 1.15) — echo debugging, assert testing, bit array improvements, JavaScript FFI API, dev directory, record update enhancements. Load before working with Gleam."
version: "1.15"
license: MIT
metadata:
  author: Nevaberry
---

# Gleam Knowledge Patch

Covers Gleam 1.7–1.15 (2025-01-05 through 2026-03-16). Claude Opus 4.6 knows Gleam through v1.6.x including core language (types, pattern matching, pipes, use expressions, Result/Option, labelled arguments, generics, opaque types, externals/FFI), BEAM and JavaScript targets, and gleam build tool basics.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Debug & testing | [references/debug-and-testing.md](references/debug-and-testing.md) | `echo` keyword, `echo` labels, `assert` for tests, `let assert` messages |
| Bit arrays | [references/bit-arrays.md](references/bit-arrays.md) | JS parity (unaligned, 16-bit float, unit, UTF-16/32), float shorthand, size expressions |
| JavaScript FFI | [references/javascript-ffi.md](references/javascript-ffi.md) | `$`-prefixed external API, BitArray FFI, `@external` on types, CommonJS |
| Type system & patterns | [references/type-system.md](references/type-system.md) | Record updates across type params, const record updates, string `<>` in guards |
| Build tool & project | [references/build-tool.md](references/build-tool.md) | Git deps, `gleam dev`, `dev/` dir, `gleam deps outdated`, formatter controls |

---

## Quick Reference — New Keywords & Syntax

| Feature | Version | Syntax |
|---|---|---|
| `echo` (debug print) | 1.9 | `echo expr` or `expr \|> echo` |
| `echo` with label | 1.12 | `echo expr as "label"` |
| `assert` (test assertion) | 1.11 | `assert expr == expected` |
| `assert` with message | 1.11 | `assert expr as "message"` |
| `let assert` message | 1.7 | `let assert Ok(x) = expr as "msg"` |
| Variant deprecation | 1.7 | `@deprecated("msg")` on variant |
| `@external` on types | 1.14 | `@external(erlang, "mod", "type")` on `pub type` |
| Record update type change | 1.7 | `Named(..data, value: new_typed_value)` |
| Record update in const | 1.14 | `const dev = Config(..base, port: 4000)` |
| String `<>` in guards | 1.15 | `case x { s if a <> b == s -> ... }` |
| Bit array float literal | 1.10 | `<<1.5>>` (no `:float` needed) |
| Bit array size expressions | 1.12 | `<<data:bytes-size(size / 8 - 1)>>` |
| Trailing comma → multiline | 1.12 | `["a", "b",]` forces multiline format |
| Git dependencies | 1.9 | `pkg = { git = "url", ref = "..." }` |
| `gleam dev` | 1.11 | Runs `dev/` directory code |
| `gleam deps outdated` | 1.14 | Check for newer Hex versions |

---

## Essential Patterns

### Debug printing with `echo` (1.9+)

```gleam
// Standalone — prints value + file:line to stderr
echo [1, 2, 3]

// In pipelines — passes value through
[1, 2, 3]
|> list.map(fn(x) { x + 1 })
|> echo
|> list.map(fn(x) { x * 2 })

// With label (1.12+)
echo config.port as "server port"
```

### Test assertions with `assert` (1.11+)

```gleam
pub fn hello_test() {
  assert telecom.ring() == "Hello, Joe!"
}

// Custom message:
pub fn system_test() {
  assert telecom.is_up(key, strict, 2025)
    as "My internet must always be up!"
}
```

### JavaScript FFI — External API (1.13+)

```gleam
// src/person.gleam
pub type Person {
  Teacher(name: String, subject: String)
  Student(name: String)
}
```

```javascript
// src/my_ffi.mjs
import { Person$Teacher, Person$Student, Person$isTeacher,
         Person$Teacher$subject, Person$name } from "./person.mjs";

let teacher = Person$Teacher("Joe", "CS");
Person$isTeacher(teacher);         // true
Person$Teacher$subject(teacher);   // "CS"
Person$name(teacher);              // "Joe" (shared field)
```

### Project structure with `dev/` (1.11+)

```
my_app/
├── src/    # Production code (gleam run)
├── test/   # Tests (gleam test)
└── dev/    # Development scripts (gleam dev)
```

The `$PACKAGENAME_dev` module's `main` function runs via `gleam dev`.

### Git dependencies in gleam.toml (1.9+)

```toml
[dependencies]
gleam_stdlib = { git = "https://github.com/gleam-lang/stdlib.git", ref = "957b83b" }
```

Supports git/HTTP URLs with a tag, branch, or commit ref.

### `@external` on type declarations (1.14+)

```gleam
@external(erlang, "erlang", "map")
@external(javascript, "../dict.d.mts", "Dict")
pub type Dict(key, value)
```

Produces precise Erlang type specs and TypeScript declarations instead of `any`.
