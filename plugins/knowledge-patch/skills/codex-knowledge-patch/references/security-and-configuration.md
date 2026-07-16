# Security and configuration

## Contents

- [Invocation overrides](#invocation-overrides)
- [Sandbox and approval presets](#sandbox-and-approval-presets)
- [Windows sandbox behavior](#windows-sandbox-behavior)
- [Persisted feature flags](#persisted-feature-flags)
- [Web-search controls](#web-search-controls)
- [CLI authentication](#cli-authentication)
- [Policy evaluation and standalone sandboxes](#policy-evaluation-and-standalone-sandboxes)
- [Configuration diagnostics](#configuration-diagnostics)
- [Global pnpm installations](#global-pnpm-installations)

## Invocation overrides

Use global invocation options to alter a single run:

- `--profile NAME` selects a configuration profile.
- `--oss` selects a local open-source provider backed by a running Ollama
  instance.
- `-C PATH` changes the workspace.
- Repeatable `--add-dir PATH` grants extra writable roots.
- Repeatable `--enable FEATURE` and `--disable FEATURE` override individual
  features for the run.
- `-c key=value` parses the value as JSON when possible and otherwise keeps it
  as a string.

When using a subcommand, place global options after the subcommand name.

```bash
codex --profile work -C ./repo --add-dir ../shared \
  --sandbox workspace-write --ask-for-approval on-request
codex exec --profile work --enable unified_exec "Run the checks"
```

## Sandbox and approval presets

`--sandbox` accepts:

- `read-only`
- `workspace-write`
- `danger-full-access`

`--ask-for-approval` accepts:

- `untrusted`
- `on-request`
- `never`

The old `on-failure` approval policy is deprecated. `--full-auto` combines
`workspace-write` with `on-request`. `--yolo` bypasses approval prompts and the
sandbox; use it only inside an externally isolated environment.

The desktop app uses the same native, configurable system-level sandbox as the
CLI. By default, app agents may edit only their active folder or branch and use
cached web search. Network access and other elevated commands require
permission. Project or team rules can automatically allow specified commands
to run elevated.

Since `0.144.0`, the `writes` app-approval mode lets declared read-only actions
run without a prompt and requires approval for writes.

Use `/permissions` to change the approval preset for later actions in the
current session without restarting.

## Windows sandbox behavior

Since `0.144.0`, Windows sandbox sessions may delete files within writable
roots and access the managed primary runtime.

On native Windows, grant an additional read path for the rest of the session
with:

```text
/sandbox-add-read-dir C:\absolute\path
```

The path must be absolute and already exist.

## Persisted feature flags

Manage persisted flags with:

```bash
codex features list
codex features enable unified_exec
codex features disable shell_snapshot
```

Changes are stored in `~/.codex/config.toml`. If Codex was launched with
`--profile`, enable and disable operations update that profile rather than the
root configuration. Use invocation-level `--enable` and `--disable` for a
one-run override.

For interactive `/experimental` toggles and restart notices, see
[tui-and-session-controls.md](tui-and-session-controls.md).

## Web-search controls

`--search` requests live search for one run. Persist a mode in configuration:

```toml
web_search = "live"
# or
web_search = "disabled"
```

Full-access sandbox settings default to live results. In `codex exec --json`
output, searches appear as `web_search` events.

## CLI authentication

Use the browser OAuth flow with bare `codex login`, or select another mode:

```bash
codex login --device-auth
printf '%s' "$API_KEY" | codex login --with-api-key
```

`--with-api-key` reads the key from stdin, not from an argument. `codex login
status` reports the active authentication mode and returns success only when
credentials are present, which makes it suitable for automation.

## Policy evaluation and standalone sandboxes

`codex execpolicy check` evaluates a command against one or more repeatable rule
files. Its JSON result contains the strictest decision and the matching rules.

```bash
codex execpolicy check -r ~/.codex/rules/default.rules --pretty -- git status
```

Run a command directly under a platform sandbox with `codex sandbox macos` or
`codex sandbox linux`. These use Seatbelt on macOS and Landlock plus seccomp on
Linux. For these standalone helpers, `--full-auto` permits writes to the
workspace and `/tmp`.

```bash
codex sandbox linux --full-auto -- make test
```

## Configuration diagnostics

`/status` reports the active runtime model, approval policy, writable roots,
and token usage.

`/debug-config` displays configuration layers from lowest to highest precedence
and the effective policy requirements. Its report covers permitted approval and
sandbox modes, MCP servers, rules, residency enforcement, and experimental
network constraints.

## Global pnpm installations

Since `0.144.0`, Codex detects global installations managed by pnpm. Diagnostics
and updates then invoke the correct package manager.
