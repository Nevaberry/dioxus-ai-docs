# Conventions and patterns

## Imports and module boundaries

Call imported functions and constants through their module qualifier. Types and
record constructors may be imported unqualified when that remains readable.

```gleam
import gleam/list

pub fn reversed(items: List(a)) -> List(a) {
  list.reverse(items)
}
```

Use singular names for every module-path segment, such as
`app/payment/invoice`, not `app/payments/invoice`.

Production modules in `src/` may import only regular dependencies and other
`src/` modules. They cannot import development dependencies or modules in
`dev/` or `test/`. Modules in `dev/` and `test/` may import from every dependency
scope and source directory.

## Types and function boundaries

Annotate every module-level function, including private functions, with types
for every argument and an explicit return type. Keep inference within function
bodies rather than at definition boundaries.

Use shared types and functionality from `gleam_stdlib`, `gleam_time`,
`gleam_json`, `gleam_http`, `gleam_erlang`, `gleam_otp`, and
`gleam_javascript` rather than recreating them. Their shared representations
allow independently developed packages to interoperate.

## Failure handling

Fallible functions return `Result`, not `Option`. Use `Nil` for the error type
when failure carries no additional information.

Libraries must not use `panic` or `let assert` for ordinary failure. An
OTP-focused library may deliberately panic when a suitable supervision tree
provides non-local handling.

```gleam
pub fn first(items: List(a)) -> Result(a, Nil) {
  case items {
    [item, ..] -> Ok(item)
    _ -> Error(Nil)
  }
}
```

## Naming

Treat acronyms as ordinary words: use `Json` and `json`, not `JSON` or
`j_s_o_n`. An all-capital name produces a segmented BEAM name such as
`j_s_o_n`.

Use `x_to_y` for a general conversion, omitting the source when the module
already supplies it, as in `identifier.to_string`. Prefer a precise format such
as `date_to_rfc3339`, or a domain operation such as `round`, when available.

Name result-returning functions by their domain operation, such as `parse_json`
or `enqueue`. Reserve `try_` for a result-propagating counterpart of an existing
operation, such as `map` and `try_map`.

## Tool configuration

Put static configuration for extra development tools under
`tools.<tool-name>` in `gleam.toml`, rather than in separate configuration
files. Dynamic settings may still come from environment variables or command-line
arguments.

```toml
[tools.lustre.build]
minify = true
outdir = "../server/priv/static"
```

## Sans-I/O clients

At each HTTP API boundary, expose one function that constructs a request and
another that parses a response, leaving transport to the caller.

```gleam
pub fn create_user_request(name: String) -> Request(String)
pub fn create_user_response(response: Response(String)) -> Result(User, ApiError)
```

Accepting an HTTP-sending callback would couple a package to incompatible
transport shapes on Erlang and JavaScript.

## FFI types

Do not use `gleam/dynamic.Dynamic` as a catch-all for foreign values. When no
existing Gleam representation fits, declare a purpose-specific opaque type.
Using `Dynamic` would promise incorrectly that every Gleam value is valid input.

```gleam
pub type Buffer
pub fn byte_size(data: Buffer) -> Int
```
