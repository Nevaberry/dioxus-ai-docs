# CLI, Automation, and Libraries

## Concise and JSON command output (`1.7.0`)

`tofu plan -concise` omits state-refresh logs. `tofu init -json` and
`tofu get -json` expose machine-readable output for automation.

OpenTofu follows the XDG Base Directory Specification, allowing its files to
use standard XDG locations instead of product-specific home-directory paths.

## Generated configuration and provider schemas (`1.8.0`)

`tofu plan -generate-config-out=generated.tf` emits JSON-shaped values as
`jsonencode(...)`, not quoted JSON strings. `TF_STATE_PERSIST_INTERVAL`
configures the state-write interval. `tofu providers schema -json` includes
provider-defined function schemas.

## Go distribution and registry libraries (`1.8.0`)

TofuDL locates the latest OpenTofu release, verifies its signature, downloads
it, and extracts the binary. Its tooling can mirror releases into air-gapped
environments. The experimental `libregistry` library provides structured
registry metadata access and building blocks for independent registry tools.

## Plan exclusions (`1.9.0`)

`tofu plan -exclude=ADDRESS` skips the selected object and everything that
depends on it. This complements `-target=ADDRESS`, which includes selected
objects and their requirements.

## Disclosure and diagnostics (`1.9.0`)

`-show-sensitive` unmasks sensitive values for `tofu plan`, `tofu apply`, and
other commands returning configuration or state. Treat its output as secret.
Use `-consolidate-warnings` and `-consolidate-errors` to control diagnostic
summarization.

`tofu console` accepts multiline expressions inside brackets or across
backslash-escaped newlines.

## Reusable selectors and concise apply (`1.10.0`)

`-target-file` and `-exclude-file` read lists of resource-instance addresses.
`tofu apply -concise` suppresses progress-like output while retaining final
results, which is useful for non-streaming automation.

```text
tofu plan -target-file=targets.txt
tofu plan -exclude-file=deferred.txt
tofu apply -concise
```

## Explicit state and plan display (`1.10.0`)

Use explicit input selection for scripts:

```text
tofu show -state
tofu show -plan=PLANFILE
```

The older positional form for a saved plan remains supported.

## Experimental initialization tracing (`1.10.0`)

Environment-controlled OpenTelemetry tracing can send partial `tofu init`
traces to a collector operated by the user. Support is experimental and the
trace currently contains limited detail.

## Configuration JSON without a plan (`1.11.0`)

`tofu show -json -config` emits a machine-readable configuration summary
without first creating a plan. Add `-module=DIR` to inspect one module.
Configuration JSON includes each input variable's type constraint and whether
it is required.

```text
tofu show -json -config
tofu show -json -config -module=modules/example
```

## Validation and registry request controls (`1.11.0`)

`tofu validate` can validate non-root modules that declare extra provider
configurations through `configuration_aliases`. Registry retry counts and
request timeouts can be configured in CLI configuration as well as with
environment variables.

## Simultaneous terminal and JSON output (`1.12.0`)

`-json-into=FILENAME` writes the same streaming machine output as `-json` while
preserving human-readable output on stdout. The destination can be a normal
file or an IPC object such as a named pipe or `/dev/fd/N`.

```text
tofu plan -json-into=plan-events.json
```

## Destroy and console controls (`1.12.0`)

`tofu destroy -suppress-forget-errors` suppresses errors for objects forgotten
during destroy and exits successfully. `tofu console` accepts `-lock=false` and
`-lock-timeout=DURATION`.

```text
tofu destroy -suppress-forget-errors
tofu console -lock-timeout=30s
```

## Environment compatibility (`1.12.0`)

`OPENTOFU_USER_AGENT`, which completely replaced the default HTTP User-Agent,
has been removed. On Unix, `tofu login` honors `BROWSER` when it names a single
command that accepts the URL as its only argument. An inherited environment
value can therefore change how the login browser launches.
