---
name: nextjs-knowledge-patch
description: Next.js
version: "16.3.0"
license: MIT
metadata:
  author: Nevaberry
---


# Next.js Knowledge Patch

Use this patch when upgrading or maintaining modern Next.js applications, especially around asynchronous request APIs, Cache Components, routing and prefetching, Turbopack, image security, or framework diagnostics. Check the application's installed Next.js version before applying version-dependent options.

## Reference Index

| Reference | Topics |
| --- | --- |
| [migration-and-runtime.md](references/migration-and-runtime.md) | Runtime floors, removed APIs, async request data, Proxy, command changes, upgrades and security |
| [routing-and-rendering.md](references/routing-and-rendering.md) | Link navigation, route fallbacks, global not-found, errors, transitions, scrolling and focus |
| [caching-and-prefetching.md](references/caching-and-prefetching.md) | Cache Components, cache keys and lifetimes, tag invalidation, route prefetching and instant routes |
| [bundlers-and-builds.md](references/bundlers-and-builds.md) | Turbopack, adapters, filesystem caches, workers, loaders, compiler integration and service workers |
| [types-and-configuration.md](references/types-and-configuration.md) | Typed routes, generated props, type generation and configuration migrations |
| [tooling-and-observability.md](references/tooling-and-observability.md) | Instrumentation, logs, inspectors, analyzers, browser tools, managed rules, testing and documentation |
| [images-css-and-assets.md](references/images-css-and-assets.md) | Image trust boundaries and defaults, ImageResponse, icons, Sass, Lightning CSS and PostCSS |

## Migration Priorities

### Await request-bound APIs

Request values are asynchronous. Await page `params` and `searchParams`, plus `cookies()`, `headers()`, and `draftMode()`. Metadata image route `params` are asynchronous too, and IDs produced by `generateImageMetadata` arrive as `Promise<string>` values.

```tsx
export default async function Page({ params }: PageProps<'/blog/[slug]'>) {
  const { slug } = await params
  return <h1>{slug}</h1>
}
```

Resolve request data outside a cached scope and pass only the serializable value into it.

### Replace Middleware with `proxy.ts`

Use one `proxy.ts` beside `app` or `pages`, at the project root or under `src`. Export `proxy` or a default function.

```ts
import { NextResponse, type NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  return NextResponse.redirect(new URL('/home', request.url))
}

export const config = { matcher: '/legacy/:path*' }
```

Proxy is for request-dependent rewrites, redirects, headers, and optimistic checks. Keep slow data loading and complete authorization in application code. Fetch caching, revalidation, and tags do not take effect in Proxy.

### Remove obsolete commands and configuration

- Replace `next lint` with the ESLint CLI or another linter. `next build` no longer runs linting.
- Replace `serverRuntimeConfig` and `publicRuntimeConfig` with environment variables.
- Move Turbopack options from `experimental.turbopack` to top-level `turbopack`.
- Remove AMP APIs and configuration, `experimental.ppr`, `experimental_ppr`, `unstable_rootParams()`, and removed development-indicator settings.
- Use top-level `typedRoutes`; use `cacheComponents` instead of the earlier `dynamicIO` preview name.

### Meet runtime floors and route requirements

Use Node.js 20.9 or newer and TypeScript 5.1 or newer. Supported browser floors are Chrome, Edge, and Firefox 111, plus Safari 16.4.

Every parallel-route slot needs `default.js`; a missing fallback is a build error. Call `notFound()` or return `null` if the slot needs no fallback UI.

```tsx
import { notFound } from 'next/navigation'

export default function Default() {
  notFound()
}
```

### Review changed defaults

- Add `data-scroll-behavior="smooth"` to `<html>` when smooth-scrolling behavior is intended.
- Audit image quality allowlists, local query patterns, private-IP access, redirect limits, cache TTLs, and generated-image fonts.
- Development and production builds use separate output directories, while project locks reject conflicting instances of the same command.
- ESLint integration defaults to Flat Config, and modern Sass behavior comes from `sass-loader` 16.

## Cache Components Quick Reference

Enable Cache Components before using `use cache`.

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = { cacheComponents: true }
export default nextConfig
```

The directive may cover a module, an async component, or an async function. In a module-level cached file, exported functions must be async; exported literal constants are allowed. Cache both layout and page when both route segments must be cached.

```tsx
async function ProductList({ category }: { category: string }) {
  'use cache'
  return db.products.findMany({ where: { category } })
}
```

### Keys and boundaries

The compiler builds keys from build identity, function identity, serialized arguments or props, captured values, and a development HMR hash. Do not assemble keys manually.

- Cache-key inputs follow Server Component serialization; class and `URL` instances are not valid inputs.
- Return values use the broader Client Component serialization and may contain JSX.
- Non-serializable children and Server Actions can pass through by reference only if cached code does not inspect or invoke them.
- `cookies()`, `headers()`, and request-time `searchParams` cannot be read directly inside the cached scope.
- Each cached scope has isolated `React.cache` state.

### Lifetime and invalidation

```ts
import { cacheLife, cacheTag } from 'next/cache'

export async function getProducts() {
  'use cache'
  cacheLife('hours')
  cacheTag('products')
  return db.products.findMany()
}
```

| API | Context | Effect |
| --- | --- | --- |
| `updateTag(tag)` | Server Actions only | Immediately expires tagged data for read-your-writes |
| `refresh()` | Server Actions only | Refreshes uncached data elsewhere without invalidating cached content |
| `revalidateTag(tag, profile)` | Server code | Applies stale-while-revalidate using a named/custom profile or `{ expire }` |

The one-argument `revalidateTag(tag)` form is deprecated. Cache lifetime values are validated early; handle `Infinity` deliberately.

## Navigation and Prefetching

Use `onNavigate` for SPA navigation guards, because it runs for navigation rather than every click. `useLinkStatus()` exposes the pending state for its enclosing link and must be called below that `Link`.

```tsx
<Link href="/dashboard" onNavigate={(event) => {
  if (hasUnsavedChanges) event.preventDefault()
}}>
  Dashboard
</Link>
```

`prefetch="auto"` explicitly selects the default link behavior. `router.prefetch(href, { onInvalidate })` can warm a route again after prefetched data becomes stale.

With Cache Components, keep navigation instant by caching work or placing it behind `Suspense`; use `export const instant = false` to accept server-bound navigation explicitly. `partialPrefetching: true` shares a route loading shell. `prefetch={true}` adds build-known content, while `export const prefetch = 'allow-runtime'` may add request-time cached content at greater server cost.

## Types and Configuration

Enable stable typed routes at the top level.

```ts
const nextConfig = { typedRoutes: true }
export default nextConfig
```

Use the generated, import-free `PageProps<'/route'>`, `LayoutProps<'/route'>`, and `RouteContext<'/route'>` helpers. Layout props include typed parallel-route slots.

Generate route types without starting a server or running a build:

```sh
next typegen && tsc --noEmit
```

The command accepts an optional project directory. Native stripping for `next.config.ts` is available through `--experimental-next-config-strip-types` on `next dev`, `next build`, and `next start`.

## Turbopack and Build Essentials

- Production Turbopack originally required `next build --turbopack`; development support alone did not select it for builds.
- Development filesystem caching is stable and enabled by default. Build caching can be enabled separately and reused in CI by restoring `.next`.
- A detected Babel configuration is enabled automatically with Turbopack.
- `serverExternalPackages` can externalize transitive dependencies.
- Stable build adapters can adjust configuration or process build output for deployment integrations.
- `import.meta.glob` supports lazy, eager, named, multiple, and negative patterns under Turbopack, but not with `--webpack`.
- Per-import loaders, text imports, same-origin workers, issue filters, SRI, service workers, and package-local PostCSS are detailed in the build and asset references.

## Diagnostics and Documentation

- Put `instrumentation-client.js` or `.ts` at the project root to initialize client monitoring before application code.
- Use `next build --debug-prerender` for focused prerender diagnostics.
- Use `next dev --inspect` for the application process and `next start --inspect` for the production server.
- Use `next experimental-analyze` to inspect client/server bundles, routes, import chains, CSS, and other asset sizes.
- Browser errors can be forwarded to the terminal with `logging.browserToTerminal`.
- Development output identifies compile versus render time, Server Function calls, hydration sides, and chained causes.
- Installed documentation is available under `node_modules/next/dist/docs/`; managed `AGENTS.md` markers can point tools there without overwriting surrounding content.
- Documentation URLs support a `.md` suffix or `Accept: text/markdown`; `/docs/llms.txt` is an index.

## Security

Treat React Server Components security updates as urgent. A critical remote-code-execution issue affects Next.js 15.x and 16.x, while denial-of-service and source-exposure issues also affect older lines. Upgrade affected applications to a patched release immediately.
