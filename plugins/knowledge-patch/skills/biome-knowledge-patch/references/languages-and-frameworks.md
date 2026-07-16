# Languages and Frameworks

Use this reference when enabling a language, parsing framework files, or
deciding whether an override is still needed.

## Contents

- [CSS](#css)
- [GraphQL](#graphql)
- [HTML and HTML-like files](#html-and-html-like-files)
- [Embedded template-literal snippets](#embedded-template-literal-snippets)
- [SVG](#svg)
- [JSON dialects](#json-dialects)
- [JavaScript and JSX](#javascript-and-jsx)
- [TypeScript syntax and resolution](#typescript-syntax-and-resolution)
- [React and Preact](#react-and-preact)
- [Vue](#vue)
- [Svelte](#svelte)
- [Astro and route filenames](#astro-and-route-filenames)
- [Test globals and assertions](#test-globals-and-assertions)

## CSS

CSS formatting and linting are enabled by default. Disable either independently
when a project is not ready to include CSS:

```json
{
  "css": {
    "formatter": { "enabled": false },
    "linter": { "enabled": false }
  }
}
```

Biome parses standard CSS, not dialects such as SCSS. Parser coverage includes
unknown at-rules, Unicode ranges, named grid lines, nested style rules, and
nested at-rules.

Enable specialized syntax when it is not inferred:

```json
{
  "css": {
    "parser": {
      "cssModules": true,
      "tailwindDirectives": true
    }
  }
}
```

The Tailwind switch covers `@theme`, `@utility`, and `@apply`. CSS Modules
syntax is enabled automatically for `*.module.css`, so remove obsolete manual
switches for those files.

The parser and formatter understand the `@function` at-rule. CSS compatibility
also recognizes:

- `dynamic-range-limit`, `overlay`, `reading-flow`, `reading-order`,
  `scroll-marker-group`, and `scroll-target-group`;
- newer picker, scroll-marker, column, checkmark, and view-transition
  pseudo-selectors;
- `@container scroll-state()`;
- general-enclosed container and supports queries.

Embedded framework styles recognize Vue `:slotted`, `:deep`, and `v-bind()` as
well as `:global` and `:local` in Astro, Svelte, and Vue.

## GraphQL

GraphQL files are formatted and linted by default. Disable the tools separately
under `graphql.formatter.enabled` and `graphql.linter.enabled`:

```json
{
  "graphql": {
    "formatter": { "enabled": false },
    "linter": { "enabled": false }
  }
}
```

Initial GraphQL lint coverage lived in nursery and included
`noDuplicateFields`. CSS and GraphQL diagnostics both support analyzer
suppression actions.

## HTML and HTML-like files

Enable full template parsing with:

```json
{
  "html": {
    "experimentalFullSupportEnabled": true,
    "parser": { "interpolation": true }
  }
}
```

Without full support, Vue, Svelte, and Astro contribute only their JavaScript or
TypeScript sections. `html.parser.interpolation` is a separate switch for
`{{ expression }}` in plain HTML.

Full support improves Vue and Svelte parsing and reduces false positives from
`noUnusedVariables`, `useConst`, `useImportType`, and `noUnusedImports`.
Re-evaluate overrides that disabled these rules as parser coverage improves.

HTML, Vue, Svelte, and Astro support accessibility analysis including
`noAutofocus`, `noPositiveTabindex`, `useAltText`, `useAnchorContent`,
`useMediaCaption`, `useHtmlLang`, `useValidLang`, `useValidAriaRole`,
`useAriaPropsForRole`, `useButtonType`, `noAccessKey`,
`noDistractingElements`, `noSvgWithoutTitle`, `noRedundantAlt`, and
`useIframeTitle`.

Enable Vue syntax in ordinary `.html` files used as external templates:

```json
{ "html": { "parser": { "vue": true } } }
```

## Embedded template-literal snippets

Enable embedded CSS and GraphQL in JavaScript template literals:

```json
{
  "javascript": {
    "experimentalEmbeddedSnippetsEnabled": true
  }
}
```

This covers styled-components, Emotion, `graphql-tag`, and Relay's `graphql`
tag. The embedded snippets are formatted and linted with their own language
rules.

## SVG

Treat `.svg` as a first-class formatted and linted language.

## JSON dialects

Biome recognizes well-known JSON files and automatically distinguishes files
that allow comments from files that allow both comments and trailing commas.

`turbo.json`, `jest.config.json`, and `.json` files under `.vscode` or `.zed`
allow comments automatically. Files in `.vscode` and `.zed` still reject
trailing commas.

JSON files under a project's `.cursor` directory and Cursor's platform user
configuration directories automatically allow both comments and trailing
commas.

The analyzer applies `noDuplicateObjectKeys` to JSON and JSONC. JSON-specific
nursery rules include `noTopLevelLiterals`, which requires an object or array at
the document root, and `noEmptyObjectKeys`, which rejects empty-string keys.

## JavaScript and JSX

JSX is accepted in `.js` by default. Set
`javascript.parser.jsxEverywhere: false` to reject it. Editor documents using
the JavaScript language identifier can also parse JSX.

For the classic React transform, declare:

```json
{
  "javascript": {
    "jsxRuntime": "reactClassic"
  }
}
```

This makes `noUnusedImports` and `useImportType` retain the otherwise apparently
unused `React` import required by the classic transform. Biome also supports
React 19.

The `Temporal` API is recognized as a global.

## TypeScript syntax and resolution

TypeScript construct signatures accept const type parameters:

```ts
interface I {
  new<const T>(x: T): T;
}
```

Import types accept a `with` object that selects `"resolution-mode"`. In `.cts`
files, type-only imports may carry the same attribute; that import-declaration
form remains restricted to `.cts`.

```ts
type Fs = typeof import("fs", { with: { "resolution-mode": "import" } });
import type { TypeFromRequire } from "pkg" with { "resolution-mode": "require" };
```

Resolver support includes `baseUrl` from `tsconfig.json`. Module resolution
prefers the most specific overlapping package `exports` pattern.

## React and Preact

`useExhaustiveDependencies` understands Preact hooks as well as React hooks. It
detects some dependencies that change on every render, missing dependencies
declared as function declarations, duplicate dependencies, and dependency
instances targeted by narrow suppression comments. It does not report a
recursive call as a missing dependency.

Configure `reportUnnecessaryDependencies` to control declared-but-unused hook
dependencies; it defaults to `true`. Configure
`reportMissingDependenciesArray` to control reports for absent dependency
arrays.

`useHookAtTopLevel.ignore` exempts named `use*` utilities. The rule detects hooks
at module scope and inside non-hook, non-component functions or methods, except
function expressions.

React-domain membership matters: `noChildrenProp`, `noReactPropAssignments`,
`noDangerouslySetInnerHtml`, `noDangerouslySetInnerHtmlWithChildren`,
`useComponentExportOnlyModules`, and `noArrayIndexKey` require the React domain
or a nearby React dependency. Recommended members are `noChildrenProp`, both
dangerously-set-inner-HTML rules, and `noArrayIndexKey`.

## Vue

Vue single-file components support generic parameters on `<script setup>`:

```vue
<script generic="T extends Record<string, any>" lang="ts" setup>
// ...
</script>
```

Vue scripts accept both `lang="tsx"` and `lang="jsx"` with their corresponding
JSX behavior. Framework rules include `useVueScopedStyles`, which requires
`scoped` or `module`, and `noVueRefAsOperand`, which catches refs used without
`.value`.

`useVueValidVOn` accepts expressionless verb modifiers such as
`<div @click.stop></div>` and `<div @click.prevent></div>`, plus the
argument-less object form `<div v-on="$listeners"></div>`.

## Svelte

`noUndeclaredVariables` recognizes Svelte 5 runes in `.svelte`, `.svelte.js`,
and `.svelte.ts` files. `noUnusedVariables` treats `$store` in a template as use
of the underlying `store` binding and permits `$bindable()` props that are
intentionally only written in the script block.

Svelte opening tags accept JavaScript line and block comments:

```svelte
<button
  // call the handler
  onclick={submit}
>Save</button>
```

## Astro and route filenames

Astro parses shorthand attributes such as:

```astro
<button {disabled}>Save</button>
```

Filename-convention analysis permits the leading `+` used by SvelteKit and
Vike routes and recognizes dynamic route names used by Next.js, SolidStart,
Nuxt, and Astro. Catch-all names such as `[...slug].js` and
`[[...slug]].js` are accepted when the parameter is alphanumeric.

## Test globals and assertions

The Playwright and test domains supply common test globals. The test domain also
provides Mocha's `context`, `run`, `setup`, `specify`, `suite`, `suiteSetup`,
`suiteTeardown`, `teardown`, `xcontext`, `xdescribe`, `xit`, and `xspecify`.

Assertion analysis recognizes Testing Library `waitFor`, method-based APIs such
as `test.each`, Jest static helpers such as `expect.any`,
`expect.objectContaining`, and `expect.extend`, and Vitest `assert`,
`expectTypeOf`, and `assertType`. Asymmetric matchers and helpers such as
`expect.extend()` are not standalone assertions.

Coverage IDs: `1.7-guide`, `1.7.0`, `1.8.0`, `1.9-guide`, `1.9.0`,
`2.0-guides`, `2.3.0`, `2.4-guide`, `2.4.0`, `2.5-guide`, `2.5.0`.
