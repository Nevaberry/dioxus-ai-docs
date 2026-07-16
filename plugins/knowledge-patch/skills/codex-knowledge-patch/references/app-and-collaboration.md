# App and collaboration

## Desktop projects and worktrees

The desktop app is available on macOS and Windows. It organizes agent threads
by project and supports diff review, inline comments, and editor handoff within
a thread.

Built-in worktrees give parallel agents isolated repository copies. Check out
an agent's changes locally while other work continues without changing the
current Git state. The app reuses session history and configuration from the
CLI and IDE extension.

## Skills on every surface

Skills bundle instructions, resources, and scripts. Create and manage them in
the app, invoke them explicitly, or let Codex select them for a task. A skill
created in the app is also available in the CLI and IDE extension. Check a
skill into a repository to share it with a team.

## Scheduled automations

Automations run instructions and optional skills in the background on a defined
schedule. Finished runs enter a review queue for follow-up.

Keep the computer open for scheduled runs. Automations currently depend on the
local computer and do not support cloud-based triggers.

## Interaction personality

Use `/personality` in the app, CLI, or IDE extension to choose between a terse,
pragmatic style and a conversational, empathetic style:

```text
/personality
```

The selection changes interaction style, not capabilities.

## Usage credits

Since `0.144.0`, the reset-credit picker labels each credit with its type and
expiration and allows the user to select which credit to redeem.

## Code Mode and approval pauses

Since `0.144.0`, Code Mode defaults to hosted mode. Every approval request
causes an elicitation pause. For the `writes` app-approval mode, declared
read-only actions proceed without a prompt and writes require approval.

See [security-and-configuration.md](security-and-configuration.md) for the
app's sandbox defaults and the CLI's approval presets.

## Image generation

Since `0.144.0`, image-generation requests use the image-generation extension
by default. Natural-language CLI prompts can create or edit image assets, and
attached images act as transformation references. Include `$imagegen` to
request the image workflow explicitly, and quote it in shell prompts to prevent
environment-variable expansion.

```bash
codex '$imagegen Create a transparent 64px application icon'
codex --image existing.png '$imagegen Extend this banner to a 3:1 aspect ratio'
```
