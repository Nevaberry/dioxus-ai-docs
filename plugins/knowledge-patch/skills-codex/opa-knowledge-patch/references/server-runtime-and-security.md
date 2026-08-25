# Server Runtime and Security

## Network exposure and HTTP behavior

### Bind explicitly for remote access (`1.0-migration`)

`opa run --server` binds to localhost instead of all interfaces. When a host,
another container, or a remote service must connect, opt in to that exposure:

```sh
opa run --server --addr 0.0.0.0:8181
```

Protect the newly exposed listener with the deployment's intended network and
authentication controls.

### Adapt to `http.ServeMux` routing (`1.6.0`)

The OPA server uses Go's `http.ServeMux` instead of `gorilla/mux`. Embedders that
touch router internals, route variables, or matching behavior must adapt and
re-test their integration.

### Accept ordinary JSON content types (`1.6.0`)

Topdown HTTP evaluation matches `application/json` content types leniently.
Responses no longer need the earlier exact header form to be decoded as JSON.

### Account for the header deadline (`1.19.0`)

All OPA HTTP servers set `ReadHeaderTimeout` to 32 seconds. Clients or
intermediaries that take longer to send complete request headers may be
disconnected.

## Configuration and resource control

### Inspect unknown-option warnings (`1.19.0`)

OPA warns about unrecognized configuration keys instead of silently ignoring
them; intentionally extensible sections are exempt. Go embedders using
`config.ParseConfig` can read the same messages through `Config.Warnings`.
Treat warnings such as `decision_log` instead of `decision_logs` as deployment
errors.

### Let container limits tune the Go runtime (`1.18.0`)

OPA sets `GOMAXPROCS` from container-aware CPU limits and `GOMEMLIMIT` from
container-aware memory limits. Include these automatically selected values when
sizing a deployment or diagnosing CPU, memory, or garbage-collection behavior.

### Reject excessive parser recursion (`1.5.0`)

The parser enforces a recursion-depth guard. Handle a parse error for deeply
nested untrusted input instead of assuming arbitrary depth is accepted.

### Preserve custom version provenance (`1.5.0`)

The runtime does not overwrite caller-supplied `commit` or `timestamp` fields
in version information, so custom builds retain injected provenance.

## Security upgrades

### Close Data API path injection (`1.4.0`)

OPA 1.4.0 fixes CVE-2025-46569 in earlier standalone servers. If
attacker-controlled text reaches a Data API HTTP path, injected Rego could
redirect the requested path, force success or failure, or consume excessive
compute. Exposure includes authorization policy that does not exactly match
`input.path` and intermediaries that copy unsanitized third-party text into the
path. Upgrade rather than attempting to sanitize around the parser flaw.

### Use the complete patched 1.4 release (`1.4.0`)

OPA 1.4.1 moves to Go 1.24.2 to address CVE-2025-22870 and CVE-2025-22871 but
omits `capabilities/v1.4.1.json`. OPA 1.4.2 restores the capability file, so
tooling that reads versioned capabilities should move directly to 1.4.2.

### Use the Go security rebuild (`1.13.0`)

OPA 1.13.2 binaries and images use Go 1.25.7, whose standard library fixes
GO-2026-4337. Use at least 1.13.2 when relying on distributed artifacts.

### Use patched plugin and HTTP releases (`1.17.0`)

OPA 1.16.0 restores plugin-originated logging lost in 1.15.x but can hang during
plugin-manager shutdown; 1.16.1 fixes it. OPA 1.17.1 distributed binaries and
images use Go 1.26.4 to fix standard-library vulnerabilities exercised by the
HTTP handler and crypto built-ins. Self-built artifacts depend on their chosen
Go toolchain.

### Avoid the annotation leak (`1.18.0`)

OPA 1.18.1 fixes an `AnnotationSet` memory leak introduced in 1.17.0. Upgrade
long-running servers that show excess memory use instead of remaining on
1.18.0.

### Use the later Go security rebuild (`1.19.0`)

OPA 1.19.1 is otherwise identical to 1.19.0 but uses Go 1.26.6 instead of
1.26.5 to fix standard-library vulnerabilities reachable through the HTTP
handler and cryptographic built-ins. A self-built binary or image depends on
the Go version selected by its builder.

## Runtime API consistency

### Apply the configured Rego version to uploads (`1.0.0`)

Policies uploaded through the REST policy API honor the runtime's selected
Rego version. Set the server's v0/v1 mode with both uploaded and bundled modules
in mind.

### Cancel long-running built-ins (`1.12.0`)

`regex.replace`, `replace`, `strings.replace_n`, and `concat` observe evaluation
context cancellation. Deadlines and canceled requests can interrupt these
operations rather than waiting for completion.

### Distinguish cancellations and timeouts (`1.0.0`)

Evaluation errors differentiate a canceled context from a timeout. Server and
embedding layers can map the actual reason to different retry, response, and
logging behavior.
