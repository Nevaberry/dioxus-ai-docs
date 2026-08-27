# CLI and Discovery

## Test path patterns

The singular `--testPathPattern` flag is replaced by plural
`--testPathPatterns`, which accepts multiple patterns: (30-guide)

```bash
jest --testPathPatterns "unit/.*" "integration/.*"
```

Programmatic watch integrations must construct a `TestPathPatterns` object
instead of passing the earlier shape.

Paths provided on the CLI match only relative test-file paths. If an invocation
previously relied on absolute-path matching, inspect the selected set and pass
a relative path or suitable pattern instead. (30.0.0)

## Initialization and required values

`jest --init` is removed. Use the package initializer: (30-guide)

```bash
npm init jest@latest
```

Flags such as `--maxWorkers` and `--selectProjects` require values. Do not rely
on an omitted value being inferred.

## Custom filters

A custom `--filter` implementation must return an object whose `filtered`
property contains the path array; returning the array directly is no longer a
valid contract: (30-guide)

```js
return {filtered: selectedPaths};
```

## Listing and collecting tests

Combine `--listTests` with `--outputFile` to write the test-file list to a file:
(30.0.0)

```bash
jest --listTests --outputFile test-files.json
```

Use `--collect-tests` to discover and list individual tests without executing
them: (30.4.0)

```bash
jest --collect-tests
```

Choose based on the required granularity: `--listTests` yields test files,
whereas `--collect-tests` discovers the tests without running them.

## Focused failure reruns

`--onlyFailures` includes test modules that failed to load. It also reruns tests
whose prior failure was a compilation error rather than silently excluding
them from the focused run. (30.1-30.3)

## JSON and coverage output

Combining `--json` with `--outputFile` preserves CLI coverage output as of
30.3. This matters when an integration needs machine-readable results in a
file while a human or CI log still needs coverage output. (30.1-30.3)

## Expanded default patterns

Default test matching recognizes `.mjs`, `.cjs`, `.mts`, and `.cts`, and `.mts`
and `.cts` are default module extensions. If the expanded defaults discover
unintended files, constrain `testMatch` or `testRegex`. (30-guide)

