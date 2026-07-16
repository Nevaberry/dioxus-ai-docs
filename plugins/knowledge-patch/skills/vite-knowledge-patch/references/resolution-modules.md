# Resolution and Module Interoperability

## ESM-only Vite package

Vite ships as ESM-only beginning with Vite 7 (since 7.0.0). Its Node.js runtime
minimums—20.19+ or 22.12+—supply unflagged `require(esm)`, so the Vite JavaScript
API remains loadable from CommonJS even though the distributed package is ESM.

Do not interpret ESM-only distribution as meaning that every API consumer must
first be rewritten to ESM. Do ensure that CommonJS consumers run on one of the
supported Node.js versions.

## Direct WebAssembly ESM imports

Vite supports WebAssembly ESM integration (since 8.1.0). Import exports directly
from a `.wasm` module:

```ts
import { add } from './add.wasm'

console.log(add(1, 2))
```

This direct ESM form does not require the earlier `?init` wrapper.
