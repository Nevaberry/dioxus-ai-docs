# CLI, Editors, and Reporters

## Select files and input behavior

`--staged` limits a command to paths present in the Git index (since
`1.7-guide`):

```shell
biome check --staged .
```

Biome reads the working-tree contents of each selected file, including
unstaged edits; this is not an isolated snapshot of the index.

`--stdin-file-path` supplies the virtual filename needed to parse and lint
Astro, Svelte, and Vue standard input correctly (since `1.7.0`). Vue lint
diagnostics are retained for standard-input sources.

Commands reading standard input return status 1 when diagnostics remain
unfixed (since `1.9.0`). By contrast, `biome lint --write` and
`biome lint --fix` do not return an error status for remaining lint findings.
Do not use those exit codes interchangeably in scripts.

`--format-with-errors` permits formatting a file with parse errors (since
`2.3.0`). The same release exposes parser gates directly as
`--css-parse-css-modules`, `--css-parse-tailwind-directives`,
`--json-parse-allow-comments`, and `--json-parse-allow-trailing-commas`.

## Focus a run

`--only` and `--skip` are repeatable, and `--skip` wins when both match (since
`1.8.0`). They initially selected rules and groups. Selecting a disabled rule
enables it at `error` when recommended and at `warn` otherwise; selecting a
group enables only its recommended preset. Nursery became selectable in
`1.9.0`.

```shell
biome lint --only=style --skip=style/useNamingConvention .
biome lint --only=nursery .
```

Linter domains became valid selectors in `2.3.0`:

```shell
biome lint --only=project
biome lint --skip=test
```

`biome check` and `biome ci` accept selectors for individual lint rules,
assist actions, their groups, and domains (since `2.4-guide`). Plugin
diagnostics also obey `--only` and `--skip` (since `2.5.1`).

```shell
biome check --only=suspicious/noDebugger src
biome ci --skip=project src
```

## Choose a reporter

Formatter and linter commands can emit JSON or pretty JSON with
`--reporter=json` and `--reporter=json-pretty` (since `1.7-guide`). Reporter
coverage subsequently expanded:

- `summary` groups formatter/import files and linter counts; `github` emits
  workflow annotations; and `junit` emits JUnit XML (since `1.8.0`).
- The summary includes parser diagnostics, while `--verbose` lists evaluated
  and changed files but excludes ignored, unsupported, extensionless, or
  unchanged paths from the corresponding lists (since `1.9.0`).
- `gitlab` emits GitLab Code Quality JSON (since `1.9.0`).
- `checkstyle` emits Checkstyle XML and `rdjson` emits reviewdog diagnostic
  JSON (since `2.3.0`).
- `sarif` is available, and `--reporter` is repeatable (since `2.4-guide`).
- `concise` prints one-line diagnostics with much less context than the
  default reporter (since `2.5-guide`).

Place `--reporter-file` directly after the reporter whose output should go to
that file:

```shell
biome ci --reporter=default --reporter=rdjson \
  --reporter-file=./reports/report.json
```

`--max-diagnostics=none` removes the default diagnostic cap (since `1.9.0`).
Any non-default reporter also ignores `--max-diagnostics` and emits an
unbounded result.

With `--diagnostic-level=error`, warnings and informational findings are absent
from both output and summary counts (since `2.4.0`). Enforced assist violations
remain visible and cause `biome check` to fail. In GitHub Actions, `biome ci`
automatically enables the GitHub reporter and strips ANSI colors from workflow
commands.

## Profile rules and plugins

`biome lint --profile-rules` and `biome check --profile-rules` report total,
average, minimum, maximum, and invocation count for lint rules, assist actions,
and GritQL plugins (since `2.4-guide`). CST-query time is excluded.

Since `2.5.0`, each plugin has a separate `plugin/<pluginName>` row matching
the name used for plugin suppressions, rather than every plugin being combined
under `plugin/plugin`.

## Use read-only watch mode

`lint`, `format`, and `check` accept `--watch` (since `2.5-guide`). Watch mode
reruns diagnostics when project files change and cannot be combined with
`--fix` or `--write`.

```shell
biome check --watch .
```

Watcher selection is also available to `lsp-proxy` and `start` through
`--watcher-kind` or `BIOME_WATCHER_KIND` (since `2.4-guide`). Values are
`recommended` (default), `polling`, and `none`. Polling uses
`--watcher-polling-interval` or `BIOME_WATCHER_POLLING_INTERVAL`, defaulting to
2000 milliseconds. CLI watch mode uses `BIOME_WATCHER_KIND` and
`BIOME_WATCHER_POLLING`.

## Configure daemon logging

`lsp-proxy` and `start` accept `--log-path`/`BIOME_LOG_PATH` and
`--log-prefix-name`/`BIOME_LOG_PREFIX_NAME` (since `1.9.0`). The prefix defaults
to `server.log`, and the language server retains at most seven log files.

```shell
biome start --log-path=./logs --log-prefix-name=biome.log
```

`format`, `lint`, `check`, `ci`, `search`, `lsp-proxy`, and `start` consistently
accept `--log-file`, `--log-level`, and `--log-kind` plus environment aliases
(since `2.4-guide`). Daemon commands additionally retain their log-prefix and
log-path controls. Set `RUST_BACKTRACE=1` when a fatal error needs a stack
trace.

## Account for editor and language-server state

The language server supports multiple LSP workspace folders (since `1.8.0`).
It can resolve a relative `configurationPath` and a configuration outside the
editor workspace (since `2.4.0`). Compatible clients may also provide an
inline, editor-only configuration that does not affect CLI behavior.

The editor extension can parse JSX in a document associated with the
JavaScript language identifier (since `1.7-guide`), supporting projects that
use `.js` as JSX.

Go-to-definition covers local and imported JavaScript variables, types, and
JSX components; CSS classes referenced by JSX, Vue, Svelte, or Astro; and
components or variables referenced across HTML-like files (since
`2.5-guide`). Starting with `2.5.1`, this feature is disabled by default because
building the module graph can leak memory when Biome is started in a home
directory. Re-enable it in the extension's editor settings only when needed.

`source.fixAll.biome` does not organize imports when
`source.organizeImports.biome` is disabled (since `2.4.0`). Import organization
must be requested explicitly.

## Upgrade standalone installations

`biome upgrade` upgrades a Homebrew installation by running
`brew upgrade biome` and upgrades manually installed binaries from the latest
release (since `2.5-guide`). For npm and other package-manager installations,
it directs the user to upgrade with that package manager instead.

## Convert JavaScript API spans

The JavaScript API provides `spanInBytesToSpanInCodeUnits` (since
`2.5-guide`). Use it to convert byte-based diagnostic spans to the UTF-16 code
unit offsets used by JavaScript strings.
