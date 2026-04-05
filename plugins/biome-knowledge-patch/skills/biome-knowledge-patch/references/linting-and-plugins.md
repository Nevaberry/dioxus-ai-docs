# Linting & Plugins (v2.0–v2.4)

## Linter Domains

Framework-specific rule groups that auto-activate based on `package.json` dependencies.

Available domains: `react`, `next`, `solid`, `vue`, `playwright`, `drizzle`, `qwik`, `project`, `types`, `test`.

```json
{
  "linter": {
    "domains": {
      "react": "recommended",
      "next": "all",
      "project": "recommended",
      "types": "recommended"
    }
  }
}
```

Values: `"recommended"` (stable rules), `"all"` (including nursery), `"none"`.
CLI filtering: `--only=project`, `--skip=test`.

## Type-Aware Linting (No TS Compiler)

Biome v2 has its own type inference engine — no `typescript` package needed.

Enable via:
- `project` domain — module graph analysis
- `types` domain — type inference

Opt-in; triggers full project scan.

Key rules:
- `noFloatingPromises` — unhandled promise results
- `noMisusedPromises` — promises used incorrectly (e.g., as conditions)
- `noImportCycles` — circular import detection
- `noUnresolvedImports` — missing imports
- `noDeprecatedImports` — usage of deprecated exports
- `useAwaitThenable` — await on non-thenable values

## Suppression Comments

### File-wide suppression

```js
// biome-ignore-all lint/suspicious/noConsole: logging file
// Suppresses the rule for the entire file
```

### Range-based suppression

```js
// biome-ignore-start lint/style/noVar: legacy code
var x = 1;
var y = 2;
// biome-ignore-end lint/style/noVar
```

## GritQL Linter Plugins

Register plugins in config:

```json
{ "plugins": ["./no-object-assign.grit"] }
```

Plugin file (`.grit` extension):

```grit
`$fn($args)` where {
    $fn <: `Object.assign`,
    register_diagnostic(
        span = $fn,
        message = "Prefer object spread instead of `Object.assign()`",
        severity = "error"
    )
}
```

For CSS targets, add `language css;` at the top of the plugin file. Only JS and CSS targets are supported.
