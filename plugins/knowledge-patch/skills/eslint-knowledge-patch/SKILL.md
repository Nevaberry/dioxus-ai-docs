---
name: eslint-knowledge-patch
description: ESLint
version: 10.0.0
license: MIT
metadata:
  author: Nevaberry
---

# ESLint Knowledge Patch

Load this skill when upgrading ESLint, diagnosing flat-config discovery,
maintaining custom rules or formatters, or updating rule tests and typed
integrations. Start with the breaking-change checks below, then open the
topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [Configuration and migration](references/configuration-and-migration.md) | Runtime prerequisites, config lookup, legacy configuration removal, recommended rules, release lifecycle |
| [Rules, tests, and integrations](references/rules-tests-and-integrations.md) | Rule API replacements, `RuleTester`, TypeScript parameters, JSX scope, AST ranges, bundled types, formatter color intent |

## Upgrade triage

For an ESLint 10 upgrade, check these areas in order:

1. Confirm the Node.js runtime is at least 20.19.0 and is not Node.js 21.x or
   23.x.
2. If `eslint.config.ts` or another TypeScript config is loaded through Jiti,
   require Jiti 2.2.0 or later.
3. Remove reliance on `.eslintrc.*`, `.eslintignore`, `/* eslint-env */`, and
   deleted legacy CLI flags.
4. Re-evaluate config selection now that lookup starts beside every linted
   file rather than at the process working directory.
5. Update custom rules and plugins away from removed `context` and
   `SourceCode` APIs.
6. Tighten or repair `RuleTester` cases with the appropriate
   `assertionOptions` contract.
7. Re-run lint without changing configuration first: `eslint:recommended`
   enables additional rules and may produce new diagnostics.

## Breaking: runtime prerequisites

ESLint 10 does not support:

- Node.js versions earlier than 20.19.0
- any Node.js 21.x release
- any Node.js 23.x release

TypeScript configuration loading through Jiti requires Jiti 2.2.0 or later.
Check both the runtime selected by local tooling or CI and the installed Jiti
version before diagnosing configuration-load failures.

## Breaking: configuration is resolved per file

Configuration lookup now begins in the directory of each linted file. It no
longer begins in the current working directory.

One command can therefore select different `eslint.config.*` files for files
in different directories. In a monorepo or nested project, reason about each
target file separately:

1. Identify the linted file's directory.
2. Determine which config is found from that directory.
3. Repeat for each target that behaves differently.
4. Do not use the invocation directory as the lookup anchor.

The `v10_config_lookup_from_file` feature flag has been removed because this
behavior is the default.

## Breaking: the eslintrc system is gone

Do not use the legacy configuration path as a fallback. ESLint 10 behaves as
follows:

| Legacy mechanism | ESLint 10 behavior |
| --- | --- |
| `ESLINT_USE_FLAT_CONFIG` | Ignored |
| `.eslintrc.*` | Not read |
| `.eslintignore` | Not read |
| `/* eslint-env */` comments | Reported as errors |
| `--no-eslintrc` | Removed |
| `--env` | Removed |
| `--resolve-plugins-relative-to` | Removed |
| `--rulesdir` | Removed |
| `--ignore-path` | Removed |

The programmatic legacy surface is also removed:

- `loadESLint()` always returns `ESLint`.
- `Linter` rejects `configType: "eslintrc"`.
- `Linter#defineParser()`, `defineRule()`, `defineRules()`, and `getRules()`
  no longer exist.
- `/use-at-your-own-risk` no longer exports `LegacyESLint` or
  `FileEnumerator`.
- `shouldUseFlatConfig()` always returns `true`.

See
[Configuration and migration](references/configuration-and-migration.md)
for the complete migration inventory and config-discovery implications.

## Breaking: deprecated rule APIs are removed

Replace removed context methods with properties:

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
cases as redesign points rather than trying to preserve the old call shape.

## Testing: enforce complete `RuleTester` errors

`RuleTester#run()` accepts an `assertionOptions` object:

- `requireMessage: true` accepts either `message` or `messageId`.
- `requireMessage: "message"` requires `message`.
- `requireMessage: "messageId"` requires `messageId`.
- `requireLocation: true` requires both `line` and `column`.
- `requireData: true` requires `data` when a `messageId` template contains
  placeholders.

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

Choose the strictness that matches the rule's public contract. When
`requireData` is enabled, inspect the selected message template before
deciding whether a test case needs `data`.

## Rules: TypeScript `this` parameters

The `max-params` rule has `countThis: "never"`, which excludes a TypeScript
`this` parameter from the parameter count. It supersedes the deprecated
`countVoidThis` option.

```js
export default [{
  rules: {
    "max-params": ["error", { max: 2, countThis: "never" }]
  }
}];
```

## Scope analysis: JSX identifiers are references

An identifier such as `Card` in `<Card />` is a normal reference to the
in-scope variable. Scope-based rules should no longer:

- report an imported JSX component as unused solely because its use is JSX;
- miss an undefined component solely because its use is JSX.

Account for this when updating expected diagnostics for scope-sensitive
rules.

## AST integrations: `Program.range`

The `Program` node's range includes the entire source, including leading and
trailing comments and whitespace. Code that assumed the previous narrower
range must not use `Program.range` as a proxy for only the inner program
content.

## Typed integrations

Espree 11.1.0 and ESLint Scope 9.1.0 ship built-in type definitions. These
replace declarations formerly supplied by `@types/espree` and
`@types/eslint-scope`, but the built-in definitions are not identical.
Expect typed integrations to need adjustments rather than assuming a
drop-in declaration swap.

## Formatter integrations

When the CLI receives `--color` or `--no-color`, it passes explicit intent in
the second argument to a formatter's `format()` method:

- `--color` produces `color: true`.
- `--no-color` produces `color: false`.

Custom formatters can read this value and honor the user's explicit styling
choice.

## Recommended configuration and support window

The ESLint 10 `eslint:recommended` configuration contains additional rules.
New diagnostics after an upgrade may therefore be caused by the changed
recommended set even when project configuration is otherwise unchanged.

ESLint 9.x is in maintenance for critical, security, and cross-major
compatibility fixes only, and reaches end of life on 2026-08-06. Use that
date when deciding whether to defer an ESLint 10 migration.

For exhaustive details, edge conditions, and API inventories, follow the
reference index rather than inferring legacy compatibility.
