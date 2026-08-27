# Reporters and Integrations

## Migrate custom reporters

The public reporter lifecycle was redesigned in 3.0.0. Review reporters built around the previous `onTaskUpdate` callback instead of assuming the old lifecycle still applies.

Test annotations are delivered through `onTestAnnotate`. The default terminal reporter prints them only for failed tests; `verbose` is the only terminal reporter that also prints annotations for passing tests. HTML and UI annotations require a call site in a test file.

JUnit, TAP, and TAP-flat retain annotation type and message but discard attachments. The GitHub Actions reporter maps `notice`, `warning`, and `error`; all other annotation types are treated as notices.

## Choose current built-in reporters

The `basic` reporter was removed in 4.0.0. The closest replacement is `default` with its summary disabled:

```ts
export default defineConfig({
  test: {
    reporters: [['default', { summary: false }]],
  },
})
```

The default reporter renders a test tree only for a single test file. Use `tree` to render it consistently. The `verbose` reporter prints each test as it finishes in every environment.

## Configure GitHub Actions summaries

In 4.1.0, the `github-actions` reporter writes test statistics and a flaky-test summary to `$GITHUB_STEP_SUMMARY` by default when running in GitHub Actions. Disable or redirect it through `jobSummary`:

```ts
export default defineConfig({
  test: {
    reporters: [[
      'github-actions',
      { jobSummary: { enabled: false } },
    ]],
  },
})
```

Set `jobSummary.outputPath` when the summary should be written elsewhere.

## Use failure-only output

The `agent` reporter added in 4.1.0 prints only failures and their errors. It suppresses passing output and logs from passing tests. Vitest selects it automatically in detected automated coding environments unless custom reporters are configured; set `AI_AGENT` for explicit detection or select it manually:

```ts
export default defineConfig({
  test: { reporters: ['agent'] },
})
```

## Update editor integration settings

As of 4.1.0, the official VS Code extension does not keep Vitest running in the background unless continuous run is enabled manually or through `watchOnStartup`. The old `maximumConfigs` option is removed.

The extension adds Run Related Tests and Toggle Continuous Run actions, supports the Deno runtime, and provides a Debug Test action for browser tests.

## Move from the early Node API

The `vitest/node` programmatic API was redesigned in 3.0.0 and was still marked experimental in that release, with removal of that tag planned for the following minor. Integrations must not assume the pre-3 experimental shape.

The 4.0.0 public API added:

- `experimental_parseSpecifications` to parse specifications without running them.
- `watcher` controls for runs when the default watcher is disabled.
- Dynamic `enableCoverage` and `disableCoverage` methods.
- `getSeed` and `getGlobalTestNamePattern` accessors.
- `waitForTestRunEnd` for completion synchronization.

## Collect and run tests programmatically

Vitest 4.1.0 added static collection through `vitest list`, avoiding test-file execution solely for discovery.

The public API also added specification filters to `createSpecification`, `runTestFiles` as an alternative to `runTestSpecifications`, `allowWrite` and `allowExec` options, and `toTestSpecification` on reported tasks.

Tag-aware tooling can pass `tagsFilter` to `startVitest` or `createVitest`, and `testTagsFilter` to `createSpecification`; see [Test APIs](test-apis.md).
