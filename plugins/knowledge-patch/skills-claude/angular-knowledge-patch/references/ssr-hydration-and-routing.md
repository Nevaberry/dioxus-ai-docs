# SSR, Hydration, and Routing

## Incremental hydration (`19-guides`)

Enable incremental hydration through `provideClientHydration(withIncrementalHydration())`. This also enables event replay. SSR renders a hydrated `@defer` block's main template, but the client leaves that content dehydrated until a hydrate trigger fires.

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

Trigger rules:

- regular `on` triggers still control later client-side rendering;
- multiple hydrate triggers are ORed;
- a nested trigger hydrates its ancestor boundaries from the top down;
- `hydrate when` can fire only on the top-most dehydrated block; and
- `hydrate never` suppresses initial hydration for the entire nested subtree, but does not suppress later client rendering.

## Current server-route contract (`20-guides`)

Use slashless `ServerRoute.path`, `renderMode`, and `getPrerenderParams`. The parameter callback runs at build time, so call `inject()` synchronously before the first `await`.

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

Parameterized prerendering can fall back to `Server`, `Client`, or `None`; server rendering is the default. Routes may set static `headers` and `status`. Router `redirectTo` rules become HTTP redirects under SSR and `<meta http-equiv="refresh">` redirects in prerendered output.

The Developer Preview contract in `19.0.0` used leading-slash paths, `mode`, and `getPrerenderPaths`. Those names describe the historical preview only; do not use them in current code.

## Keep SSR pending for application work

Router navigation and `HttpClient` work are registered automatically. Register application-owned asynchronous work explicitly so zoneless SSR does not serialize too early.

Current code uses `PendingTasks.run()` or pairs `add()` with its cleanup callback in `finally` (`21-platform-guides`):

```ts
const pending = inject(PendingTasks);
pending.run(async () => state.set(await loadRenderedState()));
```

For an Observable, use zero-argument `pendingUntilEvent()`. It holds rendering until emission, completion, error, or unsubscription.

The earlier `19.0.0` form was `pendingUntilEvent(injector)`; treat that signature as version-specific rather than copying it into newer code.

## Request-scoped server state

`REQUEST`, `RESPONSE_INIT`, and `REQUEST_CONTEXT` from `@angular/core` expose the current Web `Request`, mutable response initialization, and engine-supplied context (`20-guides`). They are `null` during builds, client rendering, static generation, and development route extraction.

```ts
const request = inject(REQUEST);
const response = inject(RESPONSE_INIT);

if (request && response) {
  response.status = request.headers.has('Authorization') ? 200 : 401;
}
```

Top-level server `useValue` providers persist across requests. Supply request-specific values with `useFactory`.

## Fully static hybrid output

An SSR-enabled build prerenders the application but ordinarily still emits a server runtime. Use `outputMode: "static"` to omit it for static hosting:

```json
{
  "build": {
    "options": {
      "outputMode": "static"
    }
  }
}
```

## HTTP transfer cache

The hydration transfer cache defaults to unauthenticated `GET` and `HEAD` requests and includes no response headers. `withHttpTransferCacheOptions` can filter requests and opt into selected headers, idempotent `POST` requests, or requests with authorization headers (`20-guides`):

```ts
provideClientHydration(withHttpTransferCacheOptions({
  includeHeaders: ['ETag'],
  includePostRequests: true,
  filter: request => !request.url.includes('/api/profile'),
}));
```

An individual `HttpClient` call can set `transferCache: false` or specify `includeHeaders`; `withNoHttpTransferCache()` disables caching globally.

```ts
http.get('/api/private', {transferCache: false});
```

Transfer-cache request keys distinguish every repeated query parameter value (`20.3.28`). `/items?tag=a&tag=b` therefore does not collide with a request whose later `tag` values differ.

## Node and Web-standard engines

`AngularNodeAppEngine` from `@angular/ssr/node` accepts Node requests and pairs with `writeResponseToNodeResponse` and `createNodeRequestHandler`. Other runtimes use `AngularAppEngine` from `@angular/ssr`, whose `render` consumes and returns standard Web `Request` and `Response` objects through `createRequestHandler`.

```ts
const nodeEngine = new AngularNodeAppEngine();
const response = await nodeEngine.handle(req);
if (response) writeResponseToNodeResponse(response, res);

const webEngine = new AngularAppEngine();
export const handler = createRequestHandler(
  request => webEngine.render(request),
);
```

## Reactive current navigation

`Router.currentNavigation` is a `Signal<Navigation | null>` (`20.0.0`). Read it reactively when UI needs the navigation currently in progress:

```ts
const currentNavigation = inject(Router).currentNavigation;
```

## Browser Navigation API

`withExperimentalPlatformNavigation()` integrates the router with the Browser Navigation API (`22.0.0`). It intercepts both `RouterLink` and ordinary anchor navigation and uses native navigation lifecycle and scroll restoration:

```ts
bootstrapApplication(AppComponent, {
  providers: [
    provideRouter(routes, withExperimentalPlatformNavigation()),
  ],
});
```

This remains experimental; confirm its current signature and browser assumptions before relying on it.

## Route injector cleanup

Opt into `withExperimentalAutoCleanupInjectors()` to destroy injectors for routes that are no longer active (`22.0.0`):

```ts
provideRouter(routes, withExperimentalAutoCleanupInjectors())
```

When a custom `RouteReuseStrategy` discards a cached route, call `destroyDetachedRouteHandle()` to destroy its component through the supported API.

## Protocol-relative URL handling

Protocol-relative special handling now applies only during router URL serialization (`22.1.2`). Elsewhere, a string beginning with `//` no longer receives that special interpretation. Audit code that passed such strings directly to non-serialization router APIs.
