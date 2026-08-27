# TUI and session controls

## Turn steering and queued work

During an active turn, `Enter` injects an instruction immediately. `Tab`
queues a prompt, slash command, or `!` shell command for the next turn. `@`
opens fuzzy workspace-file search. `!command` runs locally under the active
sandbox and approval policy.

## Prompt history and external editing

With an empty composer, press `Esc` twice to select the previous user message;
press it again to walk farther backward. Submitting an edited prior message
forks the conversation from that point.

`Ctrl+G` opens the editor configured by `VISUAL`, falling back to `EDITOR`.

## Themes

`/theme` previews themes and saves the chosen theme as `tui.theme` in
`~/.codex/config.toml`. Custom `.tmTheme` files placed in
`$CODEX_HOME/themes` appear in the picker.

## Fast mode and planning

`/fast on`, `/fast off`, and `/fast status` control Fast mode for the current
supported thread and may persist the choice.

`/plan [PROMPT]` enters plan mode with optional pasted text or images. It is
unavailable while a task is running.

## Conversation reset, copy, and branching

- `/clear` clears the terminal and starts a new conversation.
- `/new` starts a new conversation without clearing the view.
- `Ctrl+L` clears only the display.
- `/copy` or `Ctrl+O` copies the latest completed output, even if a later turn
  is still running.
- `/fork` clones the current transcript under a new thread ID.
- `codex fork` selects a saved session to clone.

## Status line and terminal title

`/statusline` interactively selects and reorders footer fields and stores them
in `tui.status_line`. `/title` does the same for window or tab title fields and
stores them in `tui.terminal_title`.

Available fields cover model and context or limits, repository state, session
identity, task progress, and version.

## Background terminal controls

When `unified_exec` is enabled, `/ps` lists each background command, its
status, and up to three recent non-empty output lines. `/stop` stops every
background terminal for the current session; `/clean` remains an alias.

## Explicit subagents and navigation

Subagents spawn only when explicitly requested. Configure roles beneath
`[agents]` in `config.toml`. Every subagent performs separate model and tool
work, so parallel workflows consume additional tokens.

`/agent` opens the thread picker and switches the active view, allowing a
spawned agent's work to be inspected or continued.
