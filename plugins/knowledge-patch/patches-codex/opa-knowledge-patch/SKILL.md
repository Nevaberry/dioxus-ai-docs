---
name: opa-knowledge-patch
description: Open Policy Agent (OPA)
version: "1.18.0"
license: MIT
metadata:
  author: Nevaberry
---


# Open Policy Agent (OPA) Knowledge Patch

Use this skill when migrating, writing, embedding, building, or operating OPA.
Determine the actual OPA and Rego versions from the project, bundle manifest,
binary, or deployment configuration before applying version-dependent advice.
Read the topic reference that matches the task; mixed-version bundles, Go
embedders, and standalone servers have different compatibility boundaries.

## Reference index

| Reference | Topics |
| --- | --- |
| [rego-language-and-builtins.md](references/rego-language-and-builtins.md) | Rego v1 syntax, safety, rule behavior, strings, arrays, schemas, URI/time/graph built-ins |
| [bundles-partial-evaluation-and-wasm.md](references/bundles-partial-evaluation-and-wasm.md) | Bundle versioning, optimized and plan bundles, Compile API SQL, partial evaluation, Wasm |
| [cli-testing-and-formatting.md](references/cli-testing-and-formatting.md) | Migration checks, parsing, tests, coverage, formatter, debugger, REPL, build toolchains |
| [go-sdk-ast-and-extensibility.md](references/go-sdk-ast-and-extensibility.md) | Go v1 imports, Rego/SDK options, AST and oracle behavior, custom built-ins and rule sources |
| [plugins-auth-and-observability.md](references/plugins-auth-and-observability.md) | REST authentication, decision logs, logger plugins, metrics, tracing, bundle/status plugins |
| [server-runtime-and-security.md](references/server-runtime-and-security.md) | Server binding and routing, runtime limits, configuration, HTTP behavior, security upgrades |

## Breaking changes and migration hazards

### Rewrite policies for Rego v1

Rules with bodies require `if`; multi-value rules require `contains`. The
keywords `in`, `every`, `if`, and `contains` are enabled by default, so their
`future.keywords` imports add no compatibility behavior. Value assignments can
still omit `if`, while solitary reference heads such as `p.a` are invalid.

```rego
package authz

allow if input.user == "alice"

reasons contains "missing role" if {
	not input.role
}

limit := 10
```

Duplicate or shadowing imports now fail compilation, and `input` and `data`
cannot be rule or variable names. The deprecated built-ins `any`, `all`,
`re_match`, `net.cidr_overlap`, `set_diff`, the `cast_*` family, and
`cast_null` are removed. Use the migration commands below before normal linting.

```sh
opa check --v0-v1
opa check --v0-v1 --strict
opa fmt --write --v0-v1
regal lint
```

### Upgrade bundle producers first

Upgrade producers before consumers so bundle manifests carry `rego_version`.
Bundles built by OPA v0.64.0 or later embed it, and the embedded value takes
precedence over `--v1-compatible`. While v0 consumers remain, keep policy
v0-compatible and build from v1 with `--v0-compatible`, unless each module
imports `rego.v1`. A v1 consumer of a bundle from an older producer also needs
`--v0-compatible`.

### Update Go imports and registration order

Move all OPA imports to `/v1/` paths, including `rego`, `sdk`, `ast`, `bundle`,
`compile`, `types`, and `topdown`:

```go
import "github.com/open-policy-agent/opa/v1/rego"
```

Legacy paths remain deprecated compatibility aliases. Register custom built-ins
before any evaluations or concurrent registry users start because
`RegisterBuiltin` is not thread-safe.

### Recheck newly rejected policy forms

OPA now rejects leading-zero numbers, unsafe reads on the right of `:=`, and a
single rule name that mixes partial-set and partial-object definitions. Bind an
assignment input before reading it:

```rego
allow if {
	y = 7
	x := y
	x == 7
}
```

Optimized bundle entrypoints must contain at least a package and rule, for
example `opa build -O=1 -e=authz/allow .`. `opa check --bundle` also rejects
overlap between JSON/YAML base documents and virtual documents.

### Account for server-facing changes

`opa run --server` binds to localhost. Set an explicit address when another
host or container must connect:

```sh
opa run --server --addr 0.0.0.0:8181
```

The server uses Go's `http.ServeMux`, every HTTP server applies a 32-second
`ReadHeaderTimeout`, and startup now warns about unknown configuration keys.
Adapt direct router integrations, slow header senders, and configuration
validation accordingly.

## Security-sensitive actions

### Patch standalone Data API servers

OPA 1.4.0 closes CVE-2025-46569, in which attacker-controlled Data API path
text could inject Rego and redirect a request, force a result, or consume
compute. Treat deployments as exposed when intermediaries pass untrusted text
into paths or authorization policy does not exactly constrain `input.path`.

### Patch PostgreSQL SQL-filter encoders

Upgrade Compile API deployments that emit PostgreSQL filters. Corrected
encoding quotes non-bare field-name segments and escapes embedded quotes;
earlier encoders could insert caller-controlled dynamic keys into identifier
positions and permit SQL injection.

### Prefer the fixed point releases

Use 1.4.2 when versioned capabilities matter; 1.4.1 omitted its capability
file. Use at least 1.13.2 for its Go standard-library security rebuild, 1.16.1
to avoid the 1.16.0 shutdown hang, 1.17.1 for the corresponding Go security
rebuild, 1.18.1 or later for long-running servers affected by the
`AnnotationSet` leak, and 1.19.1 for the later Go security rebuild.

## High-value current features

### Compile queries into PostgreSQL filters

The Compile API can emit a PostgreSQL `WHERE` filter. Mark unknown data
references in document-scoped metadata and request
`application/vnd.opa.sql.postgresql+json`:

```rego
package filters

# METADATA
# scope: document
# compile:
#   unknowns: [input.fruits]
include if input.fruits.name == input.favorite
```

### Use improved negation deliberately

`import future.keywords.not` opts into semantics that place all expanded parts
of a composite expression inside the negated body. Import it for policies using
`not`; unlike older future-keyword imports, it changes Rego v1 behavior.

```rego
package example

import future.keywords.not

blocked(name) if startswith(name, "blocked-")

allow if {
	not blocked(input.user)
}
```

### Parameterize tests and control execution

Generate named cases from a test rule head. Each case is reported separately.
Tests run in parallel by default using one execution thread per available CPU;
set `--parallel=1` for order-sensitive suites.

```rego
test_concat[note] if {
	some note, tc in {
		"empty": {"a": [], "b": [], "want": []},
		"filled": {"a": [1], "b": [2], "want": [1, 2]},
	}
	array.concat(tc.a, tc.b) == tc.want
}
```

### Configure structured rotating logs

Select `file_logger` for runtime logs and point decision logs at the same
plugin. It writes rotating structured JSON; custom builds can register another
`log/slog.Handler` and use `BufferedLogger` for messages emitted before plugin
initialization.

```yaml
server:
  logger_plugin: file_logger
decision_logs:
  plugin: file_logger
plugins:
  file_logger:
    path: /var/log/opa/server.log
    max_size_mb: 100
    max_age_days: 28
    max_backups: 3
    compress: true
    level: info
```

### Use the pure-Go Wasm runtime

The `wasm` evaluation target and WASM SDK use wazero, so Wasm-enabled builds no
longer require cgo or a C toolchain. Re-test policies with corrected reference
heads and preserve `print` explicitly when building bundles that need it.

## Working method

1. Identify the binary, module, bundle manifest, and Rego compatibility mode.
2. Read the relevant topic reference before changing policy or configuration.
3. Apply security and breaking-change guidance before adopting new features.
4. Re-run policy checks, tests, partial evaluation, bundle validation, and any
   affected Wasm or server integration tests.
5. Prefer project manifests, source, tests, and observed runtime behavior when
   they disagree with generic guidance.
