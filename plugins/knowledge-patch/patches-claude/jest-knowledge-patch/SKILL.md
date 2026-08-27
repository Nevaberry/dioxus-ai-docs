---
name: jest-knowledge-patch
description: Jest
version: "30.4.0"
license: MIT
metadata:
  author: Nevaberry
---


# Jest Knowledge Patch

Use this skill when upgrading, configuring, or debugging Jest 30 projects,
especially when behavior differs across matchers, module loading, discovery,
fake timers, environments, snapshots, or multi-project configuration.

## Working Method

1. Inspect the project's Jest, Node.js, TypeScript, transformer, and test
   environment versions before changing code.
2. Identify whether the issue concerns migration compatibility, configuration,
   discovery, modules and transforms, assertions and mocks, timers and
   lifecycle, or reporting and integrations.
3. Read the matching reference file from the index below.
4. Prefer public package exports and documented configuration or runtime APIs.
5. Make migration changes explicit; do not preserve a removed alias or old
   callback shape behind a compatibility wrapper unless the project must still
   run an older Jest release.
6. Run focused tests first, then the full suite. Review snapshot changes rather
   than accepting them mechanically.
7. When test selection changes, compare the selected file list before and after
   the configuration or CLI change.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Migration and compatibility](references/migration-and-compatibility.md) | Runtime prerequisites, removed APIs, extension defaults, path casing, package exports, glob behavior |
| [Configuration and projects](references/configuration-and-projects.md) | Config files, project settings, cleanup, type-safe helpers, workers, custom runners |
| [CLI and discovery](references/cli-and-discovery.md) | Path patterns, filters, test listing, focused reruns, JSON output, collection without execution |
| [Modules and transforms](references/modules-and-transforms.md) | Native ESM, CJS interop, Babel, TypeScript stripping, JSDOM environments, import attributes |
| [Matchers, mocks, and snapshots](references/matchers-mocks-and-snapshots.md) | Matcher semantics and types, spies, generated mocks, equality, serialization, React formatting |
| [Timers, retries, and lifecycle](references/timers-retries-and-lifecycle.md) | Rejection timing, fake timers, Temporal, retries, async setup, global cleanup |
| [Reporting and integrations](references/reporting-and-integrations.md) | Sequencers, runtime construction, result timestamps, leak detection, coverage, public types |

## Quick Reference: Migration Blockers

### Check runtime and type prerequisites

- Remove Node.js 14, 16, 19, 21, and 23 from the Jest execution matrix.
- Use TypeScript 5.4 or newer when consuming Jest's type definitions.
- Expect the standard JSDOM environment to move from JSDOM 21 to 26. Recheck
  browser behavior, particularly tests that mock `window.location`.
- Ensure `@babel/core` satisfies `^7.11` when using `babel-jest` or
  `babel-preset-jest`.

### Replace removed matcher aliases

Use the canonical names:

| Removed | Replacement |
| --- | --- |
| `toBeCalled*` | `toHaveBeenCalled*` |
| `lastCalledWith` | `toHaveBeenLastCalledWith` |
| `nthCalledWith` | `toHaveBeenNthCalledWith` |
| corresponding `toReturn*` aliases | corresponding `toHaveReturned*` matchers |
| `toThrowError` | `toThrow` |

Do the replacements in test source and any custom assertion wrappers.

### Replace removed mock APIs and types

- Replace `jest.genMockFromModule()` with `jest.createMockFromModule()`.
- Replace `jest.SpyInstance` usages with `jest.Spied`.
- Remove dependencies on the deleted `MockFunctionMetadata`,
  `MockFunctionMetadataType`, and `SpyInstance` public types.
- Match the exact filename casing in every `jest.mock()` module path, including
  on case-insensitive file systems.

### Update CLI and filter integrations

`--testPathPattern` is now `--testPathPatterns` and accepts multiple patterns:

```bash
jest --testPathPatterns "unit/.*" "integration/.*"
```

- Construct `TestPathPatterns` in programmatic watch integrations.
- Replace `jest --init` with the package initializer:

```bash
npm init jest@latest
```

- Always provide values for flags such as `--maxWorkers` and
  `--selectProjects`.
- Return `{filtered: Array<string>}` from custom `--filter` implementations,
  not a bare array.

### Stop importing package internals

Jest packages are bundled and expose ESM wrappers through package exports.
Import public package names instead of deep build paths such as
`jest-runner/build/testWorker`.

If custom patterns behave differently, review them for `glob` v10 brace
expansion or extglob differences.

## Quick Reference: Changed Defaults and Semantics

### Review discovery patterns

`.mts` and `.cts` are default module extensions. Default test matching also
recognizes `.mjs`, `.cjs`, `.mts`, and `.cts`. Add explicit `testMatch` or
`testRegex` rules if non-test files now match.

CLI paths are matched against relative test-file paths. Commands that supplied
absolute paths can therefore select a different set of tests.

### Recheck equality and matcher types

- `toEqual` and `objectContaining` ignore non-enumerable properties by default.
- Equality includes symbol-keyed properties.
- The `CalledWith` matcher family infers mocked-function parameter types, so an
  invalid assertion can now fail TypeScript checking without a runtime change.
- `toStrictEqual` accepts a `structuredClone` result even when its cross-realm
  constructor differs.
- `toMatchObject` and subset matching tolerate exotic iterables instead of
  throwing.

### Review snapshot updates

Snapshot output can change because:

- serialized errors include `cause`;
- React empty-string children are omitted;
- `ArrayBuffer` and `DataView` use human-readable formatting;
- React 19 values are supported by `pretty-format`;
- the deprecated Jest `goo.gl` documentation URL is replaced by its full URL.

Treat these as review cues, not permission to update every snapshot blindly.

### Account for rejection timing

Jest waits one additional event-loop turn before classifying a rejected promise
as unhandled. This avoids false failures when a rejection is caught
asynchronously. Set `waitForUnhandledRejections: false` only when the added wait
is unacceptable and the earlier timing is intentional.

## Quick Reference: Modules and Transforms

Native ESM execution supports `import.meta.*`, `file://`, TypeScript Jest config
files, and the default `.mts` and `.cts` extensions. When Node's native
TypeScript type stripping is active, Jest does not load a transformer merely to
strip types.

On Node 24.9 and newer, Jest can `require()` ES modules. A `.js` file containing
ESM syntax can fall back to native ESM without a `"type": "module"` marker,
including after the CommonJS parser rejects it during `require()`.

When ESM imports CommonJS:

- the complete `module.exports` value is always the default export;
- Babel-style `__esModule` default unwrapping no longer occurs;
- named imports include own properties attached to a function assigned to
  `module.exports`;
- all importers share the same CommonJS singleton.

Jest validates TC39 import attributes, including JSON imports:

```js
import data from './data.json' with {type: 'json'};
```

## Quick Reference: High-Value APIs

### Configure Babel and Jest config composition

Disable automatic injection of `babel-preset-jest` when required:

```js
transform: {
  '^.+\\.[jt]sx?$': ['babel-jest', {excludeJestPreset: true}],
}
```

Use `defineConfig` and `mergeConfig` from `jest-config` for type-safe
configuration declaration and composition. A `package.json` `jest` field may
also point to a configuration file:

```json
{"jest": "./config/jest.config.js"}
```

### Customize generated mocks and scoped spies

`jest.onGenerateMock()` receives each auto-generated mock and must return the
possibly modified mock:

```js
jest.onGenerateMock((modulePath, moduleMock) => {
  if (modulePath.includes('Database')) moduleMock.connect = jest.fn();
  return moduleMock;
});
```

With explicit resource management, a spy declared using `using` is restored
when its block exits:

```ts
using warnSpy = jest.spyOn(console, 'warn');
```

### Control retries and fake time

```js
jest.retryTimes(3, {waitBeforeRetry: 1000});
jest.retryTimes(3, {retryImmediately: true});
```

Modern fake timers provide `jest.advanceTimersToFrame()` for pending animation
frames and support Temporal values for advancing time and setting the clock.
See the timers reference for accepted Temporal types and tick-mode control.

### Discover tests without executing them

```bash
jest --collect-tests
```

Use `--listTests --outputFile <file>` when the needed output is the test-file
list rather than discovered test cases.

