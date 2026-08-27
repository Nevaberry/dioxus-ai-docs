# Migration and Runtime Requirements

## Check Node.js Support Before Upgrading

Vite `6.0.0` supports Node.js 18, 20, and 22+, but no longer supports Node.js
21.

Vite `7.0.0` raises the minimum to Node.js 20.19+ or 22.12+ and drops Node.js
18. Check the exact minor version in local development and CI; an arbitrary
Node.js 20 or 22 build may still be too old.

The Vite 7 minimums provide unflagged `require(esm)`. This permits Vite to ship
as ESM-only while its JavaScript API remains loadable from CommonJS.

## Revisit Browser Compatibility

In `7.0.0`, the default `build.target` changes from `'modules'` to
`'baseline-widely-available'`. The baseline is fixed for each Vite major. For
Vite 7, it means:

| Browser | Default minimum |
| --- | --- |
| Chrome | 107 |
| Edge | 107 |
| Firefox | 104 |
| Safari | 16.0 |

Set `build.target` explicitly if the product supports older browsers or has a
different browser contract. An omitted target no longer preserves the
previous compatibility profile.

## Upgrade Vitest With Vite

Support for Vite `7.0.0` begins with Vitest 3.2. Older Vitest releases are not
the supported pairing, so include a Vitest upgrade when moving the project to
Vite 7.

## Remove Deleted Interfaces

Vite `7.0.0` removes two deprecated interfaces:

- Sass legacy API support.
- `splitVendorChunkPlugin`.

Search the project and its build configuration for both before upgrading:

```sh
rg "splitVendorChunkPlugin|legacy API" .
```

Migrate any remaining use before expecting the Vite 7 build to succeed.
