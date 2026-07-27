# Frameworks and migrations

## Runtime and package format

Storybook 10 is ESM-only. Its packages require a Node.js version with ESM
`require()` support: Node.js 20.16+, 22.19+, or 24+.

When an upgrade fails at process startup or package loading, confirm the active
Node.js executable and CI runtime before changing Storybook configuration. A
CommonJS-oriented workaround cannot restore a supported package format.

## Angular

### Angular on Vite

The preview `@storybook/angular-vite` framework provides Vite-based Angular
development, Docs, and testing:

```js
export default {
  framework: '@storybook/angular-vite',
};
```

The Angular-to-Vite migration performs three important compatibility steps:

- preserves `zone.js`;
- installs `@analogjs/vite-plugin-angular`;
- configures addon Vitest.

Inspect all three after an automated migration, particularly if the preview
runs but interaction tests or Angular change detection behave differently.

The Webpack-based Angular framework separately supports Angular 22. Choose a
builder based on project needs rather than treating Vite as an Angular 22
requirement.

## Next.js

### Vite-powered framework

`@storybook/nextjs-vite` implements Next.js navigation, route, image, and font
mocks on Vite. It is compatible with Storybook Test and Vitest.

```ts
export default {
  framework: '@storybook/nextjs-vite',
};
```

Next.js 16 is supported without dropping support for older supported versions.

### Link behavior

The `next/link` mock supports the `as` prop. On a click, the mock calls the
consumer's `onClick` handler before preventing the default action. Tests that
assert ordering or inspect the event should reflect that sequence.

The Next.js Vite framework also supplies a Link mock compatible with
`useLinkStatus`.

## Svelte and SvelteKit

- Svelte CSF supports Svelte 5 runes and snippets.
- Storybook supports Svelte async components.
- SvelteKit mocking includes `app/state`.

These capabilities allow current Svelte syntax and application state APIs to be
used directly in stories without maintaining legacy-only story variants.

## React Native

React Native and React Native Web Storybooks can run side by side. The same
stories can run on devices or simulators and participate in the web Storybook's
Docs and Test addons. Prefer shared stories where platform behavior permits,
with platform-specific setup kept in the respective Storybook environments.

## TanStack Router

`@storybook/tanstack-react` exports `TanStackPreview` for typing CSF Next
previews. Its `RouteOptions` accepts either an `id` or a `path`, and route-group
paths are normalized.

The integration no longer provides an Outlet mock. Stories that need an outlet
must not rely on a formerly implicit integration mock.

## Test-runner compatibility

Vitest 4 is supported without dropping older supported versions. Confirm the
project's resolved Vitest and framework packages when diagnosing integration
behavior because a broad manifest range may resolve differently across local
and CI installs.

Batch attribution: `9.0-10.0`, `10.5.0`.
