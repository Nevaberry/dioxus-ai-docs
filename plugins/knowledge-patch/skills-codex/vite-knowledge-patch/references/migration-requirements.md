# Migration and Runtime Requirements

## Node.js support in Vite 6

Vite 6 supports Node.js 18, 20, and 22+, but no longer supports Node.js 21
(since 6.0.0). Check development machines and CI images rather than assuming
that every recent Node.js line is supported.

## Node.js requirements in Vite 7

Vite 7 requires Node.js 20.19+ or 22.12+ and drops Node.js 18 (since 7.0.0).
The minimum minor versions matter: earlier Node.js 20 and 22 releases do not
meet the requirement.

The new floors provide unflagged `require(esm)`. That allows Vite to be
distributed as ESM-only while its JavaScript API remains loadable from
CommonJS. Do not read the ESM-only package change as a requirement to rewrite
every CommonJS caller before it can load Vite's JavaScript API.

Use the actual runtime as the migration gate:

```sh
node --version
```

Check both local tooling and all CI or deployment images that execute Vite.

## Default browser target

Vite 7 changes the default `build.target` from `'modules'` to
`'baseline-widely-available'` (since 7.0.0). The value is fixed for each Vite
major rather than moving continuously. In Vite 7 it resolves to:

- Chrome 107
- Edge 107
- Firefox 104
- Safari 16.0

Audit the application's browser-support contract during an upgrade. Set
`build.target` explicitly if these defaults are too new or unnecessarily old;
do not assume an unset target preserves the output compatibility of an older
Vite major.

## Vitest compatibility

Official Vite 7 support starts with Vitest 3.2 (since 7.0.0). When a project
uses an older Vitest version, upgrade it as part of the Vite migration before
debugging failures as if they were application regressions.

## Removed APIs

Vite 7 removes Sass legacy API support and `splitVendorChunkPlugin` (since
7.0.0). Search for both before changing the Vite major:

```sh
rg "splitVendorChunkPlugin|legacy API" .
```

Migrate Sass integrations to a supported API and replace any dependency on
`splitVendorChunkPlugin`. An upgrade is not complete while either removed
surface remains in project or plugin configuration.
