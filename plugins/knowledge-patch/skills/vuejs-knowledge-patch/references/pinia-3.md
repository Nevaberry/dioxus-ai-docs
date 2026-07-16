# Pinia 3

## TypeScript requirement

Pinia 3 uses TypeScript's native `Awaited` utility type (3.0.0). Projects that
compile against Pinia's declarations therefore need TypeScript 4.5 or newer.

## Package formats

The package declares `"type": "module"`, but it continues to publish CommonJS
distribution files for CJS consumers (3.0.0). Do not interpret the package
metadata as removal of the provided CommonJS builds.

## Standalone IIFE build

The standalone IIFE build no longer bundles Vue Devtools because of its size
(3.0.0). Include Devtools separately when an IIFE-based workflow relies on it.
