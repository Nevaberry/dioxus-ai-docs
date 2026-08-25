---
name: codex-knowledge-patch
description: Codex
version: 0.144.0
license: MIT
metadata:
  author: Nevaberry
---



# Codex Knowledge Patch

Use this skill for current Codex app, CLI, TUI, remote, cloud, plugin, MCP,
sandbox, configuration, and collaboration behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [App and collaboration](references/app-and-collaboration.md) | Desktop availability, shared state, worktrees, skills, Automations, imports, multi-folder projects, browser, images, voice, and iOS |
| [CLI execution and cloud](references/cli-execution-and-cloud.md) | Resume, working roots, image generation, scripted execution, cloud tasks, launcher, login, package detection, and sandbox runner |
| [Remote, MCP, and connectors](references/remote-mcp-and-connectors.md) | Remote TUI, app-server authentication, MCP setup, hosted connectors, WebSockets, plugins, marketplaces, and V2 testing |
| [Security and configuration](references/security-and-configuration.md) | Approval modes, permission presets, web search, feature flags, sandbox roots, policy preflight, and diagnostics |
| [TUI and session controls](references/tui-and-session-controls.md) | Personality, themes, review, steering, history, Fast and Plan modes, conversation controls, status lines, processes, and agents |

## Breaking changes and deprecations

### Retiring ChatGPT-authenticated models

On August 31, 2026, ChatGPT-authenticated sessions lose `gpt-5.4` and
`gpt-5.4-mini`. They remain available through the API and in API-key-
authenticated sessions.

Migrate workspace defaults, saved model settings, managed configuration,
custom agents, and scheduled tasks from `gpt-5.4` to `gpt-5.6-terra`, and from
`gpt-5.4-mini` to `gpt-5.6-luna`.

### Deprecated approval policy

`on-failure` is deprecated. Approval choices are `untrusted`, `on-request`,
and `never`.

`--full-auto` combines `workspace-write` with `on-request`; `--yolo` bypasses
both safeguards.

### Global flag placement

Place global flags inherited by subcommands after the subcommand name.
Repeatable `-c key=value` overrides parse JSON values when possible.

```bash
codex exec --profile work -c 'features.unified_exec=true' --full-auto "Run the checks"
```

## High-value CLI workflows

### Resume the right session

Interactive resume defaults to sessions from the current working directory.
Use `--all` to broaden the picker; `--last` or a session ID skips it.

```bash
codex resume --last
codex exec resume --last "Continue with the implementation"
```

Non-interactive resume retains the transcript, plan history, and approvals.

### Produce scripted output

Pass `-` to `codex exec` to read a prompt from standard input. A scripted run
can emit JSONL state-change events, constrain the final response with a JSON
Schema, save only the final message, avoid rollout persistence with
`--ephemeral`, or operate outside Git with `--skip-git-repo-check`.

```bash
printf '%s\n' "Inventory licenses" | codex exec - --json \
  --output-schema result.schema.json --output-last-message final.txt
```

### Select writable project roots

`--cd` selects the working root without changing the shell directory.
Repeat `--add-dir` to expose additional writable roots.

```bash
codex --cd apps/frontend --add-dir ../backend --add-dir ../shared
```

### Submit and apply cloud work

`codex cloud` opens a task picker. `codex cloud exec` submits directly to a
configured environment and accepts one to four independent attempts.
Submission failures exit nonzero, and `Ctrl+O` selects an environment in the
picker.

```bash
codex cloud exec --env ENV_ID --attempts 3 "Summarize open bugs"
codex cloud list --env ENV_ID --limit 20 --json
codex apply TASK_ID
```

Cloud listing supports environment filtering, cursor pagination, a 1–20
result limit, and JSON with a `tasks` array plus an optional `cursor`.
Applying a task uses its latest diff, reports patched files, and exits nonzero
on `git apply` conflicts.

### Generate or edit images

Request image generation or editing in natural language or with the literal
`$imagegen`. Attach an image when the task should transform or extend it.

```bash
codex --image existing.png '$imagegen Extend this asset'
```

Image-generation requests use the image-generation extension by default.

## Permissions and configuration

### Choose a permission preset

`/permissions` switches among Auto, Read-only, and Full Access.

- Auto permits reads, edits, and commands inside the working directory, but
  asks for outside or network access.
- Read-only withholds changes and commands pending plan approval.
- Full Access removes those prompts across the machine and network.

### Control web search

Local CLI work uses cached search by default; full-access sandboxing defaults
to live results. `--search` requests live results for one run.

Persist the choice with `web_search = "live"` or
`web_search = "disabled"`. JSON execution reports searches as `web_search`
events.

### Manage feature flags

Inspect and persist feature flags with `codex features`. Changes go to
`~/.codex/config.toml`, or to the selected profile when `--profile` is used.

```bash
codex features list
codex features enable unified_exec
codex features disable shell_snapshot
```

### Preflight an execution policy

The preview `codex execpolicy check` evaluates a command against one or more
rule files and emits JSON with the strictest decision and matching rules.
Use `--pretty` to format it.

```bash
codex execpolicy check --rules ~/.codex/rules/default.rules --pretty -- git status
```

## Interaction and collaboration

### Steer or queue work

During an active turn, `Enter` injects instructions immediately. `Tab` queues
a prompt, slash command, or `!` shell command for the next turn. `@` opens
fuzzy workspace-file search, and `!command` runs locally under the active
sandbox and approval policy.

### Review without changing the tree

`/review` launches a dedicated reviewer without modifying the working tree.
Choose a base-branch diff, all uncommitted changes, one commit, or custom
instructions. Review uses the session model unless `review_model` overrides
it in configuration.

### Use explicit subagents

Subagents are spawned only when explicitly requested. Configure roles under
`[agents]` in `config.toml`. Each subagent performs its own model and tool
work, so parallel workflows consume additional tokens.

Use `/agent` to inspect or continue a spawned agent's thread.

### Work across desktop projects

The desktop app reuses projects, session history, and configuration from the
CLI and IDE extension. Built-in Git worktrees isolate parallel agent threads;
review or comment on changes in-thread, open them in an editor, or check them
out locally.

For multi-folder projects, the primary folder controls new chats, Git
operations, and automatic discovery of `AGENTS.md`, skills, and `config.toml`.
Secondary folders remain searchable, readable, and editable, and Review
aggregates repositories and changed lines across the project.

## Routing details

Read the app reference for desktop or mobile availability, Automations,
portable or recorded skills, Computer History, voice, imports, browser
context, multi-folder projects, or image review.

Read the CLI execution reference for resume behavior, structured output,
cloud workflows, working roots, authentication, app launching, global package
detection, image requests, or direct sandbox execution.

Read the remote reference for app-server hosting, remote authentication, MCP,
hosted connectors, Responses WebSockets, plugins, marketplace sources, or the
experimental V2 test client.

Read the security reference for approval semantics, sandbox scope, web-search
modes, feature persistence, Windows roots, execution-policy checks, or
configuration-layer diagnostics.

Read the TUI reference for interaction commands, session navigation, review,
themes, status lines, terminal titles, background commands, personalities,
Fast mode, Plan mode, copying, branching, or explicit agent threads.
