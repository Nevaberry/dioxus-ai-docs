# Reporters and Integrations

Relevant versioned source batches: `3.0.0`, `3.2.0`, `4.0.0`, and `4.1.0`.

## Contents

- [Migrate custom reporter lifecycles](#migrate-custom-reporter-lifecycles)
- [Choose a built-in terminal reporter](#choose-a-built-in-terminal-reporter)
- [Consume test annotations](#consume-test-annotations)
- [Configure GitHub Actions job summaries](#configure-github-actions-job-summaries)
- [Use the failure-only agent reporter](#use-the-failure-only-agent-reporter)
- [Control runs with the public API](#control-runs-with-the-public-api)
- [Collect and create specifications programmatically](#collect-and-create-specifications-programmatically)
- [Integrate custom coverage output](#integrate-custom-coverage-output)
- [Update VS Code extension settings and commands](#update-vs-code-extension-settings-and-commands)
- [Avoid Vite type skew in integrations](#avoid-vite-type-skew-in-integrations)

## Migrate custom reporter lifecycles

The public reporter API configured through `reporters` was redesigned around a new lifecycle. Review custom reporters built around the previous `onTaskUpdate` API instead of assuming that callback remains the central update path.

The programmatic API exported from `vitest/node` was also redesigned. In `3.0.0` the replacement API was still marked experimental, with removal of that tag planned for a subsequent minor. Integrations should use the current surface rather than relying on the earlier experimental shape.

## Choose a built-in terminal reporter

The `basic` reporter was removed. Replace it with the default reporter and disable the summary when matching the old concise output:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    reporters: [
      ['default', { summary: false }],
    ],
  },
})
```

Current tree behavior differs by reporter:

- `default` renders a test tree only when the run contains a single test file.
- `tree` always renders the test tree.
- `verbose` prints every test as it finishes in all environments.

## Consume test annotations

Custom messages and attachments attached to a test are available to reporters through `onTestAnnotate`. They also appear in the UI and in HTML, JUnit, TAP, and GitHub Actions output, with format-specific limitations.

Terminal behavior is intentionally selective:

- The default reporter prints annotations only for failed tests.
- `verbose` is the only terminal reporter that also prints annotations for passing tests.
- Annotations related to a failed test are printed by the CLI.

Other reporter behavior:

- HTML and UI annotations need a call site in a test file.
- JUnit, TAP, and TAP-flat discard attachments but preserve annotation type and message.
- GitHub Actions maps `notice`, `warning`, and `error`; every other annotation type is emitted as a notice.

Trace archives and browser failure artifacts can also arrive as annotations or artifact attachments. See [Browser Mode](browser-mode.md) for their creation rules.

## Configure GitHub Actions job summaries

The `github-actions` reporter writes test statistics and a flaky-test summary to `$GITHUB_STEP_SUMMARY` by default when running in GitHub Actions.

Disable the summary or redirect it through `jobSummary`:

```ts
export default defineConfig({
  test: {
    reporters: [[
      'github-actions',
      {
        jobSummary: {
          enabled: false,
        },
      },
    ]],
  },
})
```

Set `jobSummary.outputPath` instead when the summary should be written somewhere other than `$GITHUB_STEP_SUMMARY`.

## Use the failure-only agent reporter

The `agent` reporter emits failures and their errors while suppressing passing output and logs from passing tests:

```ts
export default defineConfig({
  test: {
    reporters: ['agent'],
  },
})
```

Vitest selects it automatically in detected coding-agent environments unless custom reporters are configured. Set the `AI_AGENT` environment variable for explicit detection, or list `agent` manually to make the choice deterministic.

## Control runs with the public API

The redesigned public Vitest API includes methods and properties for collection, watching, coverage, and run state:

- `experimental_parseSpecifications` parses specifications without running them.
- `watcher` controls runs when the default watcher is disabled.
- `enableCoverage` turns coverage on dynamically.
- `disableCoverage` turns coverage off dynamically.
- `getSeed` returns the active sequencing seed.
- `getGlobalTestNamePattern` returns the global test-name filter.
- `waitForTestRunEnd` waits for the active run to finish.

Use the exact current names; do not substitute methods from the earlier Node API.

## Collect and create specifications programmatically

`vitest list` can collect tests statically rather than executing every test file merely to discover its tests:

```sh
vitest list
```

The programmatic API also provides:

- Specification filters accepted by `createSpecification`.
- `runTestFiles` as an alternative to `runTestSpecifications`.
- `allowWrite` and `allowExec` API options for integrations that need those capabilities.
- `toTestSpecification` on reported tasks.

Tag-aware programmatic runs use `tagsFilter` with `startVitest` or `createVitest`; `createSpecification` uses `testTagsFilter`. These are documented with expression rules in [Test APIs](test-apis.md).

## Integrate custom coverage output

The public API can toggle coverage with `enableCoverage` and `disableCoverage`. Configuration can also load custom reporters and providers, while custom coverage HTML can be integrated with Vitest's UI and HTML reporter. See [Projects and coverage](projects-and-coverage.md) for the module contracts and root-only configuration rules.

## Update VS Code extension settings and commands

The official extension does not keep a Vitest process running in the background unless continuous run is enabled manually or through `watchOnStartup`.

Migration and capability notes:

- The old `maximumConfigs` option was removed.
- Run Related Tests is available as an action.
- Toggle Continuous Run is available as an action.
- Browser tests have a Debug Test action.
- The Deno runtime is supported.

Enable `watchOnStartup` only when a persistent process is wanted; otherwise the extension starts work on demand.

## Avoid Vite type skew in integrations

Vitest supports Vite 8 and reuses the project's installed `vite` package when possible. Editor and Node API integrations should use types from the resolved project toolchain so a second Vite copy does not create configuration type mismatches.
