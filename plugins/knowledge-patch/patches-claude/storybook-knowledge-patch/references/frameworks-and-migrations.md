# Frameworks and Migrations

## Runtime and migration boundaries

### Storybook 10 is ESM-only

Storybook 10 publishes ESM-only packages and requires a Node.js release with
ESM `require()` support (batch `9.0-10.0`):

- Node.js 20.16 or newer within the 20.x line;
- Node.js 22.19 or newer within the 22.x line;
- Node.js 24 or newer.

If startup fails before project configuration is evaluated, check the running
Node.js version before editing Storybook configuration. Rewriting installed
packages to CommonJS does not address an unsupported runtime.

## Angular

### Choose between Vite and Webpack deliberately

The preview `@storybook/angular-vite` framework provides Vite-based Angular
development, Docs, and testing (since `10.5.0`):

```js
export default {
  framework: '@storybook/angular-vite',
};
```

The Angular-to-Vite migration should:

- preserve `zone.js`;
- install `@analogjs/vite-plugin-angular`;
- configure addon Vitest.

Verify those results after migration. The separate Angular Webpack framework
also supports Angular 22, so Angular 22 alone is not a reason to select Vite.

### Update Angular-Vite dependencies

As of `10.5.1`, `@storybook/angular-vite` no longer declares
`@angular/platform-browser-dynamic` as a peer dependency. Do not install that
package only for Storybook. Its TypeScript peer range also accepts TypeScript
6.

## Next.js

### Use the Vite-powered framework

`@storybook/nextjs-vite` supplies Next.js navigation, route, image, and font
mocks on Vite and works with Storybook Test and Vitest (batch `9.0-10.0`):

```ts
export default {
  framework: '@storybook/nextjs-vite',
};
```

The supported framework and test-runner combinations include Next.js 16 and
Vitest 4 without dropping older supported versions.

### Account for Link mock behavior

The `next/link` mock supports the `as` prop and invokes a supplied `onClick`
before preventing the browser's default action (since `10.5.0`). The Next.js
Vite framework also provides a Link mock compatible with `useLinkStatus`.

When a navigation assertion depends on call order, assert the handler effect
before checking prevented navigation.

## Svelte

Svelte CSF supports Svelte 5 runes and snippets (batch `9.0-10.0`). Storybook
10 also supports async Svelte components, and its SvelteKit mocking includes
`app/state`.

Use the framework mock rather than adding an unrelated application-state shim
when a story imports from `app/state`.

## React Native

React Native and React Native Web Storybooks can run side by side (batch
`9.0-10.0`). The same stories can therefore serve device or simulator
workflows and the web-based Docs and Test addons.

Keep platform-specific decorators or parameters narrow so shared stories
remain portable between the native and web instances.

## TanStack Router

### CSF typing and route definitions

`@storybook/tanstack-react` exports `TanStackPreview` for CSF Next typing
(since `10.5.0`). Route mocks accept either `id` or `path` in `RouteOptions`,
normalize route groups, and no longer supply an Outlet mock.

Do not build stories around an implicit Outlet. Add the layout or outlet
behavior explicitly when the scenario needs it.

### Hydration and router behavior

As of `10.5.1`, the package exports `Hydrate`:

```ts
import { Hydrate } from '@storybook/tanstack-react';
```

The integration also:

- removes `@cloudflare/vite-plugin` from inherited Vite configuration;
- waits for the router to load before completing story routing;
- preserves explicit route and layout IDs when cloning routes;
- honors component overrides supplied through `routeOverrides`;
- resolves mock redirects through Vite;
- renders real `href` values from the Link mock.

Prefer assertions against the rendered `href` and loaded route state instead
of assuming routing is complete synchronously.
