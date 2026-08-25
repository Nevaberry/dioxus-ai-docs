# Languages and Frameworks

## JavaScript, JSX, and TypeScript

### Classic React JSX runtime (1.7-guide)

Setting `javascript.jsxRuntime` to `reactClassic` makes `noUnusedImports` and
`useImportType` ignore the otherwise apparently unused `React` import required
by the classic JSX transform.

```json
{
  "javascript": {
    "jsxRuntime": "reactClassic"
  }
}
```

### JSX in JavaScript files

The editor extension can parse JSX in documents associated with the JavaScript
language identifier (1.7-guide). In the 2.0-guides parser behavior, JSX in
`.js` is accepted by default and can be rejected with `jsxEverywhere: false`.

```json
{
  "javascript": {
    "parser": { "jsxEverywhere": false }
  }
}
```

### TypeScript syntax and compatibility

TypeScript construct signatures accept const type parameters (1.8.0).

```ts
interface I {
  new<const T>(x: T): T;
}
```

Import types accept a `with` object that selects `"resolution-mode"`. `.cts`
files may place the same attribute on type-only imports; that form remains
restricted to `.cts` (1.9.0).

```ts
type Fs = typeof import("fs", { with: { "resolution-mode": "import" } });
import type { TypeFromRequire } from "pkg" with { "resolution-mode": "require" };
```

Biome 2.3.0 adds React 19 support and supports `baseUrl` in `tsconfig.json`.

### JavaScript API spans (2.5-guide)

The JavaScript API exposes `spanInBytesToSpanInCodeUnits` to convert byte-based
diagnostic spans to the UTF-16 code-unit offsets used by JavaScript strings.

## JSON and JSONC

### Well-known dialects (1.7-guide)

Biome recognizes additional well-known JSON files and distinguishes files that
permit comments from those that permit both comments and trailing commas,
applying parser settings automatically.

`turbo.json`, `jest.config.json`, and `.json` files under `.vscode` or `.zed`
automatically allow comments. Files in the two editor directories still reject
trailing commas (1.9.0).

JSON files in project `.cursor` directories and Cursor platform user-config
directories automatically permit comments and trailing commas (2.4-guide).

### JSON linter analysis

`noDuplicateObjectKeys` analyzes JSON and JSONC (1.9.0). JSON nursery rules
`noTopLevelLiterals` and `noEmptyObjectKeys` respectively require an object or
array root and reject empty-string object keys (2.4.0).

## CSS

### Opt-in stage (1.8.0)

CSS formatting and linting were opt-in through CLI flags or
`css.formatter.enabled` and `css.linter.enabled`. Equivalent language linter
gates became available at `javascript.linter.enabled` and
`json.linter.enabled`.

```shell
biome check --css-formatter-enabled=true --css-linter-enabled=true .
```

The parser gained unknown at-rules, Unicode ranges, named grid lines, and
nested style rules and at-rules.

### Stable default (1.9-guide)

CSS formatting and linting became enabled by default. The parser still accepts
standard CSS rather than dialects such as SCSS. Disable either tool separately
for projects not ready to process CSS.

```json
{
  "css": {
    "formatter": { "enabled": false },
    "linter": { "enabled": false }
  }
}
```

Stable CSS rules include `a11y/useGenericFontNames`; correctness checks for
gradients, grid areas, `@import` placement, functions, media features,
properties, units, and An+B selectors; and suspicious checks for duplicate
imports, font names, keyframe selectors, empty blocks, `!important` in
keyframes, and shorthand overrides.

### CSS Modules, Tailwind, and current syntax

In the 2.0-guides parser, CSS Modules and Tailwind `@theme`, `@utility`, and
`@apply` require parser flags.

```json
{
  "css": { "parser": { "cssModules": true, "tailwindDirectives": true } }
}
```

By 2.4-guide, CSS Modules syntax is automatic for `*.module.css`; the manual
switch can be removed for those files. The parser and formatter support
`@function`, and property ordering follows `stylelint-config-recess-order`
v7.4.0 with newer containment, font-synthesis, ruby, color-adjustment,
view-transition, shape, and motion-path properties.

In 2.4.0, recognized CSS syntax also includes `dynamic-range-limit`, `overlay`,
`reading-flow`, `reading-order`, `scroll-marker-group`, and
`scroll-target-group`; newer picker, scroll-marker, column, checkmark, and
view-transition pseudo-selectors; and `@container scroll-state()` plus
general-enclosed container and supports queries.

## GraphQL

Biome formats and lints GraphQL files by default. Disable either operation with
`graphql.formatter.enabled` or `graphql.linter.enabled`. Initial lint coverage
is limited to nursery and includes `noDuplicateFields` (1.9-guide).

```json
{
  "graphql": {
    "formatter": { "enabled": false },
    "linter": { "enabled": false }
  }
}
```

CSS and GraphQL analyzer diagnostics support suppression actions as of 1.9.0.

## HTML and embedded languages

### Parser opt-ins (2.0-guides)

Embedded snippets and full HTML-ish parsing are separate experimental opt-ins.

```json
{
  "javascript": {
    "experimentalEmbeddedSnippetsEnabled": true
  },
  "html": {
    "experimentalFullSupportEnabled": true,
    "parser": { "interpolation": true }
  }
}
```

Without full support, Vue, Svelte, and Astro contribute only their
JavaScript/TypeScript sections. `html.parser.interpolation` independently
enables `{{ expression }}` in plain HTML.

### HTML formatter boundary (2.0.0)

The experimental HTML formatter is disabled by default throughout 2.0 and
initially handles only `.html`, not markup in Vue or Svelte or embedded
JavaScript and CSS. It supports `attributePosition`, `bracketSameLine`, and
`whitespaceSensitivity`.

```json
{
  "html": {
    "formatter": { "enabled": true }
  }
}
```

### Embedded indentation (2.3.0)

`html.formatter.indentScriptAndStyle` controls indentation of `<script>` and
`<style>` contents and defaults to `false`. Embedded JavaScript and CSS use
their own language formatter settings.

### CSS, GraphQL, and Relay snippets

With `javascript.experimentalEmbeddedSnippetsEnabled`, Biome formats and lints
CSS and GraphQL template literals used by styled-components, Emotion, and
`graphql-tag` (2.4-guide). Relay's `graphql` tag is also recognized (2.4.0).

### Accessibility (2.4-guide)

HTML, Vue, Svelte, and Astro gain `noAutofocus`, `noPositiveTabindex`,
`useAltText`, `useAnchorContent`, `useMediaCaption`, `useHtmlLang`,
`useValidLang`, `useValidAriaRole`, `useAriaPropsForRole`, `useButtonType`,
`noAccessKey`, `noDistractingElements`, `noSvgWithoutTitle`, `noRedundantAlt`,
and `useIframeTitle`.

### Vue syntax in HTML (2.5-guide)

`html.parser.vue` enables Vue syntax in ordinary `.html` files for projects
whose Vue templates live outside `.vue` files.

```json
{ "html": { "parser": { "vue": true } } }
```

## Vue

The analyzer accepts Vue SFC `<script setup>` blocks with generic type
parameters (1.7.0).

```vue
<script generic="T extends Record<string, any>" lang="ts" setup>
// ...
</script>
```

Vue SFCs accept `lang="tsx"` (1.8.0), and later parse `lang="jsx"` scripts as
JSX (1.9.0). `--stdin-file-path` selects Vue behavior and preserves lint output
for Vue input from standard input (1.7.0).

With full HTML support, Vue and Svelte parsing and the `noUnusedVariables`,
`useConst`, `useImportType`, and `noUnusedImports` rules produce fewer false
positives. Embedded styles recognize Vue `:slotted`, `:deep`, and `v-bind()` as
well as `:global` and `:local` in Astro, Svelte, and Vue (2.4-guide).

`useVueValidVOn` accepts verb modifiers without handlers, such as
`<div @click.stop></div>` and `<div @click.prevent></div>`, and the argument-less
object form `<div v-on="$listeners"></div>` (2.5.0).

## Svelte and Astro

`--stdin-file-path` selects the correct parser and linter for Svelte and Astro
(1.7.0). `useFilenamingConvention` permits the leading `+` used by SvelteKit
and Vike routes (1.7.0).

Svelte parsing accepts JavaScript line and block comments inside opening tags
(2.4.0).

```svelte
<button
  // call the handler
  onclick={submit}
>Save</button>
```

`noUnusedVariables` treats a `$store` template reference as use of the
underlying `store` binding and permits `$bindable()` props intentionally only
written in the script block (2.5.0).

Astro shorthand attributes such as `<button {disabled}>Save</button>` parse
correctly in embedded markup (2.5.0).

## React, Preact, and test globals

`useExhaustiveDependencies` understands Preact hooks as well as React hooks
(1.7-guide).

`Temporal` is a recognized global. The test domain supplies Mocha's `context`,
`run`, `setup`, `specify`, `suite`, `suiteSetup`, `suiteTeardown`, `teardown`,
`xcontext`, `xdescribe`, `xit`, and `xspecify` globals (2.4.0).

## SVG

Biome formats and lints `.svg` files (2.5-guide). In 2.5.1 the SVG parser also
accepts processing instructions such as an XML declaration.

```svg
<?xml version="1.0" encoding="UTF-8" ?>
<svg></svg>
```
