# CLI and Operations

## Targeting, safety, and concurrency

Target-aware operations accept `--exclude <URN>` and
`--exclude-dependents`. `pulumi up`, `preview`, and `destroy` accept
`--ignore-protect` for a one-operation protected-delete override. These controls
span batches `3.145.0-3.159.0` and `3.255.0-3.258.0`.

`PULUMI_PARALLEL` supplies `--parallel`, `PULUMI_PARALLEL_DIFF` enables
concurrent diff calculation, and effective parallelism respects container cgroup
limits. `PULUMI_SKIP_CONFIRMATIONS` applies anywhere the CLI asks for
confirmation.

## Program execution during engine operations

`refresh` and `destroy` accept `--run-program`; without it they incorporate
updated configuration but not changed program code. Use it for short-lived
credentials, fetched secrets, dynamic providers, or operation context created by
the program. `preview` and `up` accept it with `--refresh`, and
`PULUMI_RUN_PROGRAM` supplies the setting globally.

## Flag and environment mapping

`PULUMI_STACK` selects a stack for configuration and state commands. Every CLI
flag has a `PULUMI_OPTION_*` form, such as `PULUMI_OPTION_REFRESH`.
`pulumi about` reports `PULUMI_*` values and `pulumi about env` is an environment
helper. Template locations use `PULUMI_TEMPLATE_GIT_REPOSITORY`,
`PULUMI_TEMPLATE_BRANCH`, `PULUMI_POLICY_TEMPLATE_GIT_REPOSITORY`, and
`PULUMI_POLICY_TEMPLATE_BRANCH` (batch `3.199.0-3.214.0`).

`up`, `preview`, `destroy`, and `refresh` accept per-operation `--override-env`
and `--skip-config-validation`. Refreshing stack configuration includes imported
environments.

## Configuration input

`pulumi config set --type` chooses the stored scalar type. `set-all --json` and
Automation API `SetAllConfigJson` accept bulk JSON. `set --raw` preserves
newlines read from stdin. `refresh` and `destroy` accept `--config` and
`--config-path`.

YAML warns when `null` becomes an empty string. The short-lived 3.170.0 behavior
that preserved YAML types was reverted in 3.174.0. Pulumi YAML supports `object`
configuration and parses such values as objects.

## Machine-readable output and diagnostics

`up`, `preview`, `refresh`, `destroy`, and `import` accept `--output json`.
For the first four, the structured summary includes each affected resource's
URN, type, name, operation, and parent. `pulumi stack history events --summary`
produces that summary shape for a historical update and adds error diagnostics,
failed-resource markers, and language-host program errors.

Diagnostics go to stderr, `--show-full-output` defaults to false, and
`PULUMI_ENABLE_STREAMING_JSON_PREVIEW` controls streaming JSON previews. Strings
with non-UTF-8 bytes appear as `b"<base64>"` in diffs and JSON output.

`--output <format>` is also supported by stack list/history/tag list, policy
list/group list, project list, config environment list, and plugin list. `--urns`
shows full URNs in preview, up, destroy, refresh, import, and watch displays.

## Automatic logs

Encrypted automatic CLI logging was opt-in through
`PULUMI_ENABLE_AUTOMATIC_LOGGING` in `3.229.0-3.248.0` and became the default in
`3.249.0-3.254.0`. Captures live under `~/.pulumi/logs`, property-value secrets
are redacted, and `pulumi logs decrypt`, `ls`, `rm`, and `share` manage them.

`preview` and `up --show-secrets` deliberately place plaintext secrets in the
terminal and any captured output.

## Direct-resource operations

In the first resource form of `pulumi do`, `create`, `patch`, and `delete`
required `--stateless`; `--provider` could use an existing provider from state,
and project-scoped PCL received the selected organization and short stack name.

The later stateful form supports `create`, `delete`, and `upsert`; numbers and
booleans may be expressions. `--resources` exposes resources already in state,
`show-resources` lists their generated identifiers, and stateful `patch` overlays
new inputs on the existing snippet. Stateful operations accept `--provider`.
Outside a project, Pulumi creates a project and stack beneath `PULUMI_HOME`.

## Command lifecycle

`pulumi query` was removed in 3.157.0. On Windows, executable resolution checks
`.cmd` and `.ps1`. `--skip-plugin-pre-install` bypasses eager plugin installation.

The experimental local deployment-settings file workflow is removed: do not use
`Pulumi.<stack>.deploy.yaml`, `deployment settings init`, `pull`, `configure`,
`env`, `push`/`update`/`up`, `--config-file`, or SDK file readers. Use
`pulumi deployment settings get`, `edit`, and `destroy` against Pulumi Cloud.
