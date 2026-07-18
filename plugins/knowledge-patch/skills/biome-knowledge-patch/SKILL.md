---
name: biome-knowledge-patch
description: Biome
license: MIT
version: 2.5.0
metadata:
  author: Nevaberry
---

# Biome Knowledge Patch

Use this skill to choose current Biome configuration, CLI, formatter, analyzer,
language, editor, and plugin behavior. Read the topic reference that matches the
task before changing configuration or interpreting diagnostics.

## Reference map

| Reference | Topics |
| --- | --- |
| [CLI, editors, and reporters](references/cli-editors-and-reporters.md) | Command selection, reporters, exit behavior, watch mode, daemon logging, LSP, editor actions, JavaScript API |
| [Configuration and migration](references/configuration-and-migration.md) | Configuration discovery and inheritance, monorepos, includes, overrides, VCS ignores, ESLint/Prettier migration, parser gates |
| [Formatting, assists, and suppressions](references/formatting-assists-and-suppressions.md) | Formatter settings, import organization, assists, safe/unsafe fixes, suppressions, sorting |
| [GritQL search and plugins](references/gritql-search-and-plugins.md) | Structural search, custom definitions, lint plugins, languages, scoped plugins, rewrites |
| [Languages and frameworks](references/languages-and-frameworks.md) | CSS, GraphQL, HTML, SVG, JSON dialects, JSX/TypeScript syntax, React, Vue, Svelte, Astro |
| [Linting and project analysis](references/linting-and-project-analysis.md) | Domains, module graph and type inference, rule configuration, promotions, new rules, framework-aware analysis |

## Work from the effective configuration

1. Locate the effective configuration before editing it.
2. Identify whether the file belongs to a nested package configuration.
3. Resolve `extends`, include patterns, the first matching override, and any
   editor-only inline configuration.
4. Determine which language tools, linter domains, and individual rules are
   active.
5. Run the narrowest suitable command, then inspect its exit status and chosen
   reporter output.

## Handle configuration roots and inheritance

Treat every configuration as a root unless it explicitly opts out. In a nested
package, use either `"root": false` or `"extends": "//"`; the latter inherits
the monorepo root and implies `root: false`.

```json
{
  "extends": "//",
  "formatter": { "enabled": false }
}
```

Apply array-form `extends` entries from least to most relevant. Do not make an
extended configuration extend another configuration. Resolve paths declared in
shared configuration relative to the configuration that consumes it.

Pass `--config-path` or `BIOME_CONFIG_PATH` either a directory or the
configuration file itself. Account for editor clients that overlay LSP-only
configuration without changing CLI behavior.

## Use ordered includes deliberately

Apply `files.includes` in order. Let a later positive pattern re-include an
ordinary earlier exclusion. Use `!!` only to prevent the scanner from traversing
or indexing a path; use `!` when project and type analysis may still need an
excluded dependency.

```json
{
  "files": {
    "includes": ["**", "!**/*.test.js", "**/special.test.js", "!!**/dist"]
  }
}
```

Apply `linter.includes`, `formatter.includes`, and `assist.includes` after
`files.includes`. Treat these narrower scopes as filters that cannot add a file
back. Put specific overrides before broad overrides because only the first
matching override applies.

## Migrate deprecated configuration

Run `biome migrate --write` after upgrades. In particular:

- Replace `files.experimentalScannerIgnores` with `!!` entries in
  `files.includes`.
- Replace `linter.rules.recommended` with `linter.rules.preset`; choose
  `"recommended"` or `"all"`, noting that `"all"` still excludes nursery.
- Replace `javascript.formatter.trailingComma` and `--trailing-comma` with the
  plural `trailingCommas` and `--trailing-commas` forms.
- Replace deprecated rule paths and renamed promoted rules before enabling new
  presets.

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

Choose `"all"` when nursery rules are required; `"recommended"` excludes them.
Expect matching dependencies to activate supported framework and test domains.
Do not assume enabling an entire rule group also enables domain-specific rules.

Budget extra runtime for `project` and `types`: both scan the project, and
project rules can trigger a full scan including `node_modules`. Use `!!` only
when the analyzer must not read a subtree at all.

## Configure assists independently

Treat assists as source actions without diagnostics. Give them their own file
scope and action policy.

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
`source.organizeImports.biome` is disabled. Select lint rules and assist actions
for `check` or `ci` with repeatable `--only` and `--skip` filters.

## Control fixes and suppressions

Set a rule's object-form `fix` to `none`, `safe`, or `unsafe` to override action
applicability. Applying fixes through `biome check` also formats the result.

Use dependency-specific suppression comments when only one hook dependency is
wrong. Use `// biome-ignore-all` for a whole file, or pair
`// biome-ignore-start` and `// biome-ignore-end` for a range. CSS and GraphQL
diagnostics also expose suppression actions.

## Choose current language coverage

Expect CSS and GraphQL formatting and linting to run by default, while allowing
each tool to be disabled per language. Enable full HTML-like parsing when Vue,
Svelte, or Astro template analysis is required. Keep plain HTML interpolation,
Vue syntax in `.html`, embedded JavaScript template snippets, and specialized
CSS syntax behind their respective parser or experimental switches.

Expect `.module.css` to enable CSS Modules syntax automatically. Use the
dedicated parser controls for Tailwind directives or nonstandard input when
automatic detection is insufficient. Treat SVG as a formatted and linted
language.

Read [Languages and frameworks](references/languages-and-frameworks.md) before
changing overrides that disable template linting; fuller framework analysis may
make those workarounds unnecessary.

## Run focused checks

Use repeatable `--only` and `--skip` selectors for rules, groups, domains, and
assist actions. Let `--skip` win when selectors overlap.

```shell
biome check --only=suspicious/noDebugger src
biome ci --skip=project src
```

Use `--staged` to select files in the Git index, but remember that Biome reads
the working-tree contents of each selected file rather than an isolated index
snapshot. Use read-only `--watch` with `lint`, `format`, or `check`; do not
combine watch mode with `--write` or `--fix`.

## Select reporters and diagnostics

Repeat `--reporter` to produce multiple outputs and place `--reporter-file`
next to the reporter whose output it should capture.

```shell
biome ci --reporter=default --reporter=rdjson \
  --reporter-file=./reports/report.json
```

Choose among terminal, concise, summary, JSON, GitHub, GitLab, JUnit,
Checkstyle, RDJSON, and SARIF outputs according to the consumer. A non-default
reporter lifts the diagnostic cap. Use `--max-diagnostics=none` to lift it for
the default reporter.

Do not infer command success from visible warning counts alone. Diagnostic
level filtering, enforced assist violations, standard-input behavior, and
`lint --write`/`--fix` have distinct exit semantics.

## Add GritQL safely

Single-quote shell queries that contain GritQL backticks. Define reusable
patterns, predicates, and functions where useful. Load lint plugins from
top-level `plugins`, scope them with `includes`, and use
`register_diagnostic(...)` to report findings.

Mark rewrite fixes `safe` or `unsafe`; unclassified plugin fixes are unsafe.
Run unsafe rewrites only with the corresponding unsafe CLI option. Select the
plugin language explicitly for CSS or JSON rather than assuming JavaScript.

Read [GritQL search and plugins](references/gritql-search-and-plugins.md) before
authoring syntax-node patterns or cross-language transformations.

## Validate changes

Run the command used by CI after changing configuration. When analysis is slow,
use `--profile-rules` to inspect lint-rule, assist, and plugin timing. When a
daemon behaves differently from the CLI, compare LSP-only configuration,
workspace roots, watcher mode, log settings, and configuration paths before
changing project rules.
