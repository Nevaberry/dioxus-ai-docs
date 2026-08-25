# App and collaboration

## Desktop platforms and shared state

The desktop app first shipped for macOS, added Windows in the March 4 update,
and is available as a Linux preview. It reuses projects, session history, and
configuration from the CLI and IDE extension. _(codex-app)_

The Linux preview is distributed as `.deb` and `.rpm` packages for supported
Ubuntu, Debian, and Fedora releases on x64 and ARM64. It provides signed-in
access to projects, local files, and Codex. _(2026-07-10-2026-08-18)_

## Isolated parallel work and review

Agent threads are grouped by project. Built-in Git worktrees give parallel
agents isolated repository copies without changing the local Git state.
Review, comment on, and inspect changes in the thread, open them in an editor,
or check them out locally.

## Portable skills

Skills package instructions, resources, and scripts. The app can create and
manage them; users can invoke a skill explicitly or let the task select it.
App-created skills also work in the CLI and IDE extension. Commit a skill to a
repository when it should be available to the team.

On macOS, Record & Replay can turn a demonstrated workflow into a reusable
skill when Computer Use is available and enabled. Record & Replay is available
in the EU, UK, and Switzerland as well as its other supported regions.

## Scheduled automations

An Automation combines instructions with optional skills, runs on a user
schedule in the background, and sends completed results to a review queue.
Execution depends on the local computer remaining open; cloud triggers were
not yet available in the app release described here.

## Usage-credit redemption

Since `0.144.0`, usage-limit reset credits display their type and expiration.
The redemption picker lets the user choose which available credit to redeem.

## Personality selection

`/personality` works in the app, CLI, and IDE extension. It switches between
terse/pragmatic and conversational/empathetic styles without changing
capabilities.

## Import setup and recent work

Desktop **Settings > Import** can import instructions, settings, skills,
plugins, projects, and recent work from supported coding and coworking
assistants, including Cursor. Automatic updates from an import source are
optional.

In the CLI, `/import` imports supported setup and recent chats from supported
external coding assistants, including Cursor.

## Multi-folder projects

A local desktop project can contain multiple related folders. Its primary
folder controls new chats, Git operations, and automatic discovery of
`AGENTS.md`, skills, and `config.toml`. Secondary folders remain searchable,
readable, and editable.

Project review aggregates repositories and changed lines across the complete
multi-folder project.

## Computer History

Computer History is an opt-in macOS feature that turns activity from selected
apps and websites into memories and a timeline usable by ChatGPT and Codex.
Collection can be paused, and users can review or delete its history.

Initial access is for Pro, Business, and Enterprise users outside the EEA,
Switzerland, and the UK. Managed workspaces also require administrator
enablement.

## Voice and screen context

Desktop Voice can start, inspect, and steer work in other Chat, Work, or Codex
threads. On macOS, Screen context can attach an appshot of the frontmost
window.

Voice is available on desktop and through Remote on iOS for Plus, Pro,
Business, Edu, and Enterprise. When Voice starts from an existing task
composer, task actions can continue in the background.

## Browser and Chrome context

The desktop browser can revisit history from its address bar and falls back to
Google search. After browsing-history access is enabled in Settings, tasks can
search that history.

The Chrome extension can send open tabs or highlighted text to side chat,
answer questions about a YouTube video, and expose **Ask ChatGPT** in a page's
context menu.

## Image generation and refinement

Since `0.144.0`, image requests use the image-generation extension by default.
From the CLI, use a natural-language image request or quote the literal
`$imagegen` name; attach a reference image with `--image` to transform or
extend it.

```bash
codex --image existing.png '$imagegen Extend this banner'
```

Generated images can open in an expanded viewer. Switch between Focused and
Canvas views, annotate with comments, select images individually, and request
targeted edits without leaving the conversation.

## iOS task and Remote behavior

Codex task transcripts on iOS render inline visualizations, including Mermaid
diagrams. Tasks support interactive forms, standard MCP forms, and editable
message approvals.

iOS can launch directly into Codex Remote. Linked folders open in the files
sheet, and unsent prompts are restored when switching among tasks, hosts, and
workspaces. Composer autocomplete mirrors desktop plugin mentions and includes
skills supplied by installed plugins.
