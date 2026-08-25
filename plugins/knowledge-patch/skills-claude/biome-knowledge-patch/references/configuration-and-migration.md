# Configuration and Migration

## Discover the effective configuration

Biome searches for configuration names in this order: `biome.json`,
`biome.jsonc`, `.biome.json`, then `.biome.jsonc`. It searches the working
directory, then ancestors, then the platform configuration home (since
`2.4-guide`). The fallback is `$XDG_CONFIG_HOME` or `$HOME/.config/biome` on
Linux, `/Users/$USER/Library/Application Support/biome` on macOS, and
`C:\Users\$USER\AppData\Roaming\biome\config` on Windows.

`--config-path` and `BIOME_CONFIG_PATH` accept either a configuration directory
or the file itself (since `1.7-guide`):

```shell
biome format --config-path=./config/biome.json ./src
```

Compatible editors can merge inline configuration over the project
configuration for the language server only (since `2.4-guide`). VS Code uses
`biome.lsp.inlineConfig`; Zed uses `lsp.biome.settings.inline_config`. Do not
assume such a setting affects CLI runs.

## Resolve shared and monorepo configuration

Package-exported configurations in `extends` resolve from the CLI working
directory or LSP project root, and `.jsonc` is a valid extension target (since
`1.7.0`).

Every configuration is a root by default (since `2.0-guides`). A nested
configuration must either set `"root": false` or use `"extends": "//"`; the
latter inherits the monorepo root and implies `root: false`.

```json
{
  "extends": "//",
  "formatter": { "enabled": false }
}
```

Apply array-form `extends` entries from least to most relevant. Extended files
cannot themselves extend other files. Paths declared in shared configuration
are resolved relative to the configuration that extends it.

Before the configuration model changed, matching overrides became cumulative
in `1.8.0`, and `1.9.0` merged locally declared override arrays with arrays
inherited through `extends`. Current configurations use first-match override
selection (since `2.0-guides`): only the first matching entry is used. Put
specific entries before broad ones.

```json
{
  "overrides": [
    { "includes": ["src/generated/**"], "formatter": { "enabled": false } },
    { "includes": ["src/**"], "formatter": { "lineWidth": 100 } }
  ]
}
```

## Apply includes and scanner exclusions

`files.includes` is ordered (since `2.0-guides`). A later positive pattern can
re-include an ordinary earlier `!` exclusion. A `!!` force-ignore prevents the
scanner from indexing or traversing a path; `!` prevents processing but still
allows project-domain analysis to index an imported dependency.

```json
{
  "files": {
    "includes": ["**", "!**/*.test.js", "**/special.test.js", "!!**/dist"]
  }
}
```

`linter.includes`, `formatter.includes`, and `assist.includes` run after
`files.includes`. They can only narrow the initial set and cannot re-add a
file.

`files.experimentalScannerIgnores` is deprecated (since `2.3.0`). Run
`biome migrate --write` to convert those paths to `!!` entries in
`files.includes`.

`biome init` detects supported ignore files, enables Git VCS integration with
ignore-file use, and adds a force-ignore for `dist/` when that directory exists
(since `2.3.0`). When `vcs.root` is explicit, `.gitignore` is resolved relative
to that root (since `2.4.0`). Biome also honors `.git/info/exclude` and the
corresponding exclude file in linked worktrees (since `2.5-guide`).

## Migrate ESLint

`biome migrate eslint --write` ports legacy and flat ESLint configuration
(since `1.7-guide`). It handles legacy `extends`, shared/plugin configurations,
`.eslintignore`, globals, rules, and overrides. Node.js is required to resolve
plugins and `extends`; YAML configuration is unsupported. Rules merely inspired
by ESLint are skipped unless `--include-inspired` is supplied.

```shell
biome migrate eslint --write --include-inspired
```

Migration can overwrite an existing Biome configuration and may disable its
recommended rules. Review or commit the existing file first. Later migration
behavior preserves an existing `overrides` array (since `1.9.0`).

Package-level `eslintIgnore` is migrated (since `1.8.0`). Gitignore-style
patterns are converted; for example, root-relative `/src` becomes Biome's
`./src` form.

The e18e plugin is a recognized rule source for `useAtIndex`,
`useExponentiationOperator`, `noPrototypeBuiltins`, `useDateNow`, `useSpread`,
and `useObjectSpread` (since `2.4-guide`).

## Migrate Prettier

`biome migrate prettier --write` translates Prettier `overrides` and attempts
to convert `.prettierignore` patterns to Biome globs (since `1.7-guide`).
JavaScript configuration requires Node.js; JSON5, TOML, and YAML configurations
are unsupported. Migration preserves an existing Biome `overrides` array
(since `1.9.0`).

Biome can import settings from the single `.editorconfig` at the project root
when `formatter.useEditorconfig` is `true` (since `1.9-guide`). Explicit Biome
configuration takes precedence.

```json
{ "formatter": { "useEditorconfig": true } }
```

When enabled, `biome ci` loads that root file and the language server applies,
watches, and refreshes EditorConfig settings after changes (since `1.9.0`).

## Update renamed and deprecated settings

- `javascript.formatter.trailingComma` and `--trailing-comma` are deprecated;
  use `javascript.formatter.trailingCommas` and `--trailing-commas` (since
  `1.8.0`).
- `correctness/noInvalidNewBuiltin`, `style/useSingleCaseStatement`, and
  `suspicious/noConsoleLog` are deprecated; use
  `correctness/noInvalidBuiltinInstantiation`,
  `correctness/noSwitchDeclarations`, and `suspicious/noConsole` (since
  `1.9-guide`).
- The nursery rule `useAnchorHref` was removed because `useValidAnchor` covers
  the same use case (since `2.3.0`).
- `linter.rules.preset` replaces `linter.rules.recommended` (since
  `2.5-guide`). `"recommended"` retains the former selection; `"all"` enables
  all stable rules but still excludes nursery. Run `biome migrate --write`.

```json
{ "linter": { "rules": { "preset": "all" } } }
```

The `2.5-guide` stable promotions also renamed `noFloatingClasses` to
`noUnusedInstantiation`, `noMultiStr` to `noMultilineString`, `useFind` to
`useArrayFind`, and `useSpread` to `useSpreadOverApply`.

## Resolver configuration

Package-sensitive rules use the nearest relevant `package.json` in a monorepo
(since `2.0.0`). Resolution prefers the most specific overlapping package
`exports` pattern (since `2.4.0`).

Enable experimental pnpm catalog support explicitly (since `2.5-guide`):

```json
{
  "javascript": {
    "resolver": { "experimentalPnpmCatalogs": true }
  }
}
```

The resolver then reads both default and named pnpm catalogs.
