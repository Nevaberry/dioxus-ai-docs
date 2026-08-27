# Conventions and patterns

## Imports, names, and annotations

### Keep functions and constants qualified

Call imported functions and constants through their module qualifier. Types
and record constructors may be imported unqualified when readability benefits:

```gleam
import gleam/list

pub fn reversed(items: List(a)) -> List(a) {
  list.reverse(items)
}
```

### Annotate every module function

Give each module-level function, public or private, explicit types for all
arguments and its return value. Keep inference within function bodies instead
of at definition boundaries.

### Use singular module names

Every module-path segment should be singular: prefer `app/payment/invoice`
over `app/payments/invoice`.

### Treat acronyms as words

Write acronyms as ordinary words, such as `Json` and `json`, rather than
`JSON` or `j_s_o_n`. An all-capital Gleam name becomes a segmented BEAM name
such as `j_s_o_n`.

## Fallibility and function names

### Return `Result` for ordinary failure

Fallible functions return `Result`, not `Option`. Use `Nil` as the error type
when failure carries no information:

```gleam
pub fn first(items: List(a)) -> Result(a, Nil) {
  case items {
    [item, ..] -> Ok(item)
    _ -> Error(Nil)
  }
}
```

Libraries should not use `panic` or `let assert` for ordinary failure. An
OTP-oriented library may deliberately panic when a suitable supervision tree
provides non-local recovery.

### Name conversions and result-propagating operations precisely

Use `x_to_y` for a general conversion, but omit the source when the module
already identifies it, as in `identifier.to_string`. Prefer an exact format
such as `date_to_rfc3339`, or a domain operation such as `round`, when one
exists.

Give result-returning functions domain names such as `parse_json` or
`enqueue`. Reserve `try_` for a result-propagating counterpart of an existing
operation, such as `map` and `try_map`.

## Package interoperability

### Reuse foundational package types

Use `gleam_stdlib`, `gleam_time`, `gleam_json`, `gleam_http`, `gleam_erlang`,
`gleam_otp`, and `gleam_javascript` as shared foundations rather than
recreating their types or functionality. Shared representations keep
independently developed packages interoperable.

### Put tool configuration in `gleam.toml`

Store static settings for additional tools under `tools.<tool-name>` rather
than creating separate configuration files. Dynamic settings may still come
from environment variables or CLI flags.

```toml
[tools.lustre.build]
minify = true
outdir = "../server/priv/static"
```

## Source and API boundaries

### Respect source-directory imports

Production code under `src/` may import regular dependencies and other `src/`
modules only. It cannot import development dependencies or modules from
`dev/` or `test/`. Modules in `dev/` and `test/` may import from all dependency
scopes and source directories.

### Split Sans-I/O clients at the HTTP boundary

For each remote API action, expose one function that builds a request and one
that parses a response. Leave network transport to the caller:

```gleam
pub fn create_user_request(name: String) -> Request(String)
pub fn create_user_response(response: Response(String)) -> Result(User, ApiError)
```

Accepting an HTTP-sending callback instead couples a package to incompatible
transport shapes on Erlang and JavaScript.

### Use purpose-specific opaque FFI types

Do not use `gleam/dynamic.Dynamic` as a catch-all for arbitrary foreign
values. If a foreign value has no existing Gleam representation, declare an
opaque type for that purpose. `Dynamic` would incorrectly promise that every
Gleam value is valid input.

```gleam
pub type Buffer
pub fn byte_size(data: Buffer) -> Int
```
