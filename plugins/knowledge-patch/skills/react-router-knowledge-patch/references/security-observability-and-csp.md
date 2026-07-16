# Security, Observability, and CSP

## Contents

- [Cross-origin action protection](#cross-origin-action-protection)
- [Security fixes that require patched releases](#security-fixes-that-require-patched-releases)
- [CSP nonces and generated output](#csp-nonces-and-generated-output)
- [Subresource integrity](#subresource-integrity)
- [Client error reporting](#client-error-reporting)
- [Runtime instrumentation](#runtime-instrumentation)
- [JSON-LD output](#json-ld-output)

## Cross-origin action protection

UI-route submissions from external origins are rejected by default. Add only intentional
origins to `allowedActionOrigins` in `react-router.config.ts`.

```ts
export default {
  allowedActionOrigins: ["https://trusted.example"],
};
```

Since 7.13.1, the glob `**` matches every domain; use it only to intentionally disable origin
restriction. Rejected origins return a client-error `400`, not `500`, and RSC flows render the
corresponding error UI.

Custom servers can replace `allowedActionOrigins` on the imported server build before passing it
to `createRequestHandler`. This permits deployment-specific allowlists.

```ts
import { createRequestHandler } from "@react-router/express";
import type { ServerBuild } from "react-router";

async function getBuild() {
  const build: ServerBuild = await import("virtual:react-router/server-build");
  return {
    ...build,
    allowedActionOrigins:
      process.env.NODE_ENV === "development"
        ? undefined
        : ["staging.example.com", "www.example.com"],
  };
}

app.use(createRequestHandler({ build: getBuild }));
```

Origin validation compares against the host on the adapter-constructed `Request` URL, not raw
HTTP headers. Test mutations behind production reverse proxies. `@react-router/serve` and
Express without `trust proxy` may require the internal host in the allowlist if that is what the
adapter constructs.

For Architect/API Gateway, `@react-router/architect`'s `createRequestHandler` accepts
`useRequestContextDomainName` to derive the URL host from the request context. This option was
introduced before becoming the v8 default; enable it when that domain source matches the
deployment.

## Security fixes that require patched releases

- Version 7.4.1 fixes CVE-2025-31137, where insufficient port sanitization in `Host` and
  `X-Forwarded-Host` could manipulate URLs and pollute caches. Do not deploy 7.4.0.
- The 7.9 line fixes JSON-LD XSS through `Meta` in 7.9.0, unauthorized file access caused by
  unsigned `createFileSessionStorage` cookies in 7.9.4, and untrusted-path external redirects in
  7.9.6. Upgrade that line to at least 7.9.6 for all three.
- Version 7.10.1 raises `valibot` to `^1.2.0` for GHSA-vqpr-j7v3-hqw9; users of
  `@react-router/dev` should not remain on 7.10.0.
- Version 7.11.0 updates `@react-router/serve` dependencies `compression` and `morgan` for the
  `on-headers` advisory GHSA-76c9-3jph-rj3q.
- Version 7.12 validates redirect locations and escapes scroll-restoration keys, addressing its
  CSRF and two XSS advisories in addition to enabling origin protection.
- Version 7.13.2 escapes redirect locations embedded in prerendered redirect HTML.

## CSP nonces and generated output

Pass nonces to framework rendering components whose generated elements must satisfy policy:

```tsx
<Links nonce={nonce} crossOrigin="anonymous" />
<PrefetchPageLinks page="/account" nonce={nonce} />
<Scripts nonce={nonce} />
```

Nonce propagation covers these generated resources:

- `Links` and `PrefetchPageLinks` generated link elements.
- Inline `criticalCss` emitted with `Links`.
- The SRI-generated import-map script emitted with `Scripts`.
- `<link rel="modulepreload">` elements emitted with `Scripts`.

`Links` also accepts the standard `crossOrigin` prop and forwards it to generated links.

Nonce-aware SSR components fall back to the `nonce` on `ServerRouter` when they do not receive
their own value. This allows strict nonce policies without wiring the same nonce to every
component, while explicit component values can still be supplied.

## Subresource integrity

Subresource integrity generation began behind `future.unstable_subResourceIntegrity`; it
generates an import map with `integrity` metadata for browser-loaded scripts. The stable config
is top-level `subResourceIntegrity`.

```ts
export default {
  subResourceIntegrity: true,
};
```

When SRI and nonce CSP are combined, pass the nonce to `<Scripts>` so its generated import map
also receives it.

## Client error reporting

Use the stable `onError` prop on `RouterProvider` or `HydratedRouter`. It was introduced as
`unstable_onError` and later stabilized.

```tsx
<RouterProvider router={router} onError={reportError} />
```

The callback receives the error and an information object with `location`, `params`, optional
React `errorInfo`, and the matched route `pattern` where available. The second argument replaced
an earlier callback signature, and `pattern` was originally named `unstable_pattern`.

```ts
function reportError(
  error: unknown,
  info: {
    location: Location;
    params: Params;
    errorInfo?: React.ErrorInfo;
    pattern?: string;
  },
) {
  sendError({ error, ...info });
}
```

SPA Mode invokes `RouterProvider.onError` for synchronous failures from initial loaders, so the
same central reporter covers those startup failures.

## Runtime instrumentation

The `instrumentations` API can wrap server handlers, client navigation and fetch work, loaders,
actions, middleware, and `route.lazy`. It began as `unstable_instrumentations`; related type names
also lost their `unstable_` prefixes.

Register instrumentations through:

- an `instrumentations` export from `entry.server.tsx`;
- the `HydratedRouter` prop in `entry.client.tsx`; or
- the `createBrowserRouter` option in Data Mode.

Handler, loader, action, and middleware arguments expose `url` and the uninterpolated route
`pattern`, such as `/blog/:slug`, for normalized aggregation. These fields were originally
`unstable_url` and `unstable_pattern`. `Location.mask` is optional. Static handler `query` and
`queryRoute` use `normalizePath`, formerly `unstable_normalizePath`.

After outer server `handler` and router `navigate`/`fetch` instrumentations complete, the result
exposes normalized URL, pattern, and params at `result.meta`; server handlers also expose
`result.statusCode`. The metadata is available after matching even though the outer layer began
before routes were known.

```ts
export const instrumentations = [{
  handler(handler) {
    handler.instrument({
      async request(next) {
        const result = await next();
        report({
          url: result.meta?.url,
          pattern: result.meta?.pattern,
          params: result.meta?.params,
          statusCode: result.statusCode,
        });
      },
    });
  },
}];
```

Prefer `pattern` over the concrete pathname for route-level grouping, and include normalized
`url`, params, and status only where their cardinality is acceptable.

## JSON-LD output

`MetaDescriptor` accepts an array of `LdJsonObject` values for `script:ld+json`, allowing one
script to contain multiple schemas. Keep all values structured rather than hand-building markup;
patched router releases include JSON-LD escaping fixes.
