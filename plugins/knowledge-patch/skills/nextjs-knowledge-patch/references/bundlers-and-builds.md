# Bundlers and Builds

Batch attributions used here: `15.4.0`, `15.5.0`, `16.0.0`, `16.1.0`, `16.2-guide`, `16.2.0`, `16.3.0`, and `release-catalogs`.

## Production builder selection

Turbopack development support did not initially imply Turbopack production builds. In `15.5.0`, opt into the beta production builder explicitly:

```sh
next build --turbopack
```

In Next.js 16, Turbopack settings live under top-level `turbopack`; `experimental.turbopack` is removed (`16.0.0`). When Turbopack detects a Babel configuration, it enables Babel automatically instead of stopping with an error.

## Filesystem caching and memory eviction

Turbopack's development disk cache progressed through these states:

- `15.4.0` previewed persistent caching as `experimental.turbopackPersistentCaching`.
- `16.0.0` provided an opt-in beta under `experimental.turbopackFileSystemCacheForDev`.
- `16.1.0` made the `next dev` filesystem cache stable and enabled by default; build caching was not yet stable in that release.

The beta form was:

```ts
const nextConfig = {
  experimental: { turbopackFileSystemCacheForDev: true },
}

export default nextConfig
```

As of `16.3.0`, Turbopack evicts memory-backed compilation data to its development filesystem cache by default. Disable eviction only while diagnosing cache or performance behavior; the normal `turbopackMemoryEviction` value is `'full'`.

```ts
export default {
  experimental: { turbopackMemoryEviction: false },
}
```

Turbopack can also persist compilation work for production builds. CI can reuse that cache by restoring the generated `.next` directory.

```ts
export default {
  experimental: { turbopackFileSystemCacheForBuild: true },
}
```

## Build adapters

The adapter hook began as an alpha in `16.0.0`. An integration pointed `experimental.adapterPath` at a module that could adjust Next.js configuration or process build output.

```js
const nextConfig = {
  experimental: { adapterPath: require.resolve('./my-adapter.js') },
}

module.exports = nextConfig
```

The build adapter API is stable in `16.2.0`. Deployment platforms and custom build integrations can use it without relying on the experimental status, while preserving the two core responsibilities: changing configuration at build time and processing build output.

## Package externalization

Under Turbopack, `serverExternalPackages` can resolve and externalize transitive dependencies (`16.1.0`). An application no longer has to add the transitive package to its own `package.json` solely to make externalization work.

## Same-origin workers and service workers

Turbopack Web Workers report the application's domain through `location.origin` rather than an empty origin (`16.2-guide`). Relative `importScripts()` and `fetch()` calls therefore resolve correctly, including calls made by WebAssembly libraries.

In the `release-catalogs` 16.3 canary line, Turbopack compiles service workers registered from Pages Router pages and emits their bundles below `/_next/static/`.

## Subresource Integrity

Turbopack can generate build-time integrity hashes for JavaScript (`16.2-guide`). This allows a Content Security Policy to approve static scripts without forcing dynamic rendering solely to attach nonces.

```js
const nextConfig = {
  experimental: { sri: { algorithm: 'sha256' } },
}

module.exports = nextConfig
```

## Per-import loaders

Import attributes can apply a Turbopack loader to one import instead of every matching file in `turbopack.rules` (`16.2-guide`). Supported attributes are:

- `turbopackLoader`.
- `turbopackLoaderOptions`, encoded as a JSON string.
- `turbopackAs`.
- `turbopackModuleType`.

```js
import value from './data.js' with {
  turbopackLoader: 'string-replace-loader',
  turbopackLoaderOptions: '{"search":"PLACEHOLDER","replace":"value"}',
}
```

Prefer global rules when they fit; use attributes for genuinely import-specific behavior.

Text import attributes are enabled by default in the `release-catalogs` canary line, so plain text no longer needs a custom loader:

```js
import notice from './notice.txt' with { type: 'text' }
```

## `import.meta.glob`

Turbopack supports the Vite-compatible glob API (`16.3.0`). It returns path-keyed lazy import functions by default and eagerly imported modules with `{ eager: true }`. Named, multiple, and negative patterns are also supported. The API is unavailable when building with `--webpack`.

```ts
const posts = import.meta.glob('./posts/*.mdx')
const eagerPosts = import.meta.glob('./posts/*.mdx', { eager: true })
```

## Resolution and issue filtering

Turbopack accepts `#/` subpath specifiers when the project maps that prefix in the `release-catalogs` canary line:

```ts
import config from '#/config'
```

Use `turbopack.ignoreIssue` to suppress selected streaming warnings or expected overlay errors (`16.2-guide`). A rule can combine a path glob or regular expression with title and description matches expressed as strings or regular expressions.

```ts
const nextConfig = {
  turbopack: {
    ignoreIssue: [
      { path: '**/third-party/**' },
      { path: /generated\/.*\.ts/, description: /expected error/i },
    ],
  },
}

export default nextConfig
```

Keep filters narrow enough that unexpected compiler errors still reach the overlay and terminal.

## Rust React Compiler

Turbopack can run the experimental native Rust React Compiler instead of its Babel implementation when both the compiler and its backend are enabled (`16.3.0`).

```ts
export default {
  reactCompiler: true,
  experimental: { turbopackRustReactCompiler: true },
}
```

## Server Component HMR cancellation

The `serverComponentsHmrCancellation` experiment aborts a superseded Server Component refresh in the browser and cancels its corresponding server-side work (`release-catalogs`).

```ts
export default {
  experimental: { serverComponentsHmrCancellation: true },
}
```

## WebAssembly compiler package publication

Next.js `16.2.10` and `15.5.20` contain no code changes; they restore publication of `@next/swc-wasm-web`, which had accidentally been omitted beginning with `16.2.4` and `15.5.15`, respectively (`release-catalogs`). If a WebAssembly compiler install fails on an affected patch, update to the restored package release rather than searching for framework behavior changes.
