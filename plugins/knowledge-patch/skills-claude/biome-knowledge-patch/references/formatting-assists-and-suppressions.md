# Formatting, Assists, and Suppressions

## Organize imports and exports safely

Import organization preserves execution-sensitive bare imports. Each bare
side-effect import is its own group and is not reordered (since `1.7.0`), while
ordinary imports can still be sorted.

The organizer was expanded in `2.0.0`: it can move imports across ordinary
blank lines, merge imports from the same module, apply custom ordering,
organize exports, and sort import attributes. Detached comments still create
intentional boundaries between import chunks.

Since `2.4.0`, `organizeImports` also sorts and merges bare exports and keeps
import and export chunks separate. Since `2.5-guide`, it can sort bare imports,
match them with `kind: "bare"`, exclude them with `kind: "!bare"`, and group
stylesheet imports with `:STYLE:`.

Import organization is an assist rather than a lint diagnostic (since
`2.0.0`). Editor `source.fixAll.biome` does not organize imports when
`source.organizeImports.biome` is disabled (since `2.4.0`).

## Configure assists independently

Assists have their own scope and source-action policy (since `2.0-guides`):

```json
{
  "assist": {
    "includes": ["src/**"],
    "actions": { "source": { "recommended": true } }
  }
}
```

An assist acts like a fix but produces no diagnostic. `useSortedKeys` sorts
object-literal keys and `useSortedAttributes` sorts JSX attributes (since
`2.0.0`).

Additional sorting assists include:

- `noDuplicateClasses`, which removes duplicate classes from JSX `class` and
  `className`, `clsx`, `cn`, and `cva` calls, and HTML `class` attributes
  (since `2.4-guide`).
- `useSortedInterfaceMembers`, which places alphabetized TypeScript interface
  properties before call signatures (since `2.4-guide`).
- `useSortedKeys.groupByNesting`, which groups simple values before multiline
  arrays and objects, then sorts within each group (since `2.4-guide`).
- Actions that sort `package.json` fields, HTML attributes, TypeScript and
  GraphQL enum members, GraphQL selection sets, and GraphQL type fields (since
  `2.5-guide`).

`biome check` and `biome ci` can select assist actions and action groups with
repeatable `--only` and `--skip` (since `2.4-guide`).

## Set fix applicability

Object-form rule configuration accepts `fix: "none" | "safe" | "unsafe"`
(since `1.8.0`). `none` disables the action; `safe` and `unsafe` override its
declared applicability.

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

The object form must include `level` (since `2.5.1`); omitting it is a
configuration error. Applying safe or unsafe fixes through `biome check` also
formats the resulting code (since `2.4-guide`).

## Suppress the narrowest diagnostic

Analyzer comments can suppress a single rule instance (since `1.8.0`).
`useExhaustiveDependencies` uses this for one dependency, avoiding suppression
of the whole diagnostic; it also detects duplicate dependencies.

CSS and GraphQL diagnostics expose suppression actions (since `1.9.0`). For
larger JavaScript/TypeScript scopes, `// biome-ignore-all` suppresses a rule or
the formatter for a whole file (since `2.0.0`). A
`// biome-ignore-start` comment starts a range; `// biome-ignore-end` closes it,
or omission of the end marker extends the range to end of file.

Plugin suppression names match the plugin names shown in per-plugin profiling
(since `2.5.0`).

## Control general formatting

`formatter.expand`, plus JavaScript- and JSON-specific overrides, accepts
`"auto"`, `"always"`, or `"never"` (since `2.0-guides`). In `auto`, an
existing line break before an object's first property preserves multiline
layout, while arrays collapse when they fit. `package.json` behaves as
`"always"` unless explicitly overridden.

```json
{ "formatter": { "expand": "never" } }
```

`formatter.lineEnding` and `--line-ending` accept `auto` (since `2.3.0`),
choosing CRLF on Windows and LF on macOS and Linux.

```json
{ "formatter": { "lineEnding": "auto" } }
```

`formatter.trailingNewline` defaults to `true` and can be disabled globally or
per language (since `2.4-guide`). CLI equivalents include
`--formatter-trailing-newline` and
`--javascript-formatter-trailing-newline`.

`formatter.delimiterSpacing` controls spaces inside delimiters for JavaScript,
CSS, JSON, and GraphQL, with language-specific behavior (since `2.5-guide`).

```json
{ "formatter": { "delimiterSpacing": true } }
```

The JavaScript formatter follows Prettier 3.3 by parenthesizing nullish
coalescing expressions used as ternary branches (since `1.9-guide`):

```js
foo ? (bar ?? foo) : baz;
```

The singular `javascript.formatter.trailingComma` and `--trailing-comma` forms
are deprecated; use `trailingCommas` and `--trailing-commas` (since `1.8.0`).

## Format HTML-like files

The experimental HTML formatter introduced in `2.0.0` is disabled by default
and initially formats `.html` only, not Vue/Svelte markup or embedded
JavaScript and CSS. It supports `attributePosition`, `bracketSameLine`, and
`whitespaceSensitivity`.

```json
{
  "html": {
    "formatter": { "enabled": true }
  }
}
```

`html.formatter.indentScriptAndStyle` indents `<script>` and `<style>` content
and defaults to `false` for Prettier compatibility (since `2.3.0`). Embedded
JavaScript and CSS still use their own language formatter options, so settings
such as `quoteStyle` can differ inside one HTML-like file.

## Format CSS consistently

The CSS formatter supports `@function` and automatically enables CSS Modules
syntax for `*.module.css` (since `2.4-guide`). Property ordering follows
`stylelint-config-recess-order` v7.4.0, including newer containment,
font-synthesis, ruby, color-adjustment, view-transition, shape, and motion-path
properties.
