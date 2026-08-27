# Router and Navigation

## Navigation prevention

Enable the `preventNavigate` experiment before using `usePreventNavigate`:

```ts
qwikVite({ experimental: ['preventNavigate'] });
```

The hook can block SPA navigation asynchronously. For other navigation with
unsaved state, it falls back to browser dialogs.

## Initial previous URL

On the first render, the router's previous URL is `undefined`. Handle the
missing value before reading or comparing the previous location.

## Rewrite fan-in

Multiple rewrite routes may point to the same destination route. This fan-in
does not produce a route error.

## Request-event rewrites

`RequestEvent.rewrite()` performs an internal redirect while preserving the
URL visible in the browser. Throw its result from a request handler:

```ts
export const onRequest: RequestHandler = async ({ rewrite }) => {
  throw rewrite('/articles/42');
};
```

## Redirect caching

Redirects no longer inherit a parent layout's `Cache-Control` header. They
default to `no-store`, so any cacheable redirect needs its own deliberate
response policy.

Source batches: `v1.8-1.13`, `v1.14-1.19`.
