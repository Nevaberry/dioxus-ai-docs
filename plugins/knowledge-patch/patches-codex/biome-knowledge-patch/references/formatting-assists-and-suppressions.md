# Formatting, Assists, and Suppressions

## Formatter settings

### Trailing commas (1.8.0)

`javascript.formatter.trailingComma` and `--trailing-comma` are deprecated.
Use `javascript.formatter.trailingCommas` and `--trailing-commas`.

### Nullish coalescing in ternaries (1.9-guide)

The JavaScript formatter follows Prettier 3.3 by parenthesizing a nullish
coalescing expression used as a ternary branch.

```js
foo ? (bar ?? foo) : baz;
```

### Array and object expansion (2.0-guides)

`formatter.expand` and JavaScript- and JSON-specific overrides accept `"auto"`,
`"always"`, or `"never"`. In `auto`, an existing line break before the first
property preserves a multiline object, while fitting arrays collapse.
`package.json` behaves as `always` unless explicitly configured.

```json
{ "formatter": { "expand": "never" } }
```

### HTML script and style indentation (2.3.0)

`html.formatter.indentScriptAndStyle` indents `<script>` and `<style>` contents
and defaults to `false` for Prettier compatibility. Embedded JavaScript and CSS
still use their own formatter settings, so settings such as `quoteStyle` may
differ within one HTML-ish file.

```json
{
  "html": {
    "formatter": { "indentScriptAndStyle": true }
  }
}
```

### Platform-native line endings (2.3.0)

`formatter.lineEnding` and `--line-ending` accept `auto`, which selects CRLF on
Windows and LF on macOS and Linux.

```json
{ "formatter": { "lineEnding": "auto" } }
```

### Trailing newline (2.4-guide)

`formatter.trailingNewline` defaults to `true`. Set it to `false` globally or
per language to remove the final newline. CLI equivalents include
`--formatter-trailing-newline` and
`--javascript-formatter-trailing-newline`.

### Delimiter spacing (2.5-guide)

`formatter.delimiterSpacing` adds spaces inside language delimiters and is
implemented with language-specific behavior for JavaScript, CSS, JSON, and
GraphQL.

```json
{ "formatter": { "delimiterSpacing": true } }
```

## Import organization

### Side-effect boundaries (1.7.0)

Every bare side-effect import is its own group and is not reordered. This
preserves its execution order while other imports are sorted.

### Organizer overhaul (2.0.0)

The organizer can move imports across ordinary blank lines, merge imports from
the same module, apply custom ordering, organize exports, and sort import
attributes. Detached comments can preserve intentional boundaries between
chunks.

Import organization is an assist: an action such as a lint fix, but without a
diagnostic.

### Import and export coverage (2.4.0)

`organizeImports` sorts and merges bare exports and separates import and export
chunks.

### Bare and stylesheet imports (2.5-guide)

`organizeImports` can sort bare imports, select them with `kind: "bare"`,
exclude them with `kind: "!bare"`, and group stylesheet imports with the
`:STYLE:` matcher.

## Other assist actions

### Object keys and JSX attributes (2.0.0)

`useSortedKeys` sorts object-literal keys. `useSortedAttributes` sorts JSX
attributes.

### CSS classes and interfaces (2.4-guide)

`noDuplicateClasses` removes duplicate classes from JSX `class`/`className`,
`clsx`, `cn`, and `cva` usage and from HTML `class` attributes.

`useSortedInterfaceMembers` sorts TypeScript interface members, placing
alphabetized properties before call signatures.

`useSortedKeys.groupByNesting` groups simple values before multiline arrays and
objects and sorts within each group.

### Structural sorting (2.5-guide)

Assist actions can sort `package.json` fields, HTML attributes, TypeScript and
GraphQL enum members, GraphQL selection sets, and GraphQL type fields.

## Suppressions

### Dependency-specific suppressions (1.8.0)

Analyzer suppression comments can suppress an individual rule instance.
`useExhaustiveDependencies` uses this to suppress a particular dependency
instead of the whole diagnostic. The rule also reports duplicate dependencies.

### CSS and GraphQL actions (1.9.0)

Analyzer suppression actions are available for CSS and GraphQL diagnostics, so
findings in those languages can be suppressed without disabling an entire
rule.

### Whole-file and ranged forms (2.0.0)

`// biome-ignore-all` suppresses a lint rule or the formatter for the whole
file. `// biome-ignore-start` begins a range; `// biome-ignore-end` closes it.
If the end comment is omitted, the range continues to end of file.

## Fix applicability and formatting

Object-form rule configuration accepts `fix`. `none`, `safe`, and `unsafe`
disable actions or override action applicability (1.8.0).

```json
{ "linter": { "rules": { "correctness": { "noUnusedVariables": { "level": "error", "fix": "none" } } } } }
```

Applying safe or unsafe fixes through `biome check` also formats the resulting
code (2.4-guide).

## CSS formatting details

The CSS parser and formatter support the `@function` at-rule. CSS Modules
syntax is automatically enabled for `*.module.css`, so the old manual parser
switch can be removed for those files. Property ordering follows
`stylelint-config-recess-order` v7.4.0, including newer containment,
font-synthesis, ruby, color-adjustment, view-transition, shape, and motion-path
properties (2.4-guide).

## HTML formatting boundary

The experimental HTML formatter is disabled by default throughout 2.0 and
initially handles only `.html`, not markup in Vue or Svelte or embedded
JavaScript and CSS. It supports `attributePosition`, `bracketSameLine`, and
`whitespaceSensitivity` (2.0.0).

```json
{
  "html": {
    "formatter": { "enabled": true }
  }
}
```

## Editor fix-all

`source.fixAll.biome` does not organize imports when
`source.organizeImports.biome` is disabled. Import organization runs only when
explicitly requested (2.4.0).
