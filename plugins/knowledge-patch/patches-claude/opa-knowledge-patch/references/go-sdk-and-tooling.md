# Go SDK and Tooling

Use this reference for Go import migration, build toolchains, SDK evaluation
options, AST and oracle tooling, server embedding, and custom extension points.

## Imports and builds

### Move every OPA import to `/v1/` (`1.0-migration`)

OPA v1 packages insert `/v1/` into their import path. Migrate every dependency,
including `rego`, `sdk`, `ast`, `bundle`, `compile`, `types`, and `topdown`:

```go
import "github.com/open-policy-agent/opa/v1/rego"
```

The old package paths are deprecated but remain for the lifetime of OPA 1.0.

### Meet the source-build floor (`1.0.0`)

Building OPA from source, or as part of a Go integration, requires Go 1.22 or
newer.

### Reproduce the 1.9 build (`1.9.0`)

OPA 1.9.0 moved its build toolchain to Go 1.25.1. Use that version when exact
reproducibility of its source build matters.

### Reproduce the 1.12 build (`1.12.0`)

OPA 1.12.0 moved its build toolchain from Go 1.25.4 to Go 1.25.5. Use Go
1.25.5 for matching source builds.

### Use the 1.13 security rebuild (`1.13.0`)

OPA 1.13.2 binaries and images use Go 1.25.7, whose standard library fixes
GO-2026-4337. Use at least 1.13.2 when relying on distributed artifacts.

### Reproduce the 1.15 build (`1.15.0`)

OPA 1.15.0 moved its build toolchain to Go 1.26.1.

### Use the 1.19 security rebuild (`1.19.0`)

OPA 1.19.0 artifacts use Go 1.26.5. Version 1.19.1 is otherwise identical but
uses Go 1.26.6 to fix standard-library vulnerabilities reachable through the
HTTP handler and cryptographic built-ins. Self-built binaries and images
depend on their selected Go toolchain.

## Evaluation options

### Wrap `http.send` transports (`1.0.0`)

Use eval-level `EvalHTTPRoundTrip` or query-level `WithHTTPRoundTrip` to wrap
the `http.Transport` configured by Topdown and return an `http.RoundTripper`.
The wrapper controls requests issued by the `http.send` built-in.

### Provide a base cache (`1.2.0`)

The Rego and Topdown APIs accept a caller-supplied base cache, allowing an
embedded evaluator to choose the cache for an evaluation.

### Pass map data without constructing a store (`1.13.0`)

Use `rego.Data` to add map-backed data directly:

```go
r := rego.New(
	rego.Query("data.authz.allow"),
	rego.Data(map[string]any{"roles": []any{"admin"}}),
)
```

### Select JSON generation per evaluation (`1.17.0`)

Supply the Rego `GenerateJSON` function per evaluation when separate calls
through one integration need different JSON-generation behavior.

### Select transport per SDK decision (`1.19.0`)

The Go SDK can provide a different HTTP `RoundTripper` for each `Decision`,
allowing request-specific transport behavior during policy evaluation.

## AST conversion and source tooling

### Convert strings and values directly (`1.2.0`)

`ast.InterfaceToValue` accepts both `[]string` and an existing `ast.Value`,
removing the need for an intermediate conversion.

### Use the public policy oracle (`1.2.0`)

Import the oracle from `github.com/open-policy-agent/opa/v1/ast/oracle`.
Callers can pass an existing compiler instead of relying on an internally
created compiler.

### Preserve source positions for `some` (`1.5.0`)

Compiler reference resolution retains the `Location` field on `SomeDecl`
nodes. AST-based tooling can preserve their original source positions.

### Expect less escaping in reference strings (`1.5.0`)

AST reference-to-string conversion uses a JSON-escaped literal only when
needed. Tools comparing serialized references can observe fewer escapes after
upgrading.

### Resolve more definition forms (`1.6.0`)

The policy oracle supports `some` and `every`, and `FindDefinition` supports
object references. Tooling no longer needs to classify those forms as
unsupported.

### Inspect definitions inside negation (`1.18.0`)

Inner `ast.Not` expressions carry source locations, and the policy oracle can
find definitions within them. Editors and analyzers no longer need to treat
negated expressions as location or definition blind spots.

## Server and plugin embedding

### Adapt direct routing integrations (`1.6.0`)

OPA server routing uses `http.ServeMux` instead of `gorilla/mux`. Go programs
that couple directly to the server's router can break and need adaptation.

### Register custom built-ins before concurrency (`1.6.0`)

`RegisterBuiltin` is not thread-safe. Finish custom built-in registration
before evaluations or any other callers access the registry concurrently.

### Carry custom API metadata (`1.17.0`)

Wrapping servers can read extra top-level request keys from
`BuiltinContext.RequestMetadata`. Custom built-ins can write
`BuiltinContext.ResponseMetadata`. Request metadata is logged beneath
`custom.request_metadata`; non-empty response metadata is returned to the
caller and logged. The same plumbing covers the Data and Compile API handlers.
Use namespaced keys to avoid future collisions.

```json
{"input":{"user":"alice"},"com.example.opa/metadata":{"corp-id":"acme-42"}}
```

### Resolve external rules by prefix (`1.19.0`)

External rule sources can distinguish an absent rule from an unknown value and
can be parameterized by reference prefix. Use this to represent externally
resolved namespaces without conflating absence and unknown.
