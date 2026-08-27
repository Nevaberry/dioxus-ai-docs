# Security and configuration

## ChatGPT-authenticated model retirement

On August 31, 2026, ChatGPT-authenticated sessions lose `gpt-5.4` and
`gpt-5.4-mini`. Both remain available through the API and in API-key-
authenticated sessions. Migrate workspace defaults, saved model settings,
managed configuration, custom agents, and scheduled tasks from `gpt-5.4` to
`gpt-5.6-terra`, and from `gpt-5.4-mini` to `gpt-5.6-luna`.
(`2026-07-10-2026-08-18`)

## Desktop sandbox defaults

The desktop app uses the same native, configurable system sandbox as the CLI.
By default, agents may edit only the active folder or branch and use cached web
search. Network access and other elevated commands require permission unless
project or team rules allow them automatically. (`codex-app`)

## Writes-only app approvals

The `writes` app-approval mode allows declared read-only actions without
prompting while requiring approval for writes. (since `0.144.0`)

## Interactive permission presets

`/permissions` switches among Auto, Read-only, and Full Access.

- Auto permits reads, edits, and commands inside the working directory but
  asks for outside or network access.
- Read-only withholds changes and commands pending plan approval.
- Full Access removes those prompts across the machine and network.

## Approval choices and safety shortcuts

Approval choices are `untrusted`, `on-request`, and `never`; `on-failure` is
deprecated. `--full-auto` combines `workspace-write` with `on-request`, while
`--yolo` bypasses both safeguards.

## Persistent feature flags

Feature flags can be inspected and persistently changed from the CLI. Changes
go to `~/.codex/config.toml`, or to the selected profile when `--profile` is
used.

```bash
codex features list
codex features enable unified_exec
codex features disable shell_snapshot
```

## CLI web-search modes

Local CLI work uses cached search by default, while full-access sandboxing
defaults to live results. `--search` requests live results for one run.
`web_search = "live"` or `web_search = "disabled"` persists the choice. JSON
execution reports searches as `web_search` events.

## Windows writable roots

Windows sandbox sessions can delete files inside writable roots and access the
managed primary runtime.

## Native Windows read roots

`/sandbox-add-read-dir C:\absolute\path` is available only in the native
Windows CLI. The path must be an existing absolute directory. The command
refreshes the session's sandbox policy to grant later commands read access.

## Exec-policy preflight

The preview `codex execpolicy check` evaluates a command against one or more
rule files. It emits JSON with the strictest decision and matching rules;
`--pretty` formats the result.

```bash
codex execpolicy check --rules ~/.codex/rules/default.rules --pretty -- git status
```

## Configuration-layer diagnostics

`/debug-config` prints configuration layers from lowest precedence upward,
together with enabled state, policy sources, and enforced constraints such as
permitted approval policies, sandbox modes, MCP servers, residency, and
experimental networking.
