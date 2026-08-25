---
name: jest-knowledge-patch
description: Jest
version: 30.4.0
license: MIT
metadata:
  author: Nevaberry
---


# Jest Knowledge Patch

Use this skill when upgrading, configuring, or debugging Jest 30 projects.
Load the reference that matches the task before changing configuration, tests,
custom environments, runners, sequencers, transforms, or integrations.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/migration-and-runtime.md](references/migration-and-runtime.md) | Runtime requirements, removed APIs, renamed CLI options, package boundaries, path behavior |
| [references/configuration-and-cli.md](references/configuration-and-cli.md) | Configuration helpers, project settings, discovery commands, reporting, coverage, runners |
| [references/modules-transforms-and-environments.md](references/modules-transforms-and-environments.md) | ESM/CJS interop, TypeScript, Babel, import attributes, JSDOM environments |
| [references/assertions-mocks-and-snapshots.md](references/assertions-mocks-and-snapshots.md) | Matcher behavior, mock hooks, spies, data-driven tests, snapshots, formatting |
| [references/execution-and-timers.md](references/execution-and-timers.md) | Rejections, retries, fake timers, cleanup, leak detection, worker shutdown, setup hooks |

## Working method

1. Inspect the installed Jest, Node.js, TypeScript, transformer, and test
   environment versions.
2. Read the relevant reference file before editing code.
3. Search for removed names and invalid configuration shapes.
4. Update behavior-sensitive tests separately from mechanical renames.
5. Run focused tests, then the full suite, coverage, and snapshot review.
6. Treat failures in custom runners, environments, sequencers, and reporters as
   possible public-contract changes before blaming test code.

## Breaking changes first

### Check the runtime

Jest 30 does not support Node.js 14, 16, 19, 21, or 23. Its type definitions
require TypeScript 5.4 or newer. Confirm CI images, local toolchains, editor
TypeScript, and package-manager constraints before investigating test failures.

The bundled JSDOM environment moved from JSDOM 21 to 26. Recheck DOM behavior,
especially tests that mock `window.location`. A custom environment can use a
different JSDOM version through `@jest/environment-jsdom-abstract`.

### Replace removed matcher aliases

Use the canonical matcher names:

| Removed | Replacement |
| --- | --- |
| `toBeCalled` | `toHaveBeenCalled` |
| `toBeCalledTimes` | `toHaveBeenCalledTimes` |
| `toBeCalledWith` | `toHaveBeenCalledWith` |
| `lastCalledWith` | `toHaveBeenLastCalledWith` |
| `nthCalledWith` | `toHaveBeenNthCalledWith` |
| `toReturn` | `toHaveReturned` |
| `toReturnTimes` | `toHaveReturnedTimes` |
| `toReturnWith` | `toHaveReturnedWith` |
| `lastReturnedWith` | `toHaveLastReturnedWith` |
| `nthReturnedWith` | `toHaveNthReturnedWith` |
| `toThrowError` | `toThrow` |

Called-with matchers now infer the mocked function's parameter types. A
previously running assertion can become a TypeScript error when its expected
arguments do not match the mock signature.

### Migrate CLI path filters

Rename `--testPathPattern` to plural `--testPathPatterns`; it accepts multiple
patterns:

```bash
jest --testPathPatterns "unit/.*" "integration/.*"
```

Programmatic watch integrations must construct `TestPathPatterns`. CLI paths
are matched against relative test-file paths, so remove assumptions that they
match absolute paths.

`jest --init` is gone; initialize with:

```bash
npm init jest@latest
```

Pass explicit values to options such as `--maxWorkers` and
`--selectProjects`. A custom `--filter` must return
`{filtered: Array<string>}`, not an array.

### Replace removed mock APIs and types

Replace `jest.genMockFromModule()` with `jest.createMockFromModule()`. Replace
uses of `jest.SpyInstance` with `jest.Spied`; the public
`MockFunctionMetadata`, `MockFunctionMetadataType`, and `SpyInstance` types
were removed.

Match `jest.mock()` paths to the filename's exact casing even on
case-insensitive file systems.

### Stop deep-importing Jest packages

Import public package entry points. Jest packages are bundled and expose ESM
wrappers through package exports, so a path such as
`jest-runner/build/testWorker` is not a stable import.

Recheck custom glob patterns after the move to `glob` v10, particularly brace
expansion and extglob behavior.

## High-value behavior changes

### Equality and subset matching

`toEqual` and `objectContaining` ignore non-enumerable properties by default.
Equality includes symbol-keyed properties. `toStrictEqual` accepts compatible
cross-realm constructors produced by `structuredClone`, and subset matching no
longer throws on exotic iterables.

Review failures and newly passing tests as semantic changes; do not update
expectations mechanically.

### Snapshots and formatting

Snapshot text can change because:

- serialized errors include `cause`;
- React empty-string children are omitted;
- `ArrayBuffer` and `DataView` have readable formatting;
- React 19 values have formatter support;
- the deprecated `goo.gl` documentation URL is replaced by the full URL.

Review every snapshot update. Use static `SERIALIZABLE_PROPERTIES` on a custom
object when only selected properties should appear in snapshots and matcher
errors.

### Module interop

Native ESM supports `import.meta.*`, `file://`, and validated import
attributes. On supported Node.js versions, `require()` can load ES modules.

When ESM imports CommonJS, the complete `module.exports` value is the default
export. Do not expect Babel-style `__esModule` default unwrapping. Named imports
can see own properties on a function assigned to `module.exports`, and all
importers share the same CommonJS singleton.

### Test discovery

Default module extensions and test matching include `.mjs`, `.cjs`, `.mts`,
and `.cts`. If non-test files now match, constrain `testMatch` or `testRegex`.

Discover tests without executing them:

```bash
jest --collect-tests
```

Write test-file discovery to a file with:

```bash
jest --listTests --outputFile test-files.json
```

### Project configuration

Project entries can set `testTimeout`, `coverageReporters`, `reporters`,
`verbose`, `silent`, `collectCoverage`, and `coverageProvider`. Project-level
`verbose` and `silent` override the corresponding global settings.

The `jest` field in `package.json` may be a path to a configuration file:

```json
{"jest": "./config/jest.config.js"}
```

Use `defineConfig` and `mergeConfig` from `jest-config` for typed configuration
declaration and composition. Import `GlobalConfig` and `ProjectConfig` types
from `jest`.

## Useful APIs

### Auto-restoring spies

With explicit resource management, `using` restores a spy at block exit:

```ts
using warnSpy = jest.spyOn(console, 'warn');
```

### Generated mock customization

Each `jest.onGenerateMock()` callback must return the mock:

```js
jest.onGenerateMock((modulePath, moduleMock) => {
  if (modulePath.includes('Database')) moduleMock.connect = jest.fn();
  return moduleMock;
});
```

### Retry controls

Configure delay or immediate retry:

```js
jest.retryTimes(3, {waitBeforeRetry: 1000});
jest.retryTimes(3, {retryImmediately: true});
```

### Data-driven tests

Use `%$` for the test-case sequence number. Readonly tables are accepted and
receive improved callback argument inference:

```ts
const cases = [[1, 2, 3]] as const;
test.each(cases)('case %$: %i + %i = %i', (a, b, total) => {
  expect(a + b).toBe(total);
});
```

### Fake timers

Run pending animation-frame callbacks with `advanceTimersToFrame()`. Timer
advancement and clock setup also accept supported Temporal values. Consult the
execution reference before mixing fake timers, asynchronous work, and retries.

## Verification checklist

- Confirm supported Node.js and TypeScript versions in every environment.
- Search for removed matcher, mock, type, and CLI names.
- Check mock path casing and package deep imports.
- Revalidate `.mjs`, `.cjs`, `.mts`, and `.cts` discovery.
- Review relative CLI path filters and custom filter return values.
- Exercise custom runners, sequencers, environments, transformers, and
  reporters.
- Review changed equality semantics instead of blindly accepting results.
- Inspect snapshots for error, React, binary-data, and URL formatting changes.
- Test ESM/CJS boundaries and JSON import attributes.
- Run discovery-only commands and confirm selected test files.
- Validate per-project reporting and coverage behavior.
- Check cleanup warnings, leak detection, and worker shutdown behavior.
- Run the full suite after focused migration checks pass.
