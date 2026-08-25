# Security, sessions, and environment

## Typed environment variables

Since 5.0.0, `astro:env` separates client and server values, prevents secrets from reaching client code or the server bundle, supports required/optional declarations, and validates strings, numbers, booleans, and enums. Import declared secrets from `astro:env/server`.

Since 5.6.0, the Cloudflare adapter makes `astro:env/server` available throughout server modules, including module initialization outside request scope, so shared clients may be created at top level.

The 5.12.0 `experimental.rawEnvValues` flag leaves raw `import.meta.env` values such as `"true"` and `"1"` as strings; it does not change `astro:env`. In 5.13.0, `experimental.staticImportMetaEnv` supersedes it, inlines private values, removes coercion, and aligns access with Vite. Remove the older flag.

## CSP lifecycle and behavior

Astro 5.9.0 introduced hash-based CSP behind `experimental.csp`. `true` protects managed page scripts/styles; object configuration selects a hash algorithm, adds directives, and customizes script/style resources and hashes. Existing CSP response headers are enforced alongside generated policy.

Since 5.10.0, on-demand pages send CSP response headers, enabling directives such as `report-uri` and `frame-ancestors`. Prerendered pages use meta by default, but Netlify and Vercel can generate static headers with adapter `experimentalStaticHeaders`. Node gained the same adapter option in 5.11.0, and custom adapters can advertise the capability.

Astro 6.0.0 stabilizes configuration as `security.csp`; generated responsive-image styles are included automatically.

In 7.0.1-7.2.4, CSP resource and hash entries accept `kind: 'element'`, `'attribute'`, or `'default'`, targeting `script-src-elem`/`style-src-elem`, `script-src-attr`/`style-src-attr`, or generic directives. Runtime CSP insertion methods accept the same object form.

## Session configuration and defaults

In 5.3.0, experimental sessions used boolean `experimental.session`, with drivers/options at top-level `session`. Supported adapters supplied defaults: Node used filesystem storage and Netlify used Netlify Blobs.

Sessions became stable in 5.7.0. Remove the experimental flag while keeping driver settings. Access them through `Astro.session` in pages/components or context `session` in endpoints, Actions, and middleware. Any `unstorage` driver is allowed; Vercel supports Redis or Upstash with minimal setup.

In 7.0.1-7.2.4, set top-level `session: false` to opt out. Without a driver, Astro can tree-shake session runtime and `unstorage` from an SSR bundle.

## Typed and cookie-less sessions

Since 5.5.0, augment `App.SessionData` in `src/env.d.ts` to type known keys. `get()` includes `undefined`, `set()` validates values, and undeclared keys remain `any`.

Since 5.6.0, `session.load(id)` selects a session from an explicit ID rather than its cookie; a missing ID creates a session. Since sessions stabilized in 5.7.0, `session.sessionId` exposes the current or new ID so cookie-less endpoints can return it.

## Cloudflare session storage

In 5.6.0, experimental sessions with the Cloudflare adapter automatically use the Workers KV binding named `SESSION`; create the namespace and declare the binding. Since 5.13.0, the adapter supplies a local Workers KV implementation during `astro dev` with no project-code changes, with optional connection to remote KV for production data.

## Cookies

Since 5.17.0, `Astro.cookies.set()` accepts `partitioned: true` for cookies isolated by top-level site. Partitioned cookies must also be secure and are normally paired with `sameSite: 'none'`.

Since 6.3.0, `cookies.consume()` marks cookies consumed and returns `Set-Cookie` header values; later `set()` calls warn because headers were already sent. The old static form is deprecated.

After the cookie v2 change in 7.0.1-7.2.4, URL-safe values are not percent-encoded in `Set-Cookie`; already encoded values continue to round-trip.
