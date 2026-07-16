# Formatting, Assists, and Suppressions

Use this reference when changing formatter output, import organization, source
actions, fix applicability, or suppression scope.

## Contents

- [Preserve import side effects](#preserve-import-side-effects)
- [Configure assists separately](#configure-assists-separately)
- [Keep editor actions independent](#keep-editor-actions-independent)
- [Set fix applicability](#set-fix-applicability)
- [Suppress the narrowest finding](#suppress-the-narrowest-finding)
- [Control object and array expansion](#control-object-and-array-expansion)
- [Set commas, delimiters, and final newlines](#set-commas-delimiters-and-final-newlines)
- [Select platform line endings](#select-platform-line-endings)
- [Format nullish ternary branches](#format-nullish-ternary-branches)
- [Format HTML and embedded blocks](#format-html-and-embedded-blocks)
- [Format CSS consistently](#format-css-consistently)

## Preserve import side effects

Treat every bare side-effect import as its own group. Import organization does
not reorder these groups, preserving execution order while sorting other
imports.

The current organizer can:

- move imports across ordinary blank lines;
- merge imports from the same module;
- apply custom ordering;
- organize exports and sort import attributes;
- sort and merge bare exports;
- keep import and export chunks separate;
- sort bare imports, selected with `kind: "bare"` or excluded with
  `kind: "!bare"`;
- group stylesheet imports with the `:STYLE:` matcher.

Detached comments can remain intentional boundaries between import chunks.

## Configure assists separately

Treat import organization as an assist: a source action without a diagnostic.
Scope assists independently of linting and formatting:

```json
{
  "assist": {
    "includes": ["src/**"],
    "actions": { "source": { "recommended": true } }
  }
}
```

Use these structural sorting assists where appropriate:

- `useSortedKeys` sorts object-literal keys. Its `groupByNesting` option groups
  simple values before multiline arrays and objects, then sorts within groups.
- `useSortedAttributes` sorts JSX attributes.
- `useSortedInterfaceMembers` sorts TypeScript interface members, placing
  alphabetized properties before call signatures.
- `noDuplicateClasses` removes duplicate classes from JSX `class` and
  `className`, `clsx`, `cn`, and `cva` calls, and HTML `class` attributes.
- Additional actions sort `package.json` fields, HTML attributes, TypeScript
  and GraphQL enum members, GraphQL selection sets, and GraphQL type fields.

Select assist actions and groups with `biome check --only` or `--skip`. An
enforced assist violation can make `biome check` fail even when diagnostic-level
filtering hides warnings and informational diagnostics.

## Keep editor actions independent

`source.fixAll.biome` no longer organizes imports when
`source.organizeImports.biome` is disabled. Request organization explicitly if
the editor disables that source action.

## Set fix applicability

Configure a rule in object form and set `fix` to:

- `none` to disable actions;
- `safe` to classify the action as safe;
- `unsafe` to require unsafe-fix authorization.

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

Applying safe or unsafe fixes through `biome check` also formats the resulting
code. `useConsistentMethodSignatures` provides an unsafe conversion fix.

## Suppress the narrowest finding

Analyzer comments can suppress one dependency-specific instance of
`useExhaustiveDependencies` instead of hiding the whole diagnostic. The rule
also detects duplicate dependencies.

Use `// biome-ignore-all` to suppress a lint rule or the formatter for the
whole file. Start a range with `// biome-ignore-start` and close it with
`// biome-ignore-end`; without an end marker, suppression continues to end of
file.

CSS and GraphQL diagnostics expose suppression actions, so avoid disabling an
entire rule merely because a single finding is intentional.

## Control object and array expansion

Set `formatter.expand`, or the JavaScript- and JSON-specific equivalents, to
`"auto"`, `"always"`, or `"never"`:

```json
{ "formatter": { "expand": "never" } }
```

In `auto`, preserve a multiline object when its first property already starts
on a new line, while collapsing arrays that fit. Treat `package.json` as
`always` unless configuration explicitly overrides it.

## Set commas, delimiters, and final newlines

Use plural trailing-comma settings:

- `javascript.formatter.trailingCommas`
- `--trailing-commas`

The singular `trailingComma` and `--trailing-comma` forms are deprecated.

Set `formatter.delimiterSpacing: true` to add spaces inside supported language
delimiters. Behavior is language-specific and implemented for JavaScript, CSS,
JSON, and GraphQL.

```json
{ "formatter": { "delimiterSpacing": true } }
```

`formatter.trailingNewline` defaults to `true`. Set it to `false`, globally or
per language, to remove the final newline. CLI equivalents include
`--formatter-trailing-newline` and
`--javascript-formatter-trailing-newline`.

## Select platform line endings

Set `formatter.lineEnding` or `--line-ending` to `auto` for CRLF on Windows and
LF on macOS and Linux:

```json
{ "formatter": { "lineEnding": "auto" } }
```

## Format nullish ternary branches

Expect JavaScript formatting to parenthesize nullish coalescing expressions used
as ternary branches, making precedence explicit:

```js
foo ? (bar ?? foo) : baz;
```

## Format HTML and embedded blocks

The HTML formatter began as an explicit opt-in and initially formatted only
`.html`, not markup in Vue or Svelte or embedded JavaScript and CSS. Its core
options include `attributePosition`, `bracketSameLine`, and
`whitespaceSensitivity`:

```json
{
  "html": {
    "formatter": { "enabled": true }
  }
}
```

Set `html.formatter.indentScriptAndStyle: true` to indent `<script>` and
`<style>` contents. It defaults to `false` for Prettier compatibility. Embedded
JavaScript and CSS still use their own language formatter settings, so values
such as `quoteStyle` may differ within one HTML-like file.

## Format CSS consistently

CSS property ordering follows `stylelint-config-recess-order` v7.4.0, including
newer containment, font-synthesis, ruby, color-adjustment, view-transition,
shape, and motion-path properties.

Use the `useSortedClasses` rule with awareness of its boundaries: it orders
known and dynamic Tailwind variants and places arbitrary variants after known
ones, but does not support screen variants such as `sm:`, `max-md:`, or
`min-lg:`.

Coverage IDs: `1.7.0`, `1.8.0`, `1.9-guide`, `1.9.0`, `2.0-guides`, `2.0.0`,
`2.3.0`, `2.4-guide`, `2.4.0`, `2.5-guide`.
