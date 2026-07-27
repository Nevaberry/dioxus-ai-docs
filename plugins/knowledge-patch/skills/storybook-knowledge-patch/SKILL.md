---
name: storybook-knowledge-patch
description: Storybook
version: 10.5.0
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
- React CSF factories, CSF Next, tags, MDX, Docs, Controls, or docgen;
- Vite builder options, manager customization, or experimental automation.

Treat the project's manifest, lockfile, configuration, and observed behavior as
authoritative. Check the installed Storybook packages before applying an API or
migration note from this skill.

## Reference index

| Reference | Topics |
| --- | --- |
| [Frameworks and migrations](references/frameworks-and-migrations.md) | ESM runtime, Angular, Next.js, Svelte, React Native, and TanStack Router |
| [Testing and automation](references/testing-and-automation.md) | Test widget, Codegen, globals, Vitest, mocks, story tests, RSC tests, and visual review |
| [Story authoring and docs](references/story-authoring-and-docs.md) | CSF factories, CSF Next, tags, MDX, Docs APIs, and React docgen |
| [Configuration and manager](references/configuration-and-manager.md) | Vite config loading, experimental CLI behavior, browser launch controls, favicon, and viewport warnings |

## Breaking changes and deprecations

### Storybook 10 is ESM-only

Storybook 10 packages are published only as ESM. Use a Node.js release that
supports ESM through `require()`:

- Node.js 20.16 or newer within the 20.x line;
- Node.js 22.19 or newer within the 22.x line;
- Node.js 24 or newer.

If startup fails before Storybook evaluates project configuration, verify the
Node.js runtime first. Do not try to repair an unsupported runtime by rewriting
Storybook's installed packages to CommonJS.

### Removed and discouraged APIs

- `ExternalDocs` is deprecated. Avoid introducing new uses and account for the
  deprecation during Docs migrations.
- The legacy `defaultViewport` parameter now warns. A passing preview with this
  parameter is not warning-free and should still be migrated.
- TanStack Router integration no longer supplies an Outlet mock. Do not design
  new route stories around an implicit Storybook-provided Outlet.

### Angular builder choice matters

`@storybook/angular-vite` is a preview framework for Vite-powered Angular
development, Docs, and testing:

```js
export default {
  framework: '@storybook/angular-vite',
};
```

The Angular-to-Vite migration preserves `zone.js`, installs
`@analogjs/vite-plugin-angular`, and configures addon Vitest. Verify those
pieces after migration. Angular 22 support is also available through the
separate Webpack framework, so do not infer that Angular 22 requires Vite.

## Framework quick reference

### Next.js on Vite

Use the Vite-powered framework when the project needs Next.js navigation,
route, image, and font mocks together with Storybook Test and Vitest:

```ts
export default {
  framework: '@storybook/nextjs-vite',
};
```

The `next/link` mock understands `as`. Its click behavior invokes `onClick`
before preventing the default browser action. The Next.js Vite framework also
provides a Link mock compatible with `useLinkStatus`.

### Other framework integrations

- Svelte CSF supports Svelte 5 runes and snippets.
- Svelte stories can use async components, and SvelteKit mocking covers
  `app/state`.
- React Native and React Native Web Storybooks can run side by side, sharing
  stories between devices or simulators and web-based Docs and Test addons.
- `@storybook/tanstack-react` exports `TanStackPreview` for CSF Next typing.
  TanStack route options accept either `id` or `path`, and route groups are
  normalized.
- Compatibility includes Next.js 16 and Vitest 4 while retaining support for
  older supported versions.

## Testing quick reference

### Test widget and generated tests

The Test widget can run interaction and `axe-core` accessibility tests across
all stories, put results in the sidebar, and watch files to rerun the relevant
tests. It also coordinates Chromatic visual tests and line, function, and
branch coverage.

Storybook's UI can create and edit stories. The Test Codegen addon can record
interactions and assertions and save the generated test without leaving the UI.

### Pin test conditions with globals

A story or component can pin globals such as theme, viewport, locale, or
background while those globals remain selectable elsewhere:

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
available both during development and in static production builds, unlike
test-runner-only mocks that disappear from a built Storybook.

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

This supports test-only stories that can be excluded from the sidebar. React
Server Components can also be component-tested experimentally by running their
server side in the browser; the same underlying work supports direct Vitest
RSC tests.

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

Older CSF formats remain supported, so factory adoption can be incremental.

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
children, so account for inherited skipping when generated tests are missing.

### MDX, Docs, and component metadata

Addon Docs resolves CSF4 modules even when they have no default export.
Standalone MDX can give `Meta` an explicit `id`:

```mdx
<Meta id="guides-introduction" title="Guides/Introduction" />
```

`ActionItem` accepts `ariaLabel`. For unified React metadata across MCP, Docs,
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
  and `BROWSER_ARGS` are honored when browser launch behavior is requested.
- A favicon injected through `manager-head` can override the manager default.

Use the linked references for the full task-oriented details and migration
caveats before changing framework, test, or authoring configuration.
