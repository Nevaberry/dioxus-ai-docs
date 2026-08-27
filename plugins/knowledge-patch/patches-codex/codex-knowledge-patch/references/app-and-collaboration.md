# App and collaboration

## Desktop availability and shared state

The desktop app launched on macOS and added Windows in a March 4 update. It
reuses projects, session history, and configuration from the CLI and IDE
extension. (`codex-app`)

`codex app [PATH]` opens the installed desktop app or starts its installer when
the app is absent. On macOS it opens the supplied workspace path; on Windows it
prints the path to open after installation.

```bash
codex app .
```

The ChatGPT desktop app is also available as a Linux preview in `.deb` and
`.rpm` packages for supported Ubuntu, Debian, and Fedora distributions on x64
and ARM64. It provides signed-in access to projects, local files, and Codex.

## Isolated parallel work

Agent threads are organized by project. Built-in Git worktrees give parallel
agents isolated repository copies without touching local Git state. Review and
comment on changes in-thread, open them in an editor, or check them out locally.

## Portable skills and Automations

Skills bundle instructions, resources, and scripts. The app can create and
manage them; they may be invoked explicitly or selected automatically for a
task. A skill created in the app is also usable from the CLI and IDE extension,
and checking it into a repository makes it available to the team.

An Automation combines instructions with optional skills, runs in the
background on a user-defined schedule, and sends completed results to a review
queue. Its execution depends on the local computer being open; cloud-based
triggers were still future work.

On macOS, Record & Replay can turn a demonstrated workflow into a reusable
skill when Computer Use is available and enabled. Its availability includes
the EU, UK, and Switzerland. (`2026-07-10-2026-08-18`)

## Importing setup and recent work

Desktop **Settings > Import** can bring in instructions, settings, skills,
plugins, projects, and recent work from Claude Code, Claude Cowork, and Cursor,
with optional automatic updates. The CLI `/import` command imports supported
setup and recent chats from Claude Code and Cursor.

## Multi-folder projects and review

A local desktop project can contain multiple related folders. Its primary
folder controls new chats, Git operations, and automatic discovery of
`AGENTS.md`, skills, and `config.toml`; secondary folders remain searchable,
readable, and editable. Review aggregates repositories and changed lines across
the whole multi-folder project.

## Computer History

Computer History is an opt-in macOS feature that turns activity from selected
apps and websites into memories and a timeline usable by ChatGPT and Codex.
Collection can be paused, and its history can be reviewed or deleted. Initial
access is for Pro, Business, and Enterprise outside the EEA, Switzerland, and
the UK; managed workspaces require administrator enablement.

## Voice coordination and screen context

Desktop Voice can start, inspect, and steer work in other Chat, Work, or Codex
threads. On macOS, Screen context can attach an appshot of the frontmost
window. Voice is available on desktop and through Remote on iOS for Plus, Pro,
Business, Edu, and Enterprise. When started from an existing task composer, it
can continue task actions in the background.

## Browser and Chrome context

The desktop browser can revisit history from its address bar, fall back to
Google search, and let tasks search browsing history after it is enabled in
Settings. The Chrome extension can pass open tabs or highlighted text into
side chat, answer questions about a YouTube video, and expose **Ask ChatGPT**
from a page's context menu.

## Generated images

Generated images can be opened in an expanded viewer, switched between Focused
and Canvas views, annotated with comments, selected individually, and sent for
targeted edits without leaving the conversation.

Image-generation requests use the image-generation extension by default since
`0.144.0`.

## Usage-credit redemption

Usage-limit reset credits show their type and expiration. The redemption
picker lets users choose which credit to redeem.

## iOS tasks and Remote

Task transcripts on iOS render inline visualizations, including Mermaid
diagrams. Tasks support interactive forms, standard MCP forms, and editable
message approvals.

iOS can launch directly into Remote, opens linked folders in the files sheet,
and restores unsent prompts when switching among tasks, hosts, and workspaces.
Composer autocomplete mirrors desktop plugin mentions and includes skills from
installed plugins.
