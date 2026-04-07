# Runtime And Web APIs

## `AsyncLocalStorage` Defaults To `AsyncContextFrame`

Node.js 24 switches `AsyncLocalStorage` to `AsyncContextFrame` by default. Code that depends on subtle async context behavior should be retested on Node.js 24+, especially frameworks and tracing libraries.

## `URLPattern` Is Global

Node.js 24 exposes `URLPattern` on the global object, matching browser-style usage.

```js
const pattern = new URLPattern({ pathname: "/posts/:slug" });
const match = pattern.exec("https://example.com/posts/hello-world");

console.log(match.pathname.groups.slug);
```

## Permission Flag Rename

The permission model moves from `--experimental-permission` to `--permission`, which is the flag new examples should use.

```sh
node --permission --allow-fs-read=./config app.js
```

Later 24.x releases continue tightening permission checks, including `fs/promises` and `realpath.native`.

## Newer Runtime APIs

Recent 23.x and 24.x releases add or expand runtime-facing APIs:

- `process.execve()` for process replacement
- `http.setGlobalProxyFromEnv()` for process-wide HTTP proxy setup
- `fs.watch(..., { ignore })`
- additional `node:sqlite` and `node:test` surface area in semver-minor releases

```js
import http from "node:http";

http.setGlobalProxyFromEnv();
```

Treat these as version-gated features when supporting Node.js 22 or earlier.
