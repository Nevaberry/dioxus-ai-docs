# Security, sessions, and environment

## Type-safe environment variables

`astro:env` declarations separate client and server variables, prevent server secrets from entering client code or the server bundle, mark values required or optional, and validate strings, numbers, booleans, and enums (`5.0.0`). Import declared server values from `astro:env/server`:

```ts
import { STRIPE_API_KEY } from 'astro:env/server';
```

With the Cloudflare adapter, `astro:env/server` is available throughout server modules, including module initialization outside request scope, so shared clients can be constructed at the top level (`5.6.0`).

### Raw `import.meta.env` behavior

`experimental.rawEnvValues` stopped Astro from coercing strings such as `"true"`, `"false"`, `"1"`, and `"0"` in `import.meta.env`; it never affected `astro:env` (`5.12.0`).

`experimental.staticImportMetaEnv` superseded that option in `5.13.0`. It aligns direct `import.meta.env` access with Vite by inlining private values rather than replacing them with `process.env` references and by leaving values uncoerced. Remove `experimental.rawEnvValues` when enabling it.

This flag was introduced as the preview of the direct `import.meta.env` behavior intended for Astro 6.

## Content Security Policy

### Hash generation and directives

The CSP preview generated hashes for page scripts, styles, and dynamically loaded assets across prerendered, server-rendered, and SPA output (`5.9.0`). It accepted `true` or an object that selected the hash algorithm, added directives, and customized script or style hashes and resources. A pre-existing CSP response header was enforced alongside Astro's policy.

```js
export default defineConfig({
  experimental: {
    csp: {
      directives: ["default-src: 'self'"],
      scriptDirective: {
        resources: ['self', 'https://scripts.cdn.example.com'],
        scriptDynamic: true,
      },
    },
  },
});
```

On-demand pages send CSP response headers as of `5.10.0`, enabling directives such as `report-uri` and `frame-ancestors` that cannot be represented by a `<meta>` element. Prerendered pages still use meta tags unless the adapter produces static response headers.

Netlify and Vercel introduced `experimentalStaticHeaders` for prerendered CSP headers in `5.10.0`. The Node adapter and custom Adapter API feature gained the same capability in `5.11.0`:

```js
import node from '@astrojs/node';

export default defineConfig({
  experimental: { csp: true },
  adapter: node({
    mode: 'standalone',
    experimentalStaticHeaders: true,
  }),
});
```

CSP is stable under `security.csp` in Astro 6, and generated responsive-image styles are included in the policy automatically (`6.0.0`):

```js
export default defineConfig({
  security: { csp: true },
});
```

## Sessions

### Configuration and adapter defaults

The session preview used a boolean `experimental.session` flag while driver configuration lived at top-level `session` (`5.3.0`). Supported adapters could supply storage automatically: Node used the filesystem and Netlify used Netlify Blobs.

Sessions became stable in `5.7.0`. Remove `experimental.session` but retain any top-level `session` settings. Sessions are exposed as `Astro.session` in pages and components and as context `session` in endpoints, Actions, and middleware.

`session.driver` can select any `unstorage` driver. In addition to adapter defaults, Vercel supports Redis or Upstash with minimal setup.

### Typed data

Augment `App.SessionData` in `src/env.d.ts` to type known keys (`5.5.0`). `get()` then includes `undefined`, `set()` checks the declared value, and undeclared keys remain `any`.

```ts
declare namespace App {
  interface SessionData {
    user: { id: string; email: string };
    lastLogin: Date;
  }
}
```

### Explicit session IDs

`session.load(id)` selects a session independently of its cookie, useful when an API receives the ID in a header (`5.6.0`). Loading a missing ID creates a new session.

```ts
export const GET: APIRoute = async ({ session, request }) => {
  const id = request.headers.get('x-session-id');
  if (id) await session.load(id);
  return Response.json({ cart: await session.get('cart') });
};
```

For cookie-less clients, `session.sessionId` exposes the active or newly created ID so an endpoint can return it (`5.7.0`).

### Cloudflare and Netlify development storage

During the experimental phase, the Cloudflare adapter automatically used a Workers KV binding named `SESSION` when sessions were enabled (`5.6.0`). Create the namespace, bind it under that exact name, and omit a custom driver to use it.

The Netlify adapter's local development support provides local Blobs and uses them for sessions by default (`5.12.0`). The Cloudflare adapter likewise provides local Workers KV during `astro dev` with no application-code changes, and can optionally connect development to the remote production namespace (`5.13.0`).

## Cookies

### Partitioned cookies

`Astro.cookies.set()` accepts `partitioned: true` for a cookie isolated by top-level site, such as a session cookie used by an embedded application (`5.17.0`). Partitioned cookies must also be secure and are normally paired with `sameSite: 'none'`.

```astro
---
Astro.cookies.set('session', crypto.randomUUID(), {
  partitioned: true,
  secure: true,
  sameSite: 'none',
});
---
```

### Consuming response cookies

The instance method `cookies.consume()` marks cookies as consumed and returns their `Set-Cookie` header values (`6.3.0`). Calls to `set()` after consumption warn because headers have already been sent. The deprecated static `AstroCookies.consume(cookies)` remains available for adapter compatibility.
