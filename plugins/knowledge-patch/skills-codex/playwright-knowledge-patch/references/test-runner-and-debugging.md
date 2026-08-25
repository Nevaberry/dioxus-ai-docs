# Test Runner and Debugging

## Command-line debugging

In `1.59.1`, `npx playwright test --debug=cli` pauses a test for attachment
with `playwright-cli attach`. Session commands such as `step-over` can control
the attached test.

## Trace inspection without the GUI

Open a trace with:

```sh
npx playwright trace open <trace.zip>
```

Then inspect it with `actions`, `action <id>`,
`snapshot <id> --name before|after`, and `close`.

## Trace retention across retries

In `1.59.1`, trace mode `'retain-on-failure-and-retries'` records every test
attempt and keeps all those traces when an attempt fails. Passing and failing
runs of a flaky test can therefore be compared.

```ts
export default defineConfig({
  use: { trace: 'retain-on-failure-and-retries' },
});
```

## Video retry modes and annotations

In `1.59.1`, the test `video` option can configure `show.actions` and
`show.test` annotations.

Since `1.61.0`, the `video` option also accepts `'on-all-retries'`,
`'retain-on-first-failure'`, and `'retain-on-failure-and-retries'`, matching
the trace mode choices.

```ts
export default defineConfig({
  use: { video: 'retain-on-failure-and-retries' },
});
```

## Soft polling

Since `1.61.0`, `expect.soft.poll()` adds polling assertions whose final
failure is reported softly.

```ts
await expect.soft.poll(async () => readStatus()).toBe('ready');
```

## Runner and reporter data

The following runner and reporter data is available in `1.61.0`:

- `fullConfig.argv` captures the runner's `process.argv`, including custom
  arguments after `--`.
- `fullConfig.failOnFlakyTests` exposes the effective flaky-test policy.
- `testInfo.errors` expands an `AggregateError` into separate entries.
- `-G` is shorthand for `--grep-invert`.

## WebSockets in recordings

Since `1.61.0`, HAR and trace recordings include WebSocket requests.

## Story-and-gallery component testing

In `1.62.0`, component testing uses stories for concrete component scenarios
and a served gallery that renders them on demand. The `mount` fixture opens a
story by id and returns a locator scoped to its root. That locator exposes
`update(props)` and `unmount()`. A story type can be supplied as a type argument
to check props.

```ts
test('click should expand', async ({ mount }) => {
  const component = await mount('components/Expandable/Stateful');
  await component.getByRole('button').click();
  await expect(component.getByTestId('expanded')).toHaveValue('true');
});
```

## Reporter preprocessing

In `1.62.0`, a reporter's `preprocess()` hook runs after configuration
resolution and before `onBegin()`. Through its `TestRun`, it can mark individual
tests skipped, excluded, fixed, or failing before execution begins.

```ts
class MyReporter {
  async preprocess({ suite, testRun }) {
    for (const test of suite.allTests()) {
      if (shouldSkip(test)) testRun.skip(test);
    }
  }
}
```

## Isolated retry scheduling

In `1.62.0`, `testConfig.retryStrategy` controls retry ordering. Its default,
`'immediate'`, schedules a retry as soon as a worker is available. `'isolated'`
defers retries until the end and runs them serially in one worker to reduce
interference with the main suite.

```ts
export default defineConfig({
  retries: 2,
  retryStrategy: 'isolated',
});
```

## HTML report file grouping

In `1.62.0`, the HTML reporter can enable file merging directly with
`mergeFiles` rather than only through the report UI.

```ts
export default defineConfig({
  reporter: [['html', { mergeFiles: true }]],
});
```

## Platform and package support

Since `1.61.0`, Playwright supports Ubuntu 26.04.

WebKit no longer supports macOS 14 as of `1.59.1`. The JavaScript package
`@playwright/experimental-ct-svelte` was also removed in `1.59.1`.
