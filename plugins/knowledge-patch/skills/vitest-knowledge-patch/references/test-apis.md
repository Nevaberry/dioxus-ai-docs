# Test APIs

Relevant versioned source batches: `3.2.0`, `4.0.0`, and `4.1.0`.

## Contents

- [Attach messages and files to a test](#attach-messages-and-files-to-a-test)
- [Attach arbitrary metadata](#attach-arbitrary-metadata)
- [Declare a tag catalog](#declare-a-tag-catalog)
- [Resolve tag option conflicts](#resolve-tag-option-conflicts)
- [Restrict tag names with TypeScript](#restrict-tag-names-with-typescript)
- [Inherit suite and file tags](#inherit-suite-and-file-tags)
- [Filter by tag expression](#filter-by-tag-expression)
- [Define file- and worker-scoped fixtures](#define-file--and-worker-scoped-fixtures)
- [Build inferred fixtures incrementally](#build-inferred-fixtures-incrementally)
- [Use typed hooks on extended tests](#use-typed-hooks-on-extended-tests)
- [Wrap tests and suites with around hooks](#wrap-tests-and-suites-with-around-hooks)
- [Cancel underlying asynchronous work](#cancel-underlying-asynchronous-work)
- [Type custom matchers once](#type-custom-matchers-once)
- [Narrow types with an assertion signature](#narrow-types-with-an-assertion-signature)
- [Match Standard Schema values](#match-standard-schema-values)
- [Restore mocks with Explicit Resource Management](#restore-mocks-with-explicit-resource-management)
- [Configure fake-timer tick modes](#configure-fake-timer-tick-modes)
- [Use Chai-style mock assertions](#use-chai-style-mock-assertions)
- [Select a snapshot update mode](#select-a-snapshot-update-mode)

## Attach messages and files to a test

The test context exposes an asynchronous `annotate` function. Pass a message and, optionally, a type string or an attachment object:

```ts
import { test } from 'vitest'

test('creates a report', async ({ annotate }) => {
  await annotate('starting export', 'notice')

  const file = createTestSpecificFile()
  await annotate('created report', { body: file })
})
```

Each annotation is attached to the current test and delivered to reporters through `onTestAnnotate`. Vitest waits for unawaited annotation promises before completing the test, but explicitly await an annotation when subsequent code depends on it being complete.

Annotations appear in the UI and HTML, JUnit, TAP, and GitHub Actions reporters. Annotations associated with failures also appear in CLI output. Format behavior differs:

- The default terminal reporter prints only annotations from failed tests.
- `verbose` also prints annotations from passing tests.
- HTML/UI annotations require a call site in a test file.
- JUnit, TAP, and TAP-flat keep type and message but discard attachments.
- GitHub Actions recognizes `notice`, `warning`, and `error`; it maps other types to notices.

See [Reporters and integrations](reporters-and-integrations.md) when implementing `onTestAnnotate` or processing artifact attachments.

## Attach arbitrary metadata

Use the `meta` test option for custom machine-readable data that is not an annotation:

```ts
test('query', {
  meta: {
    owner: 'database',
  },
}, () => {})
```

## Declare a tag catalog

Declare tags in `test.tags`. Every catalog entry requires a name and can provide a description, shared test options, and a conflict priority:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    tags: [
      {
        name: 'db',
        description: 'Database tests',
        timeout: 60_000,
      },
      {
        name: 'flaky',
        retry: 3,
        timeout: 30_000,
        priority: 1,
      },
    ],
  },
})
```

Vitest defines no built-in tags and, by default, throws when a test uses a name absent from the catalog. Set `strictTags: false` to permit undeclared names.

Attach tags through test options:

```ts
test('query', {
  tags: ['db', 'flaky'],
}, () => {})
```

## Resolve tag option conflicts

When several tags provide the same test option:

1. Unprioritized tags merge first.
2. Lower numeric `priority` means higher priority.
3. Options written directly on the test override every tag.

If no conflicting tag has a priority, tag order resolves the conflict.

## Restrict tag names with TypeScript

Augment `TestTags` to make tag names a checked union:

```ts
import 'vitest'

declare module 'vitest' {
  interface TestTags {
    tags: 'db' | 'flaky'
  }
}
```

Inspect the configured catalog from the CLI:

```sh
vitest --list-tags
vitest --list-tags=json
```

## Inherit suite and file tags

Tags on a `describe` are inherited by all nested tests and combine with tags declared on a child:

```ts
describe('API', { tags: ['db'] }, () => {
  test('queries records', { tags: ['flaky'] }, () => {})
})
```

A JSDoc `@module-tag` declaration applies to every test in the file, regardless of where the comment appears. It is not scoped to the next test or suite:

```ts
/** @module-tag flaky */
describe('API', { tags: ['db'] }, () => {
  test('queries records', () => {})
})
```

Use test options rather than `@module-tag` for an individual test.

## Filter by tag expression

`--tags-filter` accepts:

- `and` or `&&`
- `or` or `||`
- `not` or `!`
- `*` wildcards
- Parentheses

```sh
vitest --tags-filter="db && !flaky"
```

Expression precedence is `not`, then `and`, then `or`. Repeating `--tags-filter` combines the separate expressions with AND logic.

Tag names cannot:

- Equal `and`, `or`, or `not`, case-insensitively.
- Contain whitespace.
- Contain parser characters from `()&|!*`.

The UI accepts the same expression grammar after a `tag:` prefix.

Programmatic filters use different option names at different levels:

```ts
import { startVitest } from 'vitest/node'

await startVitest('test', [], {
  tagsFilter: ['db && !flaky'],
})
```

- `startVitest` and `createVitest` accept `tagsFilter`.
- `createSpecification` accepts `testTagsFilter`.

Since `4.1.1`, `TestRunner.matchesTags(tags)` reports whether the active filter would include the supplied tags. It returns `true` when no tag filter is active, allowing expensive setup to follow the current selection:

```ts
import { beforeAll, TestRunner } from 'vitest'

beforeAll(async () => {
  if (TestRunner.matchesTags(['db'])) {
    await seedDatabase()
  }
})
```

## Define file- and worker-scoped fixtures

Fixtures declared through `test.extend` accept `scope: 'file'` and `scope: 'worker'`:

```ts
const test = baseTest.extend({
  db: [
    async ({}, use) => {
      await use(db)
      await db.close()
    },
    { scope: 'worker' },
  ],
})
```

A file-scoped fixture behaves like a lazy top-level `beforeAll`/`afterAll` pair. A worker-scoped fixture initializes once per worker. Vitest isolates workers by default, so disable isolation only when work truly needs to be shared instead of recreated in isolated workers.

## Build inferred fixtures incrementally

The builder form of `test.extend` infers each fixture type from its returned value. It also supplies `onCleanup` for teardown:

```ts
const test = baseTest
  .extend('config', { port: 3000 })
  .extend('server', async ({ config }, { onCleanup }) => {
    const server = await startServer(config.port)
    onCleanup(() => server.close())
    return server
  })
```

File- and worker-scoped fixture contexts are available to `beforeAll`, `afterAll`, and `aroundAll`. These hooks no longer receive the previously undocumented `Suite` argument.

## Use typed hooks on extended tests

The object returned by `test.extend` exposes `beforeEach` and `afterEach` hooks typed with the extended context:

```ts
import { test as baseTest } from 'vitest'

const test = baseTest.extend<{ todos: number[] }>({
  todos: async ({}, use) => {
    await use([])
  },
})

test.beforeEach(({ todos }) => {
  todos.push(1)
})
```

## Wrap tests and suites with around hooks

`test.aroundEach` wraps every test, while `test.aroundAll` wraps a suite. The callback must invoke the supplied runner or the wrapped test/suite will not run.

```ts
test.aroundEach(async (runTest, { db }) => {
  await db.transaction(runTest)
})
```

Around hooks are useful when a transaction, trace span, `AsyncLocalStorage` context, or similar resource must surround the code under test rather than merely run before and after it.

## Cancel underlying asynchronous work

The test context exposes an `AbortSignal`. It aborts when:

- The test times out.
- The user interrupts the run with Ctrl+C.
- Another test fails while `--bail` is active.

Pass the signal to cancellable resources so aborting the test also stops its underlying work:

```ts
it('stops on interruption', async ({ signal }) => {
  await fetch('/heavy-resource', { signal })
})
```

## Type custom matchers once

Augment `Matchers` once to type custom matcher implementations, instance assertions, and static asymmetric matchers:

```ts
interface CustomMatchers<R = unknown> {
  toBeFoo: (arg: string) => R
}

declare module 'vitest' {
  interface Matchers<T = any> extends CustomMatchers<T> {}
}
```

This unified interface avoids separate augmentations for the different matcher entry points.

## Narrow types with an assertion signature

`expect.assert` exposes Chai's assertion function through `expect` and carries a TypeScript assertion signature:

```ts
expect.assert(animal.__type === 'Dog')
animal.bark()
```

Use it when an ordinary matcher would validate a condition at runtime but would not narrow the type for following statements.

## Match Standard Schema values

`expect.schemaMatching` accepts a Standard Schema v1 schema and can be nested in equality-style assertions. Compatible libraries include Zod, Valibot, and ArkType:

```ts
import { z } from 'zod'

expect({
  email: 'john@example.com',
}).toEqual({
  email: expect.schemaMatching(z.string().email()),
})
```

## Restore mocks with Explicit Resource Management

Where the runtime supports Explicit Resource Management, bind a `vi.spyOn` or `vi.fn` mock with `using`. Vitest calls `mockRestore` automatically at the end of the containing block:

```ts
using spy = vi.spyOn(service, 'load')
```

`vi.doMock` also returns a disposable. Scope a dynamic module mock with `using` so it is removed when the scope exits:

```ts
using mock = vi.doMock('./service', () => ({
  value: 1,
}))
```

Browser ESM namespace objects need a different strategy: use `vi.mock(path, { spy: true })` before configuring exported functions. See [Browser Mode](browser-mode.md).

## Configure fake-timer tick modes

Vitest uses Sinon fake timers v15 and exposes `setTickMode` through its timer controls. Use those controls when timers should advance according to a specific Sinon tick policy rather than only through manual clock advancement.

## Use Chai-style mock assertions

Sinon-compatible Chai chains are available as an alternative to Vitest's mock matchers:

```ts
expect(fn).to.have.been.calledWith('value')
expect(fn).to.have.callCount(1)
```

The older `toBe*` spy assertion names are deprecated. Prefer their `toHaveBeen*` equivalents and use `toThrowError` for thrown errors.

## Select a snapshot update mode

The `--update` flag accepts explicit `new` and `all` values:

```sh
vitest --update=new
vitest --update=all
```

Snapshot configuration also accepts `update: 'none'` when updates must be prohibited.
