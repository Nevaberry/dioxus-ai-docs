# Testing, Coverage, Linting, and Formatting
Test and benchmark programs, collect coverage, author lint rules, and format supported languages.
## Contents
- [Testing](#testing)
- [Coverage](#coverage)
- [Benchmarks](#benchmarks)
- [Linting](#linting)
- [Formatting](#formatting)

## Testing

### Built-in snapshots (2.9-guide)

Test contexts now provide `t.assertSnapshot()` without an import, store snapshots under `__snapshots__`, and update or prune them with `deno test --update-snapshots` (`-u`) without requiring read/write permissions for the default location. `node:test` contexts also expose `t.assert.fileSnapshot()`.

```ts
Deno.test("renders", async (t) => {
  await t.assertSnapshot(renderHeader());
});
```

### Change-aware test selection (2.9-guide)

`deno test --changed` selects tests affected by uncommitted changes, `--changed=<ref>` compares with a branch point, and `--related=<file>` follows dependencies from a specified file across workspace members. Changes to project configuration, the lockfile, import maps, or `package.json` conservatively force a full run.

```sh
deno test --changed=origin/main
deno test --related=src/util.ts
```

### Parameterized tests (2.9-guide)

`Deno.test.each()` creates an independently filterable test for every array or object case; arrays are spread as arguments and objects are passed whole. Names accept printf tokens, `%#` for the case index, and `$key.nested` object interpolation, and the API composes with `only` and `ignore`.

```ts
Deno.test.each([
  [1, 1, 2],
  [1, 2, 3],
])("add(%i, %i) = %i", (a, b, expected) => {
  if (a + b !== expected) throw new Error("unexpected sum");
});
```

### Per-test timeouts (2.8-guide)

`Deno.test()` accepts a millisecond `timeout` and fails only that test when the deadline expires.

```ts
Deno.test("request", { timeout: 1_000 }, async () => {
  await new Promise((resolve) => setTimeout(resolve, 2_000));
});
```

### Test lifecycle hooks (2.5-guide)

`Deno.test.beforeAll()`, `beforeEach()`, `afterEach()`, and `afterAll()` register setup and teardown around tests.

```ts
Deno.test.beforeAll(() => {});
Deno.test.beforeEach(() => {});
Deno.test.afterEach(() => {});
Deno.test.afterAll(() => {});
Deno.test("example", () => {});
```

### Test retries and repeats (2.9-guide)

A test's `retry` option or the run-wide `--retry` flag allows extra attempts and reports a test that later passes as flaky; `--repeats` runs every test additional times and requires all runs to pass. Per-test values, including `0`, override the CLI settings.

```ts
Deno.test({
  name: "eventually consistent",
  retry: 2,
  fn: async () => { /* ... */ },
});
```

```sh
deno test --retry=2
deno test --repeats=5
```

### Test sanitizers are opt-in (2.8-guide)

`sanitizeOps` and `sanitizeResources` now default to `false`. Enable them per test with the existing options, for a whole module with `Deno.test.sanitizer()`, or globally under the `test` configuration.

```ts
Deno.test.sanitizer({ ops: true, resources: true });
Deno.test("strict test", () => {});
```

### Test sharding (2.9-guide)

`deno test --shard=<index>/<count>` assigns discovered test files to balanced, 1-based shards before shuffling, making CI fan-out native to the runner. An excess shard receives no files and still exits successfully.

```sh
deno test --shard=2/3
```

## Coverage

### Automatic and selectively ignored test coverage (2.3-guide)

`deno test --coverage` now generates a report when the test run finishes; add `--coverage-raw-data-only` to retain the old raw-data-only workflow. `DENO_COVERAGE_DIR` selects the storage directory, and ignore comments can exclude a line, a region, or an entire file.

```ts
// deno-coverage-ignore
unreachablePlatformBranch();

// deno-coverage-ignore-start
generatedBranchingCode();
// deno-coverage-ignore-stop
```

Use `// deno-coverage-ignore-file` for a whole file.

### Coverage and test-report behavior (2.6-guide)

Coverage collection now includes code executed in workers and excludes Blob URLs. JUnit output no longer contains ANSI escape sequences, so it can be consumed as clean XML by CI systems.

### Coverage outside the test runner (2.4-guide)

`deno run --coverage` collects coverage for ordinary script execution, so subprocess entry points can be instrumented explicitly rather than being missed by `deno test`; `deno coverage` then renders the collected data.

```sh
deno run --coverage main.ts
deno coverage
```

### Enforced coverage thresholds (2.9-guide)

Coverage commands can exit nonzero below a global percentage, while `deno.json` can set separate line, branch, and function thresholds.

```sh
deno test --coverage --coverage-threshold=90
deno coverage --threshold=90 coverage/
```

```json
{
  "coverage": {
    "thresholds": { "lines": 90, "branches": 80, "functions": 90 }
  }
}
```

### Function coverage (2.8-guide)

`deno coverage` reports function coverage alongside line and branch coverage in both text and HTML output.

```sh
deno test --coverage=cov
deno coverage cov
```

### HTML coverage reports (2.0-guide)

`deno coverage` can produce HTML reports.

## Benchmarks

### Benchmark critical sections (2.0-guide)

`deno bench` supports critical sections for isolating the code that should be measured more precisely.

### Empty benchmark discovery (2.2.0)

`deno bench --permit-no-files` permits a run that discovers no benchmark files, which is useful for CI jobs where benchmarks are optional or generated.

```sh
deno bench --permit-no-files
```

### Fixed benchmark iteration counts (2.2-guide)

`Deno.BenchDefinition.n` and `warmup` are restored. Setting them disables automatic iteration selection and runs exactly the requested warmup and measured counts.

```ts
Deno.bench({ warmup: 1_000, n: 100_000 }, () => {
  new URL("./mod.ts", import.meta.url);
});
```

## Linting

### Checked files in lint JSON (2.1.0)

`deno lint --json` now includes a list of checked files, allowing output consumers to distinguish clean inputs from files that were not examined.

### Dependency lint defaults (2.5-guide)

The recommended, default `no-unversioned-import` rule rejects `npm:` and `jsr:` imports without a version requirement. The new automatically selected `workspace` rule set includes `no-import-prefix`, which rejects inline `npm:`, `jsr:`, and `https:` dependencies when a manifest is present and instead requires declaring them in `deno.json` or `package.json` and importing a bare specifier.

### Empty formatter and linter inputs (2.3-guide)

`--permit-no-files` now works with `deno fmt` and `deno lint`, allowing globbed or generated CI inputs to match no files without failing the command.

```sh
deno lint --permit-no-files 'generated/**/*.ts'
```

### JavaScript lint plugins (2.2-guide)

Unstable lint plugins may be local TypeScript or JavaScript modules or npm/JSR packages, configured through `lint.plugins`. A plugin default-exports a named `Deno.lint.Plugin`; rules can use AST visitors or CSS-like selectors, but ESLint compatibility is not complete.

```json
{
  "lint": {
    "plugins": ["./my-plugin.ts", "jsr:@scope/lint-plugin", "npm:@scope/other-plugin"]
  }
}
```

### JSX and React lint rules (2.2-guide)

The built-in linter adds the `jsx` and `react` tags and 15 rules: `jsx-boolean-value`, `jsx-button-has-type`, `jsx-curly-braces`, `jsx-key`, `jsx-no-children-prop`, `jsx-no-comment-text-nodes`, `jsx-no-duplicate-props`, `jsx-no-unescaped-entities`, `jsx-no-useless-fragment`, `jsx-props-no-spread-multi`, `jsx-void-dom-elements-no-children`, `no-useless-rename`, `react-no-danger-with-children`, `react-no-danger`, and `react-rules-of-hooks`. `deno lint --rules` now always lists every rule and marks enabled ones; its JSON form links to rule documentation instead of embedding Markdown.

### Lint-plugin authoring surface (2.2.0)

The unstable JavaScript lint-plugin API now provides source-code helpers plus typed AST and visitor APIs aligned with TSESTree, with rule context closer to ESLint. Plugins can also use a destroy hook and return multiple fixes.

### Lint-plugin comment access (2.4-guide)

Lint-plugin visitors can access node comments, and `context.sourceCode` now provides `getAllComments()`, `getCommentsBefore()`, `getCommentsAfter()`, and `getCommentsInside()` helpers.

### Lint-plugin field selectors (2.3-guide)

Lint-plugin selector syntax now accepts field selectors such as `.<field>`, allowing a rule to target nodes occupying a particular AST field.

## Formatting

### Broader formatter input (2.0-guide)

`deno fmt` can format HTML, CSS, and YAML in addition to JavaScript and TypeScript.

### EditorConfig formatting defaults (2.9-guide)

`deno fmt` fills unset options from `.editorconfig`, with precedence CLI flags → `deno.json` → `.editorconfig` → built-in defaults.

### Embedded-language formatting and additional formatter controls (2.3-guide)

`deno fmt` formats CSS, HTML, and SQL inside tagged templates; SQL formatting still requires `--unstable-sql`. New controls are `bracePosition`, `jsx.bracketPosition`, `jsx.forceNewLinesSurroundingContent`, `jsx.multiLineParens`, `newLineKind`, `nextControlFlowPosition`, `operatorPosition`, `quoteProps`, `singleBodyPosition`, `spaceAround`, `spaceSurroundingProperties`, `trailingCommas`, `typeLiteral.separatorKind`, and `useBraces`.

```json
{
  "fmt": {
    "quoteProps": "asNeeded",
    "useBraces": "always",
    "trailingCommas": "always"
  }
}
```

### Explicit target for config-free formatting (2.5.0)

When no files are passed and no configuration file is discovered, `deno fmt` now prompts for or requires an explicit current-directory target. Scripts that relied on argument-free formatting should pass `.`.

```sh
deno fmt .
```

### Fail-fast formatting checks (2.7-guide)

`deno fmt --check --fail-fast` stops after finding the first unformatted file instead of scanning and reporting every mismatch.

### Formatter CLI behavior (2.3.0)

`deno fmt --ext` accepts `vto` and `njk`, and a formatting failure now produces a nonzero exit status so automation can detect it reliably.

### JSON trailing-comma policy (2.9-guide)

`fmt.json.trailingCommas` accepts `"never"` (the default), `"always"`, `"maintain"`, or `"jsonc"`; the last choice adds commas in JSONC and omits them in JSON.

```json
{
  "fmt": {
    "json": { "trailingCommas": "jsonc" }
  }
}
```

### Named import and export sorting (2.9-guide)

`sortNamedImports` and `sortNamedExports` select `"caseInsensitive"` (the default), `"caseSensitive"`, or `"maintain"` ordering for named specifiers.

```json
{
  "fmt": {
    "sortNamedImports": "maintain",
    "sortNamedExports": "caseSensitive"
  }
}
```

### Named import and export spacing (2.5-guide)

When `fmt.spaceSurroundingProperties` is `false`, the formatter now removes spaces inside named import and export braces as well as property braces, producing forms such as `import {foo} from "bar"`. The option still defaults to `true`.

### SQL formatting and ignored files (2.1-guide)

Unstable SQL formatting is enabled with `--unstable-sql` or the `fmt-sql` unstable feature. A first-line `-- deno-fmt-ignore-file` preserves SQL, the equivalent YAML directive starts with `#`, and both the formatter and linter now skip files listed in `.gitignore`.

```json
{ "unstable": ["fmt-sql"] }
```

```sh
deno fmt --unstable-sql
```

### Token-preserving non-JavaScript formatting (2.9-guide)

The HTML, XML, SVG, CSS, SCSS, Less, and SQL formatters now change only whitespace and pass malformed input through instead of failing or rewriting tokens. Indented `.sass` syntax is no longer supported; CSS-family and SQL formatting retain their existing unstable gates.

### UTF-8 BOM removal during formatting (2.4.0)

`deno fmt` now removes a leading UTF-8 byte-order mark instead of preserving it, so formatting a BOM-prefixed file changes its encoding bytes.

### XML, SVG, and Mustache formatting (2.4-guide)

`deno fmt` automatically recognizes `.xml` and `.svg`; `.mustache` formatting is available behind `--unstable-component` or the `unstable.fmt-component` configuration option.

```sh
deno fmt diagram.svg
deno fmt --unstable-component template.mustache
```
