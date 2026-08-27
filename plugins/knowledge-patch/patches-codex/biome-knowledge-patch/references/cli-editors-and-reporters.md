# CLI, Editors, and Reporters

## Selecting files and checks

### Staged files (1.7-guide)

`--staged` limits a command to files in the Git index. Biome still reads
unstaged changes from each selected staged file, so the command is not an
isolated view of index contents.

```shell
biome check --staged .
```

### Rules, groups, domains, actions, and plugins

Repeatable `--only` and `--skip` initially accepted rules and groups, with
`--skip` taking precedence. Selecting a disabled rule enables it at `error`
when recommended and `warn` otherwise; selecting a group only enables its
recommended preset (1.8.0).

```shell
biome lint --only=style --skip=style/useNamingConvention .
```

`nursery` became a valid selector in 1.9.0. Domain names became selectable in
2.3.0:

```shell
biome lint --only=project
biome lint --skip=test
```

`biome check` and `biome ci` accept selectors for individual lint rules and
assist actions, their groups, and domains (2.4-guide).

```shell
biome check --only=suspicious/noDebugger src
biome ci --skip=project src
```

Plugin diagnostics also obey `--only` and `--skip` as of 2.5.1.

## Standard input and parsing switches

`--stdin-file-path` selects the appropriate parser and linter for Astro,
Svelte, and Vue input; Vue lint output is retained when input comes from
standard input (1.7.0).

Commands reading standard input return status 1 when diagnostics remain
unfixed. By contrast, `biome lint --write` and `biome lint --fix` do not return
an error status (1.9.0).

`--format-with-errors` allows formatting code with parse errors. The
`--css-parse-css-modules`, `--css-parse-tailwind-directives`,
`--json-parse-allow-comments`, and `--json-parse-allow-trailing-commas` flags
expose their parser controls without a configuration-file change (2.3.0).

## Watch mode and upgrades

Read-only `lint`, `format`, and `check` accept `--watch` and rerun diagnostics
when project files change. Watch mode cannot be combined with `--fix` or
`--write`. Select watcher behavior with `BIOME_WATCHER_KIND` and
`BIOME_WATCHER_POLLING` (2.5-guide).

```shell
biome check --watch .
```

`biome upgrade` upgrades Homebrew installations through `brew upgrade biome`
and manually installed binaries from the latest release. For package-manager
installations such as npm, it directs the user to upgrade through that package
manager (2.5-guide).

## Diagnostics and exit behavior

### Diagnostic caps (1.9.0)

`--max-diagnostics=none` removes the cap. Choosing any non-default reporter also
ignores `--max-diagnostics` and lifts the limit.

```shell
biome lint --max-diagnostics=none .
```

### Diagnostic levels and assists (2.4.0)

With `--diagnostic-level=error`, warning and informational diagnostics are
excluded from output and summary counts. Enforced assist violations remain
visible and still make `biome check` fail.

Rules configured with the `info` severity emit no error code and are unaffected
by `--error-on-warnings` (1.8.0).

### Verbose accounting (1.9.0)

The summary reporter includes parser diagnostics. `--verbose` lists files
Biome evaluated and files it changed, excluding ignored, unsupported,
extensionless, and unchanged files from the corresponding lists.

## Reporter formats

### JSON reports (1.7-guide)

Formatter and linter commands can emit experimental machine-readable JSON with
`--reporter=json` or `--reporter=json-pretty`.

```shell
biome lint --reporter=json-pretty .
```

### Summary, GitHub, and JUnit (1.8.0)

`--reporter=summary` groups formatter/import files and linter counts.
`--reporter=github` emits GitHub workflow annotations, and
`--reporter=junit` emits JUnit XML.

In GitHub Actions, `biome ci` automatically enables the GitHub reporter and
removes ANSI colors from workflow commands (2.4.0).

### GitLab (1.9.0)

`--reporter=gitlab` emits GitLab Code Quality JSON.

```shell
biome lint --reporter=gitlab .
```

### Checkstyle and reviewdog JSON (2.3.0)

The CLI supports Checkstyle XML and reviewdog diagnostic JSON.

```shell
biome check --reporter=checkstyle .
biome check --reporter=rdjson .
```

### Multiple outputs, files, and SARIF (2.4-guide)

`--reporter` is repeatable. Place `--reporter-file` next to a reporter flag to
write that reporter to an arbitrary file. `sarif` is also supported.

```shell
biome ci --reporter=default --reporter=rdjson --reporter-file=./reports/report.json
```

### Concise output (2.5-guide)

The `concise` reporter prints one-line diagnostics with substantially less
context than the default reporter.

```shell
biome check --reporter=concise .
```

## Profiling

`biome lint --profile-rules` and `biome check --profile-rules` report total,
average, minimum, maximum, and invocation count for lint rules, assist actions,
and GritQL plugins; CST-query time is excluded (2.4-guide).

As of 2.5.0, each plugin appears separately as `plugin/<pluginName>`, matching
plugin-suppression names rather than combining all plugins under
`plugin/plugin`.

## Language server and editors

### JavaScript editor documents (1.7-guide)

The Biome editor extension can parse JSX in documents associated with the
JavaScript language identifier, including `.js` files used as JSX.

### Workspaces (1.8.0)

The language server supports LSP Workspaces for editor projects with multiple
workspace folders.

### EditorConfig refresh (1.9.0)

With `formatter.useEditorconfig`, the language server applies the project-root
EditorConfig, watches it, and refreshes formatter settings when it changes.

### Inline editor configuration (2.4-guide)

Compatible clients can merge configuration over the project configuration for
language-server use without changing CLI behavior. VS Code uses
`biome.lsp.inlineConfig`; Zed uses `lsp.biome.settings.inline_config`.

### Paths and fix-all boundaries (2.4.0)

The language server resolves relative `configurationPath` values and
configurations outside the workspace. `source.fixAll.biome` no longer organizes
imports when `source.organizeImports.biome` is disabled; imports are organized
only when explicitly requested.

### Definitions and default enablement

Go-to-definition handles local and imported JavaScript variables, types, and
JSX components; CSS classes referenced from JSX or Vue, Svelte, and Astro; and
components or variables referenced across HTML-like files (2.5-guide).

In 2.5.1, go-to-definition became disabled by default because enabling it
builds the module graph and could cause memory leaks if Biome starts in a home
directory. Re-enable it in the extension's editor settings when needed.

## Daemon logs and watchers

`lsp-proxy` and `start` accept `--log-path`/`BIOME_LOG_PATH` and
`--log-prefix-name`/`BIOME_LOG_PREFIX_NAME`; the prefix defaults to `server.log`
and at most seven log files are retained (1.9.0).

```shell
biome start --log-path=./logs --log-prefix-name=biome.log
```

These daemon commands also accept `--watcher-kind`/`BIOME_WATCHER_KIND` with
`recommended` (default), `polling`, and `none`. Polling uses
`--watcher-polling-interval`/`BIOME_WATCHER_POLLING_INTERVAL`, defaulting to
2000 milliseconds (2.4-guide).

`format`, `lint`, `check`, `ci`, `search`, `lsp-proxy`, and `start` consistently
accept `--log-file`, `--log-level`, and `--log-kind` plus environment aliases.
Daemon commands additionally accept `--log-prefix-name` and `--log-path`. Set
`RUST_BACKTRACE=1` to include a stack trace for fatal errors (2.4-guide).

## JavaScript API spans

`spanInBytesToSpanInCodeUnits` converts byte-based diagnostic spans to the
UTF-16 code-unit offsets used by JavaScript strings (2.5-guide).
