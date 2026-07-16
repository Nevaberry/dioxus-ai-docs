# SSR, Hydration, and Routing

Batch attribution: 19-guides, 19.0.0, 20-guides, 20.0.0, 21-platform-guides, 21.0.0, 22.0.0.

## Configure server routes with the stabilized contract

Hybrid applications can choose server rendering, client rendering, or build-time prerendering per route. The stabilized contract uses:

- a slashless `path`;
- `renderMode`, not the preview name `mode`;
- `getPrerenderParams`, not the preview name `getPrerenderPaths`.

The parameter callback runs at build time. It has an injection context, but `inject()` must be called synchronously before any `await`.

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

For prerendered parameters, `fallback` can be `Server`, `Client`, or `None`; server rendering is the default. A server route can also declare static `headers` and `status`.

Router `redirectTo` rules have platform-specific output:

- server rendering emits an HTTP redirect;
- prerendering emits a `<meta http-equiv="refresh">` redirect.

The Angular 19 developer-preview form allowed leading-slash paths and used `mode` plus `getPrerenderPaths`:

```ts
const previewRoutes: ServerRoute[] = [
  {path: '/login', mode: RenderMode.Server},
  {path: '/dashboard', mode: RenderMode.Client},
  {
    path: '/product/:id',
    mode: RenderMode.Prerender,
    async getPrerenderPaths() {
      return [{id: '1'}, {id: '2'}];
    },
  },
];
```

Recognize that shape when migrating it, but do not use it for current code.

## Build for static hosting

An SSR-enabled build prerenders the application and normally still emits a server runtime. Set `outputMode` to `static` to omit that runtime for a fully static deployment:

```json
{
  "build": {
    "options": {
      "outputMode": "static"
    }
  }
}
```

Routes that require request-time rendering are incompatible with a purely static deployment.

## Access request-scoped state safely

These tokens from `@angular/core` expose state for the current render:

- `REQUEST`: the Web `Request`;
- `RESPONSE_INIT`: mutable response initialization;
- `REQUEST_CONTEXT`: context passed to the rendering engine.

They are `null` during builds, client-side rendering, static generation, and development route extraction. Always branch for `null`.

```ts
const request = inject(REQUEST);
const response = inject(RESPONSE_INIT);

if (request && response) {
  response.status = request.headers.has('Authorization') ? 200 : 401;
}
```

Top-level server providers configured with `useValue` persist across requests. Use `useFactory` for a value that must be created per request.

## Choose the server engine for the runtime

### Node.js

`AngularNodeAppEngine` from `@angular/ssr/node` accepts Node requests. Pair it with `writeResponseToNodeResponse` and `createNodeRequestHandler`:

```ts
const engine = new AngularNodeAppEngine();
const response = await engine.handle(req);

if (response) {
  writeResponseToNodeResponse(response, res);
}
```

### Web-standard runtimes

`AngularAppEngine` from `@angular/ssr` consumes and returns standard Web `Request` and `Response` objects. Wrap it with `createRequestHandler`:

```ts
const engine = new AngularAppEngine();

export const handler = createRequestHandler(
  request => engine.render(request),
);
```

## Register pending zoneless work

Zoneless SSR serializes once no work remains registered with `PendingTasks`. Router navigation and `HttpClient` requests are registered by Angular. Wrap application-owned promises in `PendingTasks.run()`:

```ts
import {inject, PendingTasks} from '@angular/core';

const pending = inject(PendingTasks);
pending.run(async () => {
  state.set(await loadRenderedState());
});
```

For manual lifecycle control, call `add()` and invoke its cleanup callback in `finally`.

For Observables, use `pendingUntilEvent()`. It holds rendering until the source emits, completes, errors, or is unsubscribed:

```ts
stream$.pipe(pendingUntilEvent()).subscribe();
```

The Angular 19 form required an injector argument—`pendingUntilEvent(injector)`—so remove that argument when migrating to the current zero-argument operator.

## Incremental hydration

Enable incremental hydration through `provideClientHydration(withIncrementalHydration())`:

```ts
bootstrapApplication(App, {
  providers: [
    provideClientHydration(withIncrementalHydration()),
  ],
});
```

This also enables event replay. For a hydrated `@defer` block, Angular renders the main template during SSR, then leaves the client content dehydrated until a hydrate trigger fires.

```html
@defer (on idle; hydrate on interaction) {
  <heavy-panel />
} @placeholder {
  <panel-skeleton />
}
```

Trigger semantics matter:

- ordinary `on` triggers still govern later client-side renders;
- multiple hydrate triggers are ORed;
- a trigger in a nested boundary hydrates its ancestors from the top down;
- `hydrate when` can fire only on the top-most dehydrated block;
- `hydrate never` prevents initial hydration of the entire nested subtree, but does not prohibit a later client render.

Post-render callbacks can still run before a component has hydrated. Do not assume that “after render” always means a dehydrated subtree is safe for arbitrary DOM work.

## Configure viewport defer triggers

An `@defer` viewport trigger can receive `IntersectionObserver` options, including `rootMargin`, to begin loading before the trigger intersects the viewport:

```html
<div #trigger>Load boundary</div>

@defer (on viewport({trigger, rootMargin: '100px'})) {
  <section>Content</section>
}
```

The compiler diagnostic for ineffective defer triggers identifies unreachable or redundant combinations. Fix the combination instead of suppressing the check.

## Control HTTP transfer caching

The hydration transfer cache includes unauthenticated `GET` and `HEAD` requests by default and transfers no response headers. Configure the global policy with `withHttpTransferCacheOptions`:

```ts
provideClientHydration(
  withHttpTransferCacheOptions({
    includeHeaders: ['ETag'],
    includePostRequests: true,
    filter: request => !request.url.includes('/api/profile'),
  }),
);
```

The policy can:

- include selected response headers;
- include idempotent `POST` requests;
- include requests that carry authorization headers;
- filter requests entirely.

Override one call with `transferCache: false` or an object containing its own `includeHeaders`:

```ts
http.get('/api/private', {transferCache: false});
```

Use `withNoHttpTransferCache()` to disable transfer caching globally.

## Observe and clean up navigation

`Router.currentNavigation` is a `Signal<Navigation | null>`, allowing reactive inspection of the navigation currently in progress:

```ts
const currentNavigation = inject(Router).currentNavigation;
```

Angular 22 adds two experimental lifecycle features:

- `withExperimentalPlatformNavigation()` integrates the router with the browser Navigation API, intercepting both `RouterLink` and ordinary anchor navigations while using the native navigation lifecycle and scroll restoration.
- `withExperimentalAutoCleanupInjectors()` destroys dependency injectors for routes that are no longer active.

```ts
bootstrapApplication(AppComponent, {
  providers: [
    provideRouter(
      routes,
      withExperimentalPlatformNavigation(),
      withExperimentalAutoCleanupInjectors(),
    ),
  ],
});
```

When a custom `RouteReuseStrategy` discards a cached route, call `destroyDetachedRouteHandle()` to destroy its component through the supported API.

Angular DevTools includes route visualization and a Transfer State tab; see [UI Libraries, Platform Data, and DevTools](ui-platform-and-devtools.md).
