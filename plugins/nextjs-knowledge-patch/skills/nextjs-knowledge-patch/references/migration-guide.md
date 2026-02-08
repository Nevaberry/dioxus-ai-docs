# Next.js 16 Migration Guide

## Version Requirements

| Requirement | Minimum |
|-------------|---------|
| Node.js | 20.9.0 (LTS) — Node.js 18 no longer supported |
| TypeScript | 5.1.0 |
| Browsers | Chrome 111+, Edge 111+, Firefox 111+, Safari 16.4+ |

## Async APIs Enforced

In Next.js 15.x, sync access to these APIs produced warnings. In 16.0, sync access **throws an error**.

```tsx
// WRONG (16.x) — will error
export default function Page({ params }: { params: { slug: string } }) {
  return <div>{params.slug}</div>;
}

// CORRECT (16.x)
export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return <div>{slug}</div>;
}
```

All affected APIs:
- `params` in `layout.js`, `page.js`, `route.js`, `default.js`, `generateMetadata`, `generateViewport`
- `searchParams` in `page.js`
- `cookies()`, `headers()`, `draftMode()` from `next/headers`

Codemod: `npx @next/codemod@latest async-request-apis .`

## Parallel Routes: `default.js` Required

All parallel route slots now require an explicit `default.js` file. Builds fail without them.

```tsx
// app/@sidebar/default.tsx
export default function Default() {
  return null;
}

// Or, to show 404:
import { notFound } from 'next/navigation';
export default function Default() {
  notFound();
}
```

## `middleware.ts` → `proxy.ts`

`middleware.ts` is deprecated. Rename to `proxy.ts` and change the exported function name:

```ts
// Before: middleware.ts
export function middleware(request: NextRequest) { ... }

// After: proxy.ts
export function proxy(request: NextRequest) { ... }
```

`proxy.ts` runs on Node.js runtime by default. `middleware.ts` still works for Edge runtime use cases but will be removed in a future version.

## `revalidateTag()` Signature Change

The single-argument form is deprecated. A `cacheLife` profile is now required as the second argument:

```ts
// Before (15.x)
revalidateTag('posts');

// After (16.x)
revalidateTag('posts', 'max');     // built-in profile
revalidateTag('posts', { expire: 3600 }); // inline
```

For immediate consistency in Server Actions, use `updateTag('tag')` instead.

## Removals

| Removed | Replacement |
|---------|-------------|
| AMP support (`useAmp`, `config.amp`) | Remove all AMP code |
| `next lint` command | Use ESLint CLI or Biome directly |
| `legacyBehavior` on `next/link` | Remove prop and child `<a>` tags |
| `serverRuntimeConfig` / `publicRuntimeConfig` | Use `.env` files and `process.env` |
| `experimental.ppr` flag | Use `cacheComponents: true` |
| `experimental.dynamicIO` flag | Use `cacheComponents: true` |
| `export const experimental_ppr` (route-level) | Use `"use cache"` directive |
| `experimental.turbo` config | Use top-level `turbopack` key |
| `devIndicators` options (`appIsrStatus`, `buildActivity`, `buildActivityPosition`) | Indicator remains, options removed |
| `unstable_rootParams()` | Alternative API coming in a future minor |
| Automatic `scroll-behavior: smooth` | Add `data-scroll-behavior="smooth"` to HTML document |

## Turbopack Is Now Default

Turbopack is the default bundler for all apps. Opt out explicitly:

```bash
next dev --webpack
next build --webpack
```

## Image Configuration Changes

| Setting | Old Default | New Default (16.0) |
|---------|-------------|-------------------|
| `images.qualities` | `[1..100]` | `[75]` — `quality` prop coerced to closest value |
| `images.minimumCacheTTL` | 60s | 14400s (4 hours) |
| `images.imageSizes` | included `16` | `16` removed (used by only 4.2% of projects) |
| `images.dangerouslyAllowLocalIP` | allowed | blocked by default — set `true` for private networks |
| `images.maximumRedirects` | unlimited | 3 max |
| Local `src` with query strings | allowed | requires `images.localPatterns` config |

To restore previous quality behavior:

```ts
// next.config.ts
const nextConfig: NextConfig = {
  images: {
    qualities: [25, 50, 75, 100],
  },
};
```

## Deprecations (Will Be Removed Later)

| Deprecated | Replacement |
|------------|-------------|
| `middleware.ts` filename | Rename to `proxy.ts` |
| `next/legacy/image` | Use `next/image` |
| `images.domains` | Use `images.remotePatterns` |
| `revalidateTag()` single argument | Use `revalidateTag(tag, profile)` or `updateTag(tag)` |

## Config Renames Summary

| Old Location | New Location | Since |
|-------------|-------------|-------|
| `experimental.turbo` | `turbopack` | 15.3 |
| `experimental.typedRoutes` | `typedRoutes` | 15.5 |
| `experimental.reactCompiler` | `reactCompiler` | 16.0 |
| `experimental.ppr` + `experimental.dynamicIO` | `cacheComponents` | 16.0 |

## ESLint / Linting

`next lint` and automatic linting during `next build` are both removed. Set up linting directly:

```json
{
  "scripts": {
    "lint": "eslint ."
  }
}
```

Migration codemod: `npx @next/codemod@latest next-lint-to-eslint-cli .`

`@next/eslint-plugin-next` now defaults to ESLint Flat Config format.

## Other Behavior Changes

- **Prefetch cache**: Complete rewrite with layout deduplication and incremental prefetching (no code changes needed)
- **Babel in Turbopack**: Automatically enables if a babel config is found (previously hard error)
- **Dev/build output**: `next dev` and `next build` use separate output directories, enabling concurrent execution
- **Lockfile**: Prevents multiple `next dev` or `next build` instances on the same project
- **Sass**: Bumped `sass-loader` to v16 with modern Sass syntax support
