# Go SDK, AST, and Extensibility

## Imports and evaluation options

### Move every OPA import to `/v1/` (`1.0-migration`)

OPA v1 packages insert `/v1/` into the import path. Migrate every dependency,
including `rego`, `sdk`, `ast`, `bundle`, `compile`, `types`, and `topdown`.
Legacy paths are deprecated but remain available for the lifetime of OPA 1.0.

```go
import "github.com/open-policy-agent/opa/v1/rego"
```

### Distinguish cancellation from timeout (`1.0.0`)

Evaluation errors identify a canceled context separately from a timeout. Branch
on the actual cause when deciding whether to retry, report a deadline, or stop
work permanently.

### Supply a caller-owned base cache (`1.2.0`)

The Rego and Topdown APIs accept a custom base cache. Use it when an embedded
evaluator must control cache sharing, lifetime, or memory independently of the
default.

### Add map data directly (`1.13.0`)

Use `rego.Data` to provide a map without first creating a store.

```go
r := rego.New(
	rego.Query("data.authz.allow"),
	rego.Data(map[string]any{"roles": []any{"admin"}}),
)
```

### Select JSON generation per evaluation (`1.17.0`)

Go integrations can provide the Rego `GenerateJSON` function per evaluation.
Different calls through the same integration may choose different JSON
generation behavior without rebuilding the shared evaluator.

## HTTP behavior in embedded evaluation

### Wrap `http.send` transports (`1.0.0`)

Use eval-level `EvalHTTPRoundTrip` or query-level `WithHTTPRoundTrip` to wrap the
`http.Transport` configured by Topdown and return an `http.RoundTripper`. This
customizes requests made by the `http.send` built-in.

### Customize SDK transport per decision (`1.19.0`)

The SDK can provide a distinct HTTP `RoundTripper` for every `Decision`, making
request-specific transport behavior possible during decision evaluation.

### Register built-ins before concurrency (`1.6.0`)

`RegisterBuiltin` is not thread-safe. Finish all custom built-in registration
before evaluations or other callers access the registry concurrently.

## AST conversion and source fidelity

### Convert existing values directly (`1.2.0`)

`ast.InterfaceToValue` accepts both `[]string` and an existing `ast.Value`, so
embedders can avoid an intermediate conversion.

### Expect less escaping in reference strings (`1.5.0`)

AST reference-to-string conversion emits a JSON-escaped literal only when it is
needed. Tools that compare serialized references can observe fewer escapes.

### Keep `some` source locations (`1.5.0`)

Compiler reference resolution preserves `Location` on `SomeDecl` nodes. AST
tools can keep source positions instead of reconstructing them.

### Do not expect generated wildcard JSON values (`1.5.0`)

Rego result sets no longer receive synthetic JSON values for wildcard or
generated keys. Consumers must tolerate their absence.

### Inspect definitions within negation (`1.18.0`)

Inner `ast.Not` expressions have source locations, and the policy oracle can
find definitions inside those nodes. Editors and analyzers need not treat
negated expressions as a source-location or definition blind spot.

## Capabilities and the policy oracle

### Recognize `rego_v1` in v0 capabilities (`1.4.0`)

Capabilities produced for `--v0-compatible` include the `rego_v1` feature.
Metadata consumers must not infer that v0 compatibility excludes that feature.

### Use the public oracle with an existing compiler (`1.2.0`)

Import the oracle from
`github.com/open-policy-agent/opa/v1/ast/oracle`. Callers may pass their existing
compiler rather than relying on an internally created compiler.

### Resolve additional definitions (`1.6.0`)

The policy oracle supports `some` and `every`, while `FindDefinition` supports
object references. Tooling can resolve those forms instead of reporting them as
unsupported.

## Metadata and external rule sources

### Carry custom API metadata (`1.17.0`)

Wrapping servers can read extra top-level request keys through
`BuiltinContext.RequestMetadata`, and custom built-ins can populate
`BuiltinContext.ResponseMetadata`. Request metadata is logged under
`custom.request_metadata`; non-empty response metadata is returned and logged.
The same plumbing applies to Data and Compile API handlers. Namespace keys to
avoid collisions with future fields.

```json
{"input":{"user":"alice"},"com.example.opa/metadata":{"corp-id":"acme-42"}}
```

### Use prefix-aware external rule sources (`1.19.0`)

External rule sources distinguish a missing rule from a rule whose value is
unknown and can be parameterized by reference prefix. Model externally resolved
namespaces without collapsing absence into unknown.

## Embedding the server and runtime

### Adapt direct routing integrations (`1.6.0`)

OPA's server routes through `http.ServeMux` rather than `gorilla/mux`. Go
integrations that depend directly on router internals or route matching must be
adapted and re-tested.

### Preserve custom build provenance (`1.5.0`)

The runtime does not overwrite caller-supplied `commit` and `timestamp` fields
in version information. Custom builds can retain injected provenance.
