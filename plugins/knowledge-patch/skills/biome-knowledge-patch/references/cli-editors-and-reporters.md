# CLI, Editors, and Reporters

Use this reference when selecting commands, interpreting exit behavior, wiring
machine-readable output, or diagnosing differences between CLI and editor runs.

## Contents

- [File selection and focused runs](#file-selection-and-focused-runs)
- [Standard input and embedded files](#standard-input-and-embedded-files)
- [Watch mode](#watch-mode)
- [Reporter formats](#reporter-formats)
- [Diagnostic accounting and exit behavior](#diagnostic-accounting-and-exit-behavior)
- [Profiling](#profiling)
- [Logging and fatal errors](#logging-and-fatal-errors)
- [Configuration paths and discovery in tools](#configuration-paths-and-discovery-in-tools)
- [Editor actions and navigation](#editor-actions-and-navigation)
- [Initialization, upgrades, and API spans](#initialization-upgrades-and-api-spans)

## File selection and focused runs

Use `--staged` to limit a command to paths present in the Git index:

```shell
biome check --staged .
```

Treat this as path selection, not an isolated view of staged blobs: Biome reads
unstaged working-tree changes from any selected file.

Use repeatable `--only` and `--skip` selectors. `--skip` takes precedence. A
selected disabled rule is enabled at `error` when it is recommended and at
`warn` otherwise; selecting a group enables only its recommended preset. Nursery
was not selectable initially but is now a valid rule-group selector.

```shell
biome lint --only=style --skip=style/useNamingConvention .
biome lint --only=nursery .
```

Use linter-domain names with `lint`, and use rules, groups, domains, or assist
actions with `check` and `ci`:

```shell
biome lint --only=project
biome lint --skip=test
biome check --only=suspicious/noDebugger src
biome ci --skip=project src
```

## Standard input and embedded files

Pass `--stdin-file-path` so input receives the correct language, parser, and
lint behavior. It recognizes Astro, Svelte, and Vue input, and preserves Vue
lint output supplied through standard input.

Commands that read standard input return status 1 when diagnostics remain
unfixed. By contrast, `biome lint --write` and `biome lint --fix` do not return
an error status merely because lint diagnostics were found.

## Watch mode

Run `lint`, `format`, or `check` with `--watch` to repeat a read-only operation
after project files change:

```shell
biome check --watch .
```

Do not combine watch mode with `--fix` or `--write`. Choose its file watcher with
`BIOME_WATCHER_KIND` and `BIOME_WATCHER_POLLING`.

Daemon commands `lsp-proxy` and `start` use
`--watcher-kind`/`BIOME_WATCHER_KIND`; accepted values are `recommended`
(default), `polling`, and `none`. For polling, set
`--watcher-polling-interval`/`BIOME_WATCHER_POLLING_INTERVAL`; the default is
2000 milliseconds.

## Reporter formats

Use the following reporter forms according to the consumer:

- `--reporter=json` and `--reporter=json-pretty` emit machine-readable formatter
  and linter reports.
- `--reporter=summary` groups formatter/import files and linter counts; it also
  includes parser diagnostics.
- `--reporter=github` emits workflow annotations; `biome ci` selects it
  automatically in GitHub Actions and strips ANSI color from workflow commands.
- `--reporter=gitlab` emits GitLab Code Quality JSON.
- `--reporter=junit` emits JUnit XML.
- `checkstyle` emits Checkstyle XML.
- `rdjson` emits reviewdog diagnostic JSON.
- `sarif` emits SARIF.
- `concise` prints one-line diagnostics with much less context than the default.

Examples:

```shell
biome lint --reporter=json-pretty .
biome check --reporter=checkstyle .
biome check --reporter=rdjson .
biome check --reporter=concise .
```

Repeat `--reporter` to emit more than one format. Place `--reporter-file`
immediately next to the reporter whose output belongs in that file:

```shell
biome ci --reporter=default --reporter=rdjson \
  --reporter-file=./reports/report.json
```

## Diagnostic accounting and exit behavior

Use `--max-diagnostics=none` to remove the default diagnostic cap. Selecting any
non-default reporter also ignores `--max-diagnostics` and lifts the limit.

```shell
biome lint --max-diagnostics=none .
```

Use `--verbose` to list files evaluated and files changed. Biome excludes
ignored, unsupported, extensionless, and unchanged files from the corresponding
lists.

With `--diagnostic-level=error`, omit warnings and informational diagnostics
from both output and summary counts. Enforced assist violations remain visible
and still make `biome check` fail. Informational lint severity itself has no
error code and is unaffected by `--error-on-warnings`.

Use `--format-with-errors` only when formatting code that still has parse
errors. Use the dedicated parser switches when a one-off command must override
configuration:

- `--css-parse-css-modules`
- `--css-parse-tailwind-directives`
- `--json-parse-allow-comments`
- `--json-parse-allow-trailing-commas`

## Profiling

Run `biome lint --profile-rules` or `biome check --profile-rules` to report
total, average, minimum, maximum, and invocation count for lint rules, assist
actions, and GritQL plugins. CST-query time is excluded. Plugin timing is broken
out as `plugin/<pluginName>`, using the same name as plugin suppressions rather
than combining all plugins into one entry.

## Logging and fatal errors

Use `--log-file`, `--log-level`, and `--log-kind`, or their environment
aliases, consistently with `format`, `lint`, `check`, `ci`, `search`,
`lsp-proxy`, and `start`.

For daemon commands, also use `--log-path`/`BIOME_LOG_PATH` and
`--log-prefix-name`/`BIOME_LOG_PREFIX_NAME`. The prefix defaults to
`server.log`, and the language server retains at most seven log files.

```shell
biome start --log-path=./logs --log-prefix-name=biome.log
```

Set `RUST_BACKTRACE=1` to include a stack trace for fatal errors.

## Configuration paths and discovery in tools

Pass `--config-path` or `BIOME_CONFIG_PATH` either a configuration directory or
the configuration file itself:

```shell
biome format --config-path=./config/biome.json ./src
```

The language server resolves relative `configurationPath` values and can use a
configuration outside the editor workspace. It supports multiple LSP workspace
folders.

Compatible editors may merge an inline configuration over the project
configuration only for language-server operations. VS Code exposes
`biome.lsp.inlineConfig`; Zed uses `lsp.biome.settings.inline_config`.

```json
{
  "biome.lsp": {
    "inlineConfig": {
      "linter": { "rules": { "suspicious": { "noConsole": "off" } } }
    }
  }
}
```

When `formatter.useEditorconfig` is enabled, the language server applies and
watches the root `.editorconfig`, refreshing formatting settings after edits;
`biome ci` loads it as well.

The editor extension can parse JSX in documents associated with the JavaScript
language identifier, including React projects that keep JSX in `.js` files.

## Editor actions and navigation

Treat `source.fixAll.biome` and `source.organizeImports.biome` as separate
actions. Disabling import organization prevents fix-all from organizing imports;
organization runs only when explicitly requested.

The language server provides go-to-definition for local and imported JavaScript
variables, types, and JSX components; CSS classes referenced from JSX or Vue,
Svelte, and Astro; and components or variables referenced across HTML-like
files.

## Initialization, upgrades, and API spans

`biome init` detects supported ignore files, enables Git VCS integration with
ignore-file use, and force-ignores an existing `dist/` directory.

`biome upgrade` upgrades Homebrew installs with `brew upgrade biome` and
manually installed standalone binaries from the latest release. For npm and
other package-manager installs, it directs the user to that package manager
instead.

In the JavaScript API, call `spanInBytesToSpanInCodeUnits` to convert byte-based
diagnostic spans to the UTF-16 code-unit offsets used by JavaScript strings.

Coverage IDs: `1.7-guide`, `1.7.0`, `1.8.0`, `1.9.0`, `2.3.0`, `2.4-guide`,
`2.4.0`, `2.5-guide`, `2.5.0`.
