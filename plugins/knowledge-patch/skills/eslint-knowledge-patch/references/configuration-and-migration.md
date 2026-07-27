# Configuration and Migration

The changes in this reference apply to ESLint 10.0.0.

## Runtime prerequisites

ESLint 10 drops all Node.js versions before 20.19.0. It also drops every
Node.js 21.x and 23.x release.

Loading a TypeScript configuration file through Jiti requires Jiti 2.2.0 or
later. When a JavaScript config works but a TypeScript config does not, check
the Jiti version as well as the Node.js runtime.

## Configuration lookup begins at each target

For every linted file, lookup for `eslint.config.*` begins in that file's
directory. It no longer begins in the current working directory.

This changes the unit of reasoning from one invocation to one target file.
A single invocation can lint files that select different configurations. If
two files behave differently, determine the lookup result from each file's
own directory before comparing their effective configuration.

The `v10_config_lookup_from_file` feature flag no longer exists. Per-file
lookup is the default behavior, so retaining or trying to toggle the flag
cannot restore the old lookup rule.

## Legacy configuration removal

The eslintrc system is removed. The environment variable
`ESLINT_USE_FLAT_CONFIG` is ignored, and neither `.eslintrc.*` nor
`.eslintignore` is read.

Legacy environment comments are not a compatibility path:

```js
/* eslint-env node */
```

An `/* eslint-env */` comment is an error under ESLint 10.

The following legacy CLI options are gone:

- `--no-eslintrc`
- `--env`
- `--resolve-plugins-relative-to`
- `--rulesdir`
- `--ignore-path`

Remove these flags from package scripts, CI commands, editor integrations,
and wrappers rather than expecting them to be ignored uniformly.

## Programmatic legacy removal

The Node.js API no longer offers a legacy engine selection:

- `loadESLint()` always returns `ESLint`.
- `Linter` rejects `configType: "eslintrc"`.
- `Linter#defineParser()` is removed.
- `Linter#defineRule()` is removed.
- `Linter#defineRules()` is removed.
- `Linter#getRules()` is removed.
- `/use-at-your-own-risk` no longer exports `LegacyESLint`.
- `/use-at-your-own-risk` no longer exports `FileEnumerator`.
- `shouldUseFlatConfig()` always returns `true`.

Audit integrations for both direct imports and feature-detection branches.
A branch around `shouldUseFlatConfig()` cannot select eslintrc behavior
because its result is always true.

## Recommended configuration expansion

`eslint:recommended` includes additional rules in ESLint 10. An unchanged
project configuration can consequently produce new diagnostics after the
upgrade.

When triaging new findings, distinguish diagnostics introduced by the
expanded recommended set from diagnostics caused by config lookup or rule
behavior. This avoids misattributing every new report to per-file config
selection.

## ESLint 9 maintenance lifecycle

ESLint 9.x receives only critical, security, and cross-major compatibility
fixes during its maintenance period. Its end-of-life date is 2026-08-06.

Treat continued use of 9.x as a time-bounded migration decision, especially
when relying on a legacy configuration or API that no longer exists in
ESLint 10.
