---
name: biome-knowledge-patch
description: Biome
version: "2.5.0"
license: MIT
metadata:
  author: Nevaberry
---


# Biome Knowledge Patch

Use this skill when selecting current Biome configuration, CLI, formatter,
analyzer, language, editor, or plugin behavior. Read the reference matching the
task before editing configuration or interpreting diagnostics.

## Reference map

| Reference | Topics |
| --- | --- |
| [CLI, editors, and reporters](references/cli-editors-and-reporters.md) | Command selection, reporters, exit behavior, watch mode, daemon logging, LSP, editor actions, JavaScript API |
| [Configuration and migration](references/configuration-and-migration.md) | Configuration discovery and inheritance, monorepos, includes, overrides, VCS ignores, ESLint/Prettier migration |
| [Formatting, assists, and suppressions](references/formatting-assists-and-suppressions.md) | Formatter settings, import organization, assists, safe/unsafe fixes, suppressions, sorting |
| [GritQL search and plugins](references/gritql-search-and-plugins.md) | Structural search, custom definitions, lint plugins, languages, scoped plugins, rewrites |
| [Languages and frameworks](references/languages-and-frameworks.md) | CSS, GraphQL, HTML, SVG, JSON dialects, JSX/TypeScript syntax, React, Vue, Svelte, Astro |
| [Linting and project analysis](references/linting-and-project-analysis.md) | Domains, module graph and type inference, rule configuration, promotions, new rules, framework-aware analysis |

## Work from the effective configuration

1. Locate the configuration selected for the working directory or editor
   workspace.
2. Determine whether the file belongs to a nested package configuration.
3. Resolve `extends`, ordered include patterns, the first matching override,
   and any editor-only inline configuration.
4. Determine which language tools, linter domains, individual rules, and
   assist actions are active.
5. Run the narrowest suitable command and inspect its exit status and reporter
   output.

## Handle configuration roots and inheritance

Every configuration is a root unless it explicitly opts out. A nested package
must set `"root": false` or use `"extends": "//"`; the latter inherits the
monorepo root and implies `root: false`.

```json
{
  "extends": "//",
  "formatter": { "enabled": false }
}
```

Apply array-form `extends` entries from least to most relevant. An extended
configuration cannot itself extend another configuration. Resolve paths from a
shared configuration relative to the configuration that consumes it.

Pass `--config-path` or `BIOME_CONFIG_PATH` either a directory or the exact
configuration file. Remember that compatible editor clients can merge an
LSP-only inline configuration over the project configuration without changing
CLI behavior.

## Use ordered includes and overrides deliberately

Apply `files.includes` in order. A later positive pattern can re-include a path
excluded by an ordinary earlier `!`. Use `!!` only to stop the scanner from
traversing or indexing a path; use `!` when project or type analysis may still
need an excluded dependency.

```json
{
  "files": {
    "includes": ["**", "!**/*.test.js", "**/special.test.js", "!!**/dist"]
  }
}
```

Apply `linter.includes`, `formatter.includes`, and `assist.includes` after
`files.includes`. These narrower scopes cannot add a file back. Only the first
matching override applies, so put specific overrides before broad ones.

## Migrate deprecated configuration

Run `biome migrate --write` after an upgrade. In particular:

- Replace `files.experimentalScannerIgnores` with `!!` entries in
  `files.includes`.
- Replace `linter.rules.recommended` with `linter.rules.preset`; choose
  `"recommended"` or `"all"`, noting that `"all"` still excludes nursery.
- Replace `javascript.formatter.trailingComma` and `--trailing-comma` with
  `trailingCommas` and `--trailing-commas`.
- Replace removed, renamed, and promoted rule paths before adopting a new
  preset.

Read [Configuration and migration](references/configuration-and-migration.md)
before migrating ESLint or Prettier. Those migrations have Node.js,
configuration-format, ignore-pattern, and overwrite constraints.

## Enable analysis by domain

Use `linter.domains` for coherent framework, test, project, and type-aware rule
sets:

```json
{
  "linter": {
    "domains": {
      "project": "all",
      "types": "all",
      "react": "recommended",
      "test": "all"
    }
  }
}
```

Choose `"all"` when nursery rules are needed; `"recommended"` excludes them.
Matching package dependencies can activate supported framework and test
domains. Enabling an entire rule group does not enable domain-specific rules.

Budget extra runtime for `project` and `types`. Both scan the project, and
project analysis can trigger a full scan including `node_modules`. Use `!!`
only when the analyzer must not read a subtree at all.

## Configure assists independently

Assists are source actions without diagnostics. Give them their own scope and
action policy.

```json
{
  "assist": {
    "includes": ["src/**"],
    "actions": { "source": { "recommended": true } }
  }
}
```

Use assists for import/export organization and structural sorting. Remember
that `source.fixAll.biome` does not organize imports when
`source.organizeImports.biome` is disabled. Select lint rules and assist
actions for `check` or `ci` with repeatable `--only` and `--skip` filters.

## Control fixes and suppressions

An object-form rule configuration must include `level`. Its optional `fix`
field can be `none`, `safe`, or `unsafe` to override action applicability.
Applying fixes through `biome check` also formats the result.

Use dependency-specific suppression comments when only one hook dependency is
wrong. Use `// biome-ignore-all` for a whole file, or pair
`// biome-ignore-start` with `// biome-ignore-end` for a range. CSS and GraphQL
diagnostics also provide suppression actions.

## Choose language coverage explicitly

CSS and GraphQL formatting and linting run by default and can be disabled per
language. Enable full HTML-like parsing when Vue, Svelte, or Astro template
analysis is required. Plain HTML interpolation, Vue syntax in `.html`,
embedded JavaScript template snippets, and specialized CSS syntax have
separate parser or experimental switches.

Expect `.module.css` to enable CSS Modules syntax automatically. Enable the
Tailwind parser switch when its directives are present. Treat SVG as both a
formatted and linted language.

Read [Languages and frameworks](references/languages-and-frameworks.md) before
retaining old overrides that disable template linting; fuller framework
analysis may make those workarounds unnecessary.

## Run focused checks

Use repeatable `--only` and `--skip` selectors for rules, groups, domains,
assist actions, and plugins. `--skip` wins when selectors overlap.

```shell
biome check --only=suspicious/noDebugger src
biome ci --skip=project src
```

Use `--staged` to select paths from the Git index, but remember that Biome
reads the working-tree contents of every selected file. Use read-only `--watch`
with `lint`, `format`, or `check`; do not combine watch mode with `--write` or
`--fix`.

## Select reporters and diagnostics

Repeat `--reporter` to produce multiple outputs. Place `--reporter-file` next
to the reporter whose output it should capture.

```shell
biome ci --reporter=default --reporter=rdjson \
  --reporter-file=./reports/report.json
```

Choose among terminal, concise, summary, JSON, GitHub, GitLab, JUnit,
Checkstyle, RDJSON, and SARIF formats. Any non-default reporter lifts the
diagnostic cap; use `--max-diagnostics=none` to lift it for the default
reporter.

Do not infer success from visible warning counts alone. Diagnostic-level
filtering, enforced assist violations, standard-input behavior, and
`lint --write` or `--fix` have distinct exit semantics.

## Add GritQL safely

Single-quote shell queries containing GritQL backticks. Define reusable
patterns, predicates, and functions where useful. Load lint plugins from
top-level `plugins`, scope them with `includes`, and call
`register_diagnostic(...)` to report findings.

Plugin rewrites must be classified `safe` or `unsafe`; unclassified fixes are
unsafe. Apply unsafe rewrites only with the unsafe CLI option. Select the
plugin language explicitly for CSS or JSON instead of assuming JavaScript.

Read [GritQL search and plugins](references/gritql-search-and-plugins.md) before
authoring syntax-node patterns or cross-language transformations.

## Validate changes

Run the command used by CI after changing configuration. When analysis is
slow, use `--profile-rules` to inspect lint-rule, assist, and per-plugin timing.
When a daemon differs from the CLI, compare LSP-only configuration, workspace
roots, watcher mode, logging, and configuration paths before changing project
rules.
