# Matchers and Mocking

## `expect.schemaMatching` (v4)

Asymmetric matcher that validates against a Standard Schema v1 object (Zod, Valibot, ArkType):

```ts
import { z } from 'zod'
import * as v from 'valibot'
import { type } from 'arktype'

test('email validation', () => {
  const user = { email: 'john@example.com' }

  // Zod
  expect(user).toEqual({
    email: expect.schemaMatching(z.string().email()),
  })

  // Valibot
  expect(user).toEqual({
    email: expect.schemaMatching(v.pipe(v.string(), v.email())),
  })

  // ArkType
  expect(user).toEqual({
    email: expect.schemaMatching(type('string.email')),
  })
})
```

Works with all equality matchers: `toEqual`, `toStrictEqual`, `toMatchObject`, `toContainEqual`, `toThrow`, `toHaveBeenCalledWith`, `toHaveReturnedWith`, `toHaveBeenResolvedWith`.

## `expect.assert` (v4)

Type-narrowing assertion. Useful when `expect.to*` methods don't support type narrowing:

```ts
interface Cat { __type: 'Cat'; mew(): void }
interface Dog { __type: 'Dog'; bark(): void }
type Animal = Cat | Dog

const animal: Animal = { __type: 'Dog', bark: () => {} }

expect.assert(animal.__type === 'Dog')
animal.bark() // no type error
```

## `Matchers` Type (v3.2)

Extend `Matchers` to add type support for custom matchers in one place. Affects `expect().to*`, `expect.to*`, and `expect.extend({ to* })`:

```ts
import { expect } from 'vitest'

interface CustomMatchers<R = unknown> {
  toBeFoo: (arg: string) => R
}

declare module 'vitest' {
  interface Matchers<T = any> extends CustomMatchers<T> {}
}

expect.extend({
  toBeFoo(actual, arg) {
    return { pass: true, message: () => '' }
  },
})

expect('foo').toBeFoo('foo')
expect.toBeFoo('foo') // also works on expect directly
```

## `mockThrow` / `mockThrowOnce` (v4.1)

Concise mock throwing without wrapping in a function:

```ts
const fn = vi.fn()
fn.mockThrow(new Error('error message'))
fn() // throws Error<'error message'>

// Once variant:
fn.mockThrowOnce(new Error('first call only'))
```

## Chai-style Mock Assertions (v4.1)

For Sinon migration compatibility:

```ts
const fn = vi.fn()
fn('example')

expect(fn).to.have.been.called
expect(fn).to.have.been.calledWith('example')
expect(fn).to.have.returned
expect(fn).to.have.callCount(1)
```

## Mocking Changes in v4

### Constructor Support

`vi.spyOn` and `vi.fn` now support constructors. Mocks called with `new` construct the instance. Implementation must use `function` or `class` keyword (arrow functions throw):

```ts
const Spy = vi.spyOn(cart, 'Apples')
  .mockImplementation(function () {
    this.getApples = () => 0
  })
  // or with class:
  .mockImplementation(class MockApples {
    getApples() { return 0 }
  })

const mock = new Spy()
```

### Other Mocking Changes

- `vi.fn().getMockName()` returns `vi.fn()` by default (was `spy`) — affects snapshot names
- `vi.restoreAllMocks` only restores manual `vi.spyOn` spies (automocks unaffected)
- Calling `vi.spyOn` on a mock returns the same mock
- `mock.settledResults` populated immediately with `'incomplete'` result
- Automocked instance methods are isolated but share state with prototype
- Automocked methods cannot be restored (even with `.mockRestore`)
- Automocked getters return `undefined` by default (no longer call original)
- `vi.fn(impl).mockReset()` correctly returns mock implementation in `.getMockImplementation()`
- `vi.fn().mock.invocationCallOrder` starts at `1` (was `0`)
