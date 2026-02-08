---
name: nextjs-knowledge-patch
description: This skill should be used when writing Next.js code, using App Router, Server Components, Server Actions, Turbopack, or any Next.js 15.3+ / Next.js 16 features (2025-2026). It covers proxy.ts (middleware.ts replacement), "use cache", Cache Components, navigation hooks (onNavigate, useLinkStatus), caching APIs (updateTag, refresh, revalidateTag), typed routes, auto-generated PageProps, and breaking changes from 15.x to 16.x.
license: MIT
metadata:
  author: Nevaberry
  version: "16.1"
---

# Next.js Knowledge Patch (15.3 – 16.x)

Supplementary knowledge for Next.js features released after Claude's training cutoff. Covers versions 15.3 through 16.1 (April 2025 – January 2026).

## Request Interception: `proxy.ts`

Next.js 16 replaces `middleware.ts` with `proxy.ts`. Rename the file and export a `proxy` function instead of `middleware`. Runs on Node.js runtime by default.

```ts
// proxy.ts (project root)
import { NextRequest, NextResponse } from 'next/server';

export function proxy(request: NextRequest) {
  return NextResponse.next();
}
```

`middleware.ts` still works (Edge runtime) but is deprecated and will be removed.

> **15.5 note**: Middleware gained stable Node.js runtime support via `export const config = { runtime: 'nodejs' }` before the full `proxy.ts` transition.

## Caching: `"use cache"` and Cache Components

Next.js 16 introduces an opt-in caching model. All dynamic code runs at request time by default — caching is no longer implicit. Enable with:

```ts
// next.config.ts
const nextConfig: NextConfig = {
  cacheComponents: true,
};
```

Apply the `"use cache"` directive to cache pages, components, or functions. The compiler generates cache keys automatically:

```tsx
"use cache";

export default async function CachedPage() {
  const data = await fetchData();
  return <div>{data}</div>;
}
```

Replaces `experimental.ppr` and `experimental.dynamicIO`. Completes the Partial Prerendering story — static shells with dynamic holes via Suspense, fully opt-in.

For detailed caching API patterns and code examples, see **`references/caching.md`**.

### Caching API Quick Reference

| API | Context | Semantics | Use Case |
|-----|---------|-----------|----------|
| `updateTag(tag)` | Server Actions only | Read-your-writes (immediate) | Forms, user settings |
| `refresh()` | Server Actions only | Refreshes uncached data only | Notification counts, live metrics |
| `revalidateTag(tag, profile)` | Any server context | SWR (eventual consistency) | Static content invalidation |

**Breaking**: `revalidateTag()` now requires a `cacheLife` profile as 2nd argument (`'max'`, `'hours'`, `'days'`, or `{ expire: N }`).

## Navigation Hooks (15.3+)

**`onNavigate`** — prop on `<Link>`. Fires during SPA navigations only (not all clicks). Call `e.preventDefault()` to cancel.

```tsx
<Link href="/dashboard" onNavigate={(e) => {
  if (hasUnsavedChanges) e.preventDefault();
}}>
  Dashboard
</Link>
```

**`useLinkStatus`** — hook from `next/navigation`. Returns `{ pending: boolean }`. Must be used inside a `<Link>` descendant. Modeled after React's `useFormStatus`.

```tsx
'use client';
import { useLinkStatus } from 'next/navigation';

function LinkSpinner() {
  const { pending } = useLinkStatus();
  return pending ? <Spinner /> : null;
}

// <Link href="/page"><LinkSpinner /> Go</Link>
```

## TypeScript (15.5+)

### Route Props Type Helpers

Auto-generated `PageProps`, `LayoutProps`, `RouteContext` types — globally available, no imports needed:

```tsx
// app/blog/[slug]/page.tsx — no manual typing needed
export default async function Page({ params }: PageProps) {
  const { slug } = await params;
  return <article>{slug}</article>;
}
```

### Typed Routes

Compile-time route validation — moved from experimental to stable:

```ts
// next.config.ts
const nextConfig: NextConfig = { typedRoutes: true };
```

Invalid `<Link href>` paths cause TypeScript errors. Works with both Webpack and Turbopack.

### `next typegen`

Standalone type generation for CI validation without running dev/build:

```bash
next typegen && tsc --noEmit
```

## File Conventions

| File | Since | Purpose |
|------|-------|---------|
| `proxy.ts` | 16.0 | Request interception (replaces `middleware.ts`) |
| `instrumentation-client.js\|ts` | 15.3 | Client-side monitoring/analytics — runs before app code |
| `default.js` in parallel routes | 16.0 | **Required** for all slots or build fails |

## Configuration Reference

| Config | Purpose | Since |
|--------|---------|-------|
| `cacheComponents: true` | Enable `"use cache"` + PPR | 16.0 |
| `reactCompiler: true` | React Compiler (was `experimental`) | 16.0 |
| `typedRoutes: true` | Typed routes (was `experimental`) | 15.5 |
| `turbopack: { ... }` | Turbopack config (was `experimental.turbo`) | 15.3 |
| Turbopack is default bundler | Opt out with `--webpack` flag | 16.0 |

**Removed config**: `experimental.ppr`, `experimental.dynamicIO`, `serverRuntimeConfig`, `publicRuntimeConfig` (use `.env` files), `devIndicators` options.

## Tooling Changes

- **`next lint` removed** (16.0) — use ESLint CLI or Biome directly. Codemod: `npx @next/codemod@latest next-lint-to-eslint`
- **`next typegen`** (15.5) — standalone type generation for CI
- **Turbopack FS caching** — stable and on by default for `next dev` in 16.1

## React 19.2 (via App Router, 16.0+)

These are React-level APIs available through the App Router's React Canary channel. Refer to the [React 19.2 docs](https://react.dev) for full usage details.

- `<ViewTransition>` — animate elements during transitions
- `useEffectEvent()` — extract non-reactive logic from Effects into stable functions
- `<Activity>` — hide UI (`display: none`) while preserving state and cleaning up Effects

## Breaking Changes (16.0)

For full migration details with code examples, see **`references/migration-guide.md`**.

- **Node.js 20.9+**, TypeScript 5.1+, Chrome/Edge/Firefox 111+, Safari 16.4+
- **Async APIs enforced**: `await params`, `await searchParams`, `await cookies()`, `await headers()` — sync access now errors
- **Parallel routes**: all slots require explicit `default.js` or build fails
- **Removed**: AMP, `next lint`, `legacyBehavior` on Link, `serverRuntimeConfig`/`publicRuntimeConfig`
- **Image defaults**: `images.qualities` → `[75]`, `minimumCacheTTL` → 14400s, `localPatterns` required for query strings, `dangerouslyAllowLocalIP` blocks local IPs

## Additional Resources

### Reference Files

- **`references/caching.md`** — Detailed `"use cache"`, `updateTag()`, `refresh()`, `revalidateTag()` patterns with code examples
- **`references/migration-guide.md`** — Complete Next.js 16 breaking changes, removals, and migration steps
