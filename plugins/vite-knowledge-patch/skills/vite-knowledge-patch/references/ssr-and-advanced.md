# SSR & Advanced Features

## `.wasm?init` Works in SSR (8.0)

WebAssembly `.wasm?init` imports now work in SSR environments, not just client-side:

```js
import init from './module.wasm?init'
const instance = await init()
```

## Built-in `emitDecoratorMetadata` Support (8.0-beta)

Vite 8 automatically handles TypeScript's `emitDecoratorMetadata` when enabled in tsconfig — no extra plugins or config needed.

## Environment API: `buildApp` Hook (7.0, experimental)

New plugin hook to coordinate building of multiple environments. See the Environment API for Frameworks guide for details.
