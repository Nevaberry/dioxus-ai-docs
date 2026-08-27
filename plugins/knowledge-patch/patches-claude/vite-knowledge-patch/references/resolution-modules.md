# Resolution and Module Interoperability

## Account for the ESM-Only Distribution

Vite `7.0.0` requires Node.js 20.19+ or 22.12+. Those runtimes provide
unflagged `require(esm)`, allowing Vite to ship as ESM-only while keeping its
JavaScript API loadable from CommonJS.

When a CommonJS consumer cannot load the Vite JavaScript API, first verify the
exact Node.js minor version. Node.js 18 is no longer supported, and an older
minor of Node.js 20 or 22 does not satisfy the Vite 7 floor.

## Import WebAssembly Exports Directly

Since `8.1.0`, Vite supports WebAssembly ESM integration. Named exports from a
`.wasm` file can be imported directly:

```ts
import { add } from './add.wasm'

console.log(add(1, 2))
```

This direct ESM form does not require the earlier `?init` wrapper.
