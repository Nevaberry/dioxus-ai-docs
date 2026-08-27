# Testing and Automation

## Test widget and UI-authored tests

### Run the Storybook test surface

The Storybook 9 Test widget runs interaction and `axe-core` accessibility tests
across all stories (batch `9.0-10.0`). It exposes results in the sidebar and
watches files so relevant tests rerun after a change.

The same widget coordinates Chromatic visual tests and reports line, function,
and branch coverage. Use its separate result surfaces to distinguish behavior,
accessibility, visual, and coverage failures rather than treating them as a
single test outcome.

### Create stories and tests from the UI

Storybook 9 can create and edit stories from its UI (batch `9.0-10.0`). The
Test Codegen addon records interactions and assertions and writes the resulting
test without leaving Storybook.

Review the generated story or test in source control just as you would a
hand-authored change, especially selectors and timing assumptions.

## Globals in stories and Vitest projects

### Pin globals on stories or components

A story or component can pin globals such as theme, viewport, locale, or
background while those values remain configurable elsewhere (batch
`9.0-10.0`):

```ts
export const Dark = {
  ...Default,
  globals: { theme: 'dark' },
};
```

Use story-level globals when the state is part of the scenario being
documented or tested.

### Pin globals for an addon Vitest project

Addon Vitest accepts `initialGlobals` to fix the globals of an entire test
project (since `10.5.0`). This supports projects dedicated to a theme,
viewport, locale, background, or other global state.

Use `initialGlobals` for project-wide test conditions and `globals` for a
specific story or component; do not duplicate the project setting across
every story.

## Module mocking

Use `sb.mock` for module automocking with both Vite and Webpack builders (batch
`9.0-10.0`). Its API is inspired by `vi.mock`, but the important Storybook
property is lifecycle: an `sb.mock` mock remains available in development and
static production builds.

Prefer it when a published static Storybook must behave like the development
instance. A test-runner-only mock can disappear from the static build and
produce a misleading deployment-only failure.

## Story-bound tests

CSF factory stories can experimentally attach named tests with `.test()`
(batch `9.0-10.0`). The callback receives the same testing context as a `play`
function:

```ts
Disabled.test('should be disabled', async ({ canvas, userEvent }) => {
  const button = await canvas.findByRole('button');
  await userEvent.click(button);
  await expect(button).toBeDisabled();
});
```

Named tests support focused, test-only stories that can be excluded from the
sidebar. Keep user-visible examples separate when a test fixture would make
the documentation noisy.

CSF Next tag types also affect these tests: a `skip` tag propagates to generated
`.test` children (since `10.5.0`). Inspect inherited tags when a generated test
does not execute.

## React Server Component tests

Storybook can experimentally component-test React Server Components by
running the server side in the browser (batch `9.0-10.0`). This avoids making
end-to-end tests the only way to exercise an RSC.

The underlying support is also available for direct Vitest RSC tests. Choose
Storybook tests when the component scenario benefits from story composition
and the Test UI; choose direct Vitest tests when the UI adds no value.

## Experimental visual review

Enable the experimental review workflow with `features.experimentalReview`
(since `10.5.0`):

```js
export default {
  features: { experimentalReview: true },
};
```

It provides AI-curated visual changesets and search results. The option is
unset by default, which lets compatible command-line plugins opt into the
workflow rather than forcing it on every project.
