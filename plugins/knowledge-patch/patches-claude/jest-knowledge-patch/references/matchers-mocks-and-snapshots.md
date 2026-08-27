# Matchers, Mocks, and Snapshots

## Matcher property semantics

Object matchers such as `toEqual` and `objectContaining` ignore non-enumerable
properties by default. Equality checks include symbol-keyed properties, so two
objects that differ only at a symbol key are not equal. (30-guide; 30.0.0)

`toStrictEqual` no longer fails solely because a value returned by
`structuredClone` has a cross-realm constructor. `toMatchObject` and subset
matching no longer throw on exotic iterables. (30.4.0)

## Type-checked call assertions

TypeScript infers parameter types for the `CalledWith` matcher family from the
mocked function. An assertion with incompatible arguments can therefore become
a compile-time error even when runtime behavior has not changed. Fix the
assertion or mock signature rather than suppressing the useful mismatch.
(30-guide)

## Data-driven tests

`test.each()` type definitions accept readonly tables, including `as const`,
and callback argument inference is more accurate for both `test.each()` and
`describe.each()`: (30.0.0)

```ts
const cases = [[1, 2, 3]] as const;
test.each(cases)('%i + %i = %i', (a, b, total) => {
  expect(a + b).toBe(total);
});
```

Use `%$` in a `test.each` title to insert the test case's sequence number:
(30-guide)

```js
test.each(cases)('case %$ works', value => {
  expect(value).toBeDefined();
});
```

## Generated mocks

Register `jest.onGenerateMock()` to modify auto-generated mocks. The callback
receives the module path and generated mock and must return the possibly
modified mock: (30-guide)

```js
jest.onGenerateMock((modulePath, moduleMock) => {
  if (modulePath.includes('Database')) moduleMock.connect = jest.fn();
  return moduleMock;
});
```

## Automatically restored spies

In an environment with explicit resource management, declare a spy with
`using` to restore it automatically when the containing block exits:
(30-guide)

```ts
using warnSpy = jest.spyOn(console, 'warn');
```

## Custom serialization

A custom object can define static `SERIALIZABLE_PROPERTIES` to restrict which
properties Jest uses in snapshots and matcher error output. Use this when an
object's internal or unstable fields should not appear in those renderings.
(30-guide)

## Snapshot and formatting changes

Review expected output for these serializer changes: (30-guide)

- Serialized errors include `cause`.
- React empty-string children are omitted.
- `ArrayBuffer` and `DataView` receive human-readable formatting.
- Existing snapshots containing Jest's deprecated `goo.gl` documentation URL
  need the full replacement URL.

`pretty-format` supports React 19 values. Snapshot output involving those
values can now use the supported representation. (30.4.0)

