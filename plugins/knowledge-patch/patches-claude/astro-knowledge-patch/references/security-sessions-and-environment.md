# Security, sessions, and environment

## Typed environment variables (5.0.0)

`astro:env` declarations distinguish client and server values, prevent secrets
from reaching client code or the server bundle, mark fields required or
optional, and validate strings, numbers, booleans, and enums. Import declared
server values from the server-only virtual module:

```ts
import { STRIPE_API_KEY } from 'astro:env/server';
```

## Direct `import.meta.env` compatibility

Astro 5.12's `experimental.rawEnvValues` prevents coercion of strings such as
`"true"`, `"false"`, `"1"`, and `"0"` in direct `import.meta.env` access. It
does not affect `astro:env` imports (5.12.0).

Astro 5.13's `experimental.staticImportMetaEnv` supersedes that option. It
aligns with Vite by inlining private values rather than generating
`process.env` references and by leaving values uncoerced. Remove
`experimental.rawEnvValues` when enabling it; this behavior was planned as
the Astro 6 default (5.13.0).

```js
export default defineConfig({
  experimental: { staticImportMetaEnv: true },
});
```

## Cloudflare server environment access (5.6.0)

The Cloudflare adapter makes `astro:env/server` values available throughout
server modules, including module initialization outside request scope. Shared
clients can therefore be initialized once at module level.

```ts
import { API_URL } from 'astro:env/server';
import { createClient } from './client.js';

export const client = createClient(API_URL);
```

## Session configuration and defaults (5.3.0)

In the experimental Astro 5 form, `experimental.session` is a boolean while
driver and driver options belong under top-level `session`. Supported adapters
can supply storage: Node uses the filesystem and Netlify uses Netlify Blobs.

```js
export default defineConfig({
  adapter: node({ mode: 'standalone' }),
  experimental: { session: true },
  session: { driver: 'upstash' },
});
```

With Cloudflare, experimental sessions automatically use a Workers KV
namespace bound as `SESSION`. Create and declare the namespace before enabling
the feature (5.6.0):

```sh
npx wrangler kv namespace create "SESSION"
```

```json
{
  "kv_namespaces": [{ "binding": "SESSION", "id": "<SESSION_ID>" }]
}
```

## Stable sessions (5.7.0)

Remove `experimental.session` while retaining any `session` driver settings.
Sessions are exposed as `Astro.session` in pages and components and context
`session` in endpoints, Actions, and middleware.

```astro
---
export const prerender = false;
const cart = await Astro.session.get('cart');
---
<a href="/checkout">{cart?.length ?? 0} items</a>
```

Any `unstorage` driver can back sessions. Beyond adapter defaults, Vercel has
minimal setup for Redis and Upstash.

Set `session: false` to opt out. If no driver is configured, Astro can then
tree-shake the session runtime and `unstorage` from the SSR bundle
(7.0.1-7.2.4).

## Typing session data (5.5.0)

Augment `App.SessionData` in `src/env.d.ts`. Declared keys receive typed
`get()` results including `undefined`, and `set()` validates values; undeclared
keys remain `any`.

```ts
declare namespace App {
  interface SessionData {
    user: { id: string; email: string };
    lastLogin: Date;
  }
}
```

## Cookie-less session clients (5.6.0)

`session.load(id)` selects a session explicitly, for example from an API
header. Loading an unknown ID creates a new session. Return `session.sessionId`
to a cookie-less client so it can continue the active or newly created
session.

```ts
export const GET: APIRoute = async ({ session, request }) => {
  const id = request.headers.get('x-session-id');
  if (id) await session.load(id);
  return Response.json({
    cart: await session.get('cart'),
    sessionId: session.sessionId,
  });
};
```

## Partitioned cookies (5.17.0)

`Astro.cookies.set()` accepts `partitioned: true` for a cookie isolated by its
top-level site, useful when an Astro app is embedded. Partitioned cookies must
also be secure and are normally paired with `sameSite: 'none'`.

```ts
Astro.cookies.set('session', crypto.randomUUID(), {
  partitioned: true,
  secure: true,
  sameSite: 'none',
});
```

## Experimental CSP (5.9.0)

`experimental.csp` emits a hash-based policy for page scripts and styles,
including dynamically loaded assets, in static, runtime, and SPA output. It
accepts `true` or an object selecting the hash algorithm, extra directives,
and style or script hashes and resources. An existing CSP response header is
enforced alongside Astro's generated policy.

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

## CSP headers and static output

From 5.10.0, runtime pages send real CSP headers, enabling `report-uri`,
`frame-ancestors`, and other directives unavailable to a `<meta>` policy.
Prerendered pages still use meta policies unless their adapter can generate
static headers. Netlify and Vercel support this with
`experimentalStaticHeaders`.

The Node adapter adds the same option in 5.11.0; custom adapters can declare
the corresponding Adapter API feature:

```js
export default defineConfig({
  experimental: { csp: true },
  adapter: node({
    mode: 'standalone',
    experimentalStaticHeaders: true,
  }),
});
```

## Stable CSP (6.0.0)

Move configuration to `security.csp`. Generated responsive-image styles are
included automatically.

```js
export default defineConfig({
  security: { csp: true },
});
```

## Element- and attribute-specific directives (7.0.1-7.2.4)

CSP resource and hash entries accept `kind: 'element'`, `kind: 'attribute'`,
or `kind: 'default'`. These map to `script-src-elem`/`style-src-elem`,
`script-src-attr`/`style-src-attr`, or the generic directive. Runtime CSP
insertion methods accept the same object form.

```js
styleDirective: {
  resources: [{ resource: "'unsafe-inline'", kind: 'attribute' }],
}
```
