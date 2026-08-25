# GritQL Search and Plugins

## Structural search

`biome search` runs experimental GritQL structural queries. Matches ignore
trivia such as whitespace and quote style. Because code fragments use
backticks, single-quote the complete query in shells that interpret backticks
as command substitution (1.9-guide).

```shell
biome search '`console.$method($args)` where { $method <: or { `log`, `info` } }' ./
```

Search supports JSON and JavaScript with optional TypeScript or JSX flavors. It
also accepts direct Biome syntax-node patterns selected with
`engine biome(1.0)` (2.0-guides).

## Reusable definitions and async matching

GritQL supports custom pattern, predicate, and function definitions. Function
and method patterns match async declarations by default. Capture the optional
`async` token and require it to be empty to match only synchronous declarations
(1.9.0).

```grit
$async function foo() {} where $async <: .
```

## Linter plugins

### Loading and registering diagnostics (2.0-guides)

Top-level `plugins` entries load `.grit` files and run their patterns on files
handled by the linter.

```json
{ "plugins": ["./lint/no-object-assign.grit"] }
```

Register a match with `register_diagnostic(span, message, severity)`. Severity
is optional, defaults to `error`, and accepts `hint`, `info`, `warn`, or
`error`.

```grit
`$fn($args)` where {
  $fn <: `Object.assign`,
  register_diagnostic(span = $fn, message = "Prefer object spread")
}
```

Plugins default to JavaScript and may target CSS with `language css;`. At this
stage plugin targets are limited to JavaScript and CSS.

### JSON targets (2.4-guide)

GritQL can target JSON for searches, transformations, and custom lint rules.
Patterns can use native nodes such as `JsonMember` or TreeSitter-compatible
names such as `pair`, `object`, and `array`.

```grit
language json
pair(key = $k, value = $v)
```

### Path-scoped execution (2.5-guide)

A plugin entry can be an object with `path` and `includes`. Positive and
negative globs restrict the files where that plugin runs.

```json
{
  "plugins": [
    {
      "path": "./ts-only-plugin.grit",
      "includes": ["src/**/*.ts", "!src/**/*.test.ts"]
    }
  ]
}
```

### Code fixes (2.5-guide)

Attach a rewrite with `=>` and classify it through
`register_diagnostic(fix_kind = "safe" | "unsafe")`. Fixes default to unsafe
and require `lint` or `check --write --unsafe`; safe fixes run with `--write`
alone.

```grit
`console.log($msg)` as $call where {
  register_diagnostic(
    span = $call,
    message = "Use console.info instead.",
    fix_kind = "safe"
  ),
  $call => `console.info($msg)`
}
```

### Filtering and profiling

`--profile-rules` covers GritQL plugins along with lint rules and assist actions
(2.4-guide). Each plugin is reported separately as `plugin/<pluginName>`, which
matches plugin-suppression names (2.5.0).

Plugin diagnostics obey `--only` and `--skip` filters (2.5.1).
