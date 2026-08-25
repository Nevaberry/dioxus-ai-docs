---
name: biome-knowledge-patch
description: Biome
version: 2.5.0
license: MIT
metadata:
  author: Nevaberry
---


# Biome Knowledge Patch

Use this skill when configuring, migrating, running, or integrating Biome and
the requested work touches the behaviors summarized here. Read the topic guide
that matches the task before changing configuration or recommending a command.

## Topic index

| Reference | Topics |
| --- | --- |
| [CLI, Editors, and Reporters](references/cli-editors-and-reporters.md) | Command selection and filters, reporters, watch mode, daemon controls, standard input, editor and language-server behavior |
| [Configuration and Migration](references/configuration-and-migration.md) | ESLint and Prettier migration, configuration discovery and inheritance, includes and overrides, VCS ignores, presets |
| [Formatting, Assists, and Suppressions](references/formatting-assists-and-suppressions.md) | Formatter settings, import organization, assists, fix policy, and suppression forms |
| [GritQL Search and Plugins](references/gritql-search-and-plugins.md) | Structural search, reusable definitions, plugin diagnostics and fixes, target languages, path scoping |
| [Languages and Frameworks](references/languages-and-frameworks.md) | CSS, GraphQL, HTML, SVG, JSON, embedded languages, Vue, Svelte, Astro, React, and parser compatibility |
| [Linting and Project Analysis](references/linting-and-project-analysis.md) | Rule changes and options, domains, module-graph and type-aware analysis, profiling, framework-aware linting |

## Breaking changes and migrations

### Rule presets

Use `linter.rules.preset` instead of the deprecated
`linter.rules.recommended`. The `"all"` preset selects all stable rules but
still excludes nursery rules; `"recommended"` preserves the former
recommended selection. Update an existing configuration with:

```shell
biome migrate --write
```

### Object-form rule configuration

Include `level` whenever a rule uses object form. Omitting it is a
configuration error:

```json
{ "linter": { "rules": { "suspicious": { "noConsole": { "level": "warn" } } } } }
```

An optionless rule object needs only `level`; do not add an
`"options": null` property.

### Scanner ignores

Replace deprecated `files.experimentalScannerIgnores` with `!!` force-ignore
patterns in `files.includes`. A force-ignore stops traversal and indexing; a
single `!` only excludes processing and can still allow project analysis to
index an imported file.

```json
{
  "files": {
    "includes": ["**", "!**/*.test.js", "**/special.test.js", "!!**/dist"]
  }
}
```

### Override selection

Only the first matching `overrides` entry applies. Put specific patterns before
broader patterns:

```json
{
  "overrides": [
    { "includes": ["src/generated/**"], "formatter": { "enabled": false } },
    { "includes": ["src/**"], "formatter": { "lineWidth": 100 } }
  ]
}
```

### Renamed formatter and lint settings

- Use `javascript.formatter.trailingCommas` and `--trailing-commas`; the
  singular `trailingComma` and `--trailing-comma` names are deprecated.
- Replace `correctness/noInvalidNewBuiltin` with
  `correctness/noInvalidBuiltinInstantiation`.
- Replace `style/useSingleCaseStatement` with
  `correctness/noSwitchDeclarations`.
- Replace `suspicious/noConsoleLog` with `suspicious/noConsole`.
- Stable-rule promotion renamed `noFloatingClasses` to
  `noUnusedInstantiation`, `noMultiStr` to `noMultilineString`, `useFind` to
  `useArrayFind`, and `useSpread` to `useSpreadOverApply`.

### Removed and relocated rules

Do not configure the removed nursery rule `useAnchorHref`; `useValidAnchor`
covers its use case. Domain-specific rules are not enabled merely by enabling
their rule group. They require a matching dependency, an explicit domain, or
explicit rule configuration.

## Configuration quick reference

### Monorepo roots and inheritance

Each configuration is a root by default. For a nested configuration, set
`"root": false` or use `"extends": "//"`; the latter inherits the monorepo
root and implies `root: false`.

```json
{
  "extends": "//",
  "formatter": { "enabled": false }
}
```

Array-form `extends` entries run from least to most relevant. Extended files
cannot extend other files, and paths inside shared configuration resolve
relative to the configuration that extends it.

### Tool-specific file scopes

Apply `linter.includes`, `formatter.includes`, and `assist.includes` after
`files.includes`. They can narrow the initial file set but cannot add files
back. Configure assist scope and recommended source actions separately from
linting and formatting.

## CLI quick reference

### Focus checks

Repeat `--only` and `--skip` to select rules, groups, domains, assist actions,
or plugins where the command supports them. `--skip` takes precedence.

```shell
biome check --only=suspicious/noDebugger src
biome ci --skip=project src
```

Selecting a disabled rule enables it at `error` when recommended and `warn`
otherwise. Selecting a group enables only its recommended preset. Nursery is
also a valid selector.

### Staged and watched files

`--staged` selects files in the Git index, but Biome reads the current working
tree contents of each selected file rather than an isolated index snapshot.

```shell
biome check --staged .
```

Read-only `lint`, `format`, and `check` commands accept `--watch`. Do not combine
watch mode with `--fix` or `--write`.

```shell
biome check --watch .
```

### Diagnostics and reports

Use `--max-diagnostics=none` for no cap. A non-default reporter also lifts the
cap. `--reporter` is repeatable, and a neighboring `--reporter-file` sends that
reporter to a file.

```shell
biome ci --reporter=default --reporter=rdjson --reporter-file=./reports/report.json
```

Available outputs described in the reference include JSON, summary, GitHub,
GitLab, JUnit, Checkstyle, RDJSON, SARIF, and concise diagnostics.

## Linting quick reference

### Domains and project analysis

Use `linter.domains` with `"recommended"`, `"all"`, or `"none"`. Recommended
excludes nursery rules; all includes them. Project and type domains scan the
whole project and can materially increase lint time.

```json
{
  "linter": {
    "domains": { "project": "all", "types": "all" }
  }
}
```

The `project` domain supplies module-graph rules. The `types` domain enables
type inference; its covered rules are nursery rules and therefore require
`"types": "all"`, not `"recommended"`.

### Fix applicability

Object-form rule configuration accepts `fix: "none"`, `"safe"`, or
`"unsafe"` to disable actions or override applicability. Applying safe or
unsafe fixes through `biome check` also formats the result.

## Formatting and language quick reference

### Expansion and final newlines

`formatter.expand` and JavaScript- or JSON-specific overrides accept `"auto"`,
`"always"`, or `"never"`. In auto mode, an existing first-property line break
keeps an object multiline while fitting arrays collapse. `package.json`
behaves as always unless explicitly configured.

`formatter.trailingNewline` defaults to `true`; set it globally or per language
to `false` to remove the final newline.

### HTML and embedded content

The HTML formatter must be enabled explicitly. Embedded JavaScript and CSS use
their own formatter settings. `html.formatter.indentScriptAndStyle` defaults to
`false` and controls indentation inside `<script>` and `<style>` blocks.

Enable `javascript.experimentalEmbeddedSnippetsEnabled` to format and lint
recognized CSS, GraphQL, and Relay-tagged snippets in JavaScript template
literals.

### Import organization and other assists

Import organization is an assist rather than a lint diagnostic. It can move
imports across ordinary blank lines, merge same-module imports, sort attributes
and exports, and honor detached-comment boundaries. Consult the formatting
reference for other structural-sorting assists.

## GritQL quick reference

Run experimental structural searches with `biome search`. Quote a query that
contains GritQL backticks with shell single quotes when backticks would be
interpreted as command substitution.

```shell
biome search '`console.$method($args)` where { $method <: or { `log`, `info` } }' ./
```

Top-level `plugins` entries load `.grit` lint patterns. Plugins can register
diagnostics, target supported languages, restrict execution with `includes`,
and attach safe or unsafe rewrites. Read the plugin guide before authoring or
changing a pattern.

## Editor note

Go-to-definition is disabled by default as of 2.5.1 because enabling it builds
the module graph and could cause memory leaks when Biome starts in a home
directory. Re-enable it in the Biome extension settings only when needed.
