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
custom rules or formatters, updating rule tests, or debugging typed and AST
integrations. Start with the breaking-change checks, then open the reference
that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [Configuration and migration](references/configuration-and-migration.md) | Runtime support, flat-config discovery, legacy removal, language selection, suppressions, recommended rules, lifecycle |
| [Rules, tests, and integrations](references/rules-tests-and-integrations.md) | Rule APIs, `RuleTester`, TypeScript and JSX behavior, AST ranges, autofixes, bundled types, formatters |

## Upgrade triage

For an ESLint 10 upgrade, check these areas in order:

1. Confirm Node.js is at least 20.19.0 and is not a 21.x or 23.x release.
2. Require Jiti 2.2.0 or later when it loads a TypeScript config.
3. Remove `.eslintrc.*`, `.eslintignore`, `/* eslint-env */`, and deleted
   legacy CLI flags.
4. Resolve configuration from each linted file's directory, not from the
   invocation directory.
5. Update custom rules away from removed `context` and `SourceCode` APIs.
6. Repair `RuleTester` cases and select deliberate `assertionOptions`.
7. Re-run the recommended configuration and review newly enabled rules.
8. For typed integrations, require TypeScript 5.3 or later and review the
   bundled Espree and ESLint Scope declarations.

## Runtime gates

ESLint 10 does not support:

- Node.js versions earlier than 20.19.0;
- any Node.js 21.x release;
- any Node.js 23.x release.

TypeScript configuration loading through Jiti requires Jiti 2.2.0 or later.
Check the runtime used by local scripts and every CI job before investigating
config-load failures.

## Configuration is resolved per linted file

Configuration lookup starts beside each linted file. One command can therefore
select different `eslint.config.*` files for targets in different directories.

When files behave differently:

1. Start at the first target file's directory.
2. Determine which config is discovered from there.
3. Repeat for each other target.
4. Do not use the process working directory as the lookup anchor.

The `v10_config_lookup_from_file` feature flag is gone because this behavior is
the default.

## Flat configuration is the only configuration system

Do not fall back to eslintrc behavior in ESLint 10.

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

The programmatic legacy surface is removed too:

- `loadESLint()` always returns `ESLint`.
- `Linter` rejects `configType: "eslintrc"`.
- `Linter#defineParser()`, `defineRule()`, `defineRules()`, and `getRules()` are
  unavailable.
- `/use-at-your-own-risk` no longer exports `LegacyESLint` or
  `FileEnumerator`.
- `shouldUseFlatConfig()` always returns `true`.

## Replace removed rule APIs

Use properties in place of removed context accessors:

| Removed | Replacement |
| --- | --- |
| `context.getCwd()` | `context.cwd` |
| `context.getFilename()` | `context.filename` |
| `context.getPhysicalFilename()` | `context.physicalFilename` |
| `context.getSourceCode()` | `context.sourceCode` |
| `context.parserOptions` | `context.languageOptions` or `context.languageOptions.parserOptions` |

`context.parserPath` has no replacement.

Use these `SourceCode` replacements:

| Removed | Replacement |
| --- | --- |
| `getTokenOrCommentBefore()` | `getTokenBefore()` with `{ includeComments: true }` |
| `getTokenOrCommentAfter()` | `getTokenAfter()` with `{ includeComments: true }` |
| `isSpaceBetweenTokens()` | `isSpaceBetween()` |

`SourceCode#getJSDocComment()` has no replacement. Treat both no-replacement
cases as integration redesign points.

## Make `RuleTester` expectations explicit

`RuleTester#run()` accepts `assertionOptions`:

- `requireMessage: true` accepts either `message` or `messageId`.
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

Choose strictness to match the rule's public test contract. Inspect the message
template before deciding whether `requireData` requires a `data` object.

## Language-aware configuration and rules

Configuration objects can set `language`. Rule metadata can set
`meta.languages` to declare language compatibility. Use both when configuring
non-JavaScript language plugins or publishing a multi-language rule.

With ES2026 globals enabled, `Temporal` is defined but non-callable.
`no-obj-calls` reports `Temporal()` instead of treating `Temporal` as an
undefined name.

## TypeScript-specific rule behavior

`max-params` supports `countThis: "never"`, which excludes a TypeScript `this`
parameter and supersedes the deprecated `countVoidThis` option.

```js
export default [{
  rules: {
    "max-params": ["error", { max: 2, countThis: "never" }]
  }
}];
```

`no-var` can fix declarations inside `TSModuleBlock`. It withholds the autofix
when a variable is used before its declaration, avoiding an unsafe conversion.

## Re-check rule results after patch upgrades

In 10.8.1, removal edits from `no-unused-labels` and the `removeVar` suggestion
from `no-unused-vars` avoid automatic-semicolon-insertion hazards. The edits no
longer risk joining adjacent syntax into a different parse.

Also in 10.8.1:

- `id-denylist` and `id-match` ignore grammar-defined meta-property names such
  as `meta` in `import.meta` and `target` in `new.target`.
- `getter-return` and `accessor-pairs` avoid corrected false positives.

Revisit suppressions or disabled rules that worked around those diagnostics.

## Integration checks

- JSX component identifiers are ordinary scope references. Scope-based rules
  should neither mark a JSX-only import unused nor miss an undefined JSX name.
- `Program.range` covers the entire source, including leading and trailing
  comments and whitespace.
- Espree 11.1.0 and ESLint Scope 9.1.0 provide built-in types. Remove redundant
  `@types/espree` and `@types/eslint-scope` declarations carefully because the
  bundled types are not identical.
- Formatter `format()` receives explicit `color: true` or `color: false` in
  its second argument for `--color` or `--no-color`.
- Bulk-suppression functionality is available programmatically; integrations
  need not shell out to the CLI workflow.

## Final migration check

The ESLint 10 `eslint:recommended` set enables additional rules, so new
diagnostics do not necessarily mean configuration discovery failed. Run lint
without changing configuration first and classify the new findings.

ESLint 9.x receives only critical, security, and cross-major compatibility
fixes during maintenance and reaches end of life on 2026-08-06. Use that date
when evaluating a deferred migration.
