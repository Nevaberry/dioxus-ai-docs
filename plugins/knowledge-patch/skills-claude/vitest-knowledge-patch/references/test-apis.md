# Test APIs

## Choose fixture scope

Since 3.2.0, fixtures declared with `test.extend` may use `scope: 'file'` or `scope: 'worker'`. File fixtures behave like lazy top-level `beforeAll` and `afterAll`; worker fixtures initialize once per worker. Default worker isolation recreates state, so disable isolation only when sharing worker-scoped work is intentional.

```ts
const test = baseTest.extend({
  db: [async ({}, use) => {
    await use(db)
    await db.close()
  }, { scope: 'worker' }],
})
```

## Build type-inferred fixtures

Since 4.1.0, the builder form of `test.extend` infers fixtures from returned values and supplies `onCleanup` for teardown:

```ts
const test = baseTest
  .extend('config', { port: 3000 })
  .extend('server', async ({ config }, { onCleanup }) => {
    const server = await startServer(config.port)
    onCleanup(() => server.close())
    return server
  })
```

File and worker fixture contexts reach `beforeAll`, `afterAll`, and `aroundAll`. Suite hooks no longer receive the previously undocumented `Suite` argument.

## Use context-aware and around hooks

Since 4.0.0, an extended test exposes `beforeEach` and `afterEach` hooks typed with the extended context:

```ts
const test = baseTest.extend<{ todos: number[] }>({
  todos: async ({}, use) => {
    await use([])
  },
})

test.beforeEach(({ todos }) => todos.push(1))
```

Since 4.1.0, `test.aroundEach` wraps every test and `test.aroundAll` wraps suites. The callback must invoke the supplied runner. Use these for transactions, tracing spans, and `AsyncLocalStorage` contexts that must surround the code under test.

```ts
test.aroundEach(async (runTest, { db }) => {
  await db.transaction(runTest)
})
```

## Respond to cancellation

Since 3.2.0, the test context exposes an `AbortSignal`. It aborts on timeout, Ctrl+C, or when another test fails while `--bail` is active. Pass it to cancellable work so interruption stops the underlying resource.

```ts
it('stops on interruption', async ({ signal }) => {
  await fetch('/heavy-resource', { signal })
})
```

## Attach annotations

Annotations were added in 3.2.0. Call the test context's asynchronous `annotate` with a message and an optional type or attachment object. The annotation belongs to the current test and reaches custom reporters through `onTestAnnotate`.

```ts
import { test } from 'vitest'

test('creates a report', async ({ annotate }) => {
  await annotate('starting export', 'notice')
  const file = createTestSpecificFile()
  await annotate('created report', { body: file })
})
```

Vitest waits for unawaited annotation work before the test finishes, but explicitly await an annotation when later code depends on completion.

The default terminal reporter prints annotations only for failed tests; `verbose` is the only terminal reporter that also prints them for passing tests. HTML and UI annotations need a call site in a test file. JUnit, TAP, and TAP-flat discard attachments and retain type and message. GitHub Actions maps `notice`, `warning`, and `error`; other types become notices.

## Attach independent test metadata

Since 4.1.0, the `meta` test option carries arbitrary machine-readable data independent of annotations:

```ts
test('query', { meta: { owner: 'database' } }, () => {})
```

## Declare and attach tags

Tags were added in 4.1.0. Vitest has no built-in tags and normally throws if a test uses a name absent from `test.tags`; set `strictTags: false` to allow undeclared names.

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

When tag-provided options conflict, unprioritized tags merge first, lower numeric `priority` means higher priority, and test-local options win over every tag. Without priorities, tag order resolves conflicts.

Restrict tag names in TypeScript by augmenting `TestTags`:

```ts
import 'vitest'

declare module 'vitest' {
  interface TestTags {
    tags: 'db' | 'flaky'
  }
}
```

List the catalog with `vitest --list-tags` or emit JSON with `vitest --list-tags=json`.

## Inherit and filter tags

Tags on `describe` are inherited by nested tests and combine with tags on a child. A JSDoc `@module-tag` applies to every test in its file regardless of comment position; use test options for individual cases.

```ts
/** @module-tag flaky */
describe('API', { tags: ['db'] }, () => {
  test('queries records', () => {})
})
```

`--tags-filter` accepts `and` or `&&`, `or` or `||`, `not` or `!`, `*` wildcards, and parentheses. Precedence is `not`, then `and`, then `or`; repeated flags combine with AND. Tag names cannot be `and`, `or`, or `not` in any case, and cannot contain whitespace or `()&|!*`.

```sh
vitest --tags-filter="db && !flaky"
```

The UI accepts the same expression after `tag:`. Programmatic runs accept `tagsFilter` in `startVitest` or `createVitest`; `createSpecification` accepts `testTagsFilter`.

```ts
import { startVitest } from 'vitest/node'

await startVitest('test', [], {
  tagsFilter: ['db && !flaky'],
})
```

Since 4.1.1, `TestRunner.matchesTags(tags)` returns whether the active filter would include a test with those tags, or `true` when no filter is active. Use it to avoid expensive setup outside the selected tag set.

```ts
import { beforeAll, TestRunner } from 'vitest'

beforeAll(async () => {
  if (TestRunner.matchesTags(['db'])) await seedDatabase()
})
```

## Type custom matchers once

Since 3.2.0, augment `Matchers` once for instance assertions, static asymmetric matchers, and `expect.extend` implementations:

```ts
interface CustomMatchers<R = unknown> {
  toBeFoo: (arg: string) => R
}

declare module 'vitest' {
  interface Matchers<T = any> extends CustomMatchers<T> {}
}
```

## Narrow types and match schemas

Since 4.0.0, `expect.assert` exposes Chai's assertion function with an assertion signature, allowing TypeScript narrowing:

```ts
expect.assert(animal.__type === 'Dog')
animal.bark()
```

Also since 4.0.0, `expect.schemaMatching` accepts any Standard Schema v1 schema, including Zod, Valibot, and ArkType, and nests inside equality assertions:

```ts
import { z } from 'zod'

expect({ email: 'john@example.com' }).toEqual({
  email: expect.schemaMatching(z.string().email()),
})
```

## Restore and dispose mocks automatically

Since 3.2.0, runtimes with Explicit Resource Management can bind mocks from `vi.spyOn` and `vi.fn` with `using`; Vitest calls `mockRestore` when the containing block exits.

Since 4.1.0, `vi.doMock` returns a disposable, so a dynamic module mock can be removed at scope exit:

```ts
using mock = vi.doMock('./service', () => ({ value: 1 }))
```

Redirect-based mocks are constrained by the filesystem allowlist as of 4.1.11. A redirect outside the allowed boundary is rejected; keep intentional targets inside the configured filesystem scope.

## Use current mock assertion names

Since 4.1.0, Sinon-compatible Chai chains are available as an alternative to Vitest's matchers:

```ts
expect(fn).to.have.been.calledWith('value')
expect(fn).to.have.callCount(1)
```

The old `toBe*` spy assertions are deprecated. Use the corresponding `toHaveBeen*` forms and `toThrowError`.

## Control fake timers and snapshots

Vitest 4.1.0 uses Sinon fake timers v15 and exposes `setTickMode` through its timer controls.

Snapshot updates accept explicit modes:

```sh
vitest --update=new
vitest --update=all
```

Snapshot configuration also accepts `update: 'none'`.
