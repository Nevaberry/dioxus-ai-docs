# Assertions, mocks, and snapshots

Use this reference for equality semantics, matcher typing, data-driven tests,
mock generation, resource-managed spies, custom serialization, and snapshot
review.

## Object matcher semantics

Object matchers such as `toEqual` and `objectContaining` ignore non-enumerable
properties by default. If a test must compare one, expose it through an
enumerable representation or assert the property descriptor directly.

Equality checks include symbol-keyed properties:

```js
const key = Symbol('key');
expect({[key]: 1}).not.toEqual({[key]: 2});
```

This can turn an old passing comparison into a failure when symbol values
differ.

## Called-with matcher types

TypeScript infers parameter types for the `CalledWith` matcher family from the
mocked function. An assertion with an impossible argument list can become a
compile-time error even when runtime matcher behavior has not changed.

Fix either the assertion or the mock signature according to the real callable
contract. Do not cast away the error merely to preserve an invalid
expectation.

## Strict equality and subset matching

In `30.4.0`, `toStrictEqual` no longer fails only because a value produced by
`structuredClone` has a cross-realm constructor.

`toMatchObject` and internal subset matching no longer throw on exotic
iterables. Re-evaluate tests that expected matcher infrastructure to throw;
assert the iterable's contents or mismatch instead.

## Snapshot and formatter changes

Snapshot output may change in several independent ways:

- serialized errors include their `cause`;
- React empty-string children are omitted;
- `ArrayBuffer` and `DataView` use human-readable formatting;
- React 19 values are supported by `pretty-format`;
- snapshots containing Jest's deprecated `goo.gl` documentation URL need the
  full URL.

Update snapshots only after identifying which rule caused each diff. Error
causes may reveal useful nested failures and should not be stripped merely to
stabilize text.

## Custom serialization

A custom object can define static `SERIALIZABLE_PROPERTIES` to restrict which
properties Jest uses in snapshots and matcher error output.

Use this when the object's full property set is noisy, unstable, private, or
cyclic. Keep the list representative of observable state so matcher messages
remain diagnostic.

## Auto-restoring spies

In environments with explicit resource management, declare a spy with `using`
to restore it automatically at block exit:

```ts
{
  using warnSpy = jest.spyOn(console, 'warn');
  // assertions
}
```

This scopes restoration to the block, including abrupt exits. It does not
replace explicit cleanup for other mocks or resources.

## Auto-generated mock hook

`jest.onGenerateMock()` registers a callback for each automatically generated
mock. The callback receives the module path and current mock, and it must
return the possibly modified mock:

```js
jest.onGenerateMock((modulePath, moduleMock) => {
  if (modulePath.includes('Database')) {
    moduleMock.connect = jest.fn();
  }
  return moduleMock;
});
```

Keep callbacks deterministic. When registering multiple callbacks, preserve
the incoming changes by modifying or replacing the current `moduleMock` and
returning the result.

## Data-driven title numbering

`%$` in a `test.each` title expands to the test case's sequence number:

```js
test.each(cases)(
  'case %$ works',
  value => expect(value).toBeDefined(),
);
```

Use it when values alone do not make duplicate or large tables easy to
identify in reports.

## Readonly each tables

Type definitions accept readonly tables, including `as const`, and infer
callback arguments more accurately for both `test.each()` and
`describe.each()`:

```ts
const cases = [[1, 2, 3]] as const;

test.each(cases)('%i + %i = %i', (a, b, total) => {
  expect(a + b).toBe(total);
});
```

Preserve readonly input rather than widening it solely to satisfy the test
API.

## Assertion review checklist

- Replace removed aliases before debugging semantic differences.
- Decide explicitly whether non-enumerable properties matter.
- Include symbol-keyed state in equality expectations.
- Fix called-with arguments that violate the mock signature.
- Revisit cross-realm `structuredClone` expectations.
- Assert exotic iterable behavior rather than matcher crashes.
- Attribute every snapshot diff to a formatter rule.
- Preserve useful error `cause` information.
- Use `SERIALIZABLE_PROPERTIES` only for intentional projections.
- Scope spies with `using` where resource management is supported.
- Return a mock from every `onGenerateMock` callback.
- Use `%$` when data-table cases need stable report numbers.
- Keep readonly `each` tables readonly.

Symbol equality and readonly-table support were first recorded in `30.0.0`;
later matcher robustness and formatter work is recorded in `30.4.0`.
