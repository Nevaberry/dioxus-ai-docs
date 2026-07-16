# Test Runner and Debugging

## Removed support and supported platforms

As of 1.59.1:

- WebKit no longer supports macOS 14.
- The JavaScript package `@playwright/experimental-ct-svelte` has been removed.

Playwright supports Ubuntu 26.04 as of 1.61.0.

## CLI-controlled debugging

Start tests with the CLI debugger and attach to their named bound-browser session (since 1.59.1):

```bash
npx playwright test --debug=cli
playwright-cli attach
```

The attached session accepts debugger commands such as `step-over`, allowing a paused test to be controlled without a graphical debugger.

## Command-line trace inspection

Open a trace and inspect it entirely from the command line (since 1.59.1):

```bash
npx playwright trace open trace.zip
actions
action <id>
snapshot <id> --name before
snapshot <id> --name after
close
```

- `actions` lists trace actions.
- `action <id>` shows a selected action.
- `snapshot <id> --name before|after` selects the before or after snapshot.
- `close` closes the trace session.

For live recording updates, start tracing with `tracing.start({ live: true })`.

## Trace retention for retries

Trace mode `'retain-on-failure-and-retries'` records every test attempt but retains all attempt traces only if an attempt fails (since 1.59.1). This keeps both passing and failing attempts for a flaky test together for comparison.

## Video retry modes

The test `video` option supports the following retry-aware modes (since 1.61.0):

- `'on-all-retries'`
- `'retain-on-first-failure'`
- `'retain-on-failure-and-retries'`

```ts
export default defineConfig({
  use: { video: 'retain-on-failure-and-retries' },
});
```

These align video collection with the runner's trace-mode choices.

## Soft polling assertions

Polling assertions can be soft (since 1.61.0), collecting a failure without immediately stopping the test:

```ts
await expect.soft.poll(async () => readStatus()).toBe('ready');
```

## Runner configuration and reporter data

The following runner and reporting surfaces were added in 1.61.0:

- `fullConfig.argv` snapshots the runner's `process.argv`, including application-specific arguments supplied after `--`.
- `fullConfig.failOnFlakyTests` exposes the effective flaky-test policy to reporters and other consumers of full configuration.
- `testInfo.errors` expands an `AggregateError` into separate error entries.
- `-G` is shorthand for `--grep-invert`.

## Recording coverage

HAR and trace recordings include WebSocket requests as of 1.61.0.
