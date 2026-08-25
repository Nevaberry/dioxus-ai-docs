# Testing

## Runner behavior and migration hazards

### Uncaught failures and focused tests (`1.2-guide`)

`bun test` fails on uncaught exceptions or rejections between test cases rather
than silently ignoring them. `test.only()` works without `--only`.

### Equality and containment (`1.2.2`, `1.2.20`, `1.4-2`, `1.4-4`)

- `Bun.deepEquals`, and therefore `toEqual`, distinguishes objects with the
  same prototype but different internal types. Numeric-key objects no longer
  equal typed arrays.
- `toIncludeRepeated` requires exactly the requested count, not at least that
  many.
- `toContain()` uses `===`, so it does not find `NaN`.
- `expect.any(Object)` follows `typeof value === "object"`: it matches `null`
  and rejects functions.
- Temporal objects are compared by value by deep-equality and strict-equality
  APIs (`1.4-2`).

### Empty selection and CI (`1.2.18`, `1.2.23`, `1.3.1`)

`-t`/`--test-name-pattern` matching zero tests exits with an error. No discovered
tests also fail by default; use `--pass-with-no-tests` for a successful empty
run. Under `CI=true`, focused tests are errors and a missing snapshot cannot be
created without `--update-snapshots`; set `CI=false` to opt out.

An empty `--shard` is a distinct successful case.

### Output filtering (`1.3.1`, `1.3.6`, `1.3.12`, `1.4-2`)

- `--only-failures`, or bunfig `onlyFailures`, hides passing cases but retains
  the summary.
- `--grep` aliases `--test-name-pattern` and `-t`.
- `--elide-lines` is ignored rather than rejected when stdout is not a TTY.

## Reporters, snapshots, and coverage

### Reporters and coverage (`1.2-guide`)

```sh
bun test --reporter=junit --reporter-outfile=junit.xml
bun test --coverage-reporter=lcov --coverage-dir=coverage
```

`bunfig.toml` supports JUnit output under `[test.reporter]` and `coverage`,
`coverageReporter`, and `coverageDir` under `[test]`.

### Inline snapshots (`1.2-guide`, `1.2.1`)

`toMatchInlineSnapshot()` and `toThrowErrorMatchingInlineSnapshot()` are filled
by `bun test -u`. Indented bodies are accepted and updater output preserves the
detected indentation.

### Coverage exclusions (`1.2.19`)

`coveragePathIgnorePatterns` accepts one glob or an array.

```toml
[test]
coveragePathIgnorePatterns = ["**/__tests__/**", "**/fixtures/**"]
```

### Retry reporting (`1.3.10`)

`bun test --retry N` or `[test] retry = N` supplies a default; per-test options
win. JUnit emits one testcase per attempt and a failure element for failed
attempts.

## Assertions and mocks

### Custom message and collection matchers (`1.2-guide`)

`expect(value, "message")` puts a custom message in the second argument.
Collection additions include `toContainValue`, `toContainValues`,
`toContainAllValues`, `toContainAnyValues`, `toContainKey`, `toContainKeys`,
`toContainAllKeys`, `toContainAnyKeys`, `toHaveReturned`, and
`toHaveReturnedTimes`.

### Failing tests (`1.2.5`, `1.2.10`)

`test.failing` passes only when the body fails. With a done callback it passes
for a throw or `done(error)` and fails for bare `done()`.

### Global test APIs (`1.2.5`, `1.3.1`)

Jest globals are defined in helper files imported by a test, so
`expect.extend()` can live in shared modules. The typed Vitest-compatible global
`vi` supplies `vi.fn`, `vi.mock`, `vi.spyOn`, and related APIs.

### Return-value matchers and clearing (`1.2.20`)

`toHaveReturnedWith`, `toHaveLastReturnedWith`, and 1-based
`toHaveNthReturnedWith` use deep equality and asymmetric matchers.
`mock.clearAllMocks()` clears calls/results without changing implementations.

### Reset semantics (`1.4-2`)

`jest.resetAllMocks()`/`vi.resetAllMocks()` clear implementations as well as
history; a function mock then returns `undefined`, and a spy remains neutered
until `mockRestore()`. Use `clearAllMocks()` for history-only reset.

### Disposable mocks (`1.3.9`)

`mock()` and `spyOn()` implement `Symbol.dispose` as `mockRestore`, enabling
scope cleanup through `using`.

```ts
using spy = spyOn(object, "method").mockReturnValue("mocked");
```

### Type assertions (`1.2.20`)

`expectTypeOf` follows Vitest's type-level API. It does nothing at runtime; run
`bunx tsc --noEmit` for validation. Matcher types became stricter in
`1.3-guide`; widen explicitly, such as
`expect(null).toBe<string | null>("hello")`.

## Timeouts, cleanup, retries, and timers

### Default timeout (`1.2-guide`)

Set the default with `jest.setTimeout(ms)` or `setDefaultTimeout` from
`bun:test`.

### Hook timeout values (`1.4-2`)

`beforeAll`, `beforeEach`, `afterAll`, and `afterEach` accept a number or
`{ timeout }` as their second argument.

### Per-test cleanup (`1.3.2`)

`onTestFinished(fn)` runs after every `afterEach`. Call it only inside a test,
not a describe/preload or concurrent test; use `test.serial` when needed. Async
and done-style cleanup functions are accepted.

### Retry and repeat options (`1.3.3`)

The third test argument accepts `{ retry: n }`, which passes if any retry
passes, and `{ repeats: n }`, which fails if any run fails.

### Fake timers (`1.3.4`, `1.4`)

The `jest` object supplies `useFakeTimers({ now })`, `useRealTimers`, time
advancement, `advanceTimersToNextTimer`, `runAllTimers`,
`runOnlyPendingTimers`, `getTimerCount`, `clearAllTimers`, and `isFakeTimers`.
`jest.setSystemTime()` composes with advancement; fake timers drive `Bun.cron`,
and Testing Library's `waitFor` detects and advances them.

## Parameterized and randomized tests

### Case-title substitution (`1.2.19`)

`test.each` titles accept `$field` and nested `$user.name` paths alongside
printf placeholders.

### Random order (`1.2.23`)

`--randomize` shuffles tests and prints the seed. `--seed <n>` reproduces the
order and implies randomization.

## Concurrency within a file

### Concurrent tests (`1.2.23`)

`test.concurrent` parallelizes async tests; `describe.concurrent` applies to a
group and `test.serial` opts out. Default limit is 20, controlled by
`--max-concurrency`. `concurrentTestGlob` marks whole files concurrent.

Qualifiers chain, including `test.failing.each`, skip and only.

Concurrent tests do not support `expect.assertions`, `expect.hasAssertions`, or
file snapshots; inline snapshots work. `beforeAll`/`afterAll` do not run
concurrently.

## Isolation and parallel files

### File isolation and workers (`1.3.13`)

The experimental `--isolate` gives each file a fresh global in the same process
while draining microtasks and closing sockets, timers, and child processes.
Transpilation is cached across files.

`--parallel[=N]` uses worker processes with work stealing and implies isolate.
Output is buffered per file. Workers receive `JEST_WORKER_ID` and
`BUN_TEST_WORKER_ID`; define/loader/tsconfig/condition flags are forwarded.

### Sharding (`1.3.13`)

`--shard=M/N` is one-based. Files are sorted and distributed round-robin;
invalid values fail. Sharding follows changed-file filtering and randomization
occurs inside the selected shard.

### Changed tests (`1.3.13`)

`--changed` selects tests transitively importing files reported by git. Bare
mode uses staged, unstaged and untracked changes; an argument selects a commit,
branch or tag. Watch mode re-runs git each cycle. Scanning skips node_modules
and emits no code. No changed files exits cleanly, while watch stays active.

### Timing-aware balancing (`1.4`)

`--timings=path` records prior file wall times for parallel and shard balancing;
`--update-timings` rewrites the file slowest-first. Files with shared imports
stay together to benefit from module caching.

## Discovery controls

### Path exclusion (`1.3.11`)

`--path-ignore-patterns` prunes matching directories during discovery. Repeated
CLI flags replace rather than merge with bunfig `pathIgnorePatterns`.

```toml
[test]
pathIgnorePatterns = ["vendor/**", "submodules/**"]
```

## `node:test`

### Bun runner integration (`1.2.6`)

Node test files run under `bun test`. The original implementation lacked
subtests, mocks, snapshots, timers, custom reporters and programmatic run.

### Node 26 additions (`1.4-3`)

Subtests execute inline. Supported APIs include `t.plan`, `t.waitFor`,
`getTestContext`, `mock.timers`, `mock.property`, runtime skip/todo, tags,
custom assertions, callback tests, and per-test mock cleanup.

Programmatic `run()` creates one child process per file and emits Node's
TestsStream event sequence. Node 26 `expectFailure` expects the body to throw;
an unexpected pass uses failure type `expectedFailure`.
