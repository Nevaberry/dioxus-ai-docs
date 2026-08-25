# Security, Observability, and CSP

## Action-origin protection

### Default cross-origin rejection

Since 7.12.0, submissions from external origins to UI routes are rejected by
default. List intentionally trusted origins in `allowedActionOrigins`.

```ts
export default {
  allowedActionOrigins: ["https://trusted.example"],
};
```

The same release validated redirect locations and escaped scroll-restoration keys,
addressing its CSRF and two XSS advisories.

In 7.13.0, the `**` glob began matching every domain. Use it only to deliberately
allow every origin. A failed check returns a client-error 400 rather than 500;
7.13.1 also renders the appropriate error UI for RSC flows.

### Dynamic allowlists for custom servers

A custom server may replace `allowedActionOrigins` on the imported server build
before passing it to `createRequestHandler`, allowing deployment-specific hosts.

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

### Proxy and adapter host behavior

As of 7.18.0, action-origin validation compares against the host in the
adapter-constructed `Request` URL rather than reading request headers directly.
Test mutations behind the real reverse proxy. `@react-router/serve` and Express
without `trust proxy` may need the internal host in `allowedActionOrigins` if that is
what the adapter puts in the request URL.

`@react-router/architect` can set `useRequestContextDomainName` on
`createRequestHandler` to derive the request host from API Gateway request context.
This becomes the default in v8; enable it when that context matches the
deployment architecture.

## Security patch levels

### Host-header sanitization

React Router 7.4.1 fixes CVE-2025-31137, where insufficient port sanitization in
`Host` and `X-Forwarded-Host` could manipulate URLs and pollute caches. Upgrade from
7.4.0 rather than relying on proxy behavior.

### The 7.9 patch line

Applications on the 7.9 line should use at least 7.9.6. The line includes:

- 7.9.0: JSON-LD XSS through `Meta`.
- 7.9.4: unauthorized file access through unsigned
  `createFileSessionStorage` cookies.
- 7.9.6: unexpected external redirects from untrusted paths.

### Generated and dependency output

Version 7.13.2 escapes redirect locations embedded in prerendered redirect HTML.
For dependency-only fixes, 7.10.1 updates `valibot` for
GHSA-vqpr-j7v3-hqw9, and `@react-router/serve` 7.11.0 updates `compression` and
`morgan` for GHSA-76c9-3jph-rj3q.

## Content Security Policy

### Nonce propagation

Nonce coverage expanded across releases:

- In 7.8.0, `Links` and `PrefetchPageLinks` gained `nonce`, applying it to their
  generated link elements.
- In 7.12.0, `<Scripts nonce>` also applied the nonce to the SRI-generated import-map
  script.
- In 7.13.0, the nonce passed to `Links` reached inline critical CSS.
- In 7.15.0, the nonce passed to `Scripts` reached generated
  `<link rel="modulepreload">` elements.
- In 7.18.0, nonce-aware SSR components inherited `ServerRouter`'s nonce when they
  did not receive one directly.

```tsx
<ServerRouter nonce={nonce} />
<Links nonce={nonce} />
<PrefetchPageLinks page="/account" nonce={nonce} />
<Scripts nonce={nonce} />
```

Inspect actual rendered HTML under the production CSP. Explicit component values can
still override inherited server values.

### Subresource integrity and link attributes

SRI began behind `future.unstable_subResourceIntegrity` in 7.5.0 and generated an
import map whose browser scripts carried `integrity` metadata. The top-level stable
name is `subResourceIntegrity` as of 7.15.0.

`Links` accepts `crossOrigin` as of 7.13.0 and forwards it to generated links.

```tsx
<Links crossOrigin="anonymous" nonce={nonce} />
```

## Client error reporting

`RouterProvider` and `HydratedRouter` gained provisional `unstable_onError` in
7.8.0. In 7.9.0, its second argument became an object containing `location`,
`params`, and optional React `errorInfo`, a breaking change for initial adopters.

```ts
function onError(
  error: unknown,
  info: {
    location: Location;
    params: Params;
    errorInfo?: React.ErrorInfo;
  },
) {
  report(error, info);
}
```

The context added the uninterpolated route `unstable_pattern` in 7.10.0. The callback
stabilized as `onError` in 7.11.0, and `pattern` lost its prefix in 7.15.0. Group
reports by pattern as well as concrete location to prevent high-cardinality route
parameters.

SPA Mode reports synchronous initial-loader errors through `RouterProvider.onError`
as of 7.15.0.

## Instrumentation

### Registration and coverage

The 7.9.0 `unstable_instrumentations` API can wrap server handlers, browser
navigations and fetches, loaders, actions, middleware, and `route.lazy`. Register it
through an `entry.server.tsx` export, `HydratedRouter` in `entry.client.tsx`, or
`createBrowserRouter` in Data Mode.

Loaders, actions, and middleware received `unstable_pattern`, the uninterpolated
route pattern such as `/blog/:slug`. In 7.15.0, these stabilized as
`instrumentations` and `pattern`; instrumentation type names also lost
`unstable_`. Handler and instrumentation arguments use normalized `url` and
`pattern`.

### Outer result metadata

Since 8.1.0, completed server `handler` and router `navigate` or `fetch`
instrumentations expose matched metadata at `result.meta`: normalized `url`, route
`pattern`, and `params`. Server handler results additionally expose
`result.statusCode`. This lets an outer layer aggregate by route even though it runs
before matching.

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
