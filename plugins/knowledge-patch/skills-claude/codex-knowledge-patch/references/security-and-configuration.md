# Security and configuration

## Desktop sandbox defaults

The desktop app uses the same native, configurable system sandbox as the CLI.
By default, work is limited to editing the active folder or branch and using
cached web search. Network access and other elevated commands require
permission unless project or team rules allow named commands automatically.
_(codex-app)_

## Approval and sandbox choices

Supported approval policies are `untrusted`, `on-request`, and `never`.
`on-failure` is deprecated. `--full-auto` combines `workspace-write` with
`on-request`; `--yolo` bypasses both safeguards.

Since `0.144.0`, the `writes` app-approval mode permits declared read-only app
actions without prompting and requires approval for writes.

Since `0.144.0`, Code Mode defaults to hosted mode. Every approval request in
that mode causes an elicitation pause.

## Interactive permission presets

`/permissions` switches among Auto, Read-only, and Full Access:

- Auto permits reads, edits, and commands in the working directory, but asks
  for outside or network access.
- Read-only withholds changes and commands pending plan approval.
- Full Access removes those prompts across the machine and network.

## Global flags and configuration overrides

Global flags inherited by a subcommand must follow the subcommand name.
Repeatable `-c key=value` overrides parse JSON values when possible and
otherwise preserve strings.

```bash
codex exec --profile work -c 'features.unified_exec=true' \
  --full-auto "Run the checks"
```

`--cd` selects the working root without changing the parent shell's directory.
Repeat `--add-dir` to expose additional writable roots:

```bash
codex --cd apps/frontend --add-dir ../backend --add-dir ../shared
```

## Persistent feature flags

Inspect and persist feature settings with:

```bash
codex features list
codex features enable unified_exec
codex features disable shell_snapshot
```

Changes go to `~/.codex/config.toml`, or to the selected profile when
`--profile` is active.

## Web-search modes

Local CLI work uses cached search by default; full-access sandboxing defaults
to live results. `--search` requests live results for one run.
`web_search = "live"` or `web_search = "disabled"` persists the choice. JSON
execution reports searches as `web_search` events.

## Exec-policy preflight

The preview `codex execpolicy check` evaluates a command against one or more
rule files and emits JSON containing the strictest decision and matching
rules. `--pretty` formats the result.

```bash
codex execpolicy check --rules ~/.codex/rules/default.rules \
  --pretty -- git status
```

## Script-friendly login

`codex login` defaults to browser OAuth. Use `--device-auth` for a device-code
flow or `--with-api-key` to read an API key from stdin. `codex login status`
reports the active mode and exits successfully when credentials exist.

```bash
printf '%s' "$API_KEY" | codex login --with-api-key
codex login status
```

## ChatGPT-authenticated model retirement

On August 31, 2026, ChatGPT-authenticated Codex sessions lose `gpt-5.4` and
`gpt-5.4-mini`. Both models remain available through the API and in API-key
authenticated Codex sessions. _(2026-07-10-2026-08-18)_

Migrate workspace defaults, saved model settings, managed configuration,
custom agents, and scheduled tasks from `gpt-5.4` to `gpt-5.6-terra`, and from
`gpt-5.4-mini` to `gpt-5.6-luna`.

## Direct sandbox runner

The experimental `codex sandbox` helper runs a command under the same platform
policy used internally: Seatbelt on macOS, or Landlock plus seccomp on Linux.
Its `--full-auto` option gives that command write access to the current
workspace and `/tmp`.

```bash
codex sandbox linux -- make test
```

## Windows sandbox behavior

Since `0.144.0`, sandboxed Windows sessions may delete files inside writable
roots and may access the managed primary runtime.

In the native Windows CLI,
`/sandbox-add-read-dir C:\absolute\path` grants later commands read access to
an existing absolute directory. The command refreshes the current session's
sandbox policy and is unavailable on other platforms.

## Configuration diagnostics

Since `0.144.0`, globally installed pnpm is detected so diagnostics and updates
use the correct package manager.

`/debug-config` prints configuration layers from lowest precedence upward,
including enabled state, policy sources, and enforced constraints. Constraints
can cover permitted approval policies, sandbox modes, MCP servers, residency,
and experimental networking.
