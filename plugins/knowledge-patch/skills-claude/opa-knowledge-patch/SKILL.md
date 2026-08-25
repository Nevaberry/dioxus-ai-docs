---
name: opa-knowledge-patch
description: Open Policy Agent (OPA)
version: 1.18.0
license: MIT
metadata:
  author: Nevaberry
---


# Open Policy Agent Knowledge Patch

Load this skill when migrating Rego to v1, upgrading an OPA deployment,
embedding OPA in Go, building bundles, or investigating changed evaluation,
testing, plugin, security, and observability behavior.

Treat the application's manifests, configuration, policies, tests, and observed
runtime behavior as primary evidence. Use the references below for changed
defaults, compatibility traps, corrected behavior, and newly available APIs.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migration and Rego](references/migration-and-rego.md) | Rego v1 migration, syntax, safety, built-ins, schemas, and rule semantics |
| [CLI, Testing, and Bundles](references/cli-testing-and-bundles.md) | `opa check`, `fmt`, `test`, `eval`, REPL behavior, bundle builds, Wasm, and coverage |
| [Evaluation and Built-ins](references/evaluation-and-builtins.md) | Partial evaluation, SQL filters, cancellation, caching, HTTP, indexes, and corrected results |
| [Go SDK and Tooling](references/go-sdk-and-tooling.md) | Go imports and toolchains, SDK options, AST/oracle APIs, custom built-ins, and metadata |
| [Observability and Decision Logs](references/observability-and-decision-logs.md) | Decision-log delivery, masking, labels, metrics, tracing, and file logging |
| [Server, Plugins, and Security](references/server-plugins-and-security.md) | Network defaults, REST plugins, configuration, credentials, TLS, resource limits, and security fixes |

## Breaking changes and migration hazards

### Migrate Rego v1 syntax deliberately

Rules with bodies require `if`, multi-value rules require `contains`, and
`in`, `every`, `if`, and `contains` are keywords. Imports that shadow or
duplicate other imports fail compilation, as do variables or rules named
`input` or `data`. Use a current binary to check and rewrite legacy source:

```sh
opa check --v0-v1
opa check --v0-v1 --strict
opa fmt --write --v0-v1
regal lint
```

During a mixed-version bundle rollout, upgrade bundle producers before
consumers. Keep policies v0-compatible while v0 consumers remain, and use
`--v0-compatible` whenever a v1 consumer loads a bundle whose producer could
not record a Rego version.

### Make assignment inputs independently safe

The right side of `:=` must be safe before assignment. A later constraint on
the assigned variable does not make the source variable safe:

```rego
allow if {
	y = 7
	x := y
	x == 7
}
```

Rewrite policies that relied on `x := y; x = 7`, which now fails with
`rego_unsafe_var_error`. Explicit reference iteration such as
`some k; v := obj[k]` remains valid.

### Keep partial rule kinds consistent

Do not define one name as both a partial set and a partial object. Rename one
rule or make all definitions produce the same kind:

```rego
p contains "item" if true
p["key"] := "value" if true
```

These definitions can no longer coexist.

### Re-test corrected evaluation paths

Upgrades can change results for policies affected by earlier implementation
bugs. Pay particular attention to:

- partial evaluation involving default functions, `every`, nested
  comprehensions, copy propagation, or internal residual variables;
- Wasm evaluation of reference-head rules;
- overlapping indexed array and scalar rules;
- `graph.reachable_paths`, which now returns all reachable paths;
- two-variable membership over sets; and
- arithmetic or formatting of integers larger than 64 bits.

### Adapt server and integration assumptions

`opa run --server` binds to localhost unless `--addr` is explicit:

```sh
opa run --server --addr 0.0.0.0:8181
```

OPA server routing uses `http.ServeMux`, so Go integrations coupled to the old
router may need changes. HTTP servers also enforce a 32-second
`ReadHeaderTimeout`. Validate clients and intermediaries that send headers
slowly.

Startup now warns about unknown configuration keys. Inspect those warnings,
including `Config.Warnings` in Go embedders, so misspellings such as
`decision_log` do not remain unnoticed.

### Update external protocol assumptions

Outbound HTTP requests use this product token:

```text
User-Agent: Open-Policy-Agent/<version> (<os>, <arch>)
```

Update exact-match log filters and WAF rules. Compile API deployments emitting
PostgreSQL filters must also use the corrected SQL encoder before allowing
dynamic reference keys to influence identifier positions.

## High-value Rego capabilities

### Use expression interpolation

Prefix a quoted template with `$` and place expressions in braces. Undefined
expressions render as `<undefined>` rather than making the rule undefined:

```rego
message := $"User {input.username} has role {input.role}"
```

### Opt in to improved negation semantics

Import `future.keywords.not` whenever a policy uses `not` and should place all
compiler-expanded parts of a composite expression inside the negated body:

```rego
import future.keywords.not

allow if {
	not blocked(input.user)
}
```

Unlike older future-keyword imports under Rego v1, this import selects changed
behavior: undefined nested input or calls make `not` succeed.

### Use newer data helpers

- `array.flatten` flattens nested arrays; require at least 1.13.1 because
  1.13.0 mishandles single-item arrays.
- `uri.parse` returns RFC 3986 components and `uri.is_valid` reports malformed
  inputs.
- `strings.split_n` selects the first `n` fields for positive `n`, the last
  `abs(n)` fields for negative `n`, all available fields when the magnitude is
  too large, and an empty array for zero.
- `time.parse_duration_ns` accepts days, weeks, and years.
- `json.match_schema` accepts array-rooted documents; recursive schemas,
  `$ref` within `allOf`, and `pattern` validation are supported.

## High-value operations guidance

### Check bundles and preserve compatibility metadata

Use `opa check --bundle` to detect conflicts between base documents and
virtual documents. For mixed-version bundles, recheck per-module Rego version
selection and overlapping `file_rego_versions` patterns. API-created bundles
receive a default Rego version when one is omitted.

Optimized bundle entrypoints must contain at least a package and rule:

```sh
opa build -O=1 -e=authz/allow .
```

### Control testing and formatting changes

Tests run in parallel by default; use `--parallel=1` for order-sensitive
suites. Parameterized tests can generate named cases in the test-rule head,
and test output may be streamed. Coverage reports now use source ranges and
track inline heads and conjunctions, so rebaseline location and total
expectations after upgrading.

Use 1.18.2 or later before accepting formatter diffs in the 1.18 line. It
restores intended one-line formatting for single-item collections while
retaining fixes for comment-adjacent `with` clauses.

### Prefer patched point releases

Use the patched point release called out for a release line when relying on
distributed binaries or images. Several point releases restore missing
capability files or logs, fix shutdown hangs and memory leaks, correct
formatting or built-in behavior, and rebuild with Go standard-library security
fixes. Self-built artifact security depends on the selected Go toolchain.

## Working method

1. Determine the deployed OPA version, distribution source, Rego mode, and
   bundle producer versions from project evidence.
2. Read the topic reference that matches the change under investigation.
3. Apply version-specific guidance only where the project's version and mode
   make it relevant.
4. Re-run policy checks, tests, bundle validation, and integration tests that
   exercise corrected behavior.
5. Inspect startup warnings, logs, metrics, and decision output for changed
   configuration or result shapes.
