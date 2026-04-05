# SSR & Hydration (v19–v21)

## Route-level render mode (stable in v20)

Configure SSR, prerender, or client-only rendering per route via `ServerRoute[]`.

```typescript
import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRouteConfig: ServerRoute[] = [
  { path: '/login', mode: RenderMode.Server },
  { path: '/dashboard', mode: RenderMode.Client },
  {
    path: '/product/:id',
    mode: RenderMode.Prerender,
    async getPrerenderPaths() {
      const svc = inject(ProductService);
      const ids = await svc.getIds();
      return ids.map((id) => ({ id }));
    },
  },
  { path: '/**', mode: RenderMode.Prerender },
];
```

### RenderMode values

| Mode | Behavior |
|------|----------|
| `RenderMode.Server` | Server-side rendered on every request |
| `RenderMode.Client` | Client-side only (SPA behavior) |
| `RenderMode.Prerender` | Pre-rendered at build time |

Use `getPrerenderPaths()` for dynamic routes with `RenderMode.Prerender`.

---

## Incremental hydration (stable in v20)

Lazy hydration for SSR apps using `@defer` syntax with `hydrate` triggers. Components render on the server but only hydrate on the client when triggered.

### Bootstrap config

```typescript
provideClientHydration(withIncrementalHydration())
```

### Template — hydrate on viewport entry

```typescript
@defer (hydrate on viewport) {
  <shopping-cart/>
}
```

Hydration triggers follow the same syntax as `@defer` triggers: `on viewport`, `on idle`, `on interaction`, `on hover`, `on timer(5s)`, etc.
