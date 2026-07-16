# Migration and Runtime

Batch attributions used here: `15.5.0`, `16.0-guide`, `16.0.0`, `16.1.0`, and `release-catalogs`.

## Runtime minimums

Next.js 16 requires all of the following:

- Node.js 20.9 or newer.
- TypeScript 5.1 or newer.
- Chrome 111, Edge 111, Firefox 111, or Safari 16.4 and newer.

Raise CI, deployment, and local-development versions before debugging framework-level failures (`16.0.0`).

## Middleware-to-Proxy migration

Middleware gained a stable but opt-in Node.js runtime in `15.5.0`:

```ts
export const config = { runtime: 'nodejs' }
```

Next.js 16 renames the convention to Proxy (`16.0-guide`). Place the single supported `proxy.ts` next to `app` or `pages`, either at the root or under `src`, and export a named `proxy` function or a default function.

```ts
import { NextResponse, type NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  return NextResponse.redirect(new URL('/home', request.url))
}

export const config = { matcher: '/about/:path*' }
```

Use Proxy for request-dependent rewrites, redirects, response headers, and optimistic checks. It is not the place for slow fetching or complete authorization. `fetch` cache options, revalidation settings, and tags have no effect inside Proxy.

## Mandatory asynchronous request APIs

Synchronous access to request-bound APIs is removed (`16.0.0`). Await:

- Page and layout `params`.
- Page `searchParams`.
- `cookies()`, `headers()`, and `draftMode()`.
- `params` in metadata image routes.
- Every `id` returned by `generateImageMetadata`; the route receives it as a `Promise<string>`.

```tsx
export default async function Page({ params }: PageProps<'/blog/[slug]'>) {
  const { slug } = await params
  return <h1>{slug}</h1>
}
```

Do not hide synchronous access behind casts. Move callers to async boundaries and propagate `await` through their call sites.

## Removed features and configuration

The following are removed in Next.js 16 (`16.0.0`):

- AMP APIs and AMP configuration.
- The `next lint` command.
- `serverRuntimeConfig` and `publicRuntimeConfig`; use environment variables instead.
- Development-indicator options `appIsrStatus`, `buildActivity`, and `buildActivityPosition`.
- `experimental.ppr` and route-level `export const experimental_ppr`.
- `unstable_rootParams()`.

Move Turbopack options from `experimental.turbopack` to the top-level `turbopack` key. `next build` no longer performs linting.

### Linter transition

In `15.5.0`, `next lint` was deprecated, while `next build` still ran lint validation when an ESLint configuration existed. Migrate directly to the ESLint CLI with:

```sh
npx @next/codemod@latest next-lint-to-eslint-cli .
```

New applications can choose ESLint, Biome, or no linter. In Next.js 16, run the chosen linter separately because neither `next lint` nor build-time linting remains. `@next/eslint-plugin-next` now defaults to ESLint Flat Config (`16.0.0`).

## Command upgrades and runtime behavior

Use the framework upgrade command introduced in `16.1.0`:

```sh
next upgrade
```

`next dev` and `next build` use separate output directories, allowing them to run concurrently. A project lockfile still prevents conflicting instances of commands from operating on the same application (`16.0.0`).

To use Node.js native TypeScript stripping for configuration, pass `--experimental-next-config-strip-types` to `next dev`, `next build`, or `next start`; see the configuration reference for details.

## React Server Components security updates

The `release-catalogs` batch identifies urgent fixes:

- CVE-2025-66478 is a critical remote-code-execution vulnerability affecting Next.js 15.x and 16.x.
- CVE-2025-55184 is a denial-of-service vulnerability that additionally affects Next.js 13.x and 14.x.
- CVE-2025-55183 can expose source code and additionally affects Next.js 13.x and 14.x.

Upgrade every affected application to a patched release immediately. Do not treat framework configuration as a substitute for installing the security update.
