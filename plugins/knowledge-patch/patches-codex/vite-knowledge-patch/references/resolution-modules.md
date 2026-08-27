# Resolution and Module Interoperability

## ESM-only distribution with CommonJS loading

Vite 7 is distributed as ESM-only, enabled by its Node.js 20.19+ or 22.12+
runtime floors and those releases' unflagged `require(esm)` support (since
7.0.0).

The JavaScript API remains loadable from CommonJS. Distinguish the package's
distribution format from caller interoperability: the ESM-only change does not
by itself require every CommonJS caller to be converted before it can load
Vite.

If loading fails, verify the exact Node.js minor version first. Earlier Node.js
20 or 22 releases do not satisfy Vite 7's runtime floor.

## Direct WebAssembly ESM imports

Vite supports WebAssembly ESM integration with direct exports from `.wasm`
files (since 8.1.0):

```ts
import { add } from './add.wasm'

console.log(add(1, 2))
```

Use named imports from the WebAssembly module when direct ESM integration fits
the module. A `?init` wrapper is not required for this form.
