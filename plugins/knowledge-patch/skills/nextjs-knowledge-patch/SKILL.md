---
name: nextjs-knowledge-patch
description: Next.js 16.3.0 compatibility. Use for Next.js work.
license: MIT
version: 16.3.0
metadata:
  author: Nevaberry
---

# Next.js Knowledge Patch

Use this patch when changing a modern Next.js application, especially when migrating request APIs, adopting Cache Components, configuring Turbopack, or debugging routing and rendering behavior.

## Reference Index

| Reference | Topics |
| --- | --- |
| [migration-and-runtime.md](references/migration-and-runtime.md) | Runtime floors, removals, async request APIs, Proxy migration, security updates, upgrades |
| [routing-and-rendering.md](references/routing-and-rendering.md) | Link navigation, route fallbacks, global not-found, error boundaries, transitions, scrolling |
| [caching-and-prefetching.md](references/caching-and-prefetching.md) | Cache Components, cache keys and lifetimes, tag invalidation, route prefetching, instant routes |
| [bundlers-and-builds.md](references/bundlers-and-builds.md) | Turbopack, build adapters, workers, SRI, loaders, compiler caching, service workers |
| [types-and-configuration.md](references/types-and-configuration.md) | Typed routes, generated route props, type generation, configuration flags |
| [tooling-and-observability.md](references/tooling-and-observability.md) | Instrumentation, logging, inspectors, analyzers, DevTools, browser tools, testing |
| [images-css-and-assets.md](references/images-css-and-assets.md) | Image security and defaults, ImageResponse, icons, Sass, Lightning CSS, PostCSS |

## Migration Priorities

### Rename request interception to `proxy.ts`

Use one `proxy.ts` beside `app` or `pages`, either at the project root or under `src`. Export `proxy` or a default function.

```ts
import { NextResponse, type NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  return NextResponse.redirect(new URL('/home', request.url))
}

export const config = { matcher: '/legacy/:path*' }
```

Proxy is for request-dependent rewrites, redirects, headers, and optimistic checks. Keep slow data fetching and complete authorization in application code. Fetch caching, revalidation, and tags have no effect in Proxy.

Middleware's stable Node.js runtime was previously opt-in through `config.runtime = 'nodejs'`; use the `proxy.ts` convention when migrating to Next.js 16.

### Make request APIs asynchronous

Await all request-bound values. Synchronous access is removed.

```tsx
export default async function Page({ params }: PageProps<'/blog/[slug]'>) {
  const { slug } = await params
  return <h1>{slug}</h1>
}
```

- Await page `params` and `searchParams`.
- Await `cookies()`, `headers()`, and `draftMode()`.
- In metadata image routes, await `params`; each `generateImageMetadata` ID is a `Promise<string>`.

### Fix hard build failures and removals

- Add `default.js` to every parallel-route slot. Call `notFound()` or return `null` when no fallback UI is wanted.
- Replace `next lint` with the ESLint CLI or another linter; `next build` no longer runs linting.
- Move Turbopack options to top-level `turbopack`, not `experimental.turbopack`.
- Replace `serverRuntimeConfig` and `publicRuntimeConfig` with environment variables.
- Remove AMP, `experimental.ppr`, `experimental_ppr`, `unstable_rootParams()`, and removed development-indicator options.
- Meet the runtime floors: Node.js 20.9+, TypeScript 5.1+, Chrome/Edge/Firefox 111+, and Safari 16.4+.

### Review behavior changes

- Opt into smooth scrolling with `<html data-scroll-behavior="smooth">`; automatic handling was removed.
- Image optimization defaults and trust boundaries changed. Configure quality, local query patterns, redirect limits, and private-IP access deliberately.
- Development and builds use separate output directories and project locking, so they can run concurrently without allowing conflicting instances of the same command.

## Cache Components Quick Reference

Enable Cache Components before using `use cache`:

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  cacheComponents: true,
}

export default nextConfig
```

The directive can cache all exports in a file, one async component, or one async function. Every function export in a file-level cached module must be async. A fully cached route needs the directive in both layout and page because each segment has its own entry.

```tsx
async function ProductList({ category }: { category: string }) {
  'use cache'
  return db.products.findMany({ where: { category } })
}
```

Cache keys are compiler-generated from the build, function identity, serialized arguments or props, captured values, and an HMR hash in development. Do not manually assemble a key.

### Boundary rules

- Resolve `cookies()`, `headers()`, and request-time `searchParams` outside cached scopes, then pass serializable values in.
- Inputs follow Server Component serialization. Class and `URL` instances cannot be key inputs.
- Return values follow the broader Client Component serialization and may include JSX.
- Non-serializable children and Server Actions may pass through by reference only when cached code neither inspects nor invokes them.
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

| API | Allowed context | Effect |
| --- | --- | --- |
| `updateTag(tag)` | Server Actions only | Expires tagged data immediately for read-your-writes |
| `refresh()` | Server Actions only | Refreshes uncached data elsewhere without touching cached content |
| `revalidateTag(tag, profile)` | Server code | Uses stale-while-revalidate with a named/custom profile or `{ expire }` |

The one-argument `revalidateTag(tag)` form is deprecated. Use a profile such as `'max'`, a custom profile, or `{ expire: seconds }`.

## Navigation and Prefetching

Use `onNavigate` for SPA navigation guards rather than generic click handling:

```tsx
<Link
  href="/dashboard"
  onNavigate={(event) => {
    if (hasUnsavedChanges) event.preventDefault()
  }}
>
  Dashboard
</Link>
```

`useLinkStatus()` exposes the pending state for its enclosing `Link`; the caller must be rendered below that link. `prefetch="auto"` explicitly requests the default automatic behavior.

`router.prefetch(href, { onInvalidate })` can refresh stale prefetched data. Modern segment prefetching reuses shared layouts, cancels work when links leave the viewport, reprioritizes hover and re-entry, and re-prefetches after invalidation.

For Cache Components applications, use Suspense or cached work to preserve instant navigation. `export const instant = false` explicitly accepts a server-bound page or layout. `partialPrefetching: true` shares one loading shell per route; `prefetch={true}` adds build-known content and `export const prefetch = 'allow-runtime'` can include request-time cached content.

## Types and Configuration

Enable stable typed routes at the top level:

```ts
const nextConfig = { typedRoutes: true }
export default nextConfig
```

Generated, import-free helpers include `PageProps<'/route'>`, `LayoutProps<'/route'>`, and `RouteContext<'/route'>`. Layout props include typed parallel-route slots.

Generate route types without starting the server or building:

```sh
next typegen && tsc --noEmit
```

The command also accepts an optional project directory. Native type stripping for `next.config.ts` is available through `--experimental-next-config-strip-types` on `next dev`, `next build`, and `next start`.

## Turbopack and Build Essentials

- Turbopack production builds began behind `next build --turbopack`; development support did not imply production use.
- Development filesystem caching is stable and on by default. Build filesystem caching remains configurable and can be reused in CI by restoring `.next`.
- A Babel configuration is detected and enabled automatically under Turbopack.
- `serverExternalPackages` can externalize transitive dependencies.
- Build adapters can adjust configuration or process output; use the stable API for deployment integrations.
- `import.meta.glob` supports lazy, eager, named, multiple, and negative patterns under Turbopack, but not `--webpack`.
- Per-import loader attributes, text imports, same-origin workers, issue filtering, SRI, and package-local PostCSS are covered in the build and asset references.

## Diagnostics and Documentation

- Put `instrumentation-client.js` or `.ts` at the project root to initialize client monitoring before application code.
- Use `next build --debug-prerender` for focused prerender failures.
- Use `next dev --inspect` for only the application process and `next start --inspect` for the production server.
- Use `next experimental-analyze` to inspect client/server bundles, route filters, import chains, and asset sizes.
- Browser errors can be forwarded to the terminal with `logging.browserToTerminal`.
- Development output identifies compilation versus rendering time, Server Function calls, hydration sides, and chained causes.
- Installed Next.js documentation is available under `node_modules/next/dist/docs/`; managed `AGENTS.md` markers can point tools there while preserving surrounding content.
- Documentation URLs can return Markdown through a `.md` suffix or `Accept: text/markdown`; use `/docs/llms.txt` as an index.

## Security

Treat React Server Components security updates as urgent. A critical remote-code-execution issue affects Next.js 15.x and 16.x, with denial-of-service and source-exposure issues also affecting older lines. Upgrade every affected application to a patched release immediately.
