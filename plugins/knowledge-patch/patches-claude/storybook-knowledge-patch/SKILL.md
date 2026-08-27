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
modern Storybook project. Use it especially for work involving:

- the ESM-only runtime or Node.js compatibility;
- Angular, Next.js, Svelte, React Native, or TanStack Router integrations;
- the Test widget, Vitest projects, module mocks, or story-bound tests;
- React CSF factories, tags, MDX, Docs, Controls, or docgen;
- Vite builder options, manager customization, or experimental automation.

Before applying a note, inspect the installed Storybook packages and the
project's manifest, lockfile, configuration, and tests. Treat observed project
behavior as authoritative when it differs from this guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Frameworks and migrations](references/frameworks-and-migrations.md) | ESM runtime, Angular, Next.js, Svelte, React Native, and TanStack Router |
| [Testing and automation](references/testing-and-automation.md) | Test widget, UI code generation, globals, Vitest, mocks, story tests, RSC tests, and visual review |
| [Story authoring and docs](references/story-authoring-and-docs.md) | CSF factories, tags, CSF4, MDX, Docs APIs, docgen, and component metadata |
| [Configuration and manager](references/configuration-and-manager.md) | Vite loading, AI CLI behavior, browser launch controls, favicon, viewport warnings, linting, and setup dependencies |

## Breaking changes and deprecations

### Use a compatible Node.js runtime

Storybook 10 packages are ESM-only and require a Node.js release that supports
ESM through `require()`:

- Node.js 20.16 or newer on the 20.x line;
- Node.js 22.19 or newer on the 22.x line;
- Node.js 24 or newer.

When startup fails before project configuration runs, verify Node.js first.
Do not attempt to make installed Storybook packages CommonJS.

### Remove reliance on changed APIs

- `ExternalDocs` is deprecated; avoid new uses and plan its removal from Docs
  customizations.
- The legacy `defaultViewport` parameter emits a warning even when the preview
  still renders.
- TanStack Router stories no longer receive an implicit Outlet mock. Supply the
  behavior the story actually needs.

## Framework quick reference

### Angular on Vite

Use the preview `@storybook/angular-vite` framework for Vite-based Angular
development, Docs, and testing:

```js
export default {
  framework: '@storybook/angular-vite',
};
```

After migrating from Angular Webpack, verify that the migration preserved
`zone.js`, installed `@analogjs/vite-plugin-angular`, and configured addon
Vitest. Angular 22 is also supported by the separate Webpack framework.

Do not install `@angular/platform-browser-dynamic` solely to satisfy
`@storybook/angular-vite`; it is no longer a peer dependency. The framework's
TypeScript peer range accepts TypeScript 6.

### Next.js on Vite

Use the Vite-powered framework for Next.js navigation, route, image, and font
mocks with Storybook Test and Vitest:

```ts
export default {
  framework: '@storybook/nextjs-vite',
};
```

The `next/link` mock supports `as`, invokes `onClick` before preventing the
default action, and is compatible with `useLinkStatus` through the Next.js Vite
framework.

### TanStack Router

Use `TanStackPreview` from `@storybook/tanstack-react` for CSF Next typing.
Route mocks accept `id` or `path`, normalize route groups, and do not provide an
Outlet mock. The package also exports `Hydrate`:

```ts
import { Hydrate } from '@storybook/tanstack-react';
```

Current integration behavior waits for router loading, preserves explicit
route and layout IDs when cloning, honors `routeOverrides` component
overrides, resolves mock redirects through Vite, and renders real `href`
values from the Link mock.

### Svelte and React Native

- Svelte CSF supports Svelte 5 runes and snippets.
- Svelte stories support async components, and SvelteKit mocking covers
  `app/state`.
- React Native and React Native Web Storybooks can run side by side, sharing
  stories between devices or simulators and web-based Docs and Test addons.

## Testing quick reference

### Run tests from the Test widget

The Test widget can run interaction and `axe-core` accessibility tests across
all stories, show results in the sidebar, and watch files to rerun relevant
tests. It also coordinates Chromatic visual tests and reports line, function,
and branch coverage.

Storybook can create and edit stories in its UI. The Test Codegen addon records
interactions and assertions and saves the generated test without leaving the
UI.

### Pin globals at the right scope

Pin theme, viewport, locale, background, or other globals on a story or
component while leaving them selectable elsewhere:

```ts
export const Dark = {
  ...Default,
  globals: { theme: 'dark' },
};
```

For an addon Vitest project, use `initialGlobals` when the whole test project
must run with fixed globals.

### Mock modules across builders

Use `sb.mock` for module automocking with Vite or Webpack. Unlike
test-runner-only mocks, these mocks remain available in development and static
production builds.

### Attach focused tests to factory stories

CSF factory stories can experimentally attach named tests with `.test()`.
The callback receives the same testing context as `play`:

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

### Adopt React CSF factories incrementally

React CSF factories are at Preview status. A typed preview creates component
metadata and stories without separate `Meta` and `StoryObj` declarations:

```ts
import preview from '../.storybook/preview';
import Button from './Button';

const meta = preview.meta({ component: Button });
export const Primary = meta.story({
  args: { label: 'Button', primary: true },
});
```

Older CSF formats remain supported, so migration can be incremental.

### Configure and propagate tags deliberately

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
children, so check inherited tags when generated tests do not run.

### Use current Docs and metadata APIs

Addon Docs resolves CSF4 modules without a default export. Standalone MDX can
set an explicit `id` on `Meta`, and `ActionItem` accepts `ariaLabel`:

```mdx
<Meta id="guides-introduction" title="Guides/Introduction" />
```

For worker-backed React metadata shared across MCP, Docs, Controls, ArgTypes,
and `react-component-meta`, enable:

```js
export default {
  features: { experimentalDocgenServer: true },
};
```

## Configuration and experimental tooling

- Pass `configLoader` through Vite builder options when controlling how Vite
  configuration is loaded.
- Enable `features.experimentalReview` for experimental AI-curated visual
  changesets and search results. It is unset by default.
- The experimental core-bundled `storybook ai` command provides MCP
  passthrough when `STORYBOOK_FEATURE_AI_CLI` is enabled. It accepts `-p` for
  `--port` and discovers instances by working or config directory.
- Agent-driven development does not automatically open a browser. Storybook
  honors `BROWSER` and `BROWSER_ARGS` when browser launching is requested.
- A favicon injected through `manager-head` overrides the manager default.
- The Storybook ESLint plugin includes metadata and can expose its rules to an
  oxlint-based setup.
- Follow AI setup guidance with `msw-storybook-addon` v3.

Read the linked references before changing framework, test, authoring, or
manager configuration; they preserve the version-specific details and
migration caveats behind this quick reference.
