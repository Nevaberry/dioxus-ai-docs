# Testing and Assertions

## Running and discovering tests

- In 23.0.0, `node:test` `run()` accepts custom arguments, coverage, and `cwd`.
  Its stream emits `test:summary`, and coverage-file selection supports globs.
- Also in 23.0.0, the default reporter is always `spec`, `lcov` is exposed as a
  constructible reporter, default discovery includes TypeScript files, and
  module mocking supports TypeScript modules.
- In 23.5.0, test files are excluded from coverage results by default.
- In 23.6.0, test isolation and its CLI surface are stable.
- In 23.10.0, the implicit TypeScript test glob changes. In 24.1.0, that change
  is reverted to the earlier discovery behavior. Projects adapted to the
  intervening pattern should verify the selected files.
- In 24.0.0, the runner adds global setup and teardown, JSON-module mocking,
  and per-test `--test-timeout` rather than a timeout for the entire run.
- In 24.14.0, programmatic `run()` accepts `env` for the test environment.

## Completion and suite failure behavior

- In 24.0.0, `test()` and `t.test()` stop returning completion promises and the
  runner automatically waits for subtests. In 24.3.0, this is reversed:
  completion promises return and automatic subtest waiting is removed. Await a
  subtest when sequencing depends on its completion.
- In 25.9.0, test-suite-level errors set a non-zero process exit code even when
  no individual test case reports the error.

## Timers, waiting, and test context

- In 23.1.0, `MockTimers` is stable and can mock `Date` plus major timers from
  globals, `node:timers`, and `node:timers/promises`; it also supports
  `scheduler.wait()`.
- In 23.7.0, `TestContext.prototype.waitFor()` repeatedly checks a condition
  until success or timeout.
- In 24.19.0, tests accept `tags` and the runner can filter by tag. The
  `getTestContext()` helper exposes the ambient active context to helper code.

## Mocks, snapshots, and expected failures

- In 23.7.0, snapshot testing is stable. `t.assert.fileSnapshot()` compares a
  value with snapshot content in a separate file, and `t.assert.register()`
  installs a named custom assertion on the context.
- In 24.3.0, `t.mock.property()` temporarily replaces an object property and
  restores it during mock cleanup.
- In 25.5.0, tests can be marked as expected failures, distinguishing an
  anticipated negative result from an unexpected regression.
- In 25.9.0, `MockModuleOptions.defaultExport` and `namedExports` are replaced
  by one `exports` object. Its own `default` property is the default export and
  other own enumerable properties are named exports. Existing tests can migrate
  with `npx codemod @nodejs/mock-module-exports`.

## Failed-test reruns

- In 24.7.0, the runner can persist failure state and rerun only tests that
  failed previously with `--test-rerun-failures=<file>`.
- In 24.18.0, failed reruns are no longer swallowed; retry failures remain in
  the test result and process status.

## Coverage and reporting

- In 23.1.0, source-mapped test coverage requires launching with
  `--enable-source-maps`.
- In 24.19.0, test events with `testId` also have `parentId`, JUnit
  `testsuites` output includes a timestamp, and coverage ignores TypeScript
  lines erased during type stripping.
- In 26.7.0, `--test-coverage-include-all` adds eligible files never loaded by
  tests to coverage results. `TestContext.log()` emits `test:log`, and test
  stream events expose `entryFile` so reporters can retain logs and associate
  events with their entry file.

## Deep and partial comparison behavior

- In 23.0.0, deep strict comparison treats distinct `WeakMap` and `WeakSet`
  instances as unequal; only identical instances compare equal.
- In 23.3.0, an `Error` lacking `cause` differs from one whose own `cause` is
  explicitly `undefined`.
- In 23.5.0, `assert.partialDeepStrictEqual()` supports partial comparison of
  `Map` and `ArrayBuffer` values.
- In 23.6.0, partial deep strict comparison distinguishes signed zero and
  rejects `[0]` against `[-0]`.
- In 23.7.0, partial deep strict comparison handles `URL` and `File` prototypes
  correctly.
- In 23.11.0, partial deep strict comparison supports `Error` values, allowing
  expected error details to match a subset of actual details.
- In 24.9.0, `util.isDeepStrictEqual(value, expected, true)` skips constructor
  and prototype equality while comparing structure.
- In 25.0.0, deep comparison treats distinct promises as unequal and two
  invalid `Date` values as equal.
- In 25.4.0, invalid-date equality also compares own properties.
- In 24.13.0, 24.13.1 fixes deep comparison of `Map` and `Set` values containing
  mixed types.
- In 24.14.0, loose `assert.deepEqual()` correctly handles arrays containing
  `undefined` and `null`; choose `deepStrictEqual()` to keep them distinct.

## Assertion messages and diffs

- In 23.11.0, `util.diff()` exposes assertion-style value diff formatting for
  custom assertions and test tools.
- In 25.0.0, multi-argument `assert.fail()` is end-of-life; use a single
  message.
- In 26.0.0, assertion errors interpolate additional arguments into printf-
  style message placeholders.
