# Frameworks and migrations

## Runtime and migration prerequisites

### ESM-only packages

Storybook 10 packages are ESM-only (batch `9.0-10.0`). The runtime must support
loading ESM through `require()`:

- Node.js 20.16 or newer on the 20.x line;
- Node.js 22.19 or newer on the 22.x line;
- Node.js 24 or newer.

Check `node --version` before investigating configuration when the process
fails during startup. Do not patch installed packages back to CommonJS.

## Angular

### Choose the Angular framework deliberately

The preview `@storybook/angular-vite` framework provides Vite-based Angular
development, Docs, and testing (since `10.5.0`):

```js
export default {
  framework: '@storybook/angular-vite',
};
```

An Angular-to-Vite migration should:

- preserve `zone.js`;
- install `@analogjs/vite-plugin-angular`;
- configure addon Vitest.

Verify all three after running the migration. The Webpack framework separately
supports Angular 22, so that Angular version does not force a Vite migration.

### Angular-Vite dependencies

As of `10.5.1`, `@storybook/angular-vite` no longer declares
`@angular/platform-browser-dynamic` as a peer dependency. Do not install it
solely to satisfy Storybook. Its TypeScript peer range also accepts TypeScript
6.

## Next.js

### Vite-powered framework

`@storybook/nextjs-vite` supplies Next.js navigation, route, image, and font
mocks on Vite (batch `9.0-10.0`). It integrates with Storybook Test and Vitest:

```ts
export default {
  framework: '@storybook/nextjs-vite',
};
```

Compatibility includes Next.js 16 and Vitest 4 while retaining older supported
versions.

### Link behavior

The `next/link` mock supports `as` and calls the provided `onClick` before it
prevents the default action (since `10.5.0`). The Next.js Vite framework also
provides a Link mock compatible with `useLinkStatus`.

When a click assertion depends on ordering, assert the handler effect before
checking prevented navigation.

## Svelte and React Native

### Svelte support

Svelte CSF supports Svelte 5 runes and snippets (batch `9.0-10.0`). Storybook 10
also supports async Svelte components and SvelteKit mocking for `app/state`.

### Paired native and web workflows

React Native and React Native Web Storybooks can run side by side (batch
`9.0-10.0`). The same story set can serve devices or simulators while web-based
Storybook supplies Docs and Test addons.

## TanStack Router

### Types, route options, and removed mocks

`@storybook/tanstack-react` exports `TanStackPreview` for CSF Next typing (since
`10.5.0`). `RouteOptions` accepts either `id` or `path`, and route groups are
normalized. The integration no longer provides an Outlet mock, so provide
explicit route layout behavior where a story needs one.

### Hydration and routing behavior

`@storybook/tanstack-react` exports `Hydrate` as of `10.5.1`:

```ts
import { Hydrate } from '@storybook/tanstack-react';
```

The inherited Vite configuration removes `@cloudflare/vite-plugin`. Story
routing also:

- waits for the router to load before proceeding;
- preserves explicit route and layout IDs when cloning routes;
- honors component overrides supplied through `routeOverrides`;
- resolves mock redirects through Vite;
- renders real `href` values from the Link mock.

These behaviors matter to tests that inspect links, redirect resolution, or
cloned route identity.
