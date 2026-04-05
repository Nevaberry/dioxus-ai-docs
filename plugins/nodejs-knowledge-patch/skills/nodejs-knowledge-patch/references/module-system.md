# Module System, TypeScript & Compile Cache

## require(esm) -- Default Since v23.0

`require()` can now load ES modules that don't use top-level `await`. This was behind `--experimental-require-module` in v22; unflagged in v23.

### How It Works

- If an ES module has no top-level `await`, `require()` loads it synchronously
- If top-level `await` is present, `require()` throws `ERR_REQUIRE_ASYNC_MODULE`
- `process.features.require_module` returns `true` when enabled

### `module-sync` Exports Condition

New exports condition lets packages serve the same ESM source to both `require()` and `import`:

```json
{
  "type": "module",
  "exports": {
    "module-sync": "./index.js",
    "import": "./index.js",
    "require": "./index.cjs"
  }
}
```

When `require(esm)` is supported, Node.js picks `module-sync` for `require()` calls, avoiding CJS wrappers.

### CJS Named Exports from ESM Wrapper

The ESM CJS wrapper now exports `module.exports` members as named exports:

```js
// cjs-module.cjs
module.exports = { foo: 1, bar: 2 };

// esm-consumer.mjs
import { foo, bar } from './cjs-module.cjs';  // works in v23+
```

## Native TypeScript Support

### Timeline

| Version | Status |
|---------|--------|
| 23.6 | `--experimental-strip-types` unflagged, enabled by default |
| 24.x | Continued improvements (amaro transformer updated) |
| 25.2 | Type stripping marked **stable** |

### Usage

```bash
node file.ts                                      # Direct execution
node --eval 'const x: number = 1; console.log(x)' # Eval with TS
```

Workers also accept TypeScript eval input:

```js
new Worker('const x: number = 42; postMessage(x)', { eval: true });
```

### Limitations

Type stripping only -- no code transformation/downleveling:

- No `namespace` keyword (use ES modules instead)
- No legacy decorators that emit code (TC39 decorators that are type-only work)
- No `const enum` across files (single-file `const enum` works)
- No `import =` / `export =` (use standard import/export)
- Enums are supported but inlined (each file standalone)

## import.meta Properties (stable v24+)

```js
import.meta.filename  // Absolute file path (like __filename)
import.meta.dirname   // Directory path (like __dirname)
import.meta.url       // file:// URL
import.meta.resolve   // URL resolver (stable since v22)
```

`filename` and `dirname` graduated from experimental to stable in v24.

## Compile Cache

### enableCompileCache() and flushCompileCache() (v23+)

```js
import { enableCompileCache, flushCompileCache } from 'node:module';

enableCompileCache();        // Enable V8 code caching
flushCompileCache();         // Flush pending cache writes
```

Cache is written atomically (temp file then rename).

### Portable Compile Cache (v25+)

```bash
node --compile-cache-portable app.js
```

Enables sharing the compile cache across different machines or paths. Without this flag, cache entries are path-specific.

## WebAssembly Module Imports (unflagged v24.5+)

`--experimental-wasm-modules` removed; Wasm imports work by default.

### Instance Phase Import

```js
// Gets an instantiated module -- exports available directly
import { add, multiply } from './math.wasm';
console.log(add(1, 2));
```

### Source Phase Import

```js
// Gets the uninstantiated WebAssembly.Module
import source mathModule from './math.wasm';

// Instantiate with custom imports
const instance = await WebAssembly.instantiate(mathModule, {
  env: { memory: new WebAssembly.Memory({ initial: 1 }) }
});
```

### Top-Level Wasm

Wasm modules no longer require `"type": "module"` in package.json (v24+).

### JSPI -- JavaScript Promise Integration (v25+)

WebAssembly JSPI enabled, allowing Wasm to suspend and resume on JS promises.

## Module Entrypoint as URL (v23+)

```bash
node "file:///path/to/module.mjs"
```

The module entrypoint can now be specified as a URL.
