# Migration and Runtime Requirements

## Node.js support

Vite 6 supports Node.js 18, 20, and 22+, but does not support Node.js 21 (since
6.0.0). Do not infer support solely from Node.js 21 being newer than 20.

Vite 7 raises the runtime floor to Node.js 20.19+ or 22.12+ and drops Node.js 18
(since 7.0.0). Check exact minor versions in local development, CI, containers,
and deployment images.

These minimum releases provide unflagged `require(esm)`. That capability lets
Vite ship as an ESM-only package while keeping the JavaScript API loadable by
CommonJS callers.

## Default browser target

The default `build.target` changes from `'modules'` to
`'baseline-widely-available'` (since 7.0.0). This target is fixed for each Vite
major rather than moving continuously.

For Vite 7, the default browser versions are:

| Browser | Minimum |
| --- | --- |
| Chrome | 107 |
| Edge | 107 |
| Firefox | 104 |
| Safari | 16.0 |

Configure `build.target` explicitly if the product's required browsers differ
from these defaults.

## Vitest compatibility

Supported Vite 7 integration begins with Vitest 3.2 (since 7.0.0). Upgrade an
older Vitest dependency when moving to Vite 7; older versions are not the
supported pairing.

## Removed APIs

Vite 7 removes two deprecated facilities (since 7.0.0):

- Sass legacy API support.
- `splitVendorChunkPlugin`.

Locate and migrate either use before upgrading. A project that still depends on
one of them is not ready for the new major.
