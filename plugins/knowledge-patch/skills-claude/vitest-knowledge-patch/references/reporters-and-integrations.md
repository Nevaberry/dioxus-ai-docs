# Reporters and Integrations

## Migrate custom reporters

Vitest 3.0.0 redesigned the public reporter lifecycle configured through `reporters`. Review reporters built around the earlier `onTaskUpdate` API instead of assuming that lifecycle still applies.

Vitest 4.0.0 removed the `basic` reporter. Replace it with `default` and disable the summary for the closest behavior:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    reporters: [['default', { summary: false }]],
  },
})
```

The default reporter renders a test tree only for a single test file. Use `tree` to always render the tree. `verbose` prints every test as it completes in all environments.

## Write GitHub Actions summaries

Since 4.1.0, the `github-actions` reporter writes test statistics and flaky-test information to `$GITHUB_STEP_SUMMARY` by default when running in GitHub Actions. Disable it with `jobSummary.enabled` or redirect it with `jobSummary.outputPath`:

```ts
export default defineConfig({
  test: {
    reporters: [['github-actions', {
      jobSummary: { enabled: false },
    }]],
  },
})
```

## Use failure-only agent output

The `agent` reporter, added in 4.1.0, prints only failures and their errors. It suppresses passing output and passing-test logs. Vitest chooses it automatically in detected coding-agent environments unless custom reporters are configured. Set `AI_AGENT` for explicit detection or add `agent` manually:

```ts
export default defineConfig({
  test: { reporters: ['agent'] },
})
```

## Update Node API integrations

The `vitest/node` API was redesigned in 3.0.0. It was still experimental in that release, with removal of the experimental designation planned for the next minor, so integrations must not assume the pre-3 API shape.

Vitest 4.0.0 added these advanced APIs:

- `experimental_parseSpecifications` parses specifications without running them.
- `watcher` controls runs when the default watcher is disabled.
- `enableCoverage` and `disableCoverage` toggle coverage dynamically.
- `getSeed` and `getGlobalTestNamePattern` expose active run settings.
- `waitForTestRunEnd` waits for run completion.

Since 4.1.0, `vitest list` collects tests statically instead of executing files merely to discover them. The public API also provides:

- specification filters for `createSpecification`;
- `runTestFiles` as an alternative to `runTestSpecifications`;
- `allowWrite` and `allowExec` API options;
- `toTestSpecification` on reported tasks.

## Integrate annotations

Custom reporters receive test annotations through `onTestAnnotate`. Reporter-specific behavior for attachments and message types is detailed in [Test APIs](test-apis.md).

## Update the editor extension

Since 4.1.0, the official VS Code extension does not keep Vitest running in the background unless continuous run is enabled manually or through `watchOnStartup`. The removed `maximumConfigs` option must not remain in settings.

The extension adds Run Related Tests and Toggle Continuous Run actions, supports the Deno runtime, and exposes a Debug Test action for browser tests.
