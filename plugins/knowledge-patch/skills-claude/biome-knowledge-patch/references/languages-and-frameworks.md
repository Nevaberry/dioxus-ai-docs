# Languages and Frameworks

## CSS

CSS formatting and linting were opt-in in `1.8.0`, through CLI flags or
`css.formatter.enabled` and `css.linter.enabled`. Equivalent per-language
linter gates were added for JavaScript and JSON and their supersets. From
`1.9-guide`, CSS formatting and linting run by default and can be disabled
independently:

```json
{
  "css": {
    "formatter": { "enabled": false },
    "linter": { "enabled": false }
  }
}
```

The `1.8.0` parser added unknown at-rules, Unicode ranges, named grid lines,
and nested style rules and at-rules. Stable CSS in `1.9-guide` still meant
standard CSS rather than SCSS. Its stable rules covered generic font names;
gradient, grid-area, `@import`, function, media-feature, property, unit, and
An+B correctness; and duplicate imports/font names/keyframe selectors, empty
blocks, keyframe `!important`, and shorthand overrides.

CSS Modules and Tailwind `@theme`, `@utility`, and `@apply` originally required
`css.parser.cssModules` and `css.parser.tailwindDirectives` (documented in
`2.0-guides`). Since `2.4-guide`, `*.module.css` automatically enables CSS
Modules syntax; Tailwind directives still require their parser control when
automatic behavior is insufficient.

The CSS parser/formatter supports `@function` (since `2.4-guide`). CSS syntax
recognized in `2.4.0` also includes `dynamic-range-limit`, `overlay`,
`reading-flow`, `reading-order`, `scroll-marker-group`,
`scroll-target-group`, newer picker/scroll-marker/column/checkmark/
view-transition pseudo-selectors, `@container scroll-state()`, and
general-enclosed container and supports queries.

CSS rule options added in `2.4-guide` let `noUnknownProperty`,
`noUnknownFunction`, `noUnknownPseudoClass`, and `noUnknownPseudoElement`
ignore named exceptions. The CSS nursery in `2.4.0` added
`noDuplicateSelectors` within an at-rule context and `useBaseline` for
properties, values, at-rules, media conditions, functions, and pseudo-selectors
outside the configured Baseline tier.

## GraphQL

GraphQL files are formatted and linted by default (since `1.9-guide`). Either
tool can be disabled:

```json
{
  "graphql": {
    "formatter": { "enabled": false },
    "linter": { "enabled": false }
  }
}
```

Initial lint coverage was nursery-only and included `noDuplicateFields`. CSS
and GraphQL diagnostics gained suppression actions in `1.9.0`.

With `javascript.experimentalEmbeddedSnippetsEnabled`, CSS and GraphQL inside
JavaScript template literals are formatted and linted (since `2.4-guide`).
Recognized sources include styled-components, Emotion, `graphql-tag`, and,
since `2.4.0`, Relay's `graphql` tag.

GraphQL sorting assists now cover enum members, selection sets, and type fields
(since `2.5-guide`). Stable GraphQL-related rules promoted in that batch are
listed in the linting reference.

## HTML and HTML-like files

Full HTML-like parsing is an explicit opt-in via
`html.experimentalFullSupportEnabled` (documented in `2.0-guides`). Without it,
Vue, Svelte, and Astro contribute only their JavaScript/TypeScript sections.
`html.parser.interpolation` separately enables `{{ expression }}` in plain
HTML.

```json
{
  "html": {
    "experimentalFullSupportEnabled": true,
    "parser": { "interpolation": true }
  }
}
```

With full support enabled, Vue and Svelte parsing and the
`noUnusedVariables`, `useConst`, `useImportType`, and `noUnusedImports` rules
produce fewer false positives (since `2.4-guide`). Reconsider old overrides
that disabled these rules for template files. Embedded styles recognize Vue
`:slotted`, `:deep`, and `v-bind()`, plus `:global` and `:local` in Astro,
Svelte, and Vue.

HTML, Vue, Svelte, and Astro accessibility coverage added in `2.4-guide`
includes `noAutofocus`, `noPositiveTabindex`, `useAltText`,
`useAnchorContent`, `useMediaCaption`, `useHtmlLang`, `useValidLang`,
`useValidAriaRole`, `useAriaPropsForRole`, `useButtonType`, `noAccessKey`,
`noDistractingElements`, `noSvgWithoutTitle`, `noRedundantAlt`, and
`useIframeTitle`.

`noInlineStyles` checks HTML `style`, JSX style props, and
`React.createElement` (since `2.4.0`). `html.parser.vue` enables Vue syntax in
ordinary `.html` files used as external Vue templates (since `2.5-guide`).

## SVG

Biome formats and lints `.svg` files (since `2.5-guide`). The parser also
accepts processing instructions such as XML declarations (since `2.5.1`):

```svg
<?xml version="1.0" encoding="UTF-8" ?>
<svg></svg>
```

## JSON dialects

Biome recognizes well-known JSON files and automatically distinguishes those
allowing comments from those allowing comments plus trailing commas (since
`1.7-guide`). `turbo.json`, `jest.config.json`, and `.json` under `.vscode` or
`.zed` allow comments (since `1.9.0`); the editor-directory files still reject
trailing commas.

JSON files in a project's `.cursor` directory and Cursor's platform user
configuration directories allow both comments and trailing commas (since
`2.4-guide`). `noDuplicateObjectKeys` analyzes JSON and JSONC (since `1.9.0`).
The `2.4.0` JSON nursery added `noTopLevelLiterals`, which requires an object or
array root, and `noEmptyObjectKeys`, which rejects empty-string keys.

Use `--json-parse-allow-comments` and
`--json-parse-allow-trailing-commas` for explicit CLI control (since `2.3.0`).

## JavaScript, JSX, and TypeScript syntax

JSX in `.js` is accepted by default (documented in `2.0-guides`); set
`javascript.parser.jsxEverywhere` to `false` to reject it. The editor extension
can also parse JSX in documents associated with the JavaScript language ID
(since `1.7-guide`).

```json
{
  "javascript": {
    "parser": { "jsxEverywhere": false },
    "experimentalEmbeddedSnippetsEnabled": true
  }
}
```

TypeScript construct signatures accept const type parameters (since `1.8.0`):

```ts
interface I {
  new<const T>(x: T): T;
}
```

Import types can carry a `with` object containing `"resolution-mode"` (since
`1.9.0`). A `.cts` file can use the same attribute on a type-only import; that
form is restricted to `.cts`.

```ts
type Fs = typeof import("fs", { with: { "resolution-mode": "import" } });
import type { T } from "pkg" with { "resolution-mode": "require" };
```

Biome recognizes TypeScript 5.5 and 5.6 globals (since `1.9.0`) and supports
`baseUrl` from `tsconfig.json` (since `2.3.0`). `Temporal` is a recognized
global (since `2.4.0`).

## React and Preact

Set `javascript.jsxRuntime` to `reactClassic` when the classic JSX transform
requires an apparently unused `React` import (since `1.7-guide`).
`noUnusedImports` and `useImportType` then preserve it.

```json
{
  "javascript": { "jsxRuntime": "reactClassic" }
}
```

`useExhaustiveDependencies` understands Preact hooks (since `1.7-guide`). It
also recognizes values that change every render, finds missing dependencies
declared as function declarations, and ignores recursive calls as missing
dependencies (since `1.7.0`).

Biome supports React 19 (since `2.3.0`). React-specific domain membership and
rule activation are covered in the linting reference.

## Vue

Vue SFC `<script setup>` accepts generic type parameters (since `1.7.0`):

```vue
<script generic="T extends Record<string, any>" lang="ts" setup>
// ...
</script>
```

Vue SFC scripts accept `lang="tsx"` (since `1.8.0`) and `lang="jsx"` (since
`1.9.0`). `useFilenamingConvention` permits the leading `+` used by Vike and
SvelteKit routes (since `1.7.0`).

`useVueScopedStyles` requires SFC styles to use `scoped` or `module`, while
`noVueRefAsOperand` catches refs used without `.value` (since `2.4.0`).
`useVueValidVOn` accepts expressionless verb modifiers such as `@click.stop`
and `@click.prevent`, plus the argument-less object form `v-on="$listeners"`
(since `2.5.0`).

## Svelte and Astro

`noUndeclaredVariables` recognizes Svelte 5 runes in `.svelte`, `.svelte.js`,
and `.svelte.ts` files (since `1.9.0`). Svelte opening tags accept JavaScript
line and block comments (since `2.4.0`):

```svelte
<button
  // call the handler
  onclick={submit}
>Save</button>
```

`noUnusedVariables` treats a `$store` template reference as use of the
underlying `store` and permits `$bindable()` props intentionally written only
in script (since `2.5.0`). Astro shorthand attributes such as
`<button {disabled}>` parse correctly in embedded markup (since `2.5.0`).
