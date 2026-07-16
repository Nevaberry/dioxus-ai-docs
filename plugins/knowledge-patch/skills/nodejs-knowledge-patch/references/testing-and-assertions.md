# Testing and Assertions

The built-in test runner, assertions, mocks, snapshots, discovery, coverage, and reporters.

## Contents

- [Assertions and equality](#assertions-and-equality)
- [Mocks and snapshots](#mocks-and-snapshots)
- [Coverage and reporters](#coverage-and-reporters)
- [Discovery and configuration](#discovery-and-configuration)
- [Execution and lifecycle](#execution-and-lifecycle)

## Assertions and equality

### Custom test assertions (since 23.7.0)

`t.assert.register(name, fn)` adds a reusable assertion to that test context; after `t.assert.register('isEven', value => strictEqual(value % 2, 0))`, call it as `t.assert.isEven(4)`.

### Deep-comparison semantics for promises and invalid dates (since 25.0.0)

Deep equality now treats distinct `Promise` instances as unequal even when neither exposes enumerable state, while two invalid `Date` objects compare equal.

```js
import assert from 'node:assert/strict';

const promise = Promise.resolve(1);
assert.deepStrictEqual(promise, promise);
assert.notDeepStrictEqual(Promise.resolve(1), Promise.resolve(1));
assert.deepStrictEqual(new Date(NaN), new Date(NaN));
```

### File-backed snapshot assertions (since 23.7.0)

`t.assert.fileSnapshot()` compares a value with a snapshot stored in a separate file and participates in snapshot updates, for example `await t.assert.fileSnapshot(render(), './fixtures/render.txt')`.

### Invalid Date properties in deep comparisons (since 25.4.0)

`assert.deepStrictEqual()` and `util.isDeepStrictEqual()` no longer skip custom properties when comparing invalid `Date` objects. Invalid dates still compare as dates, but differing own properties now make the deep comparison fail.

### Partial assertions for maps and array buffers (since 23.5.0)

`assert.partialDeepStrictEqual()` now performs partial comparisons for `Map` values and supports `ArrayBuffer` values, correcting gaps in the API introduced in 23.4.0.

### Partial assertions for URLs and files (since 23.7.0)

`assert.partialDeepStrictEqual()` now handles URL values and `File` prototypes, filling another comparison gap in the experimental partial assertion API.

### Partial comparisons of errors (since 23.11.0)

`assert.partialDeepStrictEqual()` now performs partial comparison for `Error` objects, extending the API's earlier partial-value support to error-specific data.

### Partial deep strict assertions (since 23.4.0)

The experimental `assert.partialDeepStrictEqual(actual, expected)` recursively requires only the values in `expected`; `actual` may contain extra object properties or collection elements.

```js
import * as assert from 'node:assert';

assert.partialDeepStrictEqual(
  { user: { id: 7, role: 'admin' }, active: true },
  { user: { id: 7 } },
);
```

### Printf-style assertion messages (since 26.0.0)

`node:assert` assertion errors can now interpolate printf-style message arguments instead of treating the supplied format as only literal text.

```js
import assert from 'node:assert/strict';

assert.strictEqual(1, 2, 'expected %s, received %s', 2, 1);
```

### Programmatic value diffs (since 23.11.0)

`node:util` now exposes the assertion formatter as `diff(actual, expected)`, allowing code to produce the same style of human-readable value diff without first causing an assertion failure.

### Prototype-optional deep equality (since 24.9.0)

`util.isDeepStrictEqual()` accepts a third `skipPrototype` boolean; passing `true` compares structure without requiring matching constructors or prototypes.

### Removed `process.assert()` (since 23.0.0)

The long-deprecated `process.assert()` API has been removed. Use `assert.ok(value)` from `node:assert` instead.

### Removed assertion APIs (since 25.0.0)

The legacy multi-argument `assert.fail(actual, expected, message, operator)` signature and `assert.CallTracker` have been removed. Use the single-message `assert.fail()` form and test-runner mocks or explicit call counting.

### Signed zero in partial strict assertions (since 23.6.0)

`assert.partialDeepStrictEqual()` now distinguishes array elements containing `0` and `-0`; comparing `[0]` with `[-0]` throws.

### Stable partial strict assertions (since 24.0.0)

`assert.partialDeepStrictEqual()` is now stable after its comparison support was filled out across the Node.js 23 releases.

### Weak collections in deep comparisons (since 23.0.0)

`assert.deepStrictEqual()` and `util.isDeepStrictEqual()` no longer treat two distinct `WeakMap` or `WeakSet` instances as equal merely because their entries cannot be enumerated. The same instance still compares equal to itself.


## Mocks and snapshots

### Consolidated module-mock exports (since 25.9.0)

`MockModuleOptions.defaultExport` and `namedExports` are replaced by one `exports` option. Its own enumerable `default` property supplies the default export, while its other own enumerable properties become named exports.

```js
t.mock.module('./dependency.mjs', {
  exports: { default: defaultMock, named: namedMock },
});
```

Existing tests can be migrated with `npx codemod @nodejs/mock-module-exports`.

### JSON module mocks (since 24.0.0)

The test runner's module-mocking support can now target JSON modules, including their default export, rather than being limited to JavaScript and TypeScript modules.

### Object-property mocks (since 24.3.0)

`MockTracker.property()` can temporarily replace an object's property and restore it with the other tracked mocks; in a test, use `t.mock.property(config, 'mode', 'test')`.

### Special characters in snapshot keys (since 23.9.0)

The test runner now accepts special characters in snapshot keys.

### Stable mock timers (since 23.1.0)

The `node:test` `MockTimers` API is now stable for mocking `Date`, `setTimeout`, `setInterval`, and `setImmediate` across globals, `node:timers`, and `node:timers/promises`; it also supports `scheduler.wait()`. For example: `mock.timers.enable({ apis: ['Date'], now: new Date('1970-01-01') })`.

### Stable test plans and snapshots (since 23.4.0)

The test runner's snapshot testing and `context.plan()` API are now stable rather than experimental.


## Coverage and reporters

### Coverage file globs (since 23.0.0)

Test coverage include and exclude options now accept glob patterns, allowing coverage scope to be selected directly from the CLI.

```console
node --test --experimental-test-coverage \
  --test-coverage-include='src/**/*.js' \
  --test-coverage-exclude='src/**/fixtures/**'
```

### JUnit test locations (since 25.0.0)

The test runner's JUnit reporter now includes file attributes for test cases, allowing CI consumers to associate reported failures with their source files.

### Source-mapped test coverage (since 23.1.0)

Test-runner coverage now requires `--enable-source-maps` when coverage should be mapped through source maps, for example `node --enable-source-maps --test --experimental-test-coverage`.

### Test files excluded from coverage (since 23.5.0)

The test runner now excludes test files from coverage results by default, changing totals for projects whose reports previously counted the tests themselves.

### Test reporter changes (since 23.0.0)

The `spec` reporter is now the default regardless of whether output is a TTY; request TAP explicitly with `node --test --test-reporter=tap` if tooling parses TAP. The built-in `lcov` reporter is also exposed as a constructible reporter via `new lcov()` from `node:test/reporters`.


## Discovery and configuration

### Changed TypeScript test discovery (since 23.10.0)

The test runner's default TypeScript glob has changed, so invocations that rely on automatic discovery may select a different set of TypeScript tests. Pass the intended test paths explicitly when the selection must remain fixed.

### Per-run test environments (since 24.14.0)

The `run()` function from `node:test` now accepts an `env` option for the environment passed to test processes; it defaults to the current process environment.

```js
import { run } from 'node:test';

run({
  files: ['./test/example.test.js'],
  env: { ...process.env, FEATURE_FLAG: 'enabled' },
});
```

### Per-test timeouts (since 24.0.0)

`--test-timeout` now applies its timeout to each individual test instead of treating it as one aggregate timeout for a larger test run.

### Restored TypeScript test discovery (since 24.1.0)

The test runner reverts the default TypeScript glob change introduced in 23.10.0, restoring the earlier discovery behavior. Pass test paths explicitly if a project depended on the newer selection.

### Stable test isolation (since 23.6.0)

Test-runner isolation and its CLI controls are now stable rather than experimental.


## Execution and lifecycle

### Expected-failure test cases (since 25.5.0)

The built-in test runner now supports declaring that a test case is expected to fail, distinguishing an intentional negative case from an unexpected suite failure.

### Global test setup and teardown (since 24.0.0)

The test runner can load a module with `--test-global-setup`; that module may export `globalSetup` and `globalTeardown` hooks that run around the complete test run.

```js
// test/lifecycle.mjs
export async function globalSetup() {
  // allocate shared test resources
}

export async function globalTeardown() {
  // release shared test resources
}
```

```console
node --test --test-global-setup=./test/lifecycle.mjs
```

### Programmatic test-runner controls (since 23.0.0)

`node:test`'s `run()` can enable coverage, set a working directory, and pass custom `argv` values to test files. Its returned stream also emits a `test:summary` event for end-of-run reporting.

```js
import { run } from 'node:test';

const tests = run({
  files: ['./test.mjs'],
  argv: ['--fixture=small'],
  cwd: process.cwd(),
  coverage: true,
});
tests.on('test:summary', (summary) => console.log(summary));
```

### Rerunning failed tests (since 24.7.0)

The test runner adds an option to rerun only failed tests, reducing repeated work while iterating on a failing suite.

### Restored test completion promises (since 24.3.0)

The Node 24.0 return-value removal has been reverted: `test()` and `t.test()` once again return completion promises. The runner still automatically waits for subtests, while callers can `await` these promises when later work must be sequenced after completion.

### Test and subtest completion (since 24.0.0)

`test()` and `t.test()` no longer return completion promises. The runner automatically waits for started subtests, so callers should neither `await` these calls nor chain work from their return values.

```js
import test from 'node:test';

test('parent', (t) => {
  t.test('child', async () => {
    // asynchronous child work
  });
});
```

### Test-runner failure behavior (since 25.9.0)

Suite-level errors now set a non-zero process exit code, and the test runner is compatible with fake timers.

### TypeScript test integration (since 23.0.0)

When built-in TypeScript support is available, the test runner's default discovery also recognizes `.ts`, `.cts`, and `.mts` test files, and module mocks can target TypeScript modules. `process.features.typescript` can be used as the feature probe; builds without Amaro report no TypeScript support.

### Waiting for test conditions (since 23.7.0)

`TestContext.waitFor()` repeatedly evaluates a condition until it becomes truthy or times out; use `await t.waitFor(() => server.listening)` instead of implementing a polling loop.
