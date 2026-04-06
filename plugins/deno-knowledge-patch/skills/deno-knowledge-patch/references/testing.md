# Testing & Benchmarks

## Test Setup and Teardown Hooks (2.5+)

```ts
Deno.test.beforeAll(() => { /* once before all tests */ });
Deno.test.beforeEach(() => { /* before each test */ });
Deno.test.afterEach(() => { /* after each test */ });
Deno.test.afterAll(() => { /* once after all tests */ });
```

## Coverage Auto-Report (2.3+)

`deno test --coverage` now auto-generates the report (no separate `deno coverage` step). Use `--coverage-raw-data-only` for old behavior.

### Ignore Comments

```ts
// deno-coverage-ignore          — single line
// deno-coverage-ignore-start    — block start
// deno-coverage-ignore-stop     — block end
// deno-coverage-ignore-file     — entire file
```

## `deno bench` Explicit Iteration Control (2.2+)

```ts
Deno.bench({ warmup: 1_000, n: 100_000 }, () => {
  new URL("./foo.js", import.meta.url);
});
```

## `deno check` Without Arguments (2.3+)

`deno check` (no args) now checks all files in the current directory (equivalent to `deno check .`).
