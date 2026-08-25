# Migration and Runtime

## Runtime and browser floors (`16.0.0`)

Next.js 16 requires Node.js 20.9 or newer and TypeScript 5.1 or newer. Its supported browser floor is Chrome 111, Edge 111, Firefox 111, and Safari 16.4.

## From Middleware to Proxy (`15.5.0`, `16.0-guide`)

Next.js 15.5 made the Node.js Middleware runtime stable, but it remained opt-in through `export const config = { runtime: 'nodejs' }`. Next.js 16 renamed Middleware to Proxy. Migrate to the new convention rather than preserving the old filename/runtime opt-in.

Place the one supported `proxy.ts` beside `app` or `pages`, either at the project root or under `src`. Export a named `proxy` function or a default function.

```ts
import { NextResponse, type NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  return NextResponse.redirect(new URL('/home', request.url))
}

export const config = { matcher: '/about/:path*' }
```

Use Proxy for request-dependent rewrites, redirects, headers, and optimistic checks. Avoid slow data fetching and full authorization there. `fetch` cache, revalidation, and tag options have no effect in Proxy.

## Asynchronous request APIs (`16.0.0`, `16.3.1`)

Synchronous request-bound access is removed. Pages must await `params` and `searchParams`; code must await `cookies()`, `headers()`, and `draftMode()`.

```tsx
export default async function Page({ params }: PageProps<'/blog/[slug]'>) {
  const { slug } = await params
  return <h1>{slug}</h1>
}
```

Metadata image routes receive asynchronous `params`, and every ID returned by `generateImageMetadata` is exposed as a `Promise<string>`.

In 16.3.1, `headers()` again exposes a live view of the incoming request rather than a detached view. It remains asynchronous; code that needs current request headers should still await it.

## Removed APIs and configuration (`15.4.0`, `15.5.0`, `16.0.0`)

Remove or replace the following during a Next.js 16 migration:

- AMP APIs and configuration.
- `next lint`; use the ESLint CLI or another linter.
- `serverRuntimeConfig` and `publicRuntimeConfig`; use environment variables.
- `appIsrStatus`, `buildActivity`, and `buildActivityPosition` development-indicator options.
- `experimental.ppr` and `export const experimental_ppr`.
- `unstable_rootParams()`.
- `experimental.turbopack`; move options to top-level `turbopack`.

Before removal, `unstable_rootParams` was server-only and unsupported in Client Components. Do not preserve it while migrating.

The 15.5.0 linter codemod converts `next lint` usage to the ESLint CLI:

```sh
npx @next/codemod@latest next-lint-to-eslint-cli .
```

In 15.5, `next build` still validated lint when it found an ESLint configuration. In Next.js 16, `next build` no longer runs linting. New projects may select ESLint, Biome, or no linter.

## Output isolation and project locks (`16.0.0`)

`next dev` and `next build` use separate output directories, allowing development and builds to run concurrently. A project lockfile still prevents conflicting instances of the same command.

## Parallel-route fallback requirement (`16.0.0`)

Every parallel-route slot must provide `default.js`. A missing fallback fails the build. Call `notFound()` or return `null` to preserve an intentionally empty fallback.

```tsx
import { notFound } from 'next/navigation'

export default function Default() {
  notFound()
}
```

## Framework upgrade command (`16.1.0`)

Upgrade Next.js directly with:

```sh
next upgrade
```

## Dynamic Pages API-route localization rollback (`16.3.1`)

Next.js 16.3.1 reverted the recent i18n localization change for dynamic Pages Router API routes and restored the prior behavior. Do not depend on the temporary localization behavior for routes such as `pages/api/[slug].ts`.

## Restored WebAssembly compiler publication (`release-catalogs`)

Next.js 16.2.10 and 15.5.20 contain no code changes. They restore publication of `@next/swc-wasm-web`, which had accidentally been omitted beginning with 16.2.4 and 15.5.15.

## React Server Components security updates (`release-catalogs`)

CVE-2025-66478 is a critical remote-code-execution vulnerability affecting Next.js 15.x and 16.x. CVE-2025-55184, a denial-of-service issue, and CVE-2025-55183, a source-code exposure issue, also affect 13.x and 14.x. Upgrade every affected application to a patched release immediately.
