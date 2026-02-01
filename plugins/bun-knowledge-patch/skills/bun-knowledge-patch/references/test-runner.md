# Test Runner (`bun:test`)

## Basic Usage

```ts
import { test, expect, describe, beforeEach, afterEach } from "bun:test";

test("basic test", () => {
  expect(1 + 1).toBe(2);
});

// Custom error messages
expect(value, "Should be positive").toBeGreaterThan(0);
```

## Matchers

### Object/Key Matchers

```ts
expect(obj).toContainKey("name");
expect(obj).toContainValue("Alice");
```

### Mock Return Value Matchers

```ts
const fn = mock((i) => ({ value: i * 10 }));
fn(1); fn(2); fn(3);

expect(fn).toHaveReturned();
expect(fn).toHaveReturnedTimes(2);
expect(fn).toHaveReturnedWith({ value: 10 });      // Any call
expect(fn).toHaveLastReturnedWith({ value: 30 }); // Most recent
expect(fn).toHaveNthReturnedWith(2, { value: 20 }); // 2nd call (1-indexed)
```

### Inline Snapshots

```ts
expect(data).toMatchInlineSnapshot(); // Updates test file directly
```

## Type Testing

Vitest-compatible type assertions (checked by `tsc --noEmit`, no-op at runtime):

```ts
import { expectTypeOf, test } from "bun:test";

test("types", () => {
  expectTypeOf("hello").toBeString();
  expectTypeOf({ a: 1 }).toMatchObjectType<{ a: number }>();

  function add(a: number, b: number) { return a + b; }
  expectTypeOf(add).parameters.toEqualTypeOf<[number, number]>();
  expectTypeOf(add).returns.toBeNumber();
});
```

## Mocking

```ts
import { mock, spyOn } from "bun:test";

const fn = mock(() => "result");
fn();
expect(fn).toHaveBeenCalled();

// Clear all mocks
mock.clearAllMocks();
```

### `vi` Global

Vitest's `vi` is available globally:

```ts
test("mocking", () => {
  const fn = vi.fn();
  vi.spyOn(obj, "method");
  vi.mock("./module");
});
```

## Fake Timers

```ts
import { test, expect, jest } from "bun:test";

test("timers", () => {
  jest.useFakeTimers();

  let called = false;
  setTimeout(() => { called = true; }, 1000);

  expect(called).toBe(false);
  jest.advanceTimersByTime(1000);
  expect(called).toBe(true);

  jest.useRealTimers();
});
```

Methods: `useFakeTimers(options?)`, `useRealTimers()`, `advanceTimersByTime(ms)`, `advanceTimersToNextTimer()`, `runAllTimers()`, `runOnlyPendingTimers()`, `getTimerCount()`, `clearAllTimers()`, `isFakeTimers()`.

## Concurrent Tests

Run async tests in parallel within a file:

```ts
test.concurrent("test 1", async () => { /* runs in parallel */ });
test.concurrent("test 2", async () => { /* runs in parallel */ });

describe.concurrent("parallel suite", () => {
  test("a", async () => {});
  test("b", async () => {});
});

// Force sequential
test.serial("must run alone", () => {});

// Chain with other modifiers
test.concurrent.each([1, 2, 3])("test %i", async (n) => {});
```

Configure: `--max-concurrency=N` (default 20).

**Limitations**: No `expect.assertions()`, no `toMatchSnapshot()` (use inline).

## Test Modifiers

```ts
test.only("focused test", () => {});  // Works without --only flag
test.skip("skipped", () => {});
test.todo("not implemented");
test.failing("bug not yet fixed", () => {
  expect(brokenFunction()).toBe(expected); // Passes if it throws
});
```

## Test Options

```ts
// Retry flaky tests
test("flaky", () => { /* ... */ }, { retry: 3 });

// Repeat for stability
test("stable", () => { /* ... */ }, { repeats: 20 });
```

## `test.each` Variable Substitution

```ts
const cases = [
  { user: { name: "Alice" }, a: 1, b: 2, expected: 3 },
];

test.each(cases)("Add $a and $b for $user.name", ({ a, b, expected }) => {
  expect(a + b).toBe(expected);
});
```

## Hooks

```ts
import { onTestFinished } from "bun:test";

test("cleanup", () => {
  onTestFinished(async () => {
    await db.close(); // Runs after afterEach
  });
});
```

## Configuration

```ts
import { setDefaultTimeout } from "bun:test";
setDefaultTimeout(60_000);
```

In `bunfig.toml`:

```toml
[test]
coveragePathIgnorePatterns = ["**/__tests__/**", "**/fixtures/**"]
concurrentTestGlob = "**/integration/**/*.test.ts"
onlyFailures = true
```

## CLI Options

```sh
bun test --reporter=junit --reporter-outfile=junit.xml
bun test --coverage --coverage-reporter=lcov
bun test --grep "pattern"
bun test --randomize              # Random order
bun test --seed 12345             # Reproduce order
bun test --pass-with-no-tests     # Exit 0 when no tests
bun test --only-failures          # Show only failing
bun test -t "filter"              # Fails if no matches
```

## CI Behavior

In CI (`CI=true`), `bun test` fails if:
- `test.only()` is present
- Snapshots would be created without `--update-snapshots`
