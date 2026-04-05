# Test Fixtures and Hooks

## Scoped Fixtures (v3.2)

`test.extend` fixtures can specify `scope: 'file'` or `scope: 'worker'`:

```ts
const test = baseTest.extend({
  db: [
    async ({}, use) => {
      const db = await createDB()
      await use(db)
      await db.close()
    },
    { scope: 'worker' },
  ],
})
```

- `file` scope: like `beforeAll`/`afterAll` but only runs if the fixture is used
- `worker` scope: once per worker (by default Vitest creates one worker per test, so disable `isolate` to benefit)

## `test.extend` Builder Pattern (v4.1)

Return a value instead of calling `use()` — TypeScript infers types automatically:

```ts
import { test as baseTest } from 'vitest'

export const test = baseTest
  // Simple value — type inferred as { port: number; host: string }
  .extend('config', { port: 3000, host: 'localhost' })
  // Function fixture — type inferred from return value
  .extend('server', async ({ config }) => {
    return `http://${config.host}:${config.port}`
  })
```

### Cleanup with `onCleanup`

```ts
export const test = baseTest
  .extend('tempFile', async ({}, { onCleanup }) => {
    const filePath = `/tmp/test-${Date.now()}.txt`
    await fs.writeFile(filePath, 'test data')
    onCleanup(() => fs.unlink(filePath))
    return filePath
  })
```

### Scoped Builder Fixtures

```ts
const test = baseTest
  .extend('config', { scope: 'file' }, () => loadConfig())
  .extend('db', { scope: 'file' }, ({ config }) => createDatabase(config.port))
```

## Type-Aware Hooks (v4)

Hooks on extended test objects receive the extended context:

```ts
const test = baseTest.extend<{ todos: number[] }>({
  todos: async ({}, use) => { await use([]) },
})

test.beforeEach(({ todos }) => {
  todos.push(1) // TypeScript knows todos is number[]
})

test.afterEach(({ todos }) => {
  console.log(todos)
})
```

In v4.1, `beforeAll`, `afterAll`, and `aroundAll` also receive `file` and `worker` scoped fixtures:

```ts
test.beforeAll(async ({ db }) => {
  await db.migrateUsers()
})
```

## `aroundEach` and `aroundAll` Hooks (v4.1)

Wrap tests in a context. The callback receives `runTest` which **must** be called:

### `aroundEach` — wraps each test

Use cases: AsyncLocalStorage, tracing spans, database transactions.

```ts
const test = baseTest
  .extend('db', async ({}, { onCleanup }) => {
    const db = await createTestDatabase()
    onCleanup(() => db.close())
    return db
  })

test.aroundEach(async (runTest, { db }) => {
  await db.transaction(runTest)
})

test('insert user', async ({ db }) => {
  await db.insert({ name: 'Alice' }) // runs inside transaction
})
```

### `aroundAll` — wraps each suite

```ts
test.aroundAll(async (runSuite) => {
  const server = await startServer()
  await runSuite()
  await server.close()
})
```

## `vi.defineHelper` (v4.1)

Wraps a function so stack traces point to the call site, not the helper internals:

```ts
const assertPair = vi.defineHelper((a, b) => {
  expect(a).toEqual(b) // error won't point here
})

test('example', () => {
  assertPair('left', 'right') // error points here instead
})
```

Useful for custom assertion libraries and reusable test utilities.

Also works with trace markers in browser mode:

```ts
const myRender = vi.defineHelper(async (content: string) => {
  document.body.innerHTML = content
  await page.elementLocator(document.body).mark('render helper')
})
```

## Test `signal` API (v3.2)

Tests receive an `AbortSignal` that aborts on timeout, `--bail`, or Ctrl+C:

```ts
it('stop request on timeout', async ({ signal }) => {
  await fetch('/heavy-resource', { signal })
}, 2000)
```

## Explicit Resource Management (v3.2)

In environments supporting the TC39 proposal, use `using` to auto-restore mocks:

```ts
it('calls console.log', () => {
  using spy = vi.spyOn(console, 'log').mockImplementation(() => {})
  debug('message')
  expect(spy).toHaveBeenCalled()
})
// console.log is restored here automatically
```

Works with both `vi.spyOn` and `vi.fn`.
