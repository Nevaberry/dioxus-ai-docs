# Testing and automation

## Test widget and UI workflows

### Component and accessibility testing

The Test widget introduced for Storybook 9 can run interaction and `axe-core`
accessibility tests across all stories (batch `9.0-10.0`). It:

- exposes results in the sidebar;
- watches files and reruns relevant tests;
- coordinates Chromatic visual tests;
- reports line, function, and branch coverage.

Use the widget when a change should be exercised across the story catalog, not
only through a single opened story.

### UI-authored stories and tests

Storybook can create and edit stories in its UI (batch `9.0-10.0`). The Test
Codegen addon records interactions and assertions and saves the resulting test
without leaving Storybook.

Review generated code before committing it, especially selectors and assertions
whose stability depends on accessible roles or visible labels.

## Globals and test conditions

### Per-story and per-component globals

Stories and components can pin theme, viewport, locale, background, or other
globals while those values remain configurable elsewhere (batch `9.0-10.0`):

```ts
export const Dark = {
  ...Default,
  globals: { theme: 'dark' },
};
```

This is useful when one story expresses an invariant environment rather than
merely an initial toolbar selection.

### Fixed globals for Vitest projects

Addon Vitest accepts `initialGlobals` for a test project (since `10.5.0`). Use
it to give an entire project a fixed theme, viewport, locale, or similar global
state. Keep story-level invariants in `globals`; use `initialGlobals` when the
test project itself owns the fixed condition.

## Module mocking

### Builder-independent mocks

Use `sb.mock` for module automocking with Vite and Webpack (batch `9.0-10.0`).
Its API is modeled after `vi.mock`, but its important Storybook property is
that mocks remain available in both development and static production builds.

Prefer it when a story must behave the same in the dev server, test execution,
and a deployed static Storybook.

## Story-bound and server component tests

### Named tests on CSF factory stories

CSF factory stories can experimentally attach focused named tests with
`.test()` (batch `9.0-10.0`). The callback receives the same testing context as
`play`:

```ts
Disabled.test('should be disabled', async ({ canvas, userEvent }) => {
  const button = await canvas.findByRole('button');
  await userEvent.click(button);
  await expect(button).toBeDisabled();
});
```

This supports test-only stories that can be excluded from the sidebar. Keep the
story's render setup close to the attached assertion and use accessible queries
for resilient generated output.

### React Server Component tests

Storybook can experimentally component-test React Server Components by running
their server side in the browser (batch `9.0-10.0`). This avoids limiting RSC
coverage to end-to-end tests. The same underlying support is available for
direct Vitest RSC tests.

## Visual review automation

### Experimental review workflow

Set `features.experimentalReview` to enable AI-curated visual changesets and
search results (since `10.5.0`):

```js
export default {
  features: { experimentalReview: true },
};
```

The flag is unset by default so agent CLI plugins can opt into the experimental
review workflow. Treat its results as review assistance rather than a
replacement for deterministic interaction, accessibility, or visual tests.
