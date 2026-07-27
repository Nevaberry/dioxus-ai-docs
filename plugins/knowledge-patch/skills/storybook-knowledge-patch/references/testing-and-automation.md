# Testing and automation

## Test widget

Storybook's Test widget can run interaction tests and `axe-core` accessibility
tests across all stories. It exposes results in the sidebar and watches files
so that relevant tests rerun after changes.

The widget also coordinates:

- Chromatic visual tests;
- line coverage;
- function coverage;
- branch coverage.

Use the sidebar results to distinguish story-level failures, while retaining
the underlying test and coverage outputs for CI diagnosis.

## UI-authored stories and Test Codegen

Stories can be created and edited from the Storybook UI. The Test Codegen addon
records interactions and assertions and saves the resulting test without
leaving Storybook.

Review generated tests as maintained source: keep stable accessible queries,
remove incidental interactions, and preserve only assertions that express the
intended behavior.

## Globals at story, component, and project scope

A story or component can pin globals such as theme, viewport, locale, or
background while leaving those globals configurable for other content:

```ts
export const Dark = {
  ...Default,
  globals: { theme: 'dark' },
};
```

Addon Vitest accepts `initialGlobals` at the test-project level. Use it when an
entire project must execute with a fixed theme, viewport, locale, or other
global. Do not confuse this project-wide initial state with a story's `globals`
override.

## Cross-builder module automocking

The `sb.mock` API is inspired by `vi.mock`, but it is a Storybook module-mocking
facility that works with both Vite and Webpack builders. Its mocks remain
available in development and static production builds.

This makes `sb.mock` suitable for stories whose mocked behavior must work in a
deployed static Storybook, rather than only inside a separate test process.

## Story-bound tests

CSF factory stories can experimentally attach named tests with `.test()`. The
test callback receives the same testing context as a `play` function:

```ts
Disabled.test('should be disabled', async ({ canvas, userEvent }) => {
  const button = await canvas.findByRole('button');
  await userEvent.click(button);
  await expect(button).toBeDisabled();
});
```

This supports focused test-only stories. Such stories can be excluded from the
sidebar so the navigation tree does not have to expose every test fixture.

CSF Next tag support also affects generated tests: a `skip` tag propagates to
generated `.test` children. Check inherited tags when an expected generated
test is skipped.

## React Server Component tests

React Server Components can be component-tested experimentally by running the
server side in the browser. This removes the need to reserve every RSC test for
an end-to-end environment. The underlying capability is also available for
direct Vitest RSC tests.

Treat this as experimental infrastructure and keep environment-specific server
assumptions visible in test setup.

## Experimental visual review

Set `features.experimentalReview` to enable AI-curated visual changesets and
search results:

```js
export default {
  features: { experimentalReview: true },
};
```

The option is unset by default. This permits CLI integrations to enable the
experimental review workflow deliberately instead of changing every project's
default configuration.

Batch attribution: `9.0-10.0`, `10.5.0`.
