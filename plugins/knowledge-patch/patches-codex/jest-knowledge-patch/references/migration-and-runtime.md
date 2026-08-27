# Migration and runtime

Use this reference for runtime upgrades, removed APIs, renamed CLI switches,
path-selection changes, and extension or package-boundary surprises.

## Runtime requirements

Jest 30 drops support for Node.js 14, 16, 19, 21, and 23. Its TypeScript type
definitions require TypeScript 5.4 or newer. Audit developer machines, CI
images, editor TypeScript versions, and any consumer package constraints.

The default `jest-environment-jsdom` moves from JSDOM 21 to 26. Re-run
DOM-sensitive tests and revisit code that mocks `window.location`. This is the
bundled environment change; custom JSDOM versions are addressed separately in
the environments reference.

These major-upgrade constraints and migrations were recorded in `30-guide`;
the additional Node.js 23 and Babel peer constraints were recorded in
`30.0.0`.

## Removed matcher aliases

Replace every removed alias with its canonical name:

| Removed alias | Canonical matcher |
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

Perform this as a mechanical rename, then handle matcher semantic changes as a
separate review.

## CLI and watch-filter migrations

`--testPathPattern` is now `--testPathPatterns` and can receive multiple
patterns:

```bash
jest --testPathPatterns "unit/.*" "integration/.*"
```

Programmatic watch integrations no longer pass a plain pattern; construct a
`TestPathPatterns` object. Paths supplied on the CLI match only relative
test-file paths, so an invocation relying on an absolute-path match may select
a different test set.

`jest --init` is removed. Use the package initializer:

```bash
npm init jest@latest
```

Options such as `--maxWorkers` and `--selectProjects` require explicit values.
A custom `--filter` implementation must return:

```ts
{filtered: Array<string>}
```

Returning a bare array is no longer valid.

## Mock API and type removals

Replace `jest.genMockFromModule()` with the equivalent
`jest.createMockFromModule()`.

The public `MockFunctionMetadata`, `MockFunctionMetadataType`, and
`SpyInstance` types are removed. In particular, replace `jest.SpyInstance`
with `jest.Spied`.

Paths passed to `jest.mock()` must match the filename's exact casing, including
on case-insensitive operating systems. Fix the source string rather than
relying on local file-system behavior.

## Package exports and glob changes

Jest packages are bundled and expose ESM wrappers through package exports.
Tools and integrations must import public package names, not internal build
paths such as:

```js
import worker from 'jest-runner/build/testWorker';
```

If an integration needs an internal symbol, move it to a supported public
contract instead of finding a new deep path.

The move to `glob` v10 can change brace expansion and extglob handling in
custom patterns. Compare the files selected by custom `testMatch`, coverage,
ignore, and tooling globs before and after an upgrade.

## Custom sequencer and runtime construction

A custom `TestSequencer` receives `globalConfig` and project `contexts`.
Update constructor signatures and any test fixtures that instantiate the
sequencer.

Code that constructs Jest `Runtime` directly must pass the newly required
`globalConfig` argument. Normal CLI users do not construct the runtime and are
unaffected.

## Failure-focused reruns

In the `30.1-30.3` update, `--onlyFailures` begins including test modules that
failed to load. It also re-executes failed tests when the previous failure was
a compilation error. Focused reruns should therefore surface failures that
older behavior silently omitted.

## Migration audit

Search for all of the following:

```text
toBeCalled
lastCalledWith
nthCalledWith
toReturn
toThrowError
genMockFromModule
SpyInstance
MockFunctionMetadata
--testPathPattern
jest --init
/build/
```

Then verify:

- Node.js and TypeScript versions in local and CI environments;
- exact casing for every `jest.mock()` path;
- relative-path behavior for CLI filters;
- selected files for custom globs;
- custom sequencer constructor arguments;
- direct `Runtime` construction arguments;
- load and compilation failures under `--onlyFailures`.
