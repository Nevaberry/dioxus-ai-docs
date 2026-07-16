# Testing

Use this reference for test execution, discovery, concurrency, assertions, snapshots, mocks, timers, reporting, coverage, and compatibility APIs.

Entries are grouped by developer task. When entries describe evolving behavior, the later attribution supersedes earlier defaults or limitations.

## Running, discovery, isolation, and concurrency

### Unhandled test failures *(1.2-guide)*

`bun test` now fails the run for an uncaught exception or rejected promise that occurs between test cases. Such asynchronous errors no longer pass silently.

### Test timeouts terminate synchronous child processes *(since 1.2.10)*

`bun:test` timeouts now apply correctly while a test is blocked in `Bun.spawnSync()`, terminating the over-time child process instead of leaving the test stuck.

```ts
import { test } from "bun:test";

test("times out a synchronous child", { timeout: 1_000 }, () => {
  Bun.spawnSync(["sleep", "10"]);
});
```

### Empty filtered test runs fail *(since 1.2.18)*

`bun test -t <regex>` now fails when no tests match and no longer fills the output with skipped tests. Explicit `test.skip` and `test.todo` behavior is unchanged.

### Concurrent, randomized, and CI-safe tests *(since 1.2.23)*

`test.concurrent` and `describe.concurrent` run asynchronous tests within a file concurrently; the default limit is 20 and `--max-concurrency` changes it. `[test].concurrentTestGlob` makes every test in matching files concurrent, while `test.serial` opts individual tests out.

```toml
[test]
concurrentTestGlob = ["**/integration/**/*.test.ts"]
```

Concurrent tests cannot use `expect.assertions()`, `expect.hasAssertions()`, or file snapshots, although inline snapshots remain supported; `beforeAll` and `afterAll` hooks stay serial. Test modifiers can now be chained, such as `test.concurrent.each(...)` or `test.failing.each(...)`.

`bun test --randomize` prints a seed, and `bun test --seed 12345` both enables randomization and reproduces that order. With `CI=true`, `test.only()` and creating a new snapshot without `--update-snapshots` are errors; set `CI=false` to disable those safeguards.

### Successful empty test runs *(since 1.3.1)*

`bun test --pass-with-no-tests` exits with status 0 when no tests exist or active filters match none, while real test failures remain nonzero. Without the flag, an empty run still exits with status 1.

```sh
bun test --pass-with-no-tests
```

### Test retries and repetitions *(since 1.3.3)*

The third argument to `test()` accepts `retry` and `repeats`: a retried test passes if any attempted run passes, while a repeated test fails if any run fails.

```ts
test("eventually succeeds", runUnstableCheck, { retry: 3 });
test("remains stable", runStabilityCheck, { repeats: 20 });
```

### Global test retries *(since 1.3.10)*

`bun test --retry N` sets a default retry count for all tests, and `[test] retry = N` provides the same default in `bunfig.toml`; a test's own `{ retry: N }` still takes precedence. JUnit output records each attempted run as a separate test case.

```sh
bun test --retry 3
```

### Test discovery path exclusions *(since 1.3.11)*

`bun test` can exclude matching files and prune matching directories with repeatable `--path-ignore-patterns` flags or `test.pathIgnorePatterns` in `bunfig.toml`. Command-line patterns replace the configured list rather than merging with it.

```toml
[test]
pathIgnorePatterns = ["vendor/**", "fixtures/**", "**/test-data/**"]
```

### Isolated and parallel test files *(since 1.3.13)*

`bun test --isolate` runs each test file with a fresh global in the same process, draining microtasks and cleaning up sockets, timers, and subprocesses between files. `--parallel[=N]` distributes files across worker processes (defaulting to the CPU count), implies isolation, and sets `JEST_WORKER_ID` and `BUN_TEST_WORKER_ID` in each worker.

```sh
bun test --isolate ./tests
bun test --parallel=8 ./tests
```

### Deterministic test sharding *(since 1.3.13)*

`bun test --shard=M/N` sorts test paths and assigns them round-robin to a 1-based CI shard; an empty shard exits successfully. Sharding happens after `--changed` filtering and before `--randomize` shuffles the selected shard.

```sh
bun test --shard=2/3
```

### Git-aware changed tests *(since 1.3.13)*

`bun test --changed[=ref]` builds the tests' import graph and runs only files that transitively depend on Git changes; without a ref it includes staged, unstaged, and untracked changes. With `--watch`, every local source edit triggers a restart and the Git-based selection is recomputed.

```sh
bun test --changed
bun test --changed=main --watch
```

## Assertions, snapshots, and parameterized cases

### Indented inline snapshots *(since 1.2.1)*

When `bun test` updates Jest-style inline snapshots, it now automatically detects and preserves their indentation.

### Stricter deep equality *(since 1.2.2)*

`Bun.deepEquals()` no longer treats objects as equal merely because their indexed properties or prototypes match when their internal types differ. Because `bun:test`'s `toEqual()` uses the same comparison, tests that depended on the looser behavior may now fail.

```ts
Bun.deepEquals({ 0: 5, 1: 6, 2: 7 }, new Uint8Array([5, 6, 7])); // false
```

### Named fields in parameterized tests *(since 1.2.19)*

Object cases passed to `test.each` can interpolate `$field` and nested `$object.field` paths in test titles.

```ts
import { expect, test } from "bun:test";

test.each([{ user: { name: "Alice" }, value: 2 }])(
  "$user.name has $value items",
  ({ value }) => expect(value).toBe(2),
);
```

### Compile-time type assertions in `bun:test` *(since 1.2.20)*

`expectTypeOf` provides a Vitest-compatible API for asserting TypeScript types. Its assertions are runtime no-ops, so type tests must also be checked with `bunx tsc --noEmit`.

```ts
import { expectTypeOf } from "bun:test";
expectTypeOf((a: number, b: number) => a + b).returns.toBeNumber();
```

### Exact repeated-value assertions *(since 1.2.20)*

`toIncludeRepeated` now requires exactly the specified number of occurrences rather than accepting any greater count, aligning its behavior with Jest.

## Mocks and fake timers

### Clearing all mock state *(since 1.2.20)*

`mock.clearAllMocks()` clears the recorded calls and results of every `bun:test` mock without restoring or replacing their implementations.

### Global Vitest-compatible `vi` *(since 1.3.1)*

Test files now receive a typed `vi` global without an import, providing Vitest-compatible APIs such as `vi.fn()`, `vi.mock()`, and `vi.spyOn()`.

```ts
const fn = vi.fn();
expect(fn).not.toHaveBeenCalled();
```

### Fake timers in `bun:test` *(since 1.3.4)*

The `jest` object can replace real timers, optionally starting at a supplied `now`, then advance to a duration or the next timer, run all or only currently pending timers, count or clear timers, and restore real time. The corresponding methods are `useFakeTimers()`, `advanceTimersByTime()`, `advanceTimersToNextTimer()`, `runAllTimers()`, `runOnlyPendingTimers()`, `getTimerCount()`, `clearAllTimers()`, `isFakeTimers()`, and `useRealTimers()`.

```ts
import { expect, jest, test } from "bun:test";

test("delayed work", () => {
  jest.useFakeTimers({ now: new Date("2025-12-06") });
  let called = false;
  setTimeout(() => { called = true; }, 1_000);
  jest.advanceTimersByTime(1_000);
  expect(called).toBe(true);
  jest.useRealTimers();
});
```

### Automatically disposable test mocks *(since 1.3.9)*

`mock()` and `spyOn()` implement `Symbol.dispose` as an alias for `mockRestore()`, so a `using` declaration restores a mock automatically when its scope ends.

```ts
import { expect, spyOn } from "bun:test";

const object = { value: () => "original" };
{
  using spy = spyOn(object, "value").mockReturnValue("mocked");
  expect(object.value()).toBe("mocked");
}
expect(object.value()).toBe("original");
```

## Reporting, coverage, and editor integration

### JUnit and LCOV test output *(1.2-guide)*

`bun test` can emit JUnit XML and LCOV coverage for CI systems. The same behavior is configurable through `[test.reporter]` and `[test]` in `bunfig.toml`.

```sh
bun test --reporter=junit --reporter-outfile=junit.xml
bun test --coverage --coverage-reporter=lcov --coverage-dir=coverage
```

### VS Code Test Explorer integration *(since 1.2.19)*

The official Bun VS Code extension can now use the native Test Explorer, with `bun test` reporting discovery, progress, and results to it.

### Coverage path exclusions *(since 1.2.19)*

`test.coveragePathIgnorePatterns` in `bun.toml` accepts one glob or an array; matching files are omitted from coverage reports.

```toml
[test]
coveragePathIgnorePatterns = ["**/__tests__/**", "**/test-fixtures.ts"]
```

### Failure-only test output *(since 1.3.1)*

`bun test --only-failures` suppresses passing-test details while retaining failures and the final totals. Persist the behavior as `onlyFailures = true` under `[test]` in `bunfig.toml`.

### Test output elision outside terminals *(since 1.3.12)*

`bun test --elide-lines` is now silently ignored when standard output is not a TTY, so the same test command can run interactively and in CI or Git hooks.

## Lifecycle and compatibility APIs

### Jest-compatible test APIs *(1.2-guide)*

Inline snapshots now use `toMatchInlineSnapshot()` and are written with `bun test -u`; `test.only()` works without the old `--only` requirement. New assertion support includes key/value containment matchers, `toHaveReturned*`, a second `expect(value, message)` argument, and module-scoped timeouts through `jest.setTimeout()` or `setDefaultTimeout()` from `bun:test`.

### Expected-failure tests *(since 1.2.5)*

`test.failing()` inverts a test: throwing makes it pass, while an unexpected success fails it. Jest globals are also available in files imported by a test entrypoint, so helper files can call APIs such as `expect.extend()` directly.

```ts
test.failing("documents an unfixed bug", () => {
  expect(add(1, 2)).toBe(3);
});
```

### Initial `node:test` compatibility *(since 1.2.6)*

Bun can run basic tests imported from `node:test` using `bun:test` underneath. This initial implementation does not yet support subtests, mocks, snapshots, timers, custom reporters, or the programmatic API.

```ts
import test from "node:test";

test("basic functionality", () => {});
```

### Callback-style expected-failure tests *(since 1.2.10)*

`test.failing()` now inverts callback-style completion correctly: throwing or passing an error to `done()` makes the expected-failure test pass, while calling `done()` without an error makes it fail.

```ts
import { test } from "bun:test";

test.failing("expects an error", done => {
  done(new Error("expected failure"));
});
```

### End-of-test callbacks *(since 1.3.2)*

`onTestFinished(fn)` must be registered inside a non-concurrent test and runs after every `afterEach` hook; it supports async and done-style callbacks. Use `test.serial` when a suite otherwise uses concurrent tests.

```ts
import { onTestFinished, test } from "bun:test";

test.serial("uses a resource", () => {
  const resource = { close() {} };
  onTestFinished(() => resource.close());
});
```
