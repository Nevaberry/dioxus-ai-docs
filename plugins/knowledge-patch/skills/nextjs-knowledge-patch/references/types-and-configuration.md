# Types and Configuration

Batch attributions used here: `15.4.0`, `15.5.0`, `16.0.0`, `16.2-guide`, `16.2.0`, and `16.3.0`.

## Stable typed routes

Typed routes moved to the top-level stable flag in `15.5.0`:

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  typedRoutes: true,
}

export default nextConfig
```

Do not configure this through an experimental key.

## Generated route prop helpers

Next.js generates three global, import-free helpers from the application's route tree (`15.5.0`):

- `PageProps<'/route'>` supplies typed route parameters and page props.
- `LayoutProps<'/route'>` supplies typed route parameters, `children`, and named parallel-route slots.
- `RouteContext<'/route'>` supplies typed route context.

The route literal drives the generated types. Layout slots are inferred from the route tree.

```tsx
export default function DashboardLayout(
  props: LayoutProps<'/dashboard'>,
) {
  return (
    <>
      {props.children}
      {props.analytics}
      {props.team}
    </>
  )
}
```

Remember that modern request props such as `params` and `searchParams` are asynchronous even though the helpers provide their route-aware shape.

## Standalone route type generation

Run `next typegen` before an external TypeScript check when generated route types are needed without starting development or running a build (`15.5.0`):

```sh
next typegen && tsc --noEmit
```

`next typegen` also accepts an optional project directory. Use it in CI before `tsc` if the workspace starts without generated route artifacts.

## Native TypeScript configuration stripping

Next.js `16.0.0` can run `next.config.ts` through Node.js native type stripping. The same flag is accepted by the development, build, and production-start commands:

```sh
next dev --experimental-next-config-strip-types
next build --experimental-next-config-strip-types
next start --experimental-next-config-strip-types
```

This is a command-line execution mode, not a `next.config.ts` property.

## Experimental preview flags and their successors

The `15.4.0` canary configuration exposed several previews:

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  experimental: {
    browserDebugInfoInTerminal: true,
    dynamicIO: true,
    clientSegmentCache: true,
    devtoolSegmentExplorer: true,
    globalNotFound: true,
    turbopackPersistentCaching: true,
  },
}

export default nextConfig
```

These flags covered browser-log forwarding, caching and prerendering, client-router segment caching, route exploration, global 404 handling, and persistent Turbopack caching. Treat that snippet as historical when editing a newer application:

- `dynamicIO` became top-level `cacheComponents` in Next.js 16.
- Browser-to-terminal logging later moved to `logging.browserToTerminal` (`16.2-guide`).
- The development Turbopack filesystem cache became stable and enabled by default.
- `globalNotFound` remained the gate for `app/global-not-found.tsx` in the documented preview.
- Newer prefetch and cache controls are documented in the caching reference instead of being interchangeable with `clientSegmentCache`.

## Frequently confused configuration locations

| Setting | Location | Purpose |
| --- | --- | --- |
| `cacheComponents` | Top level | Enables Cache Components and `use cache` |
| `typedRoutes` | Top level | Enables generated typed-route validation |
| `turbopack` | Top level | Holds Turbopack rules and issue filters |
| `logging.browserToTerminal` | `logging` | Chooses browser console forwarding level |
| `partialPrefetching` | Top level | Enables reusable loading-shell prefetching |
| `agentRules` | Top level | Controls managed Next.js documentation rules |
| `prefetchInlining` | `experimental` | Combines all prefetched route segments into one response |
| `cachedNavigations` | `experimental` | Caches navigation and initial-load RSC data; requires Cache Components |
| `appNewScrollHandler` | `experimental` | Opts into the reworked scroll/focus handler where not yet default |
| `turbopackMemoryEviction` | `experimental` | Controls eviction into the development disk cache |
| `turbopackFileSystemCacheForBuild` | `experimental` | Enables persistent Turbopack build artifacts |
| `turbopackRustReactCompiler` | `experimental` | Selects the native compiler backend with `reactCompiler` enabled |

`16.2.0` and `16.3.0` introduced several of the later entries; consult their topic references before enabling them because they have cache, server-load, or compatibility tradeoffs.
