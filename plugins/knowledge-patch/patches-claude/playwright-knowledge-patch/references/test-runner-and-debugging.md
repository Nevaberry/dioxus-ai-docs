# Test Runner and Debugging

## Removed support and platform changes

- WebKit no longer supports macOS 14 (since 1.59.1).
- `@playwright/experimental-ct-svelte` was removed (since 1.59.1).
- Ubuntu 26.04 is supported (since 1.61.0).

## Command-line debugging

Run a test with the command-controlled debugger, attach to its bound session,
and step it (since 1.59.1):

```bash
npx playwright test --debug=cli
playwright-cli attach
step-over
```

## Command-line trace inspection

Inspect a saved trace without opening the GUI (since 1.59.1):

```bash
npx playwright trace open trace.zip
actions
action <id>
snapshot <id> --name before
snapshot <id> --name after
close
```

`tracing.start({ live: true })` enables live trace updates.

## Trace retention across retries

Trace mode `'retain-on-failure-and-retries'` records every attempt and retains
all attempt traces when any attempt fails (since 1.59.1). This preserves both
passing and failing executions of a flaky test for comparison.

```ts
export default defineConfig({
  use: { trace: 'retain-on-failure-and-retries' },
});
```

## Video retry modes and soft polling

The test `video` option accepts three retry-aware choices (since 1.61.0):

- `'on-all-retries'`
- `'retain-on-first-failure'`
- `'retain-on-failure-and-retries'`

```ts
export default defineConfig({
  use: { video: 'retain-on-failure-and-retries' },
});

await expect.soft.poll(async () => readStatus()).toBe('ready');
```

`expect.soft.poll()` performs a polling assertion whose final failure is
reported softly instead of immediately stopping the test.

## Isolated retry scheduling

`testConfig.retryStrategy` controls retry ordering (since 1.62.0). The default
`'immediate'` schedules a retry as soon as a worker becomes available.
`'isolated'` defers retries until the end, then runs them serially in one worker
to reduce interference with the main suite.

```ts
export default defineConfig({
  retries: 2,
  retryStrategy: 'isolated',
});
```

## Reporter preprocessing

A reporter's `preprocess()` hook runs after configuration resolution but before
`onBegin()` (since 1.62.0). Through its `TestRun`, it can mark individual tests
skipped, excluded, fixed, or failing before execution begins.

```ts
class MyReporter {
  async preprocess({ suite, testRun }) {
    for (const test of suite.allTests()) {
      if (shouldSkip(test)) testRun.skip(test);
    }
  }
}
```

## Runner and reporter data

The following additions date to 1.61.0:

- `fullConfig.argv` captures the runner's `process.argv`, including custom
  arguments after `--`.
- `fullConfig.failOnFlakyTests` exposes the effective flaky-test policy.
- `testInfo.errors` expands an `AggregateError` into separate entries.
- `-G` is shorthand for `--grep-invert`.

## Merged-file grouping in HTML reports

Enable merged-file grouping directly with the HTML reporter's `mergeFiles`
option (since 1.62.0), instead of relying only on the report UI.

```ts
export default defineConfig({
  reporter: [['html', { mergeFiles: true }]],
});
```

## WebSockets in recordings

HAR and trace recordings include WebSocket requests (since 1.61.0).
