# CLI execution and cloud workflows

## Resume sessions

Interactive resume defaults to sessions from the current working directory.
`--all` broadens the picker, while `--last` or a session ID skips it.

```bash
codex resume --last
codex exec resume --last "Continue with the implementation"
```

Non-interactive runs resume through `exec resume` and retain their transcript,
plan history, and approvals.

## Global flags and overrides

Global flags inherited by subcommands should follow the subcommand name.
Repeatable `-c key=value` overrides parse JSON values when possible.

```bash
codex exec --profile work -c 'features.unified_exec=true' --full-auto "Run the checks"
```

## Scripted output contracts

`codex exec` accepts a prompt from standard input with `-`. It can emit JSONL
state-change events, constrain the final response with a JSON Schema, save only
the final message separately, avoid rollout persistence with `--ephemeral`, and
operate outside Git with `--skip-git-repo-check`.

```bash
printf '%s\n' "Inventory licenses" | codex exec - --json \
  --output-schema result.schema.json --output-last-message final.txt
```

## Working root and extra writable roots

`--cd` chooses the working root without changing the shell directory. Repeat
`--add-dir` to expose additional writable roots for multi-project work.

```bash
codex --cd apps/frontend --add-dir ../backend --add-dir ../shared
```

## Image generation and edits

Generate or edit images through natural-language requests or the explicit
literal `$imagegen`. Attach an existing image when the task should transform or
extend it.

```bash
codex --image existing.png '$imagegen Extend this asset'
```

## Cloud task submission

`codex cloud` opens a task picker. `cloud exec` submits directly to a configured
environment and accepts one to four independent attempts. Submission failures
exit nonzero. In the picker, `Ctrl+O` selects an environment.

```bash
codex cloud exec --env ENV_ID --attempts 3 "Summarize open bugs"
```

## Cloud task inspection and application

`codex cloud list` supports environment filtering, cursor pagination, a 1–20
result limit, and JSON containing a `tasks` array plus an optional `cursor`.
`codex apply TASK_ID` applies the task's latest diff, reports patched files,
and exits nonzero on `git apply` conflicts.

```bash
codex cloud list --env ENV_ID --limit 20 --json
codex apply TASK_ID
```

## Desktop launcher

`codex app [PATH]` opens the installed desktop app or starts its installer when
absent. macOS opens the supplied workspace path; Windows prints the path to open
after installation.

```bash
codex app .
```

## Script-friendly authentication

`codex login` defaults to browser OAuth. `--device-auth` uses a device-code
flow, and `--with-api-key` reads the key from standard input. `codex login
status` reports the active mode and exits successfully when credentials exist.

```bash
printf '%s' "$API_KEY" | codex login --with-api-key
codex login status
```

## Global pnpm detection

Since `0.144.0`, global pnpm installations are detected so diagnostics and
updates use the correct package manager.

## Direct sandbox runner

The experimental `codex sandbox` helper runs arbitrary commands under the same
platform policy used internally: Seatbelt on macOS and Landlock plus seccomp on
Linux. Its `--full-auto` option grants the command write access to the current
workspace and `/tmp`.

```bash
codex sandbox linux -- make test
```
