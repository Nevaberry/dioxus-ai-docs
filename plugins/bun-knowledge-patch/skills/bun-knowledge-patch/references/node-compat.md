# Node.js Compatibility

## fs.glob

```ts
import { glob } from "node:fs/promises";

for await (const file of glob("**/*.ts")) {
  console.log(file);
}

// With options
for await (const file of glob("**/*.js", {
  cwd: "./src",
  exclude: (path) => path.includes("node_modules"),
})) {
  console.log(file);
}

// Array patterns
import { globSync } from "node:fs";
const files = globSync(["**/*.js", "**/*.ts"], {
  exclude: ["node_modules/**", "dist/**"],
});
```

## FileHandle.readLines()

```ts
import { open } from "node:fs/promises";

const file = await open("file.txt");
for await (const line of file.readLines({ encoding: "utf8" })) {
  console.log(line);
}
await file.close();
```

## ReadableStream Methods

Call `.json()`, `.text()`, `.bytes()`, `.blob()` directly:

```ts
const { stdout } = Bun.spawn({ cmd: ["echo", '{"hello": "world"}'], stdout: "pipe" });
const data = await stdout.json();
```

## ReadableStream as stdin

```ts
const response = await fetch("https://example.com/large-file");
Bun.spawn({
  cmd: ["gzip", "-c"],
  stdin: response.body,
  stdout: Bun.file("output.gz"),
});
```

## WebAssembly Streaming

```ts
const { instance } = await WebAssembly.instantiateStreaming(
  fetch("https://example.com/module.wasm")
);
instance.exports.myFunction();
```

## node:vm

```ts
import vm from "node:vm";

// SourceTextModule for ES modules
const module = new vm.SourceTextModule('export const x = 1');

// SyntheticModule for custom modules
const synthetic = new vm.SyntheticModule(['default'], function() {
  this.setExport('default', 42);
});

// compileFunction
const fn = vm.compileFunction('return a + b', ['a', 'b']);
fn(1, 2); // 3

// Script bytecode caching
const script = new vm.Script('1 + 1', { produceCachedData: true });
const cached = script.cachedData;

// DONT_CONTEXTIFY - globalThis behaves normally
const ctx = vm.createContext(vm.constants.DONT_CONTEXTIFY);
vm.runInContext("globalThis", ctx) === ctx; // true
```

## node:inspector Profiler

```ts
import inspector from "node:inspector/promises";

const session = new inspector.Session();
session.connect();

await session.post("Profiler.enable");
await session.post("Profiler.start");
// ... code to profile ...
const { profile } = await session.post("Profiler.stop");
```

## perf_hooks

```ts
import { monitorEventLoopDelay } from "perf_hooks";

const h = monitorEventLoopDelay({ resolution: 20 });
h.enable();
// ... work ...
h.disable();
console.log(h.min, h.max, h.mean, h.percentile(99));
```

## http.Server

```ts
server.close();
server.closeIdleConnections(); // Close idle keep-alive connections
```

## Worker environmentData

```ts
import { Worker, setEnvironmentData, getEnvironmentData } from "worker_threads";

setEnvironmentData("config", { debug: true });
const worker = new Worker("./worker.js");

// In worker.js:
const config = getEnvironmentData("config"); // { debug: true }
```

## require.extensions

```ts
require.extensions[".txt"] = (module, filename) => {
  module.exports = require("fs").readFileSync(filename, "utf8");
};
const text = require("./file.txt");
```

## process.features

```ts
process.features.typescript;        // "transform"
process.features.require_module;    // true
```

## DisposableStack

```ts
const stack = new DisposableStack();
stack.use({ [Symbol.dispose]() { console.log("Cleanup!"); } });
stack.dispose(); // "Cleanup!"

const asyncStack = new AsyncDisposableStack();
await asyncStack.disposeAsync();
```

## Supported Modules

- `node:http2` server
- `node:dgram` (UDP)
- `node:cluster`
- Brotli in `node:zlib`
- `node:v8` heap snapshots
