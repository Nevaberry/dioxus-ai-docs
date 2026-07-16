# Conventions and patterns

## Imports and annotations

### Keep functions and constants qualified

Call functions and constants from another module through their module qualifier. Import types and record constructors unqualified only when that remains readable.

```gleam
import gleam/list

pub fn reversed(items: List(a)) -> List(a) {
  list.reverse(items)
}
```

### Annotate module functions

Give every module-level function, including private functions, types for all arguments and an explicit return type. Keep inference inside function bodies rather than at the definition boundary.

## Naming

### Treat acronyms as words

Use `Json` and `json`, not `JSON` or `j_s_o_n`. This follows Gleam naming conventions and avoids generated BEAM names such as `j_s_o_n`.

### Name conversions by direction or format

Use `x_to_y` for a general conversion, but omit the source type when the module already establishes it, as with `identifier.to_string`. Prefer a format-specific name such as `date_to_rfc3339`, or a semantic operation such as `round`, when available.

### Reserve `try_` for counterparts

Name a `Result`-returning function after its domain operation, such as `parse_json` or `enqueue`. Use `try_` only for a result-propagating counterpart of an existing operation, such as `map` and `try_map`, rather than to describe an abstract fallibility pattern.

## Package and source design

### Share core package types

Prefer `gleam_stdlib`, `gleam_time`, `gleam_json`, `gleam_http`, `gleam_erlang`, `gleam_otp`, and `gleam_javascript` rather than recreating their data types or functionality. Shared representations keep packages interoperable.

### Put tool settings in `gleam.toml`

Store an additional development tool's static settings below `tools.<tool-name>` rather than in a dedicated configuration file. Dynamic settings may still come from environment variables or command-line arguments.

```toml
[tools.lustre.build]
minify = true
outdir = "../server/priv/static"
```

### Respect source import boundaries

Code under `src/` may import only regular dependencies and other `src/` modules. It cannot import development dependencies or modules under `dev/` or `test/`. Code under `test/` may import from every dependency and source directory.

## Portable APIs and FFI

### Design Sans-I/O clients

For each API action, expose one function that constructs an HTTP request and another that parses an HTTP response, leaving transport to the caller. Passing an HTTP-sending callback couples the package to incompatible transport shapes across targets, notably promise-based JavaScript and Erlang.

```gleam
pub fn create_user_request(name: String) -> Request(String)
pub fn create_user_response(response: Response(String)) -> Result(User, ApiError)
```

### Do not use `Dynamic` as an FFI catch-all

If a foreign value cannot be represented by an existing Gleam type, declare a purpose-specific opaque type. Exposing `gleam/dynamic.Dynamic` would incorrectly promise that every Gleam value is valid input.

```gleam
pub type Buffer
pub fn byte_size(data: Buffer) -> Int
```
