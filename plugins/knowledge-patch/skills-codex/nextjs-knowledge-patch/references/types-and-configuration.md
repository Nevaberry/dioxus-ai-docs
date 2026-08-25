# Types and Configuration

## Typed routes

### Stable configuration (`15.5.0`)

Typed routes are stable. Configure them with top-level `typedRoutes`, not an
experimental option.

```ts
const nextConfig = { typedRoutes: true }
export default nextConfig
```

### Generated route props (`15.5.0`)

Next.js generates global, import-free `PageProps`, `LayoutProps`, and
`RouteContext` helpers from the route tree. The route literal supplies typed
parameters; layout props also include typed parallel-route slots.

```tsx
export default function DashboardLayout(props: LayoutProps<'/dashboard'>) {
  return <>{props.children}{props.analytics}{props.team}</>
}
```

### Standalone type generation (`15.5.0`)

Run `next typegen` before an external TypeScript check when route types are
needed without development or a build. The command accepts an optional project
directory.

```sh
next typegen && tsc --noEmit
```

## Linting and TypeScript configuration

### Direct linter migration (`15.5.0`, `16.0.0`)

`next lint` was deprecated in 15.5. Migrate to the ESLint CLI with:

```sh
npx @next/codemod@latest next-lint-to-eslint-cli .
```

At the 15.5 stage, `next build` still performed lint validation when an ESLint
configuration existed, and new projects could choose ESLint, Biome, or no
linter. Next.js 16 removed `next lint` and stopped linting during
`next build`.

### Flat ESLint configuration (`16.0.0`)

`@next/eslint-plugin-next` defaults to ESLint Flat Config rather than the
legacy configuration format.

### Native TypeScript stripping (`16.0.0`)

Pass `--experimental-next-config-strip-types` to `next dev`, `next build`, or
`next start` to run `next.config.ts` with Node.js native TypeScript stripping.

```sh
next dev --experimental-next-config-strip-types
```

## Historical preview flags (`15.4.0`)

Canary releases exposed upcoming browser-log forwarding, caching and
prerendering, client-router caching, route exploration, global 404 handling,
and persistent Turbopack caching through experimental configuration:

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

These names describe the preview stage, not a configuration to copy forward
unchanged. In particular, `dynamicIO` became `cacheComponents` in Next.js 16,
and several other capabilities later changed stability or configuration.
