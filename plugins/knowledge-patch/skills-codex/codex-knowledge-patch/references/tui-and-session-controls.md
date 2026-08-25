# TUI and session controls

## Personality selection

`/personality` is available in the app, CLI, and IDE extension. It switches
between terse/pragmatic and conversational/empathetic interaction styles
without changing capabilities. (`codex-app`)

## Themes

`/theme` previews themes and saves the selection as `tui.theme` in
`~/.codex/config.toml`. Custom `.tmTheme` files under `$CODEX_HOME/themes`
appear in the picker.

## Isolated local review

`/review` launches a dedicated reviewer without modifying the working tree.
Presets cover a base-branch diff, all uncommitted changes, one commit, or custom
instructions. It uses the session model unless `review_model` overrides it in
configuration.

## Explicit subagents

Subagents are spawned only when explicitly requested, with roles configured
under `[agents]` in `config.toml`. Each subagent performs its own model and tool
work, so parallel workflows consume additional tokens.

## Turn steering and queued work

During an active turn, `Enter` injects instructions immediately. `Tab` queues
a prompt, slash command, or `!` shell command for the next turn. `@` opens fuzzy
workspace-file search, and `!command` runs locally under the active sandbox and
approval policy.

## Prompt history and external editing

With an empty composer, press `Esc` twice to select the previous user message;
further presses walk backward, and submitting forks from that point. `Ctrl+G`
opens the editor from `VISUAL`, falling back to `EDITOR`.

## Fast and Plan controls

`/fast on`, `/fast off`, and `/fast status` control Fast mode for the current
supported thread and can optionally persist the choice. `/plan [PROMPT]`
enters Plan mode with optional pasted content or images, but is unavailable
while a task is running.

## Conversation reset, copying, and branching

`/clear` clears the terminal and starts a fresh conversation. `/new` starts one
without clearing the view, and `Ctrl+L` clears only the display.

`/copy` or `Ctrl+O` copies the latest completed output, even during a later
running turn. `/fork` clones the current transcript under a new thread ID;
`codex fork` selects a saved session to clone.

## Status line and terminal title

`/statusline` interactively selects and reorders footer fields and persists
them to `tui.status_line`. `/title` does the same for window or tab title
fields in `tui.terminal_title`. Fields include model/context or limits,
repository state, session identity, task progress, and version.

## Background terminal controls

With `unified_exec`, `/ps` shows each background command, its status, and up to
three recent non-empty output lines. `/stop` stops every background terminal
for the current session; `/clean` remains an alias.

## Agent-thread navigation

`/agent` opens a thread picker and switches the active view so a spawned
agent's work can be inspected or continued.
