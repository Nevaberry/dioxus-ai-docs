# Bundlers and Builds

## Production builds and adapters

### Turbopack production opt-in (`15.5.0`)

Production Turbopack builds began as a beta opt-in. Turbopack development
support did not make `next build` use it automatically.

```sh
next build --turbopack
```

### Build adapters (`16.0.0`, `16.2.0`)

The adapter hook first appeared as an alpha API configured through
`experimental.adapterPath`:

```js
const nextConfig = {
  experimental: { adapterPath: require.resolve('./my-adapter.js') },
}

module.exports = nextConfig
```

The build adapter API became stable in `16.2.0`. Deployment platforms and
custom integrations can modify Next.js configuration or process build output
without relying on the experimental API.

### Stage timing (`16.0.0`)

Production builds report the duration of each stage. Development request logs
similarly separate compile time, which covers routing and compilation, from
render time, which covers application and React rendering.

## Filesystem and memory caches

### Development cache transition (`16.0.0`, `16.1.0`)

Turbopack's development filesystem cache initially required an experimental
flag:

```ts
const nextConfig = {
  experimental: { turbopackFileSystemCacheForDev: true },
}

export default nextConfig
```

It became stable, enabled by default, and persistent across `next dev`
restarts in `16.1.0`. Build filesystem caching was not yet stable at that
point.

### Development memory eviction (`16.3.0`)

Turbopack now evicts memory-backed compilation data into the development
filesystem cache by default. The normal `turbopackMemoryEviction` value is
`'full'`; disable it only while diagnosing cache or performance behavior.

```ts
export default {
  experimental: { turbopackMemoryEviction: false },
}
```

### Build filesystem cache (`16.3.0`)

Turbopack can persist work for `next build`. CI can reuse that work by
restoring the generated `.next` directory between runs.

```ts
export default {
  experimental: { turbopackFileSystemCacheForBuild: true },
}
```

## Compilation behavior

### Babel detection (`16.0.0`)

When Turbopack finds a Babel configuration, it enables Babel automatically
instead of terminating with an error.

### Transitive external packages (`16.1.0`)

Under Turbopack, `serverExternalPackages` can resolve and externalize
transitive dependencies. An application no longer needs to add the package to
its own `package.json` solely to externalize it.

### Rust React Compiler (`16.3.0`)

Turbopack can run the native Rust React Compiler instead of the Babel
implementation when both the compiler and the experimental backend are
enabled.

```ts
export default {
  reactCompiler: true,
  experimental: { turbopackRustReactCompiler: true },
}
```

### `import.meta.glob` (`16.3.0`)

Turbopack supports the Vite-compatible glob API. It returns path-keyed lazy
import functions by default and eagerly imported modules with `eager: true`.
Named, multiple, and negative patterns are supported. The API is unavailable
with `--webpack`.

```ts
const posts = import.meta.glob('./posts/*.mdx')
const eagerPosts = import.meta.glob('./posts/*.mdx', { eager: true })
```

### Subpath imports (`release-catalogs`)

Turbopack accepts `#/` import specifiers when that prefix is mapped by the
project instead of rejecting them during resolution.

```ts
import config from '#/config'
```

## Importers, workers, and generated scripts

### Same-origin workers (`16.2-guide`)

Turbopack workers report the application's domain in `location.origin` rather
than an empty origin. Relative `importScripts()` and `fetch()` calls therefore
resolve correctly, including calls made by WASM libraries.

### Per-import loaders (`16.2-guide`)

Import attributes can apply a loader to a single import rather than every
matching file in `turbopack.rules`. Supported attributes are
`turbopackLoader`, `turbopackLoaderOptions` as a JSON string, `turbopackAs`,
and `turbopackModuleType`. Prefer global rules when they fit.

```js
import value from './data.js' with {
  turbopackLoader: 'string-replace-loader',
  turbopackLoaderOptions: '{"search":"PLACEHOLDER","replace":"value"}',
}
```

### Text imports (`release-catalogs`)

Text import attributes are enabled by default under Turbopack, so text files
need no custom loader.

```js
import notice from './notice.txt' with { type: 'text' }
```

### Pages Router service workers (`release-catalogs`)

The 16.3 canary line compiles service workers registered from Pages Router
pages and emits their bundles under `/_next/static/`.

### Server Component HMR cancellation (`release-catalogs`)

The experimental `serverComponentsHmrCancellation` option aborts a superseded
Server Component refresh on the client and cancels its server-side work.

```ts
export default {
  experimental: { serverComponentsHmrCancellation: true },
}
```

## Integrity and issue control

### Subresource Integrity (`16.2-guide`)

Turbopack can experimentally generate build-time integrity hashes for
JavaScript. A CSP can then approve static scripts without forcing nonce-based
dynamic rendering.

```js
const nextConfig = {
  experimental: { sri: { algorithm: 'sha256' } },
}

module.exports = nextConfig
```

### Issue filtering (`16.2-guide`)

`turbopack.ignoreIssue` suppresses selected streaming warnings or expected
overlay errors. Rules can combine a path glob or regular expression with
title and description string or regular-expression matches.

```ts
const nextConfig = {
  turbopack: {
    ignoreIssue: [
      { path: '**/vendor/**' },
      { path: /generated\/.*\.ts/, description: /expected error/i },
    ],
  },
}
export default nextConfig
```

## Compiler package recovery (`release-catalogs`)

Next.js 16.2.10 and 15.5.20 contained no code changes; they restored
publication of `@next/swc-wasm-web`, accidentally omitted since 16.2.4 and
15.5.15 respectively.
