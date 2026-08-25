# GritQL Search and Plugins

## Run structural search

`biome search` runs structural GritQL queries whose matches ignore trivia such
as whitespace and quote style (introduced experimentally in `1.9-guide`).
GritQL fragments use backticks, so single-quote the whole query in shells that
treat backticks as command substitution.

```shell
biome search '`console.$method($args)` where { $method <: or { `log`, `info` } }' ./
```

Reusable pattern, predicate, and function definitions are supported (since
`1.9.0`). Function and method patterns match async declarations by default.
Capture the optional `async` token and require it to be empty when a pattern
must match synchronous declarations only:

```grit
$async function foo() {} where $async <: .
```

Search supports JSON and JavaScript with optional TypeScript/JSX flavors, plus
direct Biome syntax-node patterns selected with `engine biome(1.0)` (since
`2.0-guides`).

## Register lint diagnostics

Top-level `plugins` entries load `.grit` files and run their patterns across
files handled by the linter (since `2.0-guides`). Register a match with
`register_diagnostic(span, message, severity)`. Severity is optional, defaults
to `error`, and accepts `hint`, `info`, `warn`, or `error`.

```json
{ "plugins": ["./lint/no-object-assign.grit"] }
```

```grit
`$fn($args)` where {
  $fn <: `Object.assign`,
  register_diagnostic(span = $fn, message = "Prefer object spread")
}
```

Plugins default to JavaScript. Select CSS with `language css;`. At their
introduction, plugin targets were JavaScript and CSS, while search additionally
supported JSON and syntax-node patterns.

## Target JSON

GritQL can target JSON for searches, transformations, and custom lint rules
(since `2.4-guide`). Use native nodes such as `JsonMember` or Tree-sitter-style
names such as `pair`, `object`, and `array`.

```grit
language json
pair(key = $k, value = $v)
```

Select `language json` explicitly rather than allowing the JavaScript default.

## Scope plugins by path

Plugin entries can be objects with `path` and `includes` (since
`2.5-guide`). Positive and negative globs restrict where that plugin runs.

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

`--only` and `--skip` also filter plugin diagnostics (since `2.5.1`).

## Attach and classify rewrites

A plugin pattern can attach a `=>` rewrite and pass
`fix_kind = "safe" | "unsafe"` to `register_diagnostic` (since
`2.5-guide`). Unclassified fixes are unsafe. Safe fixes run with `--write`;
unsafe fixes require `lint` or `check --write --unsafe`.

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

## Profile and suppress plugins

`--profile-rules` includes GritQL plugin time along with lint-rule and assist
timing (since `2.4-guide`); CST-query time is not included. Each plugin is
reported separately as `plugin/<pluginName>` (since `2.5.0`). That name also
matches the plugin's suppression name.
