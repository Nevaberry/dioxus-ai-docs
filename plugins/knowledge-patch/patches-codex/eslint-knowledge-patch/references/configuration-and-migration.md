# Configuration and Migration

Use this reference when aligning runtimes, migrating from eslintrc, debugging
flat-config discovery, configuring languages, or evaluating migration timing.

## Runtime and toolchain prerequisites

ESLint 10 drops Node.js versions earlier than 20.19.0 and all Node.js 21.x and
23.x releases (since 10.0.0). Check the runtime selected in both local tooling
and CI before investigating secondary failures.

Loading TypeScript configuration files through Jiti requires Jiti 2.2.0 or
later (since 10.0.0). This applies when Jiti is the path used to load files
such as `eslint.config.ts`.

TypeScript 5.3 is the minimum supported TypeScript version (since 10.2.0).
Account for that floor when upgrading parsers and other typed integrations.

## Configuration lookup starts from each linted file

Lookup for `eslint.config.*` starts from the directory of each linted file,
not the current working directory (since 10.0.0). Files passed to one command
can therefore resolve different configurations.

For each file whose behavior differs:

1. Locate the file's directory.
2. Determine which `eslint.config.*` lookup selects from there.
3. Compare that result with the configuration selected for the other files.
4. Do not infer selection from the directory in which ESLint was invoked.

The `v10_config_lookup_from_file` feature flag is removed because this lookup
behavior is the default.

## Legacy configuration removal

The eslintrc system is removed (since 10.0.0). There is no legacy fallback:

| Legacy mechanism | Behavior |
| --- | --- |
| `ESLINT_USE_FLAT_CONFIG` | Ignored |
| `.eslintrc.*` | Not read |
| `.eslintignore` | Not read |
| `/* eslint-env */` comments | Errors |
| `--no-eslintrc` | Removed |
| `--env` | Removed |
| `--resolve-plugins-relative-to` | Removed |
| `--rulesdir` | Removed |
| `--ignore-path` | Removed |

The programmatic legacy surface changes at the same boundary:

- `loadESLint()` always returns `ESLint`.
- `Linter` rejects `configType: "eslintrc"`.
- `Linter#defineParser()`, `defineRule()`, `defineRules()`, and `getRules()` are
  removed.
- `/use-at-your-own-risk` no longer exports `LegacyESLint` or
  `FileEnumerator`.
- `shouldUseFlatConfig()` always returns `true`.

Move ignored-file behavior, environments, local rules, parser resolution,
and plugin resolution out of those removed mechanisms rather than expecting
them to be translated automatically.

## Language-aware configurations and rules

Configuration objects can specify a `language` (since 10.2.0). Rule metadata
also supports `meta.languages`, allowing a rule to declare the languages with
which it is compatible.

Use both surfaces when configuring non-JavaScript language plugins or
publishing a rule intended to operate with more than one language.

## Bulk suppressions through the API

Bulk-suppression functionality is exposed programmatically (since 10.2.0).
Integrations can use this capability through the API and are no longer
limited to invoking the CLI workflow.

## Expanded recommended configuration

`eslint:recommended` includes additional rules (since 10.0.0). After an
upgrade, new diagnostics can come from the changed recommended set even when
the project's own configuration has not otherwise changed.

Run lint once before modifying rule settings, then distinguish newly
recommended diagnostics from configuration-discovery or parser failures.

## Maintenance lifecycle

The 9.x release line receives only critical, security, and cross-major
compatibility fixes during maintenance (10.0.0 guidance). Its end-of-life
date is 2026-08-06. Include that support deadline when deciding whether to
defer the migration.
