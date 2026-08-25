# CLI execution and cloud workflows

## Directory-scoped resume

Interactive resume defaults to sessions associated with the current working
directory. `--all` broadens the picker; `--last` or a session ID bypasses the
picker.

```bash
codex resume --last
codex exec resume --last "Continue with the implementation"
```

Non-interactive work resumes through `exec resume`. Resumed work retains its
transcript, plan history, and approvals. Resume continues the same session;
fork creates a new thread while retaining the source transcript.

## Scripted output contracts

`codex exec` accepts a prompt as an argument or reads it from stdin when the
prompt is `-`.

```bash
printf '%s\n' 'Inventory licenses' | codex exec - --json \
  --output-schema result.schema.json \
  --output-last-message final.txt
```

- `--json` emits JSONL state-change events.
- `--output-schema` constrains the final response with JSON Schema.
- `--output-last-message` saves only the final natural-language response.
- `--ephemeral` prevents rollout-file persistence.
- `--skip-git-repo-check` permits use outside a Git repository.

## Isolated local review

`/review` launches a dedicated reviewer without modifying the working tree.
Choose a base-branch diff, all uncommitted changes, one commit, or custom
instructions. The reviewer uses the current session model unless
`review_model` overrides it in configuration.

## Cloud submission

`codex cloud` opens a task picker. `codex cloud exec` submits directly to a
configured environment and accepts one to four independent attempts.
Submission failures exit nonzero. In the picker, `Ctrl+O` selects an
environment.

```bash
codex cloud exec --env ENV_ID --attempts 3 "Summarize open bugs"
```

## Cloud listing and task application

`codex cloud list` supports environment filtering, cursor pagination, and a
result limit from 1 through 20. JSON output contains a `tasks` array and may
contain a `cursor` for the next page.

`codex apply TASK_ID` applies the latest diff for a cloud task, reports the
patched files, and exits nonzero when `git apply` conflicts.

```bash
codex cloud list --env ENV_ID --limit 20 --json
codex apply TASK_ID
```

## CLI plugins

The CLI can browse and add plugins from configured marketplaces, extending
terminal work with team tools and data.

## Marketplace source administration

`codex plugin marketplace add` accepts repository shorthand, Git or SSH URLs,
or a local marketplace root. Pin a Git source with `--ref` and request sparse
checkout paths with repeatable `--sparse`.

```bash
codex plugin marketplace add owner/repo --ref release \
  --sparse plugins/team
codex plugin marketplace upgrade
```

`upgrade` refreshes one named Git marketplace or all configured marketplaces.
`remove` deletes a configured marketplace source.

## Desktop launcher

`codex app [PATH]` opens the installed desktop app or starts its installer when
the app is absent. macOS opens the supplied workspace path. Windows prints the
path to open after installation.

```bash
codex app .
```
