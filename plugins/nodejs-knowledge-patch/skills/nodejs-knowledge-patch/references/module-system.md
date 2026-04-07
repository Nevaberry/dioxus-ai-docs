# Module System

## `require(esm)` Is Enabled By Default

Node.js 23 removes the old default `ERR_REQUIRE_ESM` behavior for native ES modules loaded with `require()`. The feature is still treated as experimental in 23.x, but it is on by default.

Use `--no-experimental-require-module` if you need to force old behavior while debugging regressions.

```js
// package.json
// { "type": "module" }

// index.cjs
const mod = require("./index.js");
console.log(mod);
```

When the load succeeds, `require()` returns an ES module namespace object, similar to `await import(...)`.

## Top-Level `await` Still Blocks `require()`

`require()` cannot load ES modules that depend on top-level `await`. That failure path changes from `ERR_REQUIRE_ESM` to `ERR_REQUIRE_ASYNC_MODULE`.

```js
try {
  require("./async-entry.js");
} catch (err) {
  if (err.code === "ERR_REQUIRE_ASYNC_MODULE") {
    console.error("Switch this edge to dynamic import()");
  }
}
```

## Detecting Support

Runtime detection is available through `process.features.require_module`.

Package authors can also use the `"module-sync"` exports condition to route both `require()` and `import` to the same native ES module entry point when the runtime supports it.

```json
{
  "exports": {
    ".": {
      "module-sync": "./dist/index.js",
      "import": "./dist/index.js",
      "require": "./dist/index.cjs"
    }
  }
}
```
