# CLI, automation, and output

## Concise and JSON output (`1.7.0`)

`tofu plan -concise` suppresses state-refresh logs. OpenTofu 1.10 extends concise mode to apply: `tofu apply -concise` removes progress-like streaming output while retaining final results for automation.

`tofu init -json` and `tofu get -json` provide machine-readable output. From 1.8, generated configuration from `tofu plan -generate-config-out=generated.tf` renders JSON-shaped values with `jsonencode(...)` rather than quoted JSON strings.

## Simultaneous terminal and JSON streams (`1.12.0`)

`-json-into=FILENAME` writes the same machine-readable stream as `-json` while preserving ordinary human-readable output on stdout.

```bash
tofu plan -json-into=plan-events.json
```

Streaming commands can target an IPC object such as a named pipe or `/dev/fd/N`, allowing another process to consume events concurrently.

## Planning selectors (`1.9.0`, `1.10.0`)

`tofu plan -exclude=ADDRESS` skips the selected object and all objects that depend on it. This is the inverse dependency direction from `-target`, which includes selected objects and their requirements.

Use files for stable, reusable lists of addresses:

```text
tofu plan -target-file=targets.txt
tofu plan -exclude-file=deferred.txt
```

## Sensitive values and diagnostics

From 1.9, `-show-sensitive` unmasks sensitive values for `tofu plan`, `tofu apply`, and other commands that return configuration or state. Treat logs and terminals as secret-bearing whenever this flag is active.

Commands also accept `-consolidate-warnings` and `-consolidate-errors` to control diagnostic summarization.

Provider-schema deprecation warnings appear when configuration references an attribute or block marked deprecated. In 1.12, `-deprecation=` can disable those diagnostics when an automation workflow must suppress them.

## Console behavior

OpenTofu 1.9 accepts multiline `tofu console` expressions inside brackets or across backslash-escaped newlines.

OpenTofu 1.12 adds state-lock controls:

```bash
tofu console -lock=false
tofu console -lock-timeout=30s
```

## State, plan, and configuration inspection

OpenTofu 1.10 adds explicit selection forms:

```bash
tofu show -state
tofu show -plan=PLANFILE
```

The older positional plan-file form remains supported.

OpenTofu 1.11 can emit configuration JSON without first building a plan:

```bash
tofu show -json -config
tofu show -json -config -module=modules/example
```

The configuration summary includes each input variable's type constraint and whether the variable is required.

## Destroy behavior (`1.12.0`)

`tofu destroy -suppress-forget-errors` suppresses errors for objects forgotten during destroy and exits successfully. Use it only when the workflow intentionally permits state-only removal.

## Provider schemas and validation

From 1.8, `tofu providers schema -json` includes provider-defined function schemas.

From 1.11, `tofu validate` can validate a non-root module that declares extra provider configurations using `configuration_aliases`.

## XDG paths and environment variables

OpenTofu 1.7 supports the XDG Base Directory Specification, so CLI files can live in standard XDG locations.

`TF_STATE_PERSIST_INTERVAL` controls the state-write interval from 1.8.

`OPENTOFU_USER_AGENT`, which replaced the entire default HTTP User-Agent, is removed in 1.12. Delete workflows that depend on it.

On Unix, `tofu login` honors `BROWSER` when it names one command that accepts the URL as its sole argument. An inherited environment value can therefore change or break browser launch behavior.

## Registry retries and timeouts (`1.11.0`)

Configure registry retry counts and request timeouts in CLI configuration or through their environment variables. Prefer checked-in or centrally managed CLI configuration when automation needs consistent behavior across machines.

## Initialization tracing (`1.10.0`)

Experimental, environment-controlled OpenTelemetry support can send partial `tofu init` traces to a collector operated by the user. Current spans contain limited detail. Protect the collector endpoint and do not assume stable telemetry shape while the feature remains experimental.

## Backend logging cautions

From 1.9, HTTP backend trace logs contain request and response bodies. Trace capture can expose credentials, state, or other sensitive payloads; restrict access and retention.

## Force unlocking

The HTTP backend supports `tofu force-unlock` from 1.10. Confirm that no live writer owns the lock before forcing it, because removing a legitimate lock permits concurrent state writes.
