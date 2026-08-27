# Migration and Compatibility

## Runtime prerequisites

Jest 30 removes support for Node.js 14, 16, 19, and 21. The 30.0.0 release also
removes support for Node.js 23. Do not leave any of those versions in the test
execution matrix. Jest's type definitions require TypeScript 5.4 or newer.

The standard `jest-environment-jsdom` moves from JSDOM 21 to JSDOM 26. Recheck
DOM-sensitive tests after upgrading, especially code that mocks
`window.location`. (30-guide; 30.0.0)

`babel-jest` and `babel-preset-jest` declare `@babel/core` with the peer range
`^7.11`. Ensure the installed Babel core satisfies that range. (30.0.0)

## Removed matcher aliases

The deprecated aliases have been removed. Replace them with their canonical
forms: (30-guide)

| Removed form | Replacement |
| --- | --- |
| `toBeCalled*` | `toHaveBeenCalled*` |
| `lastCalledWith` | `toHaveBeenLastCalledWith` |
| `nthCalledWith` | `toHaveBeenNthCalledWith` |
| corresponding `toReturn*` aliases | corresponding `toHaveReturned*` matchers |
| `toThrowError` | `toThrow` |

Search custom assertion helpers as well as test files so an indirect alias use
does not survive the migration.

## Removed mock APIs and public types

Replace `jest.genMockFromModule()` with the equivalent
`jest.createMockFromModule()`. The public `MockFunctionMetadata`,
`MockFunctionMetadataType`, and `SpyInstance` types are removed. Use
`jest.Spied` instead of `jest.SpyInstance`. (30-guide)

Module paths passed to `jest.mock()` must use the same casing as the filename,
even on a case-insensitive system. Fix case mismatches rather than relying on
the host file system. (30-guide)

## File extensions and test discovery defaults

`.mts` and `.cts` are included in the default `moduleFileExtensions`. Default
test matching also recognizes `.mjs`, `.cjs`, `.mts`, and `.cts`. A repository
with non-test files that match the expanded patterns should define explicit
`testMatch` or `testRegex` rules. (30-guide)

## Package exports and dependency boundaries

Jest packages are bundled and provide ESM wrappers through package exports.
Tools and integrations must import public package names, not internal build
paths such as `jest-runner/build/testWorker`. (30-guide)

Jest's move to `glob` v10 can change brace expansion and extglob behavior in
custom file patterns. If discovery or coverage patterns change their result,
review those pattern constructs. (30-guide)

## Behavior changes worth isolating during migration

- A CLI path now matches only against relative test-file paths; invocations
  that depended on an absolute path can select a different set. (30.0.0)
- Object matchers such as `toEqual` and `objectContaining` ignore
  non-enumerable properties by default. (30-guide)
- Equality checks include symbol-keyed properties. (30.0.0)
- Jest waits an extra event-loop turn before reporting an unhandled rejection;
  see the lifecycle reference before changing this behavior. (30-guide)

