# TUI and session controls

## Steer a running turn

While a turn is running:

- `Enter` injects text into the active turn.
- `Tab` queues normal input, slash commands, or `!` shell commands for the next
  turn.

## Edit and recover prompts

- `Ctrl+G` opens a long prompt in `VISUAL`, or in `EDITOR` when `VISUAL` is
  unset.
- `Ctrl+R` searches prompt history.
- `Up` and `Down` recover earlier drafts, including image placeholders.
- `/copy` or `Ctrl+O` copies the latest completed output, never partial output
  from an active turn.

With an empty composer, press `Esc` twice to open the previous user message for
editing. Additional presses move farther backward. Submitting the edited
message forks the conversation from that point.

## Start, clear, compact, resume, or fork

- `/clear` starts a fresh conversation and clears the terminal view.
- `Ctrl+L` clears only the terminal display.
- `/new` starts a fresh conversation without clearing the terminal view.
- `/compact` replaces older turns with a concise, context-preserving summary.
- `/resume` loads a saved transcript from a picker.
- `/fork` clones the current conversation under a new thread ID.

For equivalent CLI session commands, see
[cli-execution-and-cloud.md](cli-execution-and-cloud.md).

## Themes

`/theme` previews syntax-highlighting themes and persists the selection as
`tui.theme` in `~/.codex/config.toml`.

```text
/theme
```

Place custom TextMate `.tmTheme` files under `$CODEX_HOME/themes` to make them
available in the picker.

## Plan mode, Fast mode, and experimental features

`/plan [prompt]` switches the conversation into plan mode. Its inline prompt
accepts pasted content or images. The command is unavailable while a task is
running.

```text
/plan Propose a migration plan for this service
```

Control Fast mode for the current thread with `/fast on`, `/fast off`, and
`/fast status`. Persist the selection when the interface offers that choice.

```text
/fast status
```

`/experimental` saves feature toggles to configuration and identifies changes
that require a restart.

## Permissions and diagnostics

For `/permissions`, `/status`, and `/debug-config`, see
[security-and-configuration.md](security-and-configuration.md).

## Status line and terminal title

`/statusline` selects and reorders footer fields and saves them to
`tui.status_line`. Available fields cover model and reasoning, context, rate
limits, Git branch, tokens, session, paths, and version.

`/title` configures terminal-title fields for app, project, spinner, status,
thread, branch, model, and task progress.

## Background terminals

When `unified_exec` is active, `/ps` lists each background terminal, its
command, and up to three recent non-empty output lines. `/stop` terminates every
background terminal for the current session; `/clean` remains an alias.

## Apps, plugins, and agent threads

- `/apps` inserts a selected connector into the composer as `$app-slug`.
- `/plugins` browses allowed marketplaces; press `Space` to toggle an installed
  plugin.
- `/agent` switches to a spawned agent thread so its work can be inspected or
  continued.
