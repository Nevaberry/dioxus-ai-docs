---
name: storybook-knowledge-patch
description: Storybook
version: "10.5.0"
license: MIT
metadata:
  author: Nevaberry
---


# Storybook Knowledge Patch

## When to load this skill

Load this skill when upgrading, configuring, testing, or authoring stories in a
modern Storybook project. It is especially useful when work touches:

- the ESM-only runtime and its Node.js requirements;
- Angular, Next.js, Svelte, React Native, or TanStack Router integrations;
- the Test widget, Vitest, module mocks, story-bound tests, or React Server
  Component tests;
- React CSF factories, tags, MDX, Docs, Controls, or docgen;
- Vite builder options, manager customization, linting, or experimental
  automation.

Treat the project's manifest, lockfile, configuration, and observed behavior as
authoritative. Check installed Storybook packages before applying an API or
migration note from this skill.

## Reference index

| Reference | Topics |
| --- | --- |
| [Frameworks and migrations](references/frameworks-and-migrations.md) | ESM runtime, Angular, Next.js, Svelte, React Native, and TanStack Router |
| [Testing and automation](references/testing-and-automation.md) | Test widget, Codegen, globals, Vitest, mocks, story tests, RSC tests, and visual review |
| [Story authoring and docs](references/story-authoring-and-docs.md) | CSF factories, tags, MDX, Docs APIs, React docgen, and metadata |
| [Configuration and manager](references/configuration-and-manager.md) | Vite config loading, CLI behavior, browser controls, manager assets, viewport warnings, and lint/setup integration |

## Breaking changes and deprecations

### Storybook 10 is ESM-only

Storybook 10 packages are published only as ESM. Use a Node.js release that
supports ESM through `require()`:

- Node.js 20.16 or newer within the 20.x line;
- Node.js 22.19 or newer within the 22.x line;
- Node.js 24 or newer.

If startup fails before project configuration is evaluated, verify the Node.js
runtime first. Do not rewrite installed Storybook packages to CommonJS.

### Removed and discouraged APIs

- `ExternalDocs` is deprecated. Avoid new uses and account for it in Docs
  migrations.
- The legacy `defaultViewport` parameter emits a warning. A working preview
  that uses it still needs migration.
- TanStack Router integration no longer supplies an Outlet mock. Route stories
  must not depend on an implicit Storybook-provided Outlet.

### Angular dependency expectations

`@storybook/angular-vite` does not require
`@angular/platform-browser-dynamic` solely for Storybook. Do not add that
package unless the application itself needs it. The framework's TypeScript
peer range accepts TypeScript 6.

## Framework quick reference

### Angular on Vite

`@storybook/angular-vite` is a preview framework for Vite-powered Angular
development, Docs, and testing:

```js
export default {
  framework: '@storybook/angular-vite',
};
```

After an Angular-to-Vite migration, verify that it preserved `zone.js`,
installed `@analogjs/vite-plugin-angular`, and configured addon Vitest. Angular
22 is also supported by the separate Webpack framework; Angular 22 does not by
itself require Vite.

### Next.js on Vite

Use the Vite-powered framework when the project needs Next.js navigation,
route, image, and font mocks with Storybook Test and Vitest:

```ts
export default {
  framework: '@storybook/nextjs-vite',
};
```

The `next/link` mock understands `as`, calls `onClick` before preventing the
default browser action, and includes compatibility with `useLinkStatus`.

### Other framework integrations

- Svelte CSF supports Svelte 5 runes and snippets, async components, and
  SvelteKit mocking for `app/state`.
- React Native and React Native Web Storybooks can run side by side, sharing
  stories between devices or simulators and web-based Docs and Test addons.
- `@storybook/tanstack-react` exports `TanStackPreview` for CSF Next typing and
  `Hydrate` for hydration integration.
- TanStack route options accept either `id` or `path`; route groups are
  normalized, route cloning preserves explicit IDs, and component overrides
  are honored.
- Compatibility includes Next.js 16 and Vitest 4 without dropping older
  supported versions.

## Testing quick reference

### Test widget and generated tests

The Test widget can run interaction and `axe-core` accessibility tests across
all stories, show results in the sidebar, and watch files to rerun relevant
tests. It coordinates visual tests and line, function, and branch coverage.

Storybook's UI can create and edit stories. The Test Codegen addon records
interactions and assertions and saves the generated test from within the UI.

### Pin test conditions with globals

A story or component can pin theme, viewport, locale, background, or other
globals while those values remain selectable elsewhere:

```ts
export const Dark = {
  ...Default,
  globals: { theme: 'dark' },
};
```

For an addon Vitest project, use `initialGlobals` to give that project a fixed
theme, viewport, locale, or other global state.

### Mock modules across builders

Use `sb.mock` for module automocking with either Vite or Webpack. The mock is
available during development and in static production builds.

### Attach focused tests to factory stories

CSF factory stories can experimentally attach named tests with `.test()`. The
callback receives the same testing context as `play`:

```ts
Disabled.test('should be disabled', async ({ canvas, userEvent }) => {
  const button = await canvas.findByRole('button');
  await userEvent.click(button);
  await expect(button).toBeDisabled();
});
```

This supports test-only stories that are excluded from the sidebar. React
Server Components can also be component-tested experimentally by running their
server side in the browser; the same work supports direct Vitest RSC tests.

## Authoring and Docs quick reference

### React CSF factories

React CSF factories are at Preview status. A typed preview can create component
metadata and stories without separate `Meta` and `StoryObj` declarations:

```ts
import preview from '../.storybook/preview';
import Button from './Button';

const meta = preview.meta({ component: Button });
export const Primary = meta.story({
  args: { label: 'Button', primary: true },
});
```

Older CSF formats remain supported, so adoption can be incremental.

### Tags and story filtering

Tag filters can exclude matching stories, and `main.ts` can set the initial
filter state:

```ts
export default {
  tags: {
    experimental: { defaultFilterSelection: 'exclude' },
  },
};
```

CSF Next supports tag types. A `skip` tag propagates to generated `.test`
children, so inherited skipping can explain missing generated tests.

### MDX, Docs, and component metadata

Addon Docs resolves CSF4 modules even without a default export. Standalone MDX
can give `Meta` an explicit `id`:

```mdx
<Meta id="guides-introduction" title="Guides/Introduction" />
```

`ActionItem` accepts `ariaLabel`. For shared React metadata across MCP, Docs,
Controls, ArgTypes, and `react-component-meta`, enable the experimental
worker-backed docgen service:

```js
export default {
  features: { experimentalDocgenServer: true },
};
```

## Configuration and experimental tooling

- The Vite builder accepts `configLoader` through its builder options.
- `features.experimentalReview` enables AI-curated visual changesets and search
  results. It is unset by default, allowing CLI integrations to opt in.
- The core-bundled experimental `storybook ai` command exposes MCP passthrough
  when `STORYBOOK_FEATURE_AI_CLI` is enabled. It accepts `-p` as shorthand for
  `--port` and discovers instances by working directory or config directory.
- Agent-driven development does not automatically open a browser. `BROWSER`
  and `BROWSER_ARGS` are honored when browser launch is requested.
- A favicon injected through `manager-head` overrides the manager default.
- The Storybook ESLint plugin exposes metadata for oxlint-based rule setups.
- Follow AI setup guidance with `msw-storybook-addon` v3.

Use the linked references for task-oriented details and migration caveats
before changing framework, test, authoring, or manager configuration.
