# Security, Observability, and CSP

## Action-origin protection

### Default cross-origin rejection (`7.12.0`)

UI-route submissions from external origins are rejected by default. Add only intentional
origins to `allowedActionOrigins` in `react-router.config.ts`. The same release validates
redirect targets and escapes HTML in scroll-restoration keys, addressing CSRF and two XSS
issues.

```ts
export default {
  allowedActionOrigins: ["https://trusted.example"],
};
```

Custom servers may replace `allowedActionOrigins` on the imported `ServerBuild` before
calling `createRequestHandler`, which allows environment-specific policy
(`type-safety-and-config`).

```ts
const build: ServerBuild = await import("virtual:react-router/server-build");
return {
  ...build,
  allowedActionOrigins:
    process.env.NODE_ENV === "development"
      ? undefined
      : ["staging.example.com", "www.example.com"],
};
```

### Wildcards and rejection status (`7.13.0`)

The `**` glob matches every domain; use it only to deliberately allow all origins. Failed
origin checks return 400 rather than 500. RSC flows show the corresponding error UI from
7.13.1.

### Proxy and adapter host semantics (`7.18.0`)

Origin validation compares against the host of the adapter-constructed `Request` URL, not
raw HTTP headers. Test mutations behind the production reverse proxy and verify that URL.
`@react-router/serve` and Express without `trust proxy` may need their internal host in the
allowlist.

For Architect/API Gateway, `createRequestHandler` accepts
`useRequestContextDomainName` to derive the URL host from request context. Enable it when
that source matches the architecture; it is intended to become the v8 default.

## Security patch levels

### Host header fix (`7.4.0`)

7.4.1 fixes CVE-2025-31137: insufficient `Host`/`X-Forwarded-Host` port sanitization could
manipulate URLs and pollute caches. Upgrade deployments on 7.4.0.

### V7.9 fixes (`7.9.0`)

Applications remaining on the 7.9 line should use at least 7.9.6. The line fixes JSON-LD
XSS through `Meta` in 7.9.0, unauthorized file access caused by unsigned
`createFileSessionStorage` cookies in 7.9.4, and unexpected external redirects from
untrusted paths in 7.9.6.

### Tool dependency update (`7.10.0`)

Use `@react-router/dev` 7.10.1 or later in that line; it raises `valibot` to `^1.2.0` for
GHSA-vqpr-j7v3-hqw9.

### Serve dependency update (`7.11.0`)

`@react-router/serve` 7.11.0 updates `compression` and `morgan` to address the
`on-headers` advisory GHSA-76c9-3jph-rj3q.

### Prerender redirect escaping (`7.13.0`)

Version 7.13.2 escapes redirect locations embedded in generated prerender redirect HTML.

## Content Security Policy

### Framework links (`7.8.0`)

`Links` and `PrefetchPageLinks` accept `nonce`; pass it when their generated links must
satisfy nonce-based CSP.

```tsx
<Links nonce={nonce} />
<PrefetchPageLinks page="/account" nonce={nonce} />
```

`Links` also accepts `crossOrigin` and forwards it to generated links (`7.13.0`). Its
nonce reaches inline `criticalCss` from that release.

### SRI and import maps

`future.unstable_subResourceIntegrity` enables import-map integrity metadata in `7.5.0`.
In `7.12.0`, the nonce from `<Scripts nonce={nonce}>` reaches the generated `importmap`
script. The config becomes top-level `subResourceIntegrity` in `7.15.0`.

### Scripts, preloads, and SSR inheritance

The `Scripts` nonce reaches generated `<link rel="modulepreload">` elements from
`7.15.0`. In `7.18.0`, nonce-aware SSR components inherit the `ServerRouter` nonce when
they receive no component-specific value.

## Client-side error reporting

### Callback stabilization

`RouterProvider` and `HydratedRouter` gained provisional `unstable_onError` in `7.8.0`.
In `7.9.0`, its second argument became an object with `location`, `params`, and optional
React `errorInfo`, a breaking change for early adopters.

```ts
function onError(
  error: unknown,
  info: { location: Location; params: Params; errorInfo?: React.ErrorInfo },
) {
  report(error, info);
}
```

`7.10.0` adds `unstable_pattern` to that information for grouping by route pattern.
`7.11.0` stabilizes the prop as `onError` on both router components. In `7.15.0`, the
pattern name stabilizes, and synchronous initial-loader errors in SPA Mode also invoke
`RouterProvider.onError`.

## Runtime instrumentation

### Initial provisional surface (`7.9.0`)

`unstable_instrumentations` can wrap server handlers, client navigation/fetch, loaders,
actions, middleware, and `route.lazy`. Register through `entry.server.tsx`, the
`HydratedRouter` prop in `entry.client.tsx`, or the `createBrowserRouter` option. Handler
arguments also receive `unstable_pattern`, the uninterpolated route pattern, so telemetry
can avoid cardinality from concrete URLs.

### Stable names (`7.15.0`)

Use `instrumentations`, `pattern`, and `url`; instrumentation type names also lose
`unstable_`. `url` is normalized and `pattern` is suitable for aggregation.

### Outer result metadata (`8.1.0`)

After server `handler` and router `navigate`/`fetch` instrumentation completes, inspect
`result.meta.url`, `result.meta.pattern`, and `result.meta.params`. Server handler results
also expose `result.statusCode`. This supplies route metadata even though outer layers
start before matching.

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

## Verification checklist

- Send accepted and rejected mutations through the real proxy/adapter and assert the
  constructed request host.
- Avoid `allowedActionOrigins: ["**"]` unless the application truly accepts any origin.
- Verify nonces on links, critical CSS, import maps, scripts, module preloads, and inherited
  SSR output.
- Use a patched release within older v7 minor lines, not merely the first minor release.
- Group telemetry by `pattern` and normalized `url`; treat concrete params as potentially
  sensitive and high-cardinality.
