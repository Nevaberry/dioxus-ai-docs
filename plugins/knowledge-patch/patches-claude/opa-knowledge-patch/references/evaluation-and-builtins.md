# Evaluation and Built-ins

Use this reference for partial evaluation, Compile API SQL filters, evaluation
caches and cancellation, HTTP behavior, corrected indexing, and changed result
semantics.

## Partial evaluation

### Opt in to nondeterministic built-ins (`1.1.0`)

Partial evaluation can evaluate nondeterministic built-ins when explicitly
enabled. The opt-in is available through Topdown, the Rego API, and server
evaluation. Leave it disabled when residual policy must not embed
nondeterministic results.

### Keep support modules in v0 mode (`1.1.0`)

`opa eval --v0-compatible` applies that compatibility mode to support modules
generated during partial evaluation. Callers no longer need to compensate for
support modules being parsed in a different mode.

### Recheck default functions (`1.4.0`)

Partial evaluation handles default functions correctly. Residual policy and
results for rules depending on a default function can differ from older,
incorrect output.

### Initialize time in `PartialRun` (`1.4.0`)

Topdown `PartialRun()` initializes wall-clock time. Embedded partial
evaluations that call wall-clock-dependent built-ins can produce corrected
results after upgrading.

### Re-run queries involving `every` (`1.18.0`)

Partial evaluation correctly handles `future.keywords.not` inside `every` and
namespaces variables in comprehensions nested inside `every`. Re-run affected
queries because their residual policy or results can change.

### Re-run copy-propagation cases (`1.19.0`)

Partial evaluation no longer exposes internal variables in residual results
and no longer creates circular references when copy propagation crosses a
call. Regenerate and review residual policy for affected queries.

## Compile API SQL filters

### Translate Rego into PostgreSQL filters (`1.9.0`)

The Compile API can translate a Rego query into a PostgreSQL filter. Declare
references that must remain unknown in document-scoped compile metadata:

```rego
package filters

# METADATA
# scope: document
# compile:
#   unknowns: [input.fruits]
include if input.fruits.name == input.favorite
```

Request the SQL response with the PostgreSQL media type:

```http
POST /v1/compile/filters/include HTTP/1.1
Content-Type: application/json
Accept: application/vnd.opa.sql.postgresql+json

{"input":{"favorite":"pineapple"}}
```

The response places a filter such as `WHERE fruits.name = E'pineapple'` in
`result.query`.

### Use the injection-safe encoder (`1.19.0`)

The PostgreSQL encoder quotes non-bare field-name segments and escapes embedded
quotes when partially evaluated references become SQL. Earlier encoders could
place caller-controlled dynamic keys such as `input.fruits[input.column]`
verbatim into identifier positions, enabling SQL injection. Ordinary column
names remain unquoted and case-insensitive. Upgrade any deployment that lets
dynamic reference keys influence generated filters.

## Evaluation lifecycle and caching

### Distinguish cancellation from timeout (`1.0.0`)

Evaluation errors distinguish a canceled context from a timeout. Callers
should branch on the actual termination reason rather than treating both as a
single generic failure.

### Cancel expensive string built-ins (`1.12.0`)

`regex.replace`, `replace`, `strings.replace_n`, and `concat` observe
evaluation-context cancellation. Propagate a cancellable context when those
operations may process large inputs.

## HTTP evaluation

### Accept lenient JSON content types (`1.6.0`)

Topdown HTTP response handling matches `application/json` content types
leniently. A response no longer needs the previously strict header form to be
decoded as JSON.

## Result and rule semantics

### Omit synthetic wildcard values (`1.5.0`)

OPA does not generate JSON values for wildcard or generated keys in Rego
result sets. Consumers must not depend on synthetic values for those keys.

### Recheck indexed array/scalar overlap (`1.15.0`)

The AST rule index correctly handles overlapping array and scalar patterns.
Candidate selection and results can change for policies that rely on such
overlapping indexed rules.

### Return every reachable path (`1.17.0`)

`graph.reachable_paths` returns all reachable paths. Policies and tests that
consumed incomplete earlier output can observe additional paths.
