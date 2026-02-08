# Next.js Caching (16.0+)

## The `"use cache"` Directive

`"use cache"` marks pages, components, or functions as cacheable. The compiler automatically generates cache keys from the arguments passed. Requires `cacheComponents: true` in `next.config.ts`.

### Page-level caching

```tsx
// app/products/page.tsx
"use cache";

export default async function ProductsPage() {
  const products = await db.products.findMany();
  return <ProductList products={products} />;
}
```

### Function-level caching

```ts
// lib/data.ts
import { cacheLife } from 'next/cache';

export async function getUser(id: string) {
  "use cache";
  cacheLife('hours'); // use a built-in cache profile
  return db.users.findUnique({ where: { id } });
}
```

### Component-level caching

```tsx
async function ExpensiveChart({ data }: { data: number[] }) {
  "use cache";
  const rendered = await renderChart(data);
  return <div dangerouslySetInnerHTML={{ __html: rendered }} />;
}
```

## Cache Profiles (`cacheLife`)

Built-in profiles control cache duration and stale-while-revalidate behavior:

| Profile | Description |
|---------|-------------|
| `'max'` | Long-lived content, background revalidation |
| `'days'` | Multi-day cache |
| `'hours'` | Hour-scale cache |

Custom profiles can be defined in `next.config.ts`:

```ts
const nextConfig: NextConfig = {
  cacheComponents: true,
  cacheLife: {
    custom: { expire: 900, stale: 300 },
  },
};
```

## `updateTag(tag)` — Immediate Consistency

Server Actions only. Expires the cache entry and immediately reads fresh data within the same request. The user sees updated content right away.

```ts
'use server';
import { updateTag } from 'next/cache';

export async function updateProfile(formData: FormData) {
  const name = formData.get('name') as string;
  await db.users.update({ where: { id: userId }, data: { name } });
  updateTag('profile'); // cache expires + fresh data read immediately
}
```

Use for interactive workflows: forms, settings, toggles — anywhere the user expects to see their change reflected instantly.

## `refresh()` — Refresh Uncached Data

Server Actions only. Refreshes uncached (dynamic) data displayed elsewhere on the page. Does not touch cached content at all.

```ts
'use server';
import { refresh } from 'next/cache';

export async function markNotificationAsRead(id: string) {
  await db.notifications.update({ where: { id }, data: { read: true } });
  refresh(); // refresh dynamic data like unread count
}
```

Complementary to the client-side `router.refresh()`. Use when cached page shells and static content should remain fast, but dynamic indicators (notification counts, status badges, live metrics) need to update.

## `revalidateTag(tag, profile)` — SWR Behavior

Available in any server context (not limited to Server Actions). Invalidates tagged cache entries with stale-while-revalidate semantics — users receive cached data immediately while Next.js revalidates in the background.

```ts
import { revalidateTag } from 'next/cache';

// Built-in profile
revalidateTag('posts', 'max');

// Inline profile
revalidateTag('posts', { expire: 3600 });
```

**Breaking change from 15.x**: The second argument is now required. Without it, the call is deprecated.

### Choosing the Right API

| Scenario | API | Why |
|----------|-----|-----|
| User submits a form and expects to see updated data | `updateTag('tag')` | Immediate read-your-writes consistency |
| Background content refresh (CMS publish, cron) | `revalidateTag('tag', 'max')` | SWR — users get cached data while fresh data loads |
| Refreshing live indicators after an action | `refresh()` | Only touches uncached data, leaves cache intact |
| Client-side full page refresh | `router.refresh()` | Client-side, refetches server components |
