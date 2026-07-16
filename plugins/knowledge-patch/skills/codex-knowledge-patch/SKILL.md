---
name: codex-knowledge-patch
description: Codex 0.144.0 compatibility. Use for Codex work.
license: MIT
version: "0.144.0"
metadata:
  author: Nevaberry
---

# OpenAI Codex Knowledge Patch

Baseline: before the public Codex CLI launch, with no stable CLI, web, IDE extension, desktop app, or unified product changelog; coverage extends through `codex-app` (2026-02-02), `0.144.0` (2026-07-09), `cli-overview-and-features` (2026-07-11), and `cli-reference-and-commands` (2026-07-11).

## Reference index

| Reference | Topics |
| --- | --- |
| [app-and-collaboration.md](references/app-and-collaboration.md) | Desktop app, worktrees, shared skills, scheduled automations, personality, credits, Code Mode, image generation |
| [security-and-configuration.md](references/security-and-configuration.md) | Invocation overrides, approval and sandbox presets, feature flags, search, login, policies, Windows behavior, diagnostics |
| [remote-mcp-and-connectors.md](references/remote-mcp-and-connectors.md) | Remote TUI and WebSocket authentication, MCP administration and authentication, hosted connectors, proxied Responses WebSockets |
| [cli-execution-and-cloud.md](references/cli-execution-and-cloud.md) | Scripted execution, structured output, resume and fork, cloud tasks, plugin marketplaces, repository workflows |
| [tui-and-session-controls.md](references/tui-and-session-controls.md) | Steering and editing keys, themes, planning, Fast mode, status UI, background terminals, conversation and agent controls |

## Start with changed defaults and deprecations

### Replace `on-failure` approval policy

Use one of the supported approval policies:

```bash
codex --ask-for-approval untrusted
codex --ask-for-approval on-request
codex --ask-for-approval never
```

`on-failure` is deprecated. `--full-auto` combines `workspace-write` with
`on-request`. `--yolo` bypasses both approval prompts and sandboxing; use it
only inside an externally isolated environment.

### Account for the hosted Code Mode default

Since `0.144.0`, Code Mode defaults to hosted mode. Every approval request
causes an elicitation pause. The `writes` app-approval mode permits declared
read-only actions without prompting and requires approval for writes.

### Remove obsolete MCP authentication opt-ins

Since `0.144.0`, MCP tools may request interactive authentication by default;
an experimental opt-in is no longer required. App-server hosts may supply
Codex authentication at runtime, hosted login may redirect success to a hosted
page, and long-running sessions refresh expired authentication for the hosted
`codex_apps` connector.

### Expect the image-generation extension

Since `0.144.0`, image-generation requests use the image-generation extension
by default. From the CLI, attach reference images with `--image` and quote the
literal `$imagegen` name in shell prompts.

```bash
codex '$imagegen Create a transparent 64px application icon'
codex --image existing.png '$imagegen Extend this banner to a 3:1 aspect ratio'
```

## Choose the safety boundary

Select a sandbox and approval policy independently:

```bash
codex --sandbox workspace-write --ask-for-approval on-request
```

Sandbox values are `read-only`, `workspace-write`, and `danger-full-access`.
The desktop app uses the same native configurable sandbox as the CLI. By
default, app work is limited to the active folder or branch and cached web
search; network access and other elevated commands need permission. Project or
team rules may automatically allow named commands to run elevated.

On Windows since `0.144.0`, sandboxed sessions may delete files inside writable
roots and access the managed primary runtime. In a native Windows TUI,
`/sandbox-add-read-dir C:\absolute\path` adds an existing absolute read path for
the rest of the session.

Read [security-and-configuration.md](references/security-and-configuration.md)
before changing approval, sandbox, authentication, policy, or search settings.

## Run scripted work with structured results

Use `codex exec` or its `codex e` alias for non-interactive work. Supply the
prompt as an argument or use `-` to read it from stdin.

```bash
printf '%s\n' 'Inventory the package licenses' | \
  codex exec - --json --output-schema result.schema.json \
  --output-last-message final.txt
```

- `--json` emits JSONL state-change events.
- `--output-schema` constrains the final response with JSON Schema.
- `--output-last-message` writes the final natural-language response separately.
- `--ephemeral` avoids saving rollout files.
- `--skip-git-repo-check` permits a workspace outside a Git repository.

Resume the latest scripted session scoped to the current directory with:

```bash
codex exec resume --last "Continue with the next package"
```

Use `--all` to include sessions from other directories. `resume` continues the
same session; `fork` creates a new thread while preserving the source transcript.

## Connect a remote TUI safely

Let an app server own the workspace and execute commands while another machine
runs the TUI:

```bash
# Workspace host
codex app-server --listen ws://127.0.0.1:4500

# TUI through a forwarded loopback port
codex --remote ws://127.0.0.1:4500
```

Pass an explicit `ws://` or `wss://` URL. Use unauthenticated plain WebSockets
only on loopback or through an SSH-forwarded loopback connection. For a network
listener, use capability-token authentication over `wss://`; the client refuses
to send a token over non-loopback `ws://`.

```bash
codex app-server --listen ws://0.0.0.0:4500 \
  --ws-auth capability-token \
  --ws-token-file "$HOME/.codex/codex-app-server-token"

export CODEX_REMOTE_AUTH_TOKEN="$(ssh devbox 'cat ~/.codex/codex-app-server-token')"
codex --remote wss://devbox.example.com:4500 \
  --remote-auth-token-env CODEX_REMOTE_AUTH_TOKEN
```

For signed bearer authentication, use `--ws-auth signed-bearer-token` with
`--ws-shared-secret-file`. Tokens are HS256 JWTs with a required `exp` claim;
the shared secret must contain at least 32 bytes. Read
[remote-mcp-and-connectors.md](references/remote-mcp-and-connectors.md) for the
remaining claim-validation rules and MCP setup.

## Apply invocation overrides correctly

Global options include `--profile`, `--oss`, `-C`, repeatable `--add-dir`,
repeatable `--enable` and `--disable`, and `-c key=value`. When invoking a
subcommand, place its global options after the subcommand name. `-c` parses a
JSON value when possible and otherwise preserves a string.

```bash
codex --profile work -C ./repo --add-dir ../shared \
  --sandbox workspace-write --ask-for-approval on-request
codex exec --profile work --enable unified_exec "Run the checks"
```

`--oss` selects a local open-source provider backed by a running Ollama
instance. One-run feature overrides do not replace persisted feature settings.

## Persist common feature choices

```bash
codex features list
codex features enable unified_exec
codex features disable shell_snapshot
```

Feature changes persist in `~/.codex/config.toml`; with `--profile`, they are
stored in that profile. `--search` selects live search for one run, while
`web_search = "live"` and `web_search = "disabled"` persist the choice. A
full-access sandbox defaults to live results, and JSON execution reports
searches as `web_search` events.

## Submit and apply cloud work

`codex cloud` opens a task picker. Submit directly with an environment ID and
request one to four independent attempts:

```bash
codex cloud exec --env ENV_ID --attempts 3 "Summarize open bugs"
codex cloud list --env ENV_ID --limit 20 --json
codex apply TASK_ID
```

Submission failures return nonzero. Cloud listing supports environment filters,
cursor pagination, a limit from 1 through 20, and JSON containing `tasks` plus
an optional next cursor. `codex apply` (alias `codex a`) applies the latest task
diff, reports patched files, and exits nonzero if `git apply` conflicts.

## Use interactive controls deliberately

- Press `Enter` during a turn to inject text into it; press `Tab` to queue input,
  slash commands, or `!` shell commands for the next turn.
- Use `Ctrl+G` with `VISUAL` or `EDITOR` for long prompts and `Ctrl+R` for
  history search. `Up` and `Down` restore drafts, including image placeholders.
- Use `/copy` or `Ctrl+O` to copy only the latest completed output.
- With an empty composer, press `Esc` twice to edit the prior user message;
  continue pressing it to walk backward, then submit to fork from that point.
- Use `/clear` for a fresh conversation and cleared view, `/new` for a fresh
  conversation without clearing the terminal, and `Ctrl+L` to clear only the
  display.
- Use `/compact` to replace older turns with a concise context-preserving
  summary, `/resume` to select a saved transcript, and `/fork` to clone the
  current conversation under a new thread ID.

Read [tui-and-session-controls.md](references/tui-and-session-controls.md) for
planning, Fast mode, themes, status layout, background terminals, apps,
plugins, and spawned-agent navigation.
