---
name: codex-knowledge-patch
description: Codex
version: "0.144.0"
license: MIT
metadata:
  author: Nevaberry
---


# Codex Knowledge Patch

Use this skill when working with the Codex desktop app, CLI, TUI, remote app
server, MCP integrations, cloud tasks, plugins, or collaborative agent
workflows.

## Reference index

| Reference | Topics |
| --- | --- |
| [app-and-collaboration.md](references/app-and-collaboration.md) | Desktop platforms, projects, skills, automations, imports, browser and voice context, image review, iOS |
| [security-and-configuration.md](references/security-and-configuration.md) | Approval and sandbox modes, flags, feature settings, search, login, policy checks, diagnostics, Windows behavior |
| [remote-mcp-and-connectors.md](references/remote-mcp-and-connectors.md) | Remote TUI security, app-server authentication, MCP, connectors, proxied WebSockets, plugin sign-in |
| [cli-execution-and-cloud.md](references/cli-execution-and-cloud.md) | Scripted execution, resume and review, cloud tasks, plugin marketplaces, desktop launching |
| [tui-and-session-controls.md](references/tui-and-session-controls.md) | Steering, prompt editing, themes, planning, conversation controls, status UI, background commands, subagents |

## Replace deprecated approval behavior

Choose among the supported `untrusted`, `on-request`, and `never` approval
policies. `on-failure` is deprecated. `--full-auto` combines the `workspace-write`
sandbox with `on-request` approvals. `--yolo` bypasses sandboxing and approval
prompts, so reserve it for an externally isolated environment.

Read [security-and-configuration.md](references/security-and-configuration.md)
before changing approval, sandbox, authentication, policy, or search settings.

## Account for hosted Code Mode approvals

Since `0.144.0`, Code Mode defaults to hosted mode. Every approval request
causes an elicitation pause. The `writes` app-approval mode lets declared
read-only app actions proceed without prompting but requires approval for
writes.

## Use interactive MCP authentication directly

Since `0.144.0`, MCP tools may request interactive authentication without an
experimental opt-in. App-server hosts may provide authentication at runtime,
hosted login may redirect success to a hosted page, and long-running app
sessions refresh expired authentication for the hosted `codex_apps` connector.

Read [remote-mcp-and-connectors.md](references/remote-mcp-and-connectors.md)
before configuring remote listeners, bearer tokens, MCP servers, connectors,
or plugin authentication.

## Expect image-generation routing

Since `0.144.0`, image requests use the image-generation extension by default.
Attach a reference with `--image` for edits, and quote the literal
`$imagegen` name when invoking it from a shell:

```bash
codex --image existing.png '$imagegen Extend this asset'
```

The desktop image viewer also supports Focused and Canvas views, annotations,
individual selection, and targeted follow-up edits.

## Run scripted work with explicit output contracts

Use `codex exec` for non-interactive work. Pass a prompt as an argument or use
`-` to read stdin:

```bash
printf '%s\n' 'Inventory package licenses' | \
  codex exec - --json --output-schema result.schema.json \
  --output-last-message final.txt
```

- `--json` emits JSONL state-change events.
- `--output-schema` constrains the final response with JSON Schema.
- `--output-last-message` writes the final natural-language response alone.
- `--ephemeral` avoids saving rollout files.
- `--skip-git-repo-check` permits execution outside a Git repository.

Resume the latest scripted session for the current directory with:

```bash
codex exec resume --last "Continue with the implementation"
```

Interactive and scripted resume retain transcript, plan history, and
approvals. Use `--all` to include other directories; use fork when a new thread
should retain the source transcript without continuing the same session.

## Connect a remote TUI safely

Run the app server where the workspace lives and connect a TUI through an
explicit `ws://` or `wss://` URL:

```bash
codex app-server --listen ws://127.0.0.1:4500
codex --remote ws://127.0.0.1:4500
```

For non-local use, put authenticated connections behind TLS. Capability-token
authentication uses `--ws-token-file` on the server and
`--remote-auth-token-env` on the client. Signed bearer authentication uses an
HS256 JWT with an `exp` claim and a shared secret of at least 32 bytes. The
client sends bearer tokens only over `wss://` or loopback `ws://`.

## Apply invocation and feature overrides correctly

Global options inherited by a subcommand go after the subcommand name.
Repeatable `-c key=value` overrides parse JSON when possible and otherwise
remain strings.

```bash
codex exec --profile work -c 'features.unified_exec=true' \
  --full-auto "Run the checks"
```

Use `--cd` to choose the working root without changing the parent shell, and
repeat `--add-dir` for additional writable roots:

```bash
codex --cd apps/frontend --add-dir ../backend --add-dir ../shared
```

Persist feature choices with `codex features list`, `enable`, and `disable`.
Settings go to `~/.codex/config.toml` or the selected profile. `--search`
requests live web search for one run; `web_search = "live"` or `"disabled"`
persists the choice.

## Submit, inspect, and apply cloud work

`codex cloud` opens the task picker. Submit directly to an environment with
one to four independent attempts:

```bash
codex cloud exec --env ENV_ID --attempts 3 "Summarize open bugs"
codex cloud list --env ENV_ID --limit 20 --json
codex apply TASK_ID
```

Submission failures exit nonzero. Listing supports cursor pagination, a limit
from 1 through 20, and JSON containing a `tasks` array plus an optional
`cursor`. Applying a task uses its latest diff, reports changed files, and
exits nonzero on `git apply` conflicts.

## Use the desktop collaboration boundary

Desktop projects share projects, session history, and configuration with the
CLI and IDE extension. Built-in Git worktrees isolate parallel agent threads.
In a multi-folder project, the primary folder controls new chats, Git
operations, and automatic discovery of `AGENTS.md`, skills, and `config.toml`;
secondary folders remain searchable, readable, and editable.

Automations combine instructions with optional skills and send scheduled
results to a review queue. They require the local computer to remain open.
Review aggregates repositories and changed lines across a multi-folder
project.

## Use interactive controls deliberately

- Press `Enter` during a turn to inject instructions; press `Tab` to queue a
  prompt, slash command, or `!` command for the next turn.
- Use `Ctrl+G` for `VISUAL`/`EDITOR`, `@` for workspace-file search, and an
  empty composer followed by `Esc` twice to edit and fork from prior prompts.
- Use `/clear` for a new conversation and cleared view, `/new` for a new
  conversation without clearing, and `Ctrl+L` to clear only the display.
- Use `/copy` or `Ctrl+O` for the latest completed output, `/fork` to clone the
  current transcript, and `/agent` to inspect or continue spawned threads.
- Use `/plan [PROMPT]` before a task starts and `/fast on`, `/fast off`, or
  `/fast status` for supported threads.
- With `unified_exec`, use `/ps` to inspect background commands and `/stop` to
  stop all background terminals for the session; `/clean` remains an alias.

Subagents are created only when explicitly requested. Configure roles under
`[agents]` in `config.toml`, and account for the separate model and tool work
performed by every spawned agent.

Read [tui-and-session-controls.md](references/tui-and-session-controls.md) for
the complete interaction, appearance, status, terminal, and thread controls.
