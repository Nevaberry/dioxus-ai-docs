# Configuration and Migration

## Migration commands

### ESLint migration (1.7-guide)

`biome migrate eslint --write` ports legacy or flat ESLint configuration,
including legacy `extends`, shared and plugin configurations, `.eslintignore`,
globals, rules, and overrides. It needs Node.js to resolve plugins and
`extends`, does not support YAML configuration, and skips rules merely inspired
by ESLint unless `--include-inspired` is passed. Migration overwrites the
existing Biome configuration and may disable its recommended rules.

```shell
biome migrate eslint --write --include-inspired
```

Migration also handles the `eslintIgnore` field from `package.json` and
converts ESLint gitignore-style patterns, including root-relative `/src` to
Biome's `./src` form (1.8.0).

### Prettier migration (1.7-guide)

`biome migrate prettier --write` translates Prettier `overrides` into Biome
overrides and attempts to convert `.prettierignore` patterns to Biome-compatible
globs. JavaScript configurations require Node.js; JSON5, TOML, and YAML
configurations are unsupported.

As of 1.9.0, Prettier and ESLint migration preserve an existing
configuration's `overrides` rather than overwriting them.

### Scanner-ignore migration (2.3.0)

`files.experimentalScannerIgnores` is deprecated. Replace it with `!!`
force-ignore entries in `files.includes`; `biome migrate --write` performs this
update.

### Rule preset migration (2.5-guide)

`linter.rules.preset` replaces deprecated `linter.rules.recommended`.
`"all"` selects all stable rules while excluding nursery; `"recommended"`
preserves the former recommended selection. Run `biome migrate --write` to
update existing configuration.

## Discovery and explicit paths

### Search order (2.4-guide)

Biome searches configuration names in this order:

1. `biome.json`
2. `biome.jsonc`
3. `.biome.json`
4. `.biome.jsonc`

It searches first in the working directory, then ancestors, then the platform
configuration home. The fallback locations are `$XDG_CONFIG_HOME` or
`$HOME/.config/biome` on Linux, `/Users/$USER/Library/Application Support/biome`
on macOS, and `C:\Users\$USER\AppData\Roaming\biome\config` on Windows.

### Direct paths (1.7-guide)

`--config-path` and `BIOME_CONFIG_PATH` accept a configuration directory or the
configuration file itself.

```shell
biome format --config-path=./config/biome.json ./src
```

As of 2.4.0, the language server resolves relative `configurationPath` values
and configurations outside the editor workspace.

## Inheritance and monorepos

### Shared and JSONC configurations (1.7.0)

Package-exported configurations named in `extends` resolve from the CLI
working directory or the LSP project root. `.jsonc` files are valid extension
targets.

### Nested roots (2.0-guides)

Every configuration is a root by default. A nested configuration must set
`"root": false` or use `"extends": "//"`; the latter inherits the monorepo
root configuration and implies `root: false`.

```json
{
  "extends": "//",
  "formatter": { "enabled": false }
}
```

Array-form `extends` entries apply from least to most relevant. Extended files
cannot extend other files. Paths declared in shared configuration resolve
relative to the configuration that extends it.

### Package-local analysis (2.0.0)

Rules that consult `package.json` use the manifest belonging to the relevant
package in a monorepo, keeping dependency-sensitive analysis scoped to that
package.

## Includes, excludes, and overrides

### Ordered includes and force-ignores (2.0-guides)

`files.includes` supports ordered negations: a later positive pattern can
re-include an earlier exception. `!!` prevents the scanner from indexing or
traversing a path. A normal `!` only prevents processing, so project-domain
analysis may still index an excluded file when an included file imports it.

```json
{
  "files": {
    "includes": ["**", "!**/*.test.js", "**/special.test.js", "!!**/dist"]
  }
}
```

`linter.includes`, `formatter.includes`, and `assist.includes` run after
`files.includes`. They can only narrow the initial set and cannot add a file
back.

### Override behavior before and after 2.0

In 1.8.0, overlapping matching overrides accumulated: an unset field in a
later override did not restore the base and conceal an earlier override. Local
`overrides` also merged with inherited arrays rather than replacing them as of
1.9.0.

With the 2.0-guides behavior, only the first matching override entry is used.
Put specific patterns before broad patterns:

```json
{
  "overrides": [
    { "includes": ["src/generated/**"], "formatter": { "enabled": false } },
    { "includes": ["src/**"], "formatter": { "lineWidth": 100 } }
  ]
}
```

## Rule and tool configuration shapes

### Group and optionless rules (1.7.0)

At group level, `"all": false` disables the group's recommended rules even
when top-level `recommended` is true or omitted. Before object-form `level`
became mandatory, a rule without options could use object form with only
`level`, without `"options": null`.

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

As of 2.5.1, every object-form rule configuration must include `level`; omitting
it is a configuration error.

```json
{ "linter": { "rules": { "suspicious": { "noConsole": { "level": "warn" } } } } }
```

### Independent assist scope (2.0-guides)

Assist has its own enablement, file scope, and recommended safe source actions:

```json
{
  "assist": {
    "includes": ["src/**"],
    "actions": { "source": { "recommended": true } }
  }
}
```

### EditorConfig

Set `formatter.useEditorconfig` to `true` to import formatting settings from
the single `.editorconfig` at the project root; explicit Biome configuration
wins (1.9-guide).

```json
{ "formatter": { "useEditorconfig": true } }
```

When enabled, `biome ci` loads the root file, and the language server applies
and watches it and refreshes formatting settings after changes (1.9.0).

### Editor-only overlay (2.4-guide)

Compatible clients can merge an editor-only configuration over the project
configuration without changing CLI behavior. VS Code exposes
`biome.lsp.inlineConfig`; Zed uses `lsp.biome.settings.inline_config`.

```json
{ "biome.lsp": { "inlineConfig": { "linter": { "rules": { "suspicious": { "noConsole": "off" } } } } } } }
```

## VCS integration and repository ignores

`biome init` detects supported ignore files and enables Git VCS integration
with ignore-file use. If it finds `dist/`, it adds a force-ignore entry
(2.3.0).

With ignore-file support enabled, Biome also honors `.git/info/exclude`, using
the appropriate exclude file in linked worktrees (2.5-guide). An explicitly
configured `vcs.root` is the base used to resolve `.gitignore` (2.4.0).

## Resolver configuration

The JavaScript resolver can read default and named pnpm catalogs when
`javascript.resolver.experimentalPnpmCatalogs` is enabled (2.5-guide).

```json
{
  "javascript": {
    "resolver": { "experimentalPnpmCatalogs": true }
  }
}
