# Test APIs

## Attach annotations

Annotations were added in 3.2.0. Call the test context's asynchronous `annotate` function with a message plus an optional type or attachment object. The annotation is attached to the current test and sent to reporters through `onTestAnnotate`.

```ts
import { test } from 'vitest'

test('creates a report', async ({ annotate }) => {
  await annotate('starting export', 'notice')
  const file = createTestSpecificFile()
  await annotate('created report', { body: file })
})
```

Vitest waits for otherwise-unawaited annotation work before the test finishes. Explicitly await an annotation when later code depends on its completion. Annotation display and attachment support vary by reporter; see [Reporters and integrations](reporters-and-integrations.md).

## Use file- and worker-scoped fixtures

Fixtures declared with `test.extend` can set `scope: 'file'` or `scope: 'worker'` (3.2.0). File fixtures act like lazy top-level `beforeAll`/`afterAll` hooks. Worker fixtures initialize once per worker, but default worker isolation can still recreate shared state; disable isolation only when cross-file sharing is intentional.

```ts
const test = baseTest.extend({
  db: [async ({}, use) => {
    await use(db)
    await db.close()
  }, { scope: 'worker' }],
})
```

The builder form introduced in 4.1.0 infers fixture types from returned values and supplies `onCleanup` for teardown:

```ts
const test = baseTest
  .extend('config', { port: 3000 })
  .extend('server', async ({ config }, { onCleanup }) => {
    const server = await startServer(config.port)
    onCleanup(() => server.close())
    return server
  })
```

The object returned by `test.extend` also has type-aware `beforeEach` and `afterEach` hooks (4.0.0):

```ts
const test = baseTest.extend<{ todos: number[] }>({
  todos: async ({}, use) => use([]),
})

test.beforeEach(({ todos }) => todos.push(1))
```

File and worker fixture contexts reach `beforeAll`, `afterAll`, and `aroundAll` in 4.1.0. Suite hooks no longer receive the undocumented `Suite` argument.

## Wrap execution with around hooks

`test.aroundEach` wraps every test and `test.aroundAll` wraps suites (4.1.0). The callback must invoke the supplied runner. Use these hooks for transactions, tracing spans, or `AsyncLocalStorage` that must surround the code under test.

```ts
test.aroundEach(async (runTest, { db }) => {
  await db.transaction(runTest)
})
```

## Respond to cancellation

Since 3.2.0, the test context exposes an `AbortSignal`. It aborts on timeout, Ctrl+C, or when another failure activates `--bail`. Pass it into cancellable work so interruption stops the underlying operation.

```ts
it('stops on interruption', async ({ signal }) => {
  await fetch('/heavy-resource', { signal })
})
```

## Type custom matchers once

The unified `Matchers` interface introduced in 3.2.0 types instance assertions, static asymmetric matchers, and `expect.extend` implementations from one augmentation.

```ts
interface CustomMatchers<R = unknown> {
  toBeFoo: (arg: string) => R
}

declare module 'vitest' {
  interface Matchers<T = any> extends CustomMatchers<T> {}
}
```

## Narrow types and match schemas

`expect.assert` exposes Chai's assertion function with an assertion signature, allowing TypeScript narrowing where ordinary matchers cannot (4.0.0):

```ts
expect.assert(animal.__type === 'Dog')
animal.bark()
```

`expect.schemaMatching` accepts a Standard Schema v1 implementation such as Zod, Valibot, or ArkType and can be nested in equality assertions (4.0.0):

```ts
import { z } from 'zod'

expect({ email: 'john@example.com' }).toEqual({
  email: expect.schemaMatching(z.string().email()),
})
```

## Restore and dispose mocks automatically

Where Explicit Resource Management is available, bind `vi.spyOn` and `vi.fn` with `using`; Vitest calls `mockRestore` when the block exits (3.2.0).

```ts
using spy = vi.spyOn(service, 'load')
```

`vi.doMock` returns a disposable in 4.1.0, so a dynamically registered module mock can also be scoped and removed automatically:

```ts
using mock = vi.doMock('./service', () => ({ value: 1 }))
```

Browser-native ESM exports require `{ spy: true }` module mocking rather than `vi.spyOn`; see [Browser Mode](browser-mode.md).

## Use current mock assertions and timers

Vitest 4.1.0 supports Sinon-compatible Chai chains as an alternative to standard mock matchers:

```ts
expect(fn).to.have.been.calledWith('value')
expect(fn).to.have.callCount(1)
```

Old `toBe*` spy assertions are deprecated; use corresponding `toHaveBeen*` assertions or `toThrowError`. Vitest also uses Sinon fake timers v15 and exposes `setTickMode` through timer controls.

## Select snapshot update modes

Vitest 4.1.0 accepts explicit values for `--update`, while snapshot configuration can disable updates:

```sh
vitest --update=new
vitest --update=all
```

Set the snapshot configuration's `update` value to `'none'` when updates must be disabled.

## Attach test metadata

Use the `meta` test option for arbitrary machine-readable data independent of annotations (4.1.0):

```ts
test('query', { meta: { owner: 'database' } }, () => {})
```

## Declare a tag catalog

Tags arrived in 4.1.0. Vitest has no built-in tags and normally throws when a test uses a name absent from `test.tags`; set `strictTags: false` only when undeclared tags are intentional.

```ts
export default defineConfig({
  test: {
    tags: [
      { name: 'db', description: 'Database tests', timeout: 60_000 },
      { name: 'flaky', retry: 3, timeout: 30_000, priority: 1 },
    ],
  },
})

test('query', { tags: ['db', 'flaky'] }, () => {})
```

When tag-provided options conflict, unprioritized tags merge first, then prioritized tags apply with lower numeric `priority` taking precedence. Direct test options win over all tags. Without priorities, tag order resolves conflicts.

Restrict names in TypeScript by augmenting `TestTags`. List the catalog as text or JSON:

```ts
import 'vitest'

declare module 'vitest' {
  interface TestTags {
    tags: 'db' | 'flaky'
  }
}
```

```sh
vitest --list-tags
vitest --list-tags=json
```

## Inherit and filter tags

Tags on `describe` are inherited by nested tests and combine with child tags. A JSDoc `@module-tag` applies to every test in the file regardless of comment position, so use test options for individual cases.

```ts
/** @module-tag flaky */
describe('API', { tags: ['db'] }, () => {
  test('queries records', () => {})
})
```

`--tags-filter` accepts `and`/`&&`, `or`/`||`, `not`/`!`, `*`, and parentheses. Repeated flags combine with AND; precedence is `not`, `and`, then `or`. Names cannot be reserved `and`, `or`, or `not` values, ignoring case, and cannot contain whitespace or `()&|!*`.

```sh
vitest --tags-filter="db && !flaky"
```

The UI uses the same grammar after `tag:`. `startVitest` and `createVitest` accept `tagsFilter`; `createSpecification` accepts `testTagsFilter`.

```ts
import { startVitest } from 'vitest/node'

await startVitest('test', [], {
  tagsFilter: ['db && !flaky'],
})
```

Since 4.1.1, `TestRunner.matchesTags(tags)` reports whether the active filter includes a tag set and returns `true` when no filter is active. Use it to avoid expensive setup that the selected tests do not need.

```ts
import { beforeAll, TestRunner } from 'vitest'

beforeAll(async () => {
  if (TestRunner.matchesTags(['db'])) await seedDatabase()
})
```
