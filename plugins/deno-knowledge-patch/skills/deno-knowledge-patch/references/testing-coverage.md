# Testing & Coverage

## Test Hooks (2.5+)

`Deno.test.beforeAll`, `Deno.test.beforeEach`, `Deno.test.afterAll`, `Deno.test.afterEach` — top-level setup/teardown for test files (not nested in test steps).

```ts
Deno.test.beforeAll(() => {
  // runs once before all tests in this file
});

Deno.test.afterAll(() => {
  // runs once after all tests in this file
});

Deno.test.beforeEach(() => {
  // runs before each test
});

Deno.test.afterEach(() => {
  // runs after each test
});
```

## Auto Coverage Reports (2.3+)

`deno test --coverage` now auto-generates the coverage report (no separate `deno coverage` step). Use `--coverage-raw-data-only` to opt out. Set `DENO_COVERAGE_DIR` to control output location.

## Coverage Ignore Comments (2.3+)

```ts
// deno-coverage-ignore
ignoredLine();

// deno-coverage-ignore-start
ignoredBlock();
// deno-coverage-ignore-stop

// deno-coverage-ignore-file  (at top of file — ignores entire file)
```

## Deno.bench Options (2.2+)

Control exact iteration counts:

```ts
Deno.bench({ warmup: 1_000, n: 100_000 }, fn);
```
