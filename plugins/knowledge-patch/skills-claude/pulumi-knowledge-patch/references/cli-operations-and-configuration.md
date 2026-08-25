# CLI Operations and Configuration

Use this reference for local command behavior, project creation, configuration, machine-readable output, Neo, logging, and tracing.

## Engine targeting and parallelism (batch `3.145.0-3.159.0`)

Target-aware operations accept `--exclude <URN>`; add `--exclude-dependents` to omit children of the excluded resource. `PULUMI_PARALLEL` supplies `--parallel`, `PULUMI_PARALLEL_DIFF` enables concurrent diff calculations, and effective parallelism observes container cgroup limits.

`PULUMI_STACK` selects a stack for configuration and state commands without persisting `pulumi stack select`. `preview` and `up` accept `--show-secrets`, which exposes plaintext secrets in terminal and captured log output. `pulumi config set --type` selects the stored scalar type explicitly.

## Removed query and early package publication (batch `3.145.0-3.159.0`)

`pulumi query` was removed in 3.157.0. Replace scripts that call it. `pulumi new` can use templates defined in Pulumi Cloud. Package publishing was experimental in 3.158.0; do not infer current stability from that introduction.

## Run program before refresh or destroy (batch `release-notes-117`)

`pulumi refresh --run-program` and `pulumi destroy --run-program` execute the stack program before the operation, allowing changed code to establish short-lived credentials, retrieve secrets, or define dynamic providers. Without the flag, these commands incorporate changed stack configuration but not changed program code.

## Refresh-enabled previews and updates (batch `3.160.0-3.181.0`)

`PULUMI_RUN_PROGRAM` globally supplies the run-program setting. `pulumi preview --refresh` and `pulumi up --refresh` accept `--run-program`; it is tied to refresh for those two operations.

```shell
PULUMI_RUN_PROGRAM=true pulumi up --refresh
pulumi preview --refresh --run-program
```

## Diagnostics, preview output, and YAML config (batch `3.182.0-3.198.0`)

CLI diagnostics are written to stderr rather than stdout. `--show-full-output` defaults to false, and `PULUMI_ENABLE_STREAMING_JSON_PREVIEW` controls streaming JSON previews.

Pulumi YAML accepts `object` as a configuration type and parses those values as objects. The CLI warns when YAML `null` would be read as an empty string. The temporary 3.170.0 behavior that preserved YAML types was reverted in 3.174.0 and is not the final behavior.

## Registry templates and project creation (batch `3.182.0-3.198.0`)

`pulumi new` accepts qualified Registry template names and lists templates published with `pulumi template publish`. Private Registry publishing and resolution no longer need `PULUMI_EXPERIMENTAL`; set `PULUMI_DISABLE_REGISTRY_RESOLVE=true` to disable Registry resolution for `pulumi new`.

## Configuration inputs and generic flag environment variables (batch `3.199.0-3.214.0`)

`refresh` and `destroy` accept `--config` and `--config-path`. Every CLI flag can be supplied as `PULUMI_OPTION_<FLAG>`; for example, `PULUMI_OPTION_REFRESH=true` maps to `--refresh`. `pulumi about` reports `PULUMI_*` variables, and `pulumi about env` is an environment helper.

Template locations can be overridden with `PULUMI_TEMPLATE_GIT_REPOSITORY`, `PULUMI_TEMPLATE_BRANCH`, `PULUMI_POLICY_TEMPLATE_GIT_REPOSITORY`, and `PULUMI_POLICY_TEMPLATE_BRANCH`.

## JSON bulk configuration and Windows executables (batch `3.199.0-3.214.0`)

`pulumi config set-all --json` accepts bulk JSON, with `SetAllConfigJson` as the Automation API counterpart. On Windows, executable resolution searches `.cmd` and `.ps1` extensions.

## Required CLI versions and native Bun (batch `3.214.1-3.228.0`)

Projects can set `requiredPulumiVersion` in `Pulumi.yaml`. Language checks are exposed as Node.js `requirePulumiVersion`, Python `require_pulumi_version`, Go `CheckPulumiVersion`, and generated .NET `RequirePulumiVersion`.

`pulumi-language-bun` runs programs, plugins, debuggers, and policy packs with Bun as a native runtime. This is different from using Bun only as a Node.js package manager.

## Journaling and trace export (batch `3.214.1-3.228.0`)

Engine journaling is enabled by default. Set `PULUMI_DISABLE_JOURNALING=true` only to disable it explicitly.

`--otel-traces` accepts a relative file or a gRPC endpoint, including `grpcs://`; exporters support header authentication and `OTEL_RESOURCE_ATTRIBUTES`. Provider OpenTracing spans are bridged into OpenTelemetry traces.

## Machine-readable operations (batch `3.229.0-3.248.0`)

`pulumi up`, `preview`, `refresh`, `destroy`, and `import` accept `--output json`. The first four return structured affected-resource entries with URN, type, name, operation, and parent.

## Runtime-free projects and `npx` (batch `3.229.0-3.248.0`)

Projects can omit a runtime in CLI operations and Automation API project settings. `pulumi project new -y` creates a minimal project without a template, `pulumi new` aliases `pulumi project new`, and the `pulumi` package lets Node.js users run commands through `npx pulumi`.

## Direct Pulumi Cloud API calls (batch `3.229.0-3.248.0`)

`pulumi api <op-or-path>` calls a Pulumi Cloud API operation or path. It supports fields, headers, request input or body, path templates, content negotiation, and dry runs. `list` and `describe` expose the OpenAPI surface. `--paginate` combines cursor pages into one JSON envelope and `--emit-events` writes pagination progress to stderr. Use `--output`, not the earlier `--format` spelling.

## Neo terminal workflow (batch `3.229.0-3.248.0`)

`pulumi neo` is available without `PULUMI_EXPERIMENTAL`. It runs requested shell and filesystem tools locally in the working directory while the conversation is backed by Pulumi Console. It supports non-interactive `--print`, approval and permission modes, and `--disable-integrations`.

Plan mode must be chosen before the first message. Until the plan is approved, it blocks file writes, `pulumi up`, and pull-request creation.

## Automatic logs before the default changed (batch `3.229.0-3.248.0`)

This batch introduced encrypted CLI logs behind `PULUMI_ENABLE_AUTOMATIC_LOGGING`, stored under `~/.pulumi/logs`. `pulumi logs decrypt`, `logs ls`, and `logs rm` manage them. Later behavior enables capture by default.

## PCL/HCL command behavior (batch `3.229.0-3.248.0`)

The HCL language runtime is downloaded on demand rather than bundled. `pulumi convert --from hcl` installs its converter automatically.

## CLI automation and observability (batch `3.229.0-3.248.0`)

`pulumi config set --raw` preserves newlines piped through stdin. `--urns` shows full URNs in preview, up, destroy, refresh, import, and watch displays. `--skip-plugin-pre-install` bypasses eager plugin installation. `PULUMI_SKIP_CONFIRMATIONS` applies wherever the CLI asks for confirmation, and `TRACEPARENT` parents CLI spans under an existing trace.

## Automatic logging is now default (batch `3.249.0-3.254.0`)

Encrypted CLI log capture is enabled for every command by default; `PULUMI_ENABLE_AUTOMATIC_LOGGING` is no longer required. Property-value secrets are redacted. Use `pulumi logs share` to share a captured log with Pulumi.

## Per-operation environment and config validation (batch `3.249.0-3.254.0`)

`up`, `preview`, `destroy`, and `refresh` accept `--override-env` to replace imported environments for one run without changing stack configuration. They also accept `--skip-config-validation` to bypass the project's config schema for one run.

## List output formats and deployment settings removal (batch `3.249.0-3.254.0`)

`--output <format>` is supported on `pulumi stack list`, `stack history`, `stack tag list`, `policy list`, `policy group list`, `project list`, `config env list`, and `plugin list`.

The experimental local `Pulumi.<stack>.deploy.yaml` workflow was removed. The removed surface includes `deployment settings init`, `pull`, `configure`, `env`, `push`/`update`/`up`, `--config-file`, and SDK helpers that read the file. Use `pulumi deployment settings get`, `edit`, and `destroy` with Pulumi Cloud.

## Neo editor and recovery (batch `3.249.0-3.254.0`)

`pulumi neo acp` runs Neo as an Agent Client Protocol process over stdio, with read-only and plan session modes. `pulumi neo resume` restores conversation history. `--debug-update` and `--debug-preview` start investigation of failed operations.

## Machine output for non-UTF-8 strings (batch `3.249.0-3.254.0`)

Diffs and JSON output represent strings containing non-UTF-8 bytes as `b"<base64>"`, rather than emitting invalid text.

## Historical summaries and protection overrides (batch `3.255.0-3.258.0`)

`pulumi stack history events --summary` reduces a past update to the structured summary produced by `pulumi up --output json`, adding error diagnostics, failed-resource markers, and language-host program errors.

`pulumi up`, `preview`, and `destroy` accept `--ignore-protect` for a single operation that intentionally allows deletion of protected resources. It does not require first changing protection in state.

## Remote execution and project creation (batch `3.255.0-3.258.0`)

Failed `pulumi up --remote` and `pulumi deployment run` commands now exit nonzero. Remote updates no longer require a local `Pulumi.yaml`. `pulumi new` installs packages required by the generated program, matching `pulumi install`.

## Removed Pulumi AI mode (batch `3.255.0-3.258.0`)

The Pulumi AI mode of `pulumi new` was removed after its service shut down. The interactive choice and the `--ai` and `--language` flags tied to that mode are gone; use `pulumi neo` instead.

## HTTPS trace export (batch `3.255.0-3.258.0`)

The endpoint passed to `--otel-traces` may use HTTPS.
