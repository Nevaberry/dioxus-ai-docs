# SolidStart

## SolidStart 1.0

SolidStart is the official meta-framework for SolidJS. It uses Vinxi (Vite + Nitro) under the hood.

### Basic Setup

```tsx
import { Suspense } from 'solid-js';
import { Router } from '@solidjs/router';
import { FileRoutes } from '@solidjs/start/router';

export default function App() {
  return (
    <Router root={(props) => <Suspense>{props.children}</Suspense>}>
      <FileRoutes />
    </Router>
  );
}
```

`props.children` must be wrapped in `<Suspense>` since each route component is lazy-loaded.

### File-Based Routing

Files in `routes/` directory become URL paths:

| URL | File |
|-----|------|
| `/` | `routes/index.tsx` |
| `/blog` | `routes/blog.tsx` |
| `/blog/article-1` | `routes/blog/article-1.tsx` |

### Nested Layouts

A file with the same name as a route folder acts as its layout:

```
routes/
  blog.tsx              <- layout for /blog/*
  blog/
    article-1.tsx       <- /blog/article-1
    article-2.tsx       <- /blog/article-2
```

```tsx
// routes/blog.tsx
import { RouteSectionProps } from '@solidjs/router';

export default function BlogLayout(props: RouteSectionProps) {
  return <div>{props.children}</div>;
}
```

### Renamed Index

To avoid many `index.tsx` files, rename to the folder name in parentheses:

```
routes/
  socials/
    (socials).tsx       <- /socials (same as index.tsx)
```

### Escaping Nested Routes

Use parentheses to create routes that share a URL prefix but have separate layouts:

```
routes/
  users/
    index.tsx           <- /users (uses users.tsx layout)
    projects.tsx        <- /users/projects
  users(details)/
    [id].tsx            <- /users/1 (uses users(details).tsx layout)
```

### Dynamic Routes

```
routes/users/[id].tsx           <- /users/:id
routes/users/[id]/[name].tsx    <- /users/:id/:name
routes/[...missing].tsx         <- catch-all /*
```

```tsx
import { useParams } from '@solidjs/router';

export default function UserPage() {
  const params = useParams();
  return <div>User {params.id}</div>;
}
```

### Optional Parameters

Double brackets for optional segments:

```
routes/users/[[id]].tsx         <- matches /users and /users/1
```

### Route Groups

Parenthesized folder names organize routes without affecting URLs:

```
routes/
  (static)/
    about-us/index.tsx          <- /about-us
    contact-us/index.tsx        <- /contact-us
```

### Route Config (preload)

Export a `route` object for additional config:

```tsx
import type { RouteDefinition } from '@solidjs/router';

export const route = {
  preload() {
    // preload data for this route
  },
} satisfies RouteDefinition;

export default function UsersLayout(props) {
  return <div>{props.children}</div>;
}
```

### Server Function Meta

`getServerFunctionMeta` moved from `@solidjs/start/server` to `@solidjs/start` in 1.1. The old export is deprecated.

## SolidStart 1.1

Released Feb 2025. Key changes:

- **Vite 6 support**
- **OPTIONS HTTP method** added to fs-router (enables CORS preflight handling)
- **RequestEventLocals** moved to `App` namespace for easier retyping
- **Vinxi updated** to 0.5.3
- Adopted TanStack server functions plugin
- Bug fixes: 404 for missing server functions, middleware response awaiting

## SolidStart 2.0 Roadmap (DeVinxi)

SolidStart 2.0 replaces Vinxi with a pure Vite-based system:

| Release | Milestone |
|---------|-----------|
| `2.0.0-alpha` | Feature parity with 1.x |
| `2.0.0-beta` | Support for Solid 2.x |
| `2.0.0` | Battle-tested |

Close collaboration with TanStack Start team. Nitro v3 integration planned before stability.
