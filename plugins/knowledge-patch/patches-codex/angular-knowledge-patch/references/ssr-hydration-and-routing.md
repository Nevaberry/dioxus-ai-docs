# SSR, Hydration, and Routing

## Incremental hydration

Enable incremental hydration with
`provideClientHydration(withIncrementalHydration())`; this also enables event
replay. SSR renders a hydrated `@defer` block's main template, while the client
leaves it dehydrated until a hydrate trigger fires. Regular `on` triggers still
govern later client-side rendering. (`19-guides`)

```ts
bootstrapApplication(App, {
  providers: [provideClientHydration(withIncrementalHydration())],
});
```

```html
@defer (on idle; hydrate on interaction) {
  <heavy-panel />
} @placeholder {
  <panel-skeleton />
}
```

Multiple hydrate triggers are ORed. A nested trigger hydrates ancestor
boundaries from the top down. `hydrate when` can fire only on the top-most
dehydrated block. `hydrate never` suppresses initial hydration for the entire
nested subtree, but not a later client render. (`19-guides`)

## Server-route contract

The v19 developer-preview contract used leading-slash paths, `mode`, and
`getPrerenderPaths`; its callback ran in an injection context (`19.0.0`). The
stabilized contract uses slashless paths, `renderMode`, and
`getPrerenderParams`. Treat the old spellings as preview-only history.
(`20-guides`)

`getPrerenderParams` runs at build time and must call `inject()` synchronously
before any `await`. Parameterized prerendering can choose `Server`, `Client`, or
`None` fallback, with server rendering as the default. Routes also accept static
`headers` and `status`. Router `redirectTo` rules become HTTP redirects during
SSR and `<meta http-equiv="refresh">` redirects when prerendered. (`20-guides`)

```ts
export const serverRoutes: ServerRoute[] = [{
  path: 'post/:id',
  renderMode: RenderMode.Prerender,
  fallback: PrerenderFallback.Client,
  async getPrerenderParams() {
    const posts = inject(PostService);
    return (await posts.ids()).map(id => ({id}));
  },
}];
```

## Request-scoped server state

`REQUEST`, `RESPONSE_INIT`, and `REQUEST_CONTEXT` from `@angular/core` expose
the current Web `Request`, mutable response initialization, and engine context.
They are `null` during builds, CSR, SSG, and development route extraction.
Top-level server `useValue` providers persist across requests, so request data
requires `useFactory`. (`20-guides`)

```ts
const request = inject(REQUEST);
const response = inject(RESPONSE_INIT);
if (request && response) {
  response.status = request.headers.has('Authorization') ? 200 : 401;
}
```

## Pending asynchronous work

The v19 zoneless SSR API applied `pendingUntilEvent(injector)` to an Observable
to keep rendering pending until it emitted (`19.0.0`). The current operator is
zero-argument `pendingUntilEvent()` and keeps rendering pending through an
emission, completion, error, or unsubscription. (`21-platform-guides`)

For other application-owned work, use `PendingTasks.run()` or pair `add()` with
its cleanup callback in `finally`. Router navigation and `HttpClient` requests
are registered by Angular; without other registered work, zoneless SSR
serializes. (`21-platform-guides`)

```ts
import {inject, PendingTasks} from '@angular/core';
const pending = inject(PendingTasks);
pending.run(async () => state.set(await loadRenderedState()));
```

## Static and portable server builds

An SSR-enabled build normally prerenders and still emits a server file. Set
`outputMode: "static"` to omit the server runtime for static hosting.
(`20-guides`)

```json
{"build":{"options":{"outputMode":"static"}}}
```

`AngularNodeAppEngine` from `@angular/ssr/node` handles Node requests and pairs
with `writeResponseToNodeResponse` and `createNodeRequestHandler`. For non-Node
runtimes, `AngularAppEngine` from `@angular/ssr` renders standard Web `Request`
objects to `Response` objects through `createRequestHandler`. (`20-guides`)

```ts
const nodeEngine = new AngularNodeAppEngine();
const response = await nodeEngine.handle(req);
if (response) writeResponseToNodeResponse(response, res);

const webEngine = new AngularAppEngine();
export const handler = createRequestHandler(request => webEngine.render(request));
```

## HTTP transfer cache

The hydration transfer cache defaults to unauthenticated `GET` and `HEAD`
requests and includes no response headers. `withHttpTransferCacheOptions` can
filter requests and include selected headers, idempotent `POST` requests, or
requests with authorization headers. Per-call `transferCache: false` disables
it, a per-call object can set `includeHeaders`, and
`withNoHttpTransferCache()` disables it globally. (`20-guides`)

```ts
provideClientHydration(withHttpTransferCacheOptions({
  includeHeaders: ['ETag'],
  includePostRequests: true,
  filter: request => !request.url.includes('/api/profile'),
}));

http.get('/api/private', {transferCache: false});
```

Transfer-cache keys preserve repeated parameter values; `/items?tag=a&tag=b`
does not collide with a request whose later `tag` values differ (`20.3.28`).

## Router lifecycle and browser navigation

The experimental platform-navigation feature intercepts both `RouterLink` and
ordinary anchors, using the browser Navigation API lifecycle and scroll
restoration. (`22.0.0`)

```ts
bootstrapApplication(AppComponent, {
  providers: [provideRouter(routes, withExperimentalPlatformNavigation())],
});
```

Use `withExperimentalAutoCleanupInjectors()` to destroy injectors for routes no
longer active. When a custom `RouteReuseStrategy` discards a cached route, call
`destroyDetachedRouteHandle()` to destroy its component. (`22.0.0`)

Protocol-relative URL handling is now limited to serialization. Outside URL
serialization, strings beginning with `//` receive no special router treatment.
(`22.1.2`)
