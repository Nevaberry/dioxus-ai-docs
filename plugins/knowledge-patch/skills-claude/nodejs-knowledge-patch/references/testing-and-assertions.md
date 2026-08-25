# Testing and Assertions

Use this reference for testing and assertions work.

## Changed TypeScript test discovery (`23.10.0`)

The test runner changes its default TypeScript glob in this release. Projects relying on implicit TypeScript test discovery should verify the files selected after upgrading.

## Coverage for unexecuted files (`26.7.0`)

`--test-coverage-include-all` lets test coverage include eligible source files even when the tests never load them, making completely untested files visible in coverage results.

```sh
node --test --experimental-test-coverage --test-coverage-include-all
```

## Custom test assertions (`23.7.0`)

`t.assert.register()` adds a named assertion to the test context's assertion object.

```js
t.assert.register('isEven', value => assert.equal(value % 2, 0));
t.assert.isEven(4);
```

## Deep comparisons of promises and invalid dates (`25.0.0`)

Deep equality now compares promises by identity, so two distinct promises fail comparison even if they settle identically. Two invalid `Date` objects now compare equal; both changes affect assertions and `util.isDeepStrictEqual()`.

```js
import assert from 'node:assert/strict';

assert.deepStrictEqual(Promise.resolve(1), Promise.resolve(1)); // throws
assert.deepStrictEqual(new Date(NaN), new Date(NaN)); // passes
```

## Expected-failure tests (`25.5.0`)

The test runner can mark a test case as expected to fail, so negative tests can distinguish an anticipated failure from an unexpected regression.

## Failed-test reruns (`24.7.0`)

The test runner can persist failure state and rerun only tests that failed in the preceding run.

```sh
node --test --test-rerun-failures=.test-failures
```

## Failed-test reruns preserve failures (`24.18.0`)

`--test-rerun-failures` no longer swallows failures encountered during a retry, so unsuccessful reruns remain visible in the test result and process status.

## File-backed test snapshots (`23.7.0`)

Snapshot testing is stable, and `t.assert.fileSnapshot()` compares a value with snapshot content stored in a separate file.

```js
t.assert.fileSnapshot(rendered, './fixtures/rendered.txt');
```

## Global test setup and per-test timeouts (`24.0.0`)

The test runner adds global setup and teardown, supports mocking JSON modules, and applies `--test-timeout` to each test rather than the whole run.

```sh
node --test --test-global-setup=./test/setup.mjs --test-timeout=5000
```

## Invalid dates retain own-property semantics (`25.4.0`)

Deep comparisons still treat two invalid `Date` values as equal, but no longer skip their own properties. Invalid dates with different attached state now compare unequal.

```js
import assert from 'node:assert/strict';

const left = Object.assign(new Date(NaN), { zone: 'UTC' });
const right = Object.assign(new Date(NaN), { zone: 'local' });
assert.deepStrictEqual(left, right); // throws
```

## Mock timers are stable (`23.1.0`)

The `node:test` `MockTimers` API is now stable and can mock `Date` plus the major timers from globals, `node:timers`, and `node:timers/promises`. Mock timers also support `scheduler.wait()`.

```js
import { mock } from 'node:test';

mock.timers.enable({
  apis: ['Date'],
  now: new Date('1970-01-01'),
});
```

## Object property mocking (`24.3.0`)

The test runner can temporarily replace an object's property with `t.mock.property()` and restore it during mock cleanup.

```js
import assert from 'node:assert/strict';
import { test } from 'node:test';

test('uses a mocked property', (t) => {
  const config = { mode: 'production' };
  t.mock.property(config, 'mode', 'test');
  assert.equal(config.mode, 'test');
});
```

## Partial deep comparisons distinguish signed zero (`23.6.0`)

`assert.partialDeepStrictEqual()` now rejects a comparison between `[0]` and `[-0]`.

```js
import assert from 'node:assert/strict';

assert.partialDeepStrictEqual([0], [-0]); // throws
```

## Partial deep comparisons for Maps and ArrayBuffers (`23.5.0`)

`assert.partialDeepStrictEqual()` now performs partial comparison for `Map` values and supports `ArrayBuffer` values.

## Per-run test environments (`24.14.0`)

The programmatic `run()` function from `node:test` now accepts an `env` option for the test environment.

```js
import { run } from 'node:test';

run({
  env: { ...process.env, FEATURE_FLAG: 'enabled' },
});
```

## Permission and test JSON configuration (`25.4.0`)

JSON configuration files now support Permission Model and test-runner settings. The test namespace is `test`, not `testRunner`, and declaring a namespace implicitly enables its corresponding mode.

## Printf-style assertion messages (`26.0.0`)

Assertion errors can interpolate additional arguments into printf-style message placeholders.

```js
import assert from 'node:assert/strict';

assert.strictEqual(1, 2, 'expected %s, received %s', 2, 1);
```

## Programmatic test-run controls (`23.0.0`)

`node:test`'s `run()` API now supports custom arguments, coverage, and a `cwd` option, and its stream emits a `test:summary` event. Coverage-file selection supports glob matching.

## Prototype-independent deep equality (`24.9.0`)

`util.isDeepStrictEqual()` accepts a third `skipPrototype` boolean. Passing `true` compares object structure without requiring the same constructors or prototypes.

```js
import { isDeepStrictEqual } from 'node:util';

class Point { constructor(x) { this.x = x; } }
class Coordinate { constructor(x) { this.x = x; } }
isDeepStrictEqual(new Point(1), new Coordinate(1), true); // true
```

## Public assertion-style diffs (`23.11.0`)

`util.diff()` exposes the value-diff formatter used by assertion errors, allowing custom checks and test tools to produce the same kind of diagnostics.

```js
import { diff } from 'node:util';

console.log(diff({ answer: 41 }, { answer: 42 }));
```

## Richer test reporting and TypeScript coverage (`24.19.0`)

Test events carrying a `testId` now also carry `parentId`, and JUnit `testsuites` output includes a timestamp. Coverage also ignores TypeScript lines erased during type stripping, avoiding uncovered-line results for code that never reaches JavaScript.

## Source-mapped test coverage (`23.1.0`)

Source-map coverage in the test runner now requires launching Node with `--enable-source-maps`.

## Test completion promises are restored (`24.3.0`)

Node.js 24.3 reverses the 24.0 change: `test()` and `t.test()` return completion promises again, and automatic subtest waiting is reverted. Await subtests when their completion must be sequenced.

```js
test('parent', async (t) => {
  await t.test('child', () => {});
});
```

## Test coverage excludes tests by default (`23.5.0`)

The test runner now excludes test files from coverage results by default.

## Test discovery and reporters (`23.0.0`)

The test runner always defaults to the `spec` reporter, and the `lcov` reporter is exposed as a constructible function. Default test discovery now includes TypeScript files, and module mocking supports TypeScript modules.

## Test functions no longer return completion promises (`24.0.0`)

In Node.js 24.0, `test()` and `t.test()` no longer return promises; the runner automatically waits for subtests. Code must not use those return values to detect completion.

## Test isolation is stable (`23.6.0`)

The test runner's isolation support and its CLI surface are now stable rather than experimental.

## Test logging and entry-file metadata (`26.7.0`)

`TestContext.log()` emits a `test:log` event, and `TestStream` events now report `entryFile`. Custom reporters can retain test-authored logs and associate events with their originating entry file.

```js
import { test } from 'node:test';

test('connects', (context) => {
  context.log('starting connection');
});
```

## Test tags and ambient test contexts (`24.19.0`)

Tests accept a `tags` option and the runner can filter by tag name. `getTestContext()` exposes the active test context to helper code without requiring callers to pass it through explicitly.

```js
import { getTestContext, test } from 'node:test';

test('fast path', { tags: ['unit'] }, () => {
  getTestContext().diagnostic('running unit test');
});
```

## Test-runner suite failures (`25.9.0`)

Errors that occur at the test-suite level now set a non-zero process exit code, so CI correctly treats them as failures even when no individual test case reports the error.

## TypeScript test-discovery rollback (`24.1.0`)

This release reverts the default TypeScript test glob change introduced in 23.10.0, restoring the earlier implicit discovery behavior. Projects that adapted to the intervening pattern should re-check which TypeScript tests run by default.

## Waiting for test conditions (`23.7.0`)

`TestContext.prototype.waitFor()` repeatedly checks a condition until it succeeds or times out.

```js
await t.waitFor(() => server.ready, { timeout: 1_000 });
```

## Weak collections compare by identity (`23.0.0`)

Deep strict comparisons now treat distinct `WeakMap` and `WeakSet` instances as unequal; only the same instance compares equal. This affects both assertions and `util.isDeepStrictEqual()`.

```js
import assert from 'node:assert/strict';

const weak = new WeakMap();
assert.deepStrictEqual(weak, weak); // passes
assert.deepStrictEqual(weak, new WeakMap()); // throws
```
