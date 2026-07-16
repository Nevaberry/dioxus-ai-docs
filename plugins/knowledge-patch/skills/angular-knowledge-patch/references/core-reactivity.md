# Core Reactivity, Components, and Change Detection

Batch attribution: 19-guides, 20.0.0, 21-platform-guides, 21.0.0, 22.0.0, signals-and-control-flow, strategy-ai-and-news.

## Asynchronous resources

The `resource` and `httpResource` APIs are stable in Angular 22. Use them for reads whose lifecycle should be represented as reactive state.

### Loader lifecycle

`resource` accepts reactive `params` and an asynchronous `loader`. Returning `undefined` from `params` leaves the resource idle. When parameters change, Angular aborts an outstanding load and gives its loader the corresponding `AbortSignal`.

```ts
const user = resource({
  params: () => id() ? {id: id()} : undefined,
  loader: ({params, abortSignal}) =>
    fetch(`/api/users/${params.id}`, {signal: abortSignal})
      .then(response => response.json()),
});
```

Guard `value()` with `hasValue()`: reading `value()` in the error state throws. Calling `reload()` retains the previous value with status `reloading`; local `set()` and `update()` operations produce status `local`.

### Snapshot composition

Every resource exposes a `snapshot` signal containing the status and either the value or error. Transform it with ordinary signal APIs, then pass the result to `resourceFromSnapshots` to retain the `Resource` interface. For example, preserve an old value while changed parameters reload:

```ts
const stickySnapshot = linkedSignal<
  ResourceSnapshot<User>,
  ResourceSnapshot<User>
>({
  source: user.snapshot,
  computation: (next, previous) =>
    next.status === 'loading' &&
    previous &&
    previous.value.status !== 'error'
      ? {status: 'loading' as const, value: previous.value.value}
      : next,
});

const stickyUser = resourceFromSnapshots(stickySnapshot);
```

### `httpResource`

After `provideHttpClient()` is configured, `httpResource` eagerly starts a request. It tracks signals read by the request factory, reissues when they change, and cancels the old request. It retains `HttpClient` interceptors and the `HttpClient` testing backend.

JSON is the default response type. Use `.text()`, `.blob()`, or `.arrayBuffer()` for other representations. A `parse` callback can validate the payload and determine the type of `value()`:

```ts
const user = httpResource(() => `/api/users/${id()}`, {
  parse: UserSchema.parse,
});
```

Use it for reads, not mutations.

### Observable and stream sources

Experimental `rxResource` was added in Angular 19.2. Its loader returns an Observable, and each emission updates the resource value rather than resolving only once:

```ts
const liveValue = rxResource({
  loader: () => values$,
});
```

A resource can instead supply `stream`. The stream resolves to a signal of `ResourceStreamItem<T>`; every signal update publishes either `{value}` or `{error}`:

```ts
const item = signal<{value: string[]}>({value: []});
const messages = resource({
  stream: () => Promise.resolve(item),
});

socket.onmessage = event => {
  item.update(({value}) => ({value: [...value, event.data]}));
};
```

### Gate requests on explicit submission

Do not use live draft text directly as `params` if typing should not issue requests. Copy the draft into a submitted signal only when the user submits. Signals read only inside `loader`, such as `sessionId` below, contribute their current values without becoming reload triggers.

```ts
draft = signal('');
submitted = signal<string | undefined>(undefined);
sessionId = signal('session-1');

answer = resource({
  params: () => this.submitted(),
  loader: ({params}) => fetch('/api/answer', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      prompt: params,
      sessionId: this.sessionId(),
    }),
  }).then(response => response.json()),
});

submit() {
  this.submitted.set(this.draft());
}
```

## Effects and post-render work

Angular 19 permits signal writes inside `effect` by default and removes the need for `allowSignalWrites`.

Effect scheduling also changed:

- root effects run before all component checks;
- view effects run before their associated component is checked;
- effects are no longer independent microtasks;
- `toObservable()` over input signals can consequently emit earlier.

Code that needs checked queries or committed DOM should use `afterRenderEffect`.

```ts
afterRenderEffect({
  earlyRead: () => host().nativeElement.getBoundingClientRect(),
  write: rect => {
    host().nativeElement.style.height = `${rect().width}px`;
  },
});
```

The phased form supports `earlyRead`, `write`, `mixedReadWrite`, and `read`. Each later phase receives the previous phase's result as a signal. An unphased callback defaults to `mixedReadWrite`. This API is client-only, but can run before the component has hydrated, so direct DOM access still requires a hydration-safe design.

## Zoneless change detection

Angular 21 applications are zoneless by default. Remove an old `provideZoneChangeDetection()` override, delete `zone.js` and `zone.js/testing` from application and test polyfills, and uninstall the package. Angular 20 applications opt in with `provideZonelessChangeDetection()`.

### Notification contract

Zoneless Angular schedules change detection in response to:

- `ChangeDetectorRef.markForCheck()`;
- `ComponentRef.setInput()`;
- an update to a signal read by a template;
- a bound host or template listener;
- attaching a view already marked dirty.

`OnPush` is a sound design even where it is not required. A default-strategy component can work without ZoneJS if it uses the notification mechanisms above. Be careful when an `OnPush` library host dynamically creates a user component that still assumes ZoneJS; the host can prevent that component from refreshing.

### `NgZone` compatibility

Under zoneless change detection:

- `NgZone.onMicrotaskEmpty`, `onUnstable`, and `onStable` never emit;
- `NgZone.isStable` is always `true`.

Replace render-timing dependencies with `afterNextRender` or `afterEveryRender`. Use a DOM API such as `MutationObserver` when the code genuinely waits for external DOM state. `NgZone.run()` and `runOutsideAngular()` remain compatible; do not mechanically remove them from a library that also supports ZoneJS applications.

### Reactive Forms are not notifications

Reactive Forms operations such as `setValue()`, `patchValue()`, and `FormArray.push()` update state and emit their Observables, but do not schedule a view refresh. If a template reads the changed state, bridge the relevant Observable to `markForCheck()` or to a signal that the template consumes.

For SSR pending-work registration and zoneless test patterns, see [SSR, Hydration, and Routing](ssr-hydration-and-routing.md) and [Testing, Build Tooling, and Migrations](testing-and-tooling.md).

## Component change-detection default

Starting in Angular 22, a component with no explicit `changeDetection` uses `OnPush`. `ChangeDetectionStrategy.Eager` is the new name for the old default strategy:

```ts
@Component({
  selector: 'legacy-widget',
  template: `...`,
  changeDetection: ChangeDetectionStrategy.Eager,
})
export class LegacyWidget {}
```

Audit plain-field mutation and legacy assumptions during migration. Prefer signal state or an explicit notification instead of opting every component back into eager checking.

## Runtime component composition

`createComponent` accepts `inputBinding`, `outputBinding`, and `twoWayBinding` entries, plus directives. An applied directive can have its own binding list:

```ts
const ref = createComponent(Dialog, {
  environmentInjector,
  bindings: [
    inputBinding('canClose', canClose),
    outputBinding<Result>('onClose', result => console.log(result)),
    twoWayBinding('title', title),
  ],
  directives: [
    FocusTrap,
    {
      type: HasColor,
      bindings: [inputBinding('color', () => 'red')],
    },
  ],
});
```

`TestBed.createComponent` accepts the same binding objects, so a test can set reactive inputs without a wrapper component:

```ts
const fixture = TestBed.createComponent(MyCheckbox, {
  bindings: [inputBinding('isChecked', isChecked)],
});
```

`NgComponentOutlet` accepts an `EnvironmentInjector`, letting a dynamically created component use an isolated provider set:

```html
<ng-container
  *ngComponentOutlet="componentType; environmentInjector: myEnvironmentInjector">
</ng-container>
```

## Root and code-split services

`@Service()` is a concise replacement for `@Injectable({providedIn: 'root'})` for most root singletons. Keep `@Injectable` when deeper provider configuration or constructor injection is required.

```ts
import {Service} from '@angular/core';

@Service()
export class DataStore {}
```

`injectAsync` loads an auto-provided service on first use and returns an asynchronous accessor. The target must use `@Service()`. The `prefetch: onIdle` option enables idle-time prefetching.

```ts
private exporter = injectAsync(() => import('./report-exporter'));

async export() {
  const exporter = await this.exporter();
  exporter.export();
}
```

## Signal and core type utilities

Use `isSignal(value)` to detect any signal and `isWritableSignal(value)` to narrow writable signals. A computed signal passes only the first guard.

```ts
const count = signal(0);
const doubled = computed(() => count() * 2);

isSignal(count);             // true
isWritableSignal(count);     // true
isWritableSignal(doubled);   // false
```

Angular 21 also makes `SimpleChanges` generic for stronger typing of previous and current values, and lets `KeyValuePipe` accept object types with optional keys.
