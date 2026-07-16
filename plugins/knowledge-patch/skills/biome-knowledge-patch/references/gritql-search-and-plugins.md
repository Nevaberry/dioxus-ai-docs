# GritQL Search and Plugins

Use this reference when writing structural searches, transformations, or custom
lint rules with GritQL.

## Contents

- [Run structural searches](#run-structural-searches)
- [Define reusable logic](#define-reusable-logic)
- [Register a lint plugin](#register-a-lint-plugin)
- [Scope plugins by path](#scope-plugins-by-path)
- [Attach safe or unsafe rewrites](#attach-safe-or-unsafe-rewrites)
- [Profile plugin cost](#profile-plugin-cost)

## Run structural searches

Run `biome search` with a structural query. Matches ignore trivia such as
whitespace and quote style. Because GritQL code fragments use backticks,
single-quote the complete query in shells that interpret backticks:

```shell
biome search '`console.$method($args)` where { $method <: or { `log`, `info` } }' ./
```

Search supports JSON and JavaScript with optional TypeScript or JSX flavors. It
can also use direct Biome syntax-node patterns selected with
`engine biome(1.0)`.

## Define reusable logic

Define custom patterns, predicates, and functions instead of repeating complex
match logic. Function and method patterns match async declarations by default.
Capture the optional `async` token and require it to be empty when the query
must match synchronous declarations only:

```grit
$async function foo() {} where $async <: .
```

## Register a lint plugin

Load `.grit` files from top-level `plugins`:

```json
{ "plugins": ["./lint/no-object-assign.grit"] }
```

Report a match with `register_diagnostic(span, message, severity)`. Severity is
optional, defaults to `error`, and accepts `hint`, `info`, `warn`, or `error`.

```grit
`$fn($args)` where {
  $fn <: `Object.assign`,
  register_diagnostic(span = $fn, message = "Prefer object spread")
}
```

Plugins default to JavaScript. Select another supported language explicitly.
CSS plugins use `language css;`. JSON plugins use `language json` and may match
native nodes such as `JsonMember` or TreeSitter-compatible names such as
`pair`, `object`, and `array`:

```grit
language json
pair(key = $k, value = $v)
```

## Scope plugins by path

Use object-form plugin entries with `path` and ordered `includes`. Combine
positive and negative globs to restrict where a plugin runs:

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

## Attach safe or unsafe rewrites

Attach a rewrite with `=>`, then classify it using
`register_diagnostic(fix_kind = "safe" | "unsafe")`:

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

Fixes default to unsafe. Run safe fixes with `lint --write` or `check --write`.
Add `--unsafe` to apply an unsafe plugin rewrite.

## Profile plugin cost

Run `biome lint --profile-rules` or `biome check --profile-rules` to include
plugin timing with rules and assists. Measurements include total, average,
minimum, maximum, and invocation count but exclude CST-query time. Each plugin
appears as `plugin/<pluginName>`, matching its suppression name.

Coverage IDs: `1.9-guide`, `1.9.0`, `2.0-guides`, `2.4-guide`, `2.5-guide`,
`2.5.0`.
