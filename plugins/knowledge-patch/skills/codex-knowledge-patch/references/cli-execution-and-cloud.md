# CLI execution and cloud workflows

## Non-interactive execution

`codex exec`, with alias `codex e`, runs a prompt non-interactively. Pass the
prompt as an argument or pass `-` to read it from stdin.

```bash
printf '%s\n' 'Inventory the package licenses' | \
  codex exec - --json --output-schema result.schema.json \
  --output-last-message final.txt
```

Execution options include:

- `--json` emits JSONL state-change events.
- `--output-schema FILE` constrains the final response with a JSON Schema.
- `--output-last-message FILE` writes the final natural-language response to a
  separate file.
- `--ephemeral` avoids saving rollout files.
- `--skip-git-repo-check` permits work outside a Git repository.

## Resume or fork a session

Continue a scripted session with `codex exec resume [SESSION_ID]`; include a
follow-up prompt or images when needed.

```bash
codex exec resume --last "Continue with the next package"
```

For scripted and interactive resume, `--last` selects the newest session scoped
to the current working directory. `--all` includes sessions from other
directories.

```bash
codex resume --last
codex fork --last
```

`codex fork [SESSION_ID]` creates a new thread while preserving the original
transcript instead of continuing the source session.

## Submit cloud tasks

`codex cloud` opens a picker for browsing tasks and applying their results
locally. Submit directly with an environment ID. `--attempts` accepts one to
four and requests that many independent solutions.

```bash
codex cloud exec --env ENV_ID --attempts 3 "Summarize open bugs"
```

Submission failures return a nonzero exit status for scripts and CI.

## List and apply cloud tasks

`codex cloud list` supports environment filtering, a result limit from 1 to 20,
cursor pagination, and JSON output. Its JSON object contains a `tasks` array and
an optional next cursor.

```bash
codex cloud list --env ENV_ID --limit 20 --json
```

`codex apply TASK_ID`, with alias `codex a`, applies the task's latest diff
locally and reports the patched files. It exits nonzero when `git apply`
encounters conflicts.

```bash
codex apply TASK_ID
```

## Plugin marketplace sources

Register marketplaces from `owner/repo` shorthand, Git or SSH URLs, or local
marketplace roots. Pin a Git source with `--ref` and request sparse checkout
paths with repeatable `--sparse`.

```bash
codex plugin marketplace add owner/repo@v1 --sparse marketplace
codex plugin marketplace upgrade
```

`upgrade [name]` refreshes one named Git marketplace or all registered Git
marketplaces when no name is supplied. `remove` unregisters a marketplace.

## Repository and review workflows

- `/diff` includes staged, unstaged, and untracked changes.
- `/mention PATH` attaches a file to the conversation.
- `/init` scaffolds repository instructions.
- `/review` inspects the working tree for behavioral problems and missing
  tests. It uses the current session model unless `review_model` is configured.

For `/plugins` and `/agent`, see
[tui-and-session-controls.md](tui-and-session-controls.md).
