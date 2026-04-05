# Test Runner (`node:test`)

## Auto-Await Subtests (v24 -- Breaking Change)

In v24, the test runner automatically waits for subtests to complete. Previously, subtests had to be manually awaited.

```js
// v24+: subtests auto-awaited
test('parent', (t) => {
  t.test('child 1', () => { /* ... */ });  // no await needed
  t.test('child 2', () => { /* ... */ });  // runs sequentially after child 1
});

// Pre-v24: had to await each subtest
test('parent', async (t) => {
  await t.test('child 1', () => { /* ... */ });
  await t.test('child 2', () => { /* ... */ });
});
```

**Breaking**: `test()` and `t.test()` no longer return promises in v24+. Code that awaited them still works (awaiting undefined is a no-op), but code that stored or chained the promise will break.

## Global Setup and Teardown (v24+)

```js
import { before, after, beforeEach, afterEach } from 'node:test';

// Runs once before ALL test files
before(() => {
  console.log('Global setup');
});

// Runs once after ALL test files
after(() => {
  console.log('Global teardown');
});
```

## test:summary Event (v23+)

```js
import { run } from 'node:test';

const stream = run({ files: ['test.js'] });
stream.on('test:summary', (summary) => {
  console.log(`Total: ${summary.counts.total}, Passed: ${summary.counts.passed}`);
});
```

## test:complete Event (v22+)

Reflects actual execution order (not declaration order):

```js
stream.on('test:complete', (data) => {
  console.log(`Completed: ${data.name}`);
});
```

## Coverage via run() (v23+)

```js
import { run } from 'node:test';

const stream = run({
  files: ['test.js'],
  coverage: true,
  coverageIncludeGlobs: ['src/**/*.js'],
  coverageExcludeGlobs: ['src/vendor/**']
});
```

Glob patterns supported for coverage file filtering.

## spec Reporter Default (v23+)

The `spec` reporter is now the default reporter (replaces `tap`).

## lcov Reporter (v23+)

```js
import { lcov } from 'node:test/reporters';
// Exposed as a newable function
```

## Custom Arguments in run() (v23+)

```js
import { run } from 'node:test';

const stream = run({
  files: ['test.js'],
  execArgv: ['--experimental-vm-modules']  // Custom Node.js arguments
});
```

## Test Isolation (stable v23+)

Test isolation (running each test file in a separate process) marked as stable.

## test.suite() (v22+)

```js
import { suite, test } from 'node:test';

suite('math operations', () => {
  test('addition', () => { /* ... */ });
  test('subtraction', () => { /* ... */ });
});
```

## JUnit File Attribute (v25+)

JUnit reporter now includes file attribute support for better CI integration.

## Suite Timeout Fix (v25+)

Suite-level timeouts now work correctly.
