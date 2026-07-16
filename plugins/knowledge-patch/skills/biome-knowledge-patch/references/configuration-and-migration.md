# Configuration and Migration

Use this reference when locating configuration, composing monorepo settings,
scoping files, migrating another tool, or updating deprecated Biome options.

## Contents

- [Discover and select configuration](#discover-and-select-configuration)
- [Compose root and nested configurations](#compose-root-and-nested-configurations)
- [Scope files and scanner work](#scope-files-and-scanner-work)
- [Configure VCS ignore behavior](#configure-vcs-ignore-behavior)
- [Migrate ESLint](#migrate-eslint)
- [Migrate Prettier](#migrate-prettier)
- [Import EditorConfig settings](#import-editorconfig-settings)
- [Configure rules and fixes](#configure-rules-and-fixes)
- [Gate language and parser support](#gate-language-and-parser-support)
- [Configure resolver experiments](#configure-resolver-experiments)

## Discover and select configuration

Biome searches configuration names in this order:

1. `biome.json`
2. `biome.jsonc`
3. `.biome.json`
4. `.biome.jsonc`

It searches the working directory, then ancestors, then the platform
configuration home:

- Linux: `$XDG_CONFIG_HOME`, or `$HOME/.config/biome`
- macOS: `/Users/$USER/Library/Application Support/biome`
- Windows: `C:\Users\$USER\AppData\Roaming\biome\config`

Use `--config-path` or `BIOME_CONFIG_PATH` with either a directory or a direct
configuration-file path. Package-exported configuration names in `extends`
resolve from the CLI working directory or the language-server project root.
Files ending in `.jsonc` are valid extension targets.

## Compose root and nested configurations

Treat every configuration as a root by default. Make a nested configuration
non-root with `"root": false`, or inherit the monorepo root with `"extends":
"//"`; the latter also implies `root: false`.

```json
{
  "extends": "//",
  "formatter": { "enabled": false }
}
```

Apply an array of `extends` entries from least to most relevant. Do not make an
extended file extend another file. Resolve paths declared inside shared
configuration relative to the configuration that extends it.

Merge a local `overrides` array with arrays inherited through `extends`, so
shared and package-specific entries both remain available. Within the effective
`overrides` array, only the first matching entry applies; put narrow patterns
before broad patterns.

```json
{
  "overrides": [
    { "includes": ["src/generated/**"], "formatter": { "enabled": false } },
    { "includes": ["src/**"], "formatter": { "lineWidth": 100 } }
  ]
}
```

Earlier configurations accumulated fields from every matching override, with
later unset fields no longer restoring base values. Reorder and consolidate
such overlapping entries when migrating to first-match semantics.

## Scope files and scanner work

Use ordered `files.includes` patterns. A later positive glob can re-include an
earlier ordinary exclusion:

```json
{
  "files": {
    "includes": ["**", "!**/*.test.js", "**/special.test.js", "!!**/dist"]
  }
}
```

Distinguish the two exclusion forms:

- `!pattern` prevents the matched files from being processed but still permits
  the scanner to index a file reached through an included dependency.
- `!!pattern` prevents both traversal and indexing. Use it when project-domain
  rules must not inspect that path.

Apply `linter.includes`, `formatter.includes`, and `assist.includes` after
`files.includes`. These tool-specific filters can only narrow the file set; they
cannot re-include a file excluded at the top level.

Replace deprecated `files.experimentalScannerIgnores` with `!!` entries by
running:

```shell
biome migrate --write
```

## Configure VCS ignore behavior

When ignore-file support is enabled, account for both `.gitignore` and
repository-local `.git/info/exclude`. In a linked worktree, Biome selects the
appropriate exclude file for that worktree.

Resolve `.gitignore` relative to an explicitly configured `vcs.root`. Let
`biome init` detect supported ignore files and turn on Git VCS integration; it
also writes a force-ignore for an existing `dist/` directory.

## Migrate ESLint

Run the writable migration to port legacy or flat ESLint configuration:

```shell
biome migrate eslint --write --include-inspired
```

The migration handles legacy `extends`, flat configuration, shared and plugin
configuration, `.eslintignore`, globals, rules, and overrides. It also migrates
the `eslintIgnore` field from `package.json` and converts gitignore-style
patterns, including root-relative `/src` to Biome's `./src` form.

Observe these constraints:

- Install or expose Node.js so the migration can resolve plugins and `extends`.
- Do not expect YAML ESLint configuration to work.
- Pass `--include-inspired` to include Biome rules that are inspired by, rather
  than direct equivalents of, ESLint rules.
- Review the result because migration overwrites the existing Biome
  configuration and may disable Biome's recommended rules.

Biome recognizes the e18e ESLint plugin as a source for `useAtIndex`,
`useExponentiationOperator`, `noPrototypeBuiltins`, `useDateNow`, `useSpread`,
and `useObjectSpread` mappings.

## Migrate Prettier

Run:

```shell
biome migrate prettier --write
```

The migration translates Prettier `overrides` into Biome overrides and attempts
to convert `.prettierignore` patterns into compatible globs. JavaScript
configuration requires Node.js. JSON5, TOML, and YAML configurations are not
supported.

Current ESLint and Prettier migrations preserve an existing Biome
`overrides` array instead of overwriting it. Still inspect ordering because
Biome uses first-match override selection.

## Import EditorConfig settings

Opt in with:

```json
{ "formatter": { "useEditorconfig": true } }
```

Biome imports formatting values from the single `.editorconfig` at the project
root. Explicit Biome configuration takes precedence. `biome ci` loads that file,
and the language server applies it, watches it, and refreshes settings after a
change.

## Configure rules and fixes

At group level, set `"all": false` to disable that group's recommended rules
even when top-level `recommended` is true or omitted. Configure an optionless
rule with object form containing only `level`; do not add `"options": null`.

```json
{
  "linter": {
    "rules": {
      "recommended": true,
      "style": { "all": false }
    }
  }
}
```

For current presets, use `linter.rules.preset` instead of the deprecated
`linter.rules.recommended`:

```json
{ "linter": { "rules": { "preset": "all" } } }
```

Choose `"recommended"` to preserve the former recommended selection or
`"all"` to select every stable rule. Neither value includes nursery rules. Run
`biome migrate --write` to update existing configuration.

Set an object-form rule's `fix` property to `none`, `safe`, or `unsafe` to
disable its action or override its applicability:

```json
{
  "linter": {
    "rules": {
      "correctness": {
        "noUnusedVariables": { "level": "error", "fix": "none" }
      }
    }
  }
}
```

Use `"info"` for informational diagnostics. They emit no error code and are not
promoted by `--error-on-warnings`.

## Gate language and parser support

CSS formatter and linter gates were initially opt-in under
`css.formatter.enabled` and `css.linter.enabled`, with matching CLI flags.
They are now enabled by default. JavaScript and JSON retain per-language linter
gates at `javascript.linter.enabled` and `json.linter.enabled`.

```shell
biome check --css-formatter-enabled=true --css-linter-enabled=true .
```

GraphQL formatting and linting are enabled by default and can be disabled
independently:

```json
{
  "graphql": {
    "formatter": { "enabled": false },
    "linter": { "enabled": false }
  }
}
```

Use explicit parser gates for syntax that is not inferred:

```json
{
  "javascript": {
    "parser": { "jsxEverywhere": false },
    "experimentalEmbeddedSnippetsEnabled": true
  },
  "css": {
    "parser": { "cssModules": true, "tailwindDirectives": true }
  },
  "html": {
    "experimentalFullSupportEnabled": true,
    "parser": { "interpolation": true, "vue": true }
  }
}
```

JSX in `.js` is accepted by default; set `jsxEverywhere: false` to reject it.
`html.parser.interpolation` separately enables `{{ expression }}` in plain
HTML. `html.parser.vue` enables Vue syntax in ordinary `.html` files.

## Configure resolver experiments

Enable default and named pnpm catalog resolution explicitly:

```json
{
  "javascript": {
    "resolver": { "experimentalPnpmCatalogs": true }
  }
}
```

Coverage IDs: `1.7-guide`, `1.7.0`, `1.8.0`, `1.9-guide`, `1.9.0`,
`2.0-guides`, `2.3.0`, `2.4-guide`, `2.4.0`, `2.5-guide`.
