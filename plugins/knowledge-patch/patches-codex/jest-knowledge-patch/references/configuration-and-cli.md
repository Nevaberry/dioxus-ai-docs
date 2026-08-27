# Configuration and CLI

Use this reference for test discovery, configuration composition, multi-project
settings, coverage, output files, custom runners, and integration result data.

## Default extensions and test matching

`.mts` and `.cts` are in the default `moduleFileExtensions`. Default test
matching recognizes `.mjs`, `.cjs`, `.mts`, and `.cts` as well.

A project that previously kept non-test files under names matching the default
patterns can discover extra tests after upgrading. Set an explicit `testMatch`
or `testRegex` rather than removing useful module extensions.

## Configuration file paths

The `jest` field in `package.json` can point to a configuration file instead of
holding inline configuration:

```json
{
  "jest": "./config/jest.config.js"
}
```

Resolve the path from the package containing the field and keep only one
authoritative configuration.

## Type-safe configuration

`jest-config` exports `defineConfig` and `mergeConfig` helpers for typed
declaration and composition. Use them instead of local casts when merging base
and project configuration.

The `jest` package publicly exports `GlobalConfig` and `ProjectConfig`:

```ts
import type {GlobalConfig, ProjectConfig} from 'jest';
```

Use these public types for integrations rather than recreating internal
configuration shapes.

## Project configuration

Individual project configurations accept:

- `testTimeout`
- `coverageReporters`
- `reporters`
- `verbose`
- `silent`
- `collectCoverage`
- `coverageProvider`

For example:

```js
export default {
  projects: [
    {
      testTimeout: 10_000,
      reporters: ['default'],
      coverageReporters: ['text'],
      verbose: true,
      collectCoverage: true,
    },
  ],
};
```

Project-level `verbose` and `silent` values override their global values for
that project's tests. The first three project options were added in `30.0.0`;
the remaining project options are available in `30.4.0`.

## Test discovery without execution

Use `--collect-tests` to discover and list test cases without running them:

```bash
jest --collect-tests
```

This differs from `--listTests`, which lists test files. `--listTests` can
write its output to a file:

```bash
jest --listTests --outputFile test-files.json
```

Choose the command based on whether an integration needs individual test cases
or only test-file paths.

## JSON, output files, and coverage

As of the `30.1-30.3` update, combining `--json` with `--outputFile` preserves
coverage output on the CLI. A machine-readable result file no longer requires
sacrificing the terminal coverage report.

Global coverage thresholds now continue to apply to files that do not match a
more specific glob or path threshold. For example, when both `global` and a
directory rule exist, unmatched files are still checked against `global`.
Re-run threshold checks after changing path rules; do not assume unmatched
files are exempt.

`babel-jest` can collect coverage from `.mts` and `.cts` files. If those files
are missing from coverage, inspect transforms and collection patterns before
adding a separate extension workaround.

## Worker shutdown

`workerGracefulExitTimeout` controls how long workers may exit gracefully
before Jest force-kills them. Increase it only when a worker legitimately needs
more cleanup time; also investigate leaked handles and unfinished asynchronous
work.

## Custom runners

A custom runner can receive configuration through tuple syntax:

```js
export default {
  runner: ['./runner.js', {customOption: true}],
};
```

Read the options from the runner's supported configuration contract. Preserve
the simple string form when no options are needed.

## Resolution through mapped paths

`moduleNameMapper` now applies to `require.resolve()` calls that use the
`paths` option. Test both direct resolution and `require.resolve(specifier,
{paths})` when maintaining a resolver integration.

## Test-case result timing

`TestCaseResultObject` passed to `onTestCaseResult` includes `startedAt`.
Reporters and integrations can retain the actual test-case start timestamp
instead of deriving it from completion time or suite timing.

Treat it as the test case's start value and keep existing duration handling
separate.

## Configuration checklist

- Decide whether package configuration is inline or path-based.
- Use public configuration helpers and types.
- Validate every option placed inside `projects`.
- Confirm project-level `verbose` and `silent` precedence.
- Constrain default test matching when new extensions select extra files.
- Distinguish `--collect-tests` from `--listTests`.
- Verify JSON file output and terminal coverage together.
- Exercise global coverage thresholds against unmatched files.
- Include `.mts` and `.cts` in expected coverage.
- Tune worker shutdown only after checking cleanup defects.
- Pass custom runner options with tuple syntax.
- Test mapped `require.resolve()` calls.
- Store `startedAt` without changing duration semantics.
