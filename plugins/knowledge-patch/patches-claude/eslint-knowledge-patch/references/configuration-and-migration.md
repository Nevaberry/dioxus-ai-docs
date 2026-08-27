# Configuration and Migration

Use this reference for runtime compatibility, flat-config discovery, language
selection, suppression integrations, recommended-rule changes, and migration
planning.

## Runtime prerequisites

Since 10.0.0, ESLint requires Node.js 20.19.0 or later and excludes all Node.js
21.x and 23.x releases. A numerically newer odd-numbered runtime is not
automatically supported, so check the exact local and CI versions.

Loading `eslint.config.ts` or another TypeScript configuration through Jiti
requires Jiti 2.2.0 or later. Verify both prerequisites before diagnosing a
TypeScript config that does not load.

## Config lookup starts from each linted file

Since 10.0.0, ESLint begins `eslint.config.*` discovery in the directory of
each linted file, not the current working directory. A single command can find
different configs for files in different directories.

For monorepos and nested projects:

1. Identify the directory of each lint target.
2. Walk config discovery from that directory.
3. Compare the selected config for targets with different results.
4. Do not infer selection from the directory where the command was invoked.

The `v10_config_lookup_from_file` feature flag was removed because per-file
lookup is now the default.

## Removed eslintrc configuration

Since 10.0.0, the eslintrc system is unavailable. Do not use a legacy fallback
when migrating or debugging.

| Legacy mechanism | Behavior |
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

Move ignore patterns, globals, environments, plugin resolution, and local
rules into flat configuration rather than trying to preserve the deleted
flags or files.

### Removed programmatic legacy surface

The API follows the same flat-only contract:

- `loadESLint()` always returns `ESLint`.
- `Linter` rejects `configType: "eslintrc"`.
- `Linter#defineParser()`, `defineRule()`, `defineRules()`, and `getRules()` no
  longer exist.
- `/use-at-your-own-risk` no longer exports `LegacyESLint` or
  `FileEnumerator`.
- `shouldUseFlatConfig()` always returns `true`.

Update callers to construct flat configuration and use supported plugin APIs.
Do not branch on `shouldUseFlatConfig()` or expect `loadESLint()` to select a
legacy implementation.

## Language-aware configuration

Since 10.2.0, a configuration object can specify `language`. Rule metadata can
also define `meta.languages`, allowing a rule to declare which languages it
supports.

For a non-JavaScript language plugin:

1. Select the language in the matching configuration object.
2. Declare compatible languages in each published rule's metadata.
3. Treat compatibility as rule-specific when a plugin serves multiple
   languages.

## Programmatic bulk suppressions

Since 10.2.0, bulk-suppression functionality is exposed through the API.
Integrations can invoke it directly instead of being limited to the CLI
workflow. Prefer the programmatic surface when suppression generation is part
of an editor, build service, or other in-process tool.

## Recommended configuration changes

Since 10.0.0, `eslint:recommended` contains additional rules. An upgrade can
therefore produce new diagnostics even when the project configuration is
otherwise unchanged.

When triaging new findings:

1. Run lint before changing configuration.
2. Separate diagnostics from newly recommended rules from config-discovery
   failures.
3. Review or configure the newly active rules deliberately.

## TypeScript compatibility floor

Since 10.2.0, the documented minimum supported TypeScript version is 5.3.
Check the compiler version as well as parser and typed-integration versions
when an ESLint upgrade exposes TypeScript compatibility failures.

## ESLint 9 maintenance window

As documented with 10.0.0, ESLint 9.x is limited to critical, security, and
cross-major compatibility fixes during maintenance. It reaches end of life on
2026-08-06. Account for this date when deciding whether to defer migration to
ESLint 10.
