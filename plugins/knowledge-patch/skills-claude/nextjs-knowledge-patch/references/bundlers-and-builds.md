# Bundlers and Builds

## Production Turbopack opt-in (`15.5.0`)

Production Turbopack builds were introduced in beta behind an explicit flag. Turbopack use in development did not imply production build use.

```sh
next build --turbopack
```

## Development filesystem caching (`16.0.0`, `16.1.0`)

In 16.0.0, Turbopack's development disk cache was beta and opt-in:

```ts
const nextConfig = {
  experimental: { turbopackFileSystemCacheForDev: true },
}

export default nextConfig
```

In 16.1.0, development filesystem caching became stable, enabled by default, and no longer needed the experimental flag. It persists compiler artifacts across restarts. Filesystem caching for `next build` was not yet stable in that release.

## Build adapters (`16.0.0`, `16.2.0`)

The 16.0.0 alpha adapter hook allowed deployment integrations to adjust Next.js configuration or process build output through `experimental.adapterPath`.

```js
const nextConfig = {
  experimental: { adapterPath: require.resolve('./my-adapter.js') },
}

module.exports = nextConfig
```

The build adapter API became stable in 16.2.0. Deployment platforms and custom integrations can use the stable API rather than relying on the experimental hook.

## Babel configuration detection (`16.0.0`)

When Turbopack finds a Babel configuration, it enables Babel automatically instead of terminating with an error.

## Separate output and process locking (`16.0.0`)

Development and builds use separate output directories, so `next dev` and `next build` may run concurrently. A project lockfile prevents conflicting command instances.

## Transitive server externals (`16.1.0`)

Under Turbopack, `serverExternalPackages` can resolve and externalize transitive dependencies. An application no longer needs to add such a package to its own `package.json` merely to externalize it.

## Same-origin Web Workers (`16.2-guide`)

Turbopack workers report the application's domain in `location.origin` instead of an empty origin. Relative `importScripts()` and `fetch()` calls resolve correctly, including calls made by WebAssembly libraries.

## Subresource Integrity (`16.2-guide`)

Turbopack can experimentally generate build-time integrity hashes for JavaScript. A Content Security Policy can approve static scripts with these hashes without requiring nonce-based dynamic rendering.

```js
const nextConfig = {
  experimental: { sri: { algorithm: 'sha256' } },
}

module.exports = nextConfig
```

## Per-import loaders (`16.2-guide`)

Import attributes may apply a Turbopack loader to a single import instead of every matching file in `turbopack.rules`. Supported attributes are:

- `turbopackLoader`
- `turbopackLoaderOptions`, encoded as a JSON string
- `turbopackAs`
- `turbopackModuleType`

```js
import value from './data.js' with {
  turbopackLoader: 'string-replace-loader',
  turbopackLoaderOptions: '{"search":"PLACEHOLDER","replace":"value"}',
}
```

Prefer global rule configuration when it fits the whole file class.

## Issue filtering (`16.2-guide`)

`turbopack.ignoreIssue` suppresses selected streaming warnings or expected overlay errors. A rule can combine a path glob or regular expression with title and description string or regular-expression matches.

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

## Development memory eviction (`16.3.0`)

Turbopack evicts memory-backed compilation data to its development filesystem cache by default. The normal `turbopackMemoryEviction` value is `'full'`. Disable eviction only while diagnosing cache or performance behavior.

```ts
export default {
  experimental: { turbopackMemoryEviction: false },
}
```

## Filesystem caching for builds (`16.3.0`)

Turbopack can persist work from `next build`. A CI job can reuse the work by restoring the generated `.next` directory between runs.

```ts
export default {
  experimental: { turbopackFileSystemCacheForBuild: true },
}
```

## Rust React Compiler (`16.3.0`)

Turbopack can run the native Rust React Compiler rather than the Babel implementation when both the compiler and its experimental backend are enabled.

```ts
export default {
  reactCompiler: true,
  experimental: { turbopackRustReactCompiler: true },
}
```

## `import.meta.glob` (`16.3.0`)

Turbopack supports the Vite-compatible glob API. It returns path-keyed lazy import functions by default and eagerly imported modules with `eager: true`. Named, multiple, and negative patterns are supported. The API is unavailable when building with `--webpack`.

```ts
const posts = import.meta.glob('./posts/*.mdx')
const eagerPosts = import.meta.glob('./posts/*.mdx', { eager: true })
```

## Package-local PostCSS (`16.3.0`)

Monorepos can resolve the nearest PostCSS configuration for each CSS file and fall back to the project-root configuration.

```ts
export default {
  experimental: { turbopackLocalPostcssConfig: true },
}
```

## Pages Router service workers (`release-catalogs`)

The 16.3 canary line compiles service workers registered from Pages Router pages and emits their bundles beneath `/_next/static/`.

## Text imports (`release-catalogs`)

Turbopack enables text import attributes by default, removing the need for a custom loader.

```js
import notice from './notice.txt' with { type: 'text' }
```

## Server Component HMR cancellation (`release-catalogs`)

The experimental `serverComponentsHmrCancellation` option aborts a superseded Server Component refresh on the client and cancels its server-side work.

```ts
export default {
  experimental: { serverComponentsHmrCancellation: true },
}
```

## `#/` subpath imports (`release-catalogs`)

Turbopack accepts `#/`-prefixed subpath imports when the project maps that prefix, instead of rejecting them during resolution.

```ts
import config from '#/config'
```
