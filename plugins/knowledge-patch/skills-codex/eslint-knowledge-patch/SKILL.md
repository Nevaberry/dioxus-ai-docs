---
name: eslint-knowledge-patch
description: ESLint
version: 10.0.0
license: MIT
metadata:
  author: Nevaberry
---


# ESLint Knowledge Patch

Load this skill when upgrading ESLint, migrating configuration, maintaining
custom rules or formatters, updating rule tests, or repairing typed and AST
integrations. Begin with the breaking-change checks, then open the reference
that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [Configuration and migration](references/configuration-and-migration.md) | Runtime prerequisites, flat-config discovery, legacy removal, language-aware configuration, suppressions, recommended rules, support lifecycle |
| [Rules, tests, and integrations](references/rules-tests-and-integrations.md) | Rule API replacements, `RuleTester`, TypeScript and JSX behavior, AST ranges, bundled types, formatter context, autofix safety |

## Upgrade triage

Check these areas in order:

1. Confirm that Node.js is at least 20.19.0 and is not a 21.x or 23.x
   release.
2. If TypeScript configuration is loaded through Jiti, require Jiti 2.2.0 or
   later.
3. Remove reliance on `.eslintrc.*`, `.eslintignore`, `/* eslint-env */`, and
   deleted legacy CLI flags.
4. Resolve configuration from each linted file's directory, not from the
   invocation directory.
5. If TypeScript is part of the toolchain, require TypeScript 5.3 or later.
6. Update custom rules and plugins away from removed `context` and
   `SourceCode` APIs.
7. Revisit `RuleTester` assertions and scope-sensitive JSX expectations.
8. Run lint before changing rules: `eslint:recommended` can add diagnostics
   after the upgrade.

## Breaking: runtime prerequisites

The supported Node.js runtime is:

- Node.js 20.19.0 or later on supported release lines;
- no Node.js 21.x release;
- no Node.js 23.x release.

Loading `eslint.config.ts` or another TypeScript configuration through Jiti
requires Jiti 2.2.0 or later. Check both the runtime selected by local tooling
or CI and the installed Jiti version when configuration loading fails.

TypeScript 5.3 is the minimum supported TypeScript version. Account for that
minimum when aligning parsers and typed integrations.

## Breaking: configuration resolves per linted file

Lookup for `eslint.config.*` begins in the directory of each linted file. It
does not begin in the current working directory.

One invocation can consequently select different configurations for files in
different directories. For monorepos and nested projects:

1. Start with the linted file's directory.
2. Determine which `eslint.config.*` that file selects.
3. Repeat for each target that behaves differently.
4. Do not treat the shell's working directory as the lookup anchor.

The `v10_config_lookup_from_file` feature flag is removed because per-file
lookup is the default.

## Breaking: the eslintrc system is removed

Do not use the legacy configuration path as a fallback.

| Legacy mechanism | Current behavior |
| --- | --- |
| `ESLINT_USE_FLAT_CONFIG` | Ignored |
| `.eslintrc.*` | Not read |
| `.eslintignore` | Not read |
| `/* eslint-env */` | Reported as an error |
| `--no-eslintrc` | Removed |
| `--env` | Removed |
| `--resolve-plugins-relative-to` | Removed |
| `--rulesdir` | Removed |
| `--ignore-path` | Removed |

The programmatic legacy surface is also gone:

- `loadESLint()` always returns `ESLint`.
- `Linter` rejects `configType: "eslintrc"`.
- `Linter#defineParser()`, `defineRule()`, `defineRules()`, and `getRules()` no
  longer exist.
- `/use-at-your-own-risk` no longer exports `LegacyESLint` or
  `FileEnumerator`.
- `shouldUseFlatConfig()` always returns `true`.

See [Configuration and migration](references/configuration-and-migration.md)
for language-aware configuration, the bulk-suppression API, and migration
details.

## Breaking: deprecated rule APIs are removed

Replace removed `context` methods with properties:

| Removed | Use |
| --- | --- |
| `context.getCwd()` | `context.cwd` |
| `context.getFilename()` | `context.filename` |
| `context.getPhysicalFilename()` | `context.physicalFilename` |
| `context.getSourceCode()` | `context.sourceCode` |
| `context.parserOptions` | `context.languageOptions` or `context.languageOptions.parserOptions` |

`context.parserPath` has no replacement.

Replace removed `SourceCode` methods as follows:

| Removed | Use |
| --- | --- |
| `getTokenOrCommentBefore()` | `getTokenBefore()` with `{ includeComments: true }` |
| `getTokenOrCommentAfter()` | `getTokenAfter()` with `{ includeComments: true }` |
| `isSpaceBetweenTokens()` | `isSpaceBetween()` |

`SourceCode#getJSDocComment()` has no replacement. Treat both no-replacement
cases as redesign points instead of preserving the old call shape.

## Testing: require complete `RuleTester` errors

`RuleTester#run()` accepts an `assertionOptions` object:

- `requireMessage: true` permits either `message` or `messageId`.
- `requireMessage: "message"` requires `message`.
- `requireMessage: "messageId"` requires `messageId`.
- `requireLocation: true` requires both `line` and `column`.
- `requireData: true` requires `data` when the selected `messageId` template
  contains placeholders.

```js
ruleTester.run("my-rule", rule, {
  valid: [],
  invalid: [{
    code: "foo",
    errors: [{
      messageId: "unexpected",
      data: { name: "foo" },
      line: 1,
      column: 1
    }]
  }],
  assertionOptions: {
    requireMessage: "messageId",
    requireLocation: true,
    requireData: true
  }
});
```

Choose assertion strictness to match the rule's public contract. Before
requiring `data`, inspect whether the chosen message template has
placeholders.

## Configuration and rule additions

Configuration objects can specify a `language`. Rule metadata can declare
compatibility through `meta.languages`, which is relevant to non-JavaScript
language plugins and rules intended for multiple languages.

The ES2026 global set includes `Temporal`. Because `no-obj-calls` recognizes
it as a non-callable object, `Temporal()` is reported when ES2026 globals are
enabled.

For `max-params`, `countThis: "never"` excludes a TypeScript `this` parameter
from the count and supersedes deprecated `countVoidThis`:

```js
export default [{
  rules: {
    "max-params": ["error", { max: 2, countThis: "never" }]
  }
}];
```

The bulk-suppression workflow is exposed programmatically, so integrations
can use the API instead of being limited to the CLI workflow.

## Scope and AST integration checks

An identifier such as `Card` in `<Card />` is a normal reference to the
in-scope variable. Scope-based rules should neither report an imported JSX
component as unused solely because its use is JSX nor miss an undefined
component solely because it appears in JSX.

The `Program` node's `range` covers the entire source, including leading and
trailing comments and whitespace. Do not use it as a proxy for only the inner
program content.

Espree 11.1.0 and ESLint Scope 9.1.0 include built-in type definitions. They
replace declarations from `@types/espree` and `@types/eslint-scope`, but are
not identical; typed integrations can require adjustments.

## Autofix and diagnostic corrections

`no-var` can fix declarations inside TypeScript `TSModuleBlock` nodes. It
withholds the autofix when a variable is used before its declaration, avoiding
an unsafe conversion.

The `no-unused-labels` autofix and the `removeVar` suggestion from
`no-unused-vars` account for automatic semicolon insertion when removing code,
so their edits do not join adjacent syntax in a way that changes parsing.

`id-denylist` and `id-match` ignore grammar-defined meta-property names such
as `meta` in `import.meta` and `target` in `new.target`.

Corrected false positives in `getter-return` and `accessor-pairs` mean that
projects carrying suppressions or disabled settings for those diagnostics
should re-check them after upgrading.

See [Rules, tests, and integrations](references/rules-tests-and-integrations.md)
for the full behavior and migration inventory.

## Formatter integration

When the CLI receives `--color` or `--no-color`, the second argument to a
formatter's `format()` method contains explicit intent:

- `--color` produces `color: true`.
- `--no-color` produces `color: false`.

Custom formatters can read that value and honor the requested styling.

## Recommended rules and maintenance

`eslint:recommended` includes additional rules, so an upgrade can produce new
diagnostics even when project configuration is otherwise unchanged.

The 9.x line receives only critical, security, and cross-major compatibility
fixes during maintenance and reaches end of life on 2026-08-06. Use that date
when deciding whether to defer migration.
