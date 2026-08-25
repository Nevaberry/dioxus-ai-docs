# Bundles, Partial Evaluation, and Wasm

## Rego versions in bundles

### Upgrade producers before consumers (`1.0-migration`)

Upgrade bundle producers first so manifests carry their Rego version. Bundles
built by OPA v0.64.0 or later contain `rego_version`, and that embedded value
takes precedence over `--v1-compatible`.

While v0 consumers remain, keep policies v0-compatible and run v1 producers
with `--v0-compatible`, unless modules explicitly import `rego.v1`. Conversely,
a v1 consumer loading a bundle from a v0 producer needs `--v0-compatible`
because that producer cannot declare a Rego version.

### Honor runtime mode for uploaded policy (`1.0.0`)

Policy uploaded through the REST policy API uses the runtime's configured Rego
version. Treat API-loaded modules and filesystem or bundle modules as governed
by the same v0/v1 server setting.

### Account for the bundle API default (`1.5.0`)

The bundle API supplies a default Rego version when callers omit one. Embedded
producers must not assume that an unspecified value remains unset in the
resulting manifest metadata.

### Resolve versions per module (`1.18.0`)

Bundle handling corrects per-module Rego-version lookup and resolves overlapping
`file_rego_versions` patterns deterministically. Recheck mixed-version bundles
and manifests whose patterns overlap because a module's selected version can
change.

## Building and validating bundles

### Use multi-term optimized entrypoints (`1.3.0`)

Optimized builds reject single-term entrypoint paths. Specify at least a package
and rule:

```sh
opa build -O=1 -e=authz/allow .
```

### Detect base/virtual document conflicts (`1.6.0`)

`opa check --bundle` rejects paths where JSON or YAML base documents overlap
virtual documents produced by Rego rules. Resolve the ambiguous path before
building or distributing the bundle.

```sh
opa check --bundle ./bundle
```

### Validate polling intervals (`1.12.0`)

Bundle-plugin configuration validates polling intervals, preventing a malformed
value from causing nanosecond-level polling.

### Select plan representation (`1.19.0`)

`opa build --format` selects protobuf or JSON for a plan bundle's plan
representation.

## Compile API SQL filters

### Compile Rego to PostgreSQL (`1.9.0`)

Declare data references that must stay unknown in document-scoped compile
metadata, then request the PostgreSQL response media type.

```rego
package filters

# METADATA
# scope: document
# compile:
#   unknowns: [input.fruits]
include if input.fruits.name == input.favorite
```

```http
POST /v1/compile/filters/include HTTP/1.1
Content-Type: application/json
Accept: application/vnd.opa.sql.postgresql+json

{"input":{"favorite":"pineapple"}}
```

Read `result.query` from the response; it contains a filter such as
`WHERE fruits.name = E'pineapple'`.

### Upgrade SQL-filter encoders (`1.19.0`)

The PostgreSQL encoder now quotes non-bare field-name segments and escapes
embedded quotes in partially evaluated references. Earlier encoders could
place caller-controlled dynamic keys such as `input.fruits[input.column]`
verbatim in identifier positions, allowing SQL injection. Ordinary bare column
names remain unquoted and case-insensitive.

## Partial evaluation

### Opt in to nondeterministic built-ins (`1.1.0`)

Partial evaluation can evaluate nondeterministic built-ins when explicitly
enabled. The option is available through Topdown, the Rego API, and server
evaluation; leave it disabled when reproducible residual policy is required.

### Keep support modules in v0 mode (`1.1.0`)

`opa eval --v0-compatible` applies that mode to partial-evaluation support
modules as well as the main query.

### Re-evaluate default functions (`1.4.0`)

Partial evaluation now handles default functions correctly. Residual policy or
results for rules depending on a default function can differ from older output.

### Expect wall-clock time in `PartialRun` (`1.4.0`)

Topdown `PartialRun()` initializes wall-clock time. Embedded partial evaluation
that invokes time-dependent built-ins can produce corrected results.

### Re-run queries involving `every` (`1.18.0`)

Partial evaluation correctly handles `future.keywords.not` negation inside
`every` and namespaces variables in comprehensions nested in `every`. Regenerate
and re-test affected residual policy.

### Re-run copy-propagation cases (`1.19.0`)

Partial evaluation no longer exposes internal variables in residual results or
creates circular references when copy propagation crosses a call. Do not
compare affected residual policy byte-for-byte with older output.

## Wasm compilation and evaluation

### Preserve `print` when needed (`1.0.0`)

Use the `opa build` option that retains `print` statements when targeting
`wasm`; otherwise do not assume debugging output survives compilation.

### Recheck reference-head results (`1.3.0`)

The planner no longer applies an over-eager optimization to affected
reference-head rules. Wasm and non-Wasm evaluation now agree, so upgrading may
change Wasm results for policy that encountered the bug.

### Build without a C toolchain (`1.18.0`)

The `wasm` target and WASM SDK use the pure-Go wazero runtime instead of
`wasmtime-go`. Wasm-enabled builds no longer require cgo or a C toolchain.

### Preserve package annotations (`1.19.0`)

Wasm bundle compilation retains package annotations. Metadata-dependent tooling
can consume package-scoped annotations after `opa build` instead of losing
them.
