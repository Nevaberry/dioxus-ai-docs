# Build Tool & Project Structure

## Git dependencies (1.9)

The build tool now supports git repository dependencies in `gleam.toml`. Specify a git/HTTP URL with a tag, branch, or commit ref.

```toml
[dependencies]
gleam_stdlib = { git = "https://github.com/gleam-lang/stdlib.git", ref = "957b83b" }
```

## `gleam dev` and the `dev/` directory (1.11)

New `dev/` source directory for development-only code (database setup, asset compilation, etc.). Not included in production builds. The `$PACKAGENAME_dev` module's `main` function runs via `gleam dev`.

```
my_app/
├── src/    # Production code (gleam run)
├── test/   # Tests (gleam test)
└── dev/    # Development scripts (gleam dev)
```

## `gleam deps outdated` (1.14)

New command to check which dependencies have newer versions available on Hex.

```
$ gleam deps outdated
Package  Current  Latest
-------  -------  ------
wibble   1.4.0    1.4.1
wobble   1.0.1    2.3.0
```

## External modules in subdirectories (1.7)

External (FFI) modules can now reside in subdirectories of `src/` and `test/`, not just at the top level.

## Formatter removes redundant function captures (1.9)

The formatter now auto-simplifies redundant function capture syntax (where no additional arguments are provided).

```gleam
// Before formatting:
let print = io.print(_)
// After formatting:
let print = io.print
```

## List formatting control via trailing comma (1.12)

The formatter now respects trailing commas to force multiline list layout. Add a comma before `]` to spread elements; remove it to allow single-line.

```gleam
// Single line (no trailing comma):
["natu", "chimecho", "milotic"]

// Multiline (trailing comma):
[
  "natu",
  "chimecho",
  "milotic",
]
```

## `gleam.toml` key naming consistency (1.15)

`dev-dependencies` and `tag-prefix` are now canonically `dev_dependencies` and `tag_prefix` (snake_case). The old sausage-case format still works but is deprecated.
