# Test Runner & Configuration

## test.step Improvements (1.50)

`test.step` accepts a `timeout` option and `test.step.skip()` disables a step:
```js
await test.step('upload', async () => { /* ... */ }, { timeout: 5000 });
await test.step.skip('not ready yet', async () => { /* skipped */ });
```

## TestStepInfo (1.51)

Test steps receive a `step` argument with `skip()` and `attach()`:
```js
await test.step('my step', async step => {
  step.skip(isMobile, 'not relevant on mobile');
  await step.attach('data', { body: 'content' });
});
```

## testProject.workers (1.52)

Set concurrent workers per project (global `testConfig.workers` limit still applies):
```js
{ name: 'chromium', use: { ...devices['Desktop Chrome'] }, workers: 2 }
```

## failOnFlakyTests (1.52)

```js
export default defineConfig({ failOnFlakyTests: true });
```

## captureGitInfo (1.51)

```js
// playwright.config.ts
export default defineConfig({
  captureGitInfo: { commit: true, diff: true }
});
```

## testConfig.tag (1.57)

Add a tag to all tests in a run (useful with merge-reports):
```js
export default defineConfig({ tag: '@nightly' });
```

## webServer.wait (1.57)

Wait for stdout/stderr regex before running tests. Named capture groups become env vars:
```js
export default defineConfig({
  webServer: {
    command: 'npm run start',
    wait: { stdout: /Listening on port (?<my_server_port>\d+)/ },
  },
});
// Access as process.env.MY_SERVER_PORT
```

## webServer.gracefulShutdown (1.51)

Specify kill signal instead of SIGKILL for graceful web server shutdown.

## Playwright Test Agents (1.56)

Three agent definitions for LLM-driven test creation:
- **planner** — explores app, produces Markdown test plan
- **generator** — transforms plan into Playwright Test files
- **healer** — runs tests, automatically repairs failures

```bash
npx playwright init-agents --loop=claude    # or --loop=vscode, --loop=opencode
```

Regenerate agents after each Playwright upgrade.

## updateSnapshots Behavior Change (1.50)

`updateSnapshots: 'all'` now updates ALL snapshots (not just changed ones). Use new `'changed'` value for old behavior. New `updateSourceMethod` option controls how source is updated: `'patch'` (default), `'overwrite'`, or `'3-way'`.
```bash
npx playwright test --update-snapshots=changed --update-source-method=3way
```
