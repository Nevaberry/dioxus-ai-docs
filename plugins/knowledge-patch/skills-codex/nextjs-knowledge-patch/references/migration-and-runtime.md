# Migration and Runtime

## Request interception

### Node.js Middleware runtime (`15.5.0`)

Middleware gained a stable Node.js runtime, but it remained opt-in at this
stage. Select it when Middleware needs Node APIs or npm packages:

```ts
export const config = { runtime: 'nodejs' }
```

### Move Middleware to Proxy (`16.0-guide`)

Next.js 16 renamed Middleware to Proxy without changing its purpose. Place the
single supported `proxy.ts` beside `app` or `pages`, either at the project root
or under `src`, and export a named `proxy` function or a default function.

```ts
import { NextResponse, type NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  return NextResponse.redirect(new URL('/home', request.url))
}

export const config = { matcher: '/about/:path*' }
```

Use Proxy for request-dependent rewrites, redirects, headers, and optimistic
checks. Do not put slow fetching or complete authorization there. `fetch`
cache, revalidation, and tag options have no effect in Proxy.

## Runtime and upgrade requirements

### Platform minimums (`16.0.0`)

Next.js 16 requires Node.js 20.9+ and TypeScript 5.1+. Supported browser floors
are Chrome 111+, Edge 111+, Firefox 111+, and Safari 16.4+.

### Removed commands and configuration (`16.0.0`)

Remove or replace all of the following when upgrading:

- AMP APIs and configuration.
- `next lint`; invoke the ESLint CLI or another linter directly. `next build`
  no longer performs linting.
- `serverRuntimeConfig` and `publicRuntimeConfig`; use environment variables.
- `appIsrStatus`, `buildActivity`, and `buildActivityPosition` development
  indicator options.
- `experimental.ppr`, `export const experimental_ppr`, and
  `unstable_rootParams()`.
- `experimental.turbopack`; move its options to top-level `turbopack`.

### Asynchronous request APIs (`16.0.0`)

Synchronous request access has been removed. Await page `params` and
`searchParams`, plus `cookies()`, `headers()`, and `draftMode()`.

```tsx
export default async function Page({ params }: PageProps<'/blog/[slug]'>) {
  const { slug } = await params
  return <h1>{slug}</h1>
}
```

Metadata image routes also receive asynchronous `params`. Every `id` returned
by `generateImageMetadata` is exposed to the image route as a
`Promise<string>`.

### Upgrade command (`16.1.0`)

Upgrade the framework directly with:

```sh
next upgrade
```

### Concurrent commands and locking (`16.0.0`)

`next dev` and `next build` use separate output directories, allowing them to
run concurrently. A project lockfile prevents conflicting instances of the
same command.

## Request compatibility corrections

### Live `headers()` view (`16.3.1`)

`headers()` again exposes a live view of the incoming request instead of a
detached view. The API remains asynchronous, so continue to await it.

### Dynamic Pages API route localization (`16.3.1`)

The recent i18n localization change for dynamic Pages Router API routes was
reverted. The earlier behavior is restored; do not depend on the temporary
localization behavior for routes such as `pages/api/[slug].ts`.

## Security upgrades (`release-catalogs`)

CVE-2025-66478 is a critical remote-code-execution vulnerability affecting
Next.js 15.x and 16.x. CVE-2025-55184 (denial of service) and CVE-2025-55183
(source exposure) also affect 13.x and 14.x. Upgrade every affected application
to a patched release immediately.
