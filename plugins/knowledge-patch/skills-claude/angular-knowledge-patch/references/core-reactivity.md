# Core Reactivity, Components, and Change Detection

## Resource lifecycle (`19-guides`)

`resource` accepts reactive `params` and an asynchronous `loader`. Returning `undefined` from `params` leaves the resource idle. A parameter change aborts an outstanding load and provides the next loader with an `AbortSignal`.

```ts
const user = resource({
  params: () => id() ? {id: id()} : undefined,
  loader: ({params, abortSignal}) =>
    fetch(`/api/users/${params.id}`, {signal: abortSignal})
      .then(response => response.json()),
});
```

Guard `value()` with `hasValue()` because `value()` throws in the error state. `reload()` retains the old value while status is `reloading`; local `set()` or `update()` changes status to `local`.

Resources, including `httpResource`, are stable in v22 (`22.0.0`). They model reads; keep explicit mutation commands outside the resource.

## Derived resources from snapshots

Every resource exposes a `snapshot` signal containing status and a value or error. Transform it through normal signal APIs, then pass the result to `resourceFromSnapshots` to retain the `Resource` interface. This can preserve the old value during a parameter-driven reload:

```ts
const stickySnapshot = linkedSignal<ResourceSnapshot<User>, ResourceSnapshot<User>>({
  source: user.snapshot,
  computation: (next, previous) =>
    next.status === 'loading' && previous && previous.value.status !== 'error'
      ? {status: 'loading' as const, value: previous.value.value}
      : next,
});

const stickyUser = resourceFromSnapshots(stickySnapshot);
```

## HTTP resources

With `provideHttpClient()` configured, `httpResource` eagerly requests data and reissues while cancelling the previous request when a read signal changes. It retains interceptors and the `HttpClient` test backend. JSON is the default response type; `.text()`, `.blob()`, and `.arrayBuffer()` select others. `parse` validates data and determines the type of `value()`.

```ts
const user = httpResource(() => `/api/users/${id()}`, {
  parse: UserSchema.parse,
});
```

Use it for reads, not mutations.

## Observable and streaming resources

`rxResource` (`19.0.0`) accepts an Observable-returning loader and updates on every emission:

```ts
const liveValue = rxResource({loader: () => values$});
```

A streaming resource (`20.0.0`) supplies `stream` instead of `loader`. The stream resolves to a signal of `ResourceStreamItem<T>`; every update publishes `{value}` or `{error}`:

```ts
const item = signal<{value: string[]}>({value: []});
const messages = resource({stream: () => Promise.resolve(item)});

socket.onmessage = event => {
  item.update(({value}) => ({value: [...value, event.data]}));
};
```

## Submission-gated requests

Do not let draft typing trigger a request. Keep the draft in one signal, copy it into the signal read by `resource.params` on submission, and read ancillary state inside the loader when it must not become a reload dependency (`strategy-ai-and-news`):

```ts
draft = signal('');
submitted = signal<string | undefined>(undefined);
sessionId = signal('session-1');

answer = resource({
  params: () => this.submitted(),
  loader: ({params}) => fetch('/api/answer', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({prompt: params, sessionId: this.sessionId()}),
  }).then(response => response.json()),
});

submit() {
  this.submitted.set(this.draft());
}
```

Signals read only inside `loader` provide their current values without becoming reload triggers.

## Effects and render timing

Signal writes are allowed in `effect`; `allowSignalWrites` is obsolete (`19-guides`). Effects are not independently queued microtasks: root effects run before all component checks and view effects before the associated component check. `toObservable()` over an input signal can therefore emit earlier than older timing assumptions expect.

Use `afterRenderEffect` for DOM or query work. It runs after DOM commits and supports `earlyRead`, `write`, `mixedReadWrite`, and `read`; an unphased callback defaults to `mixedReadWrite`. Each later phase receives the previous result as a signal.

```ts
afterRenderEffect({
  earlyRead: () => host().nativeElement.getBoundingClientRect(),
  write: rect => {
    host().nativeElement.style.height = `${rect().width}px`;
  },
});
```

It is client-only and can run before its component hydrates, so guard hydration-sensitive DOM access.

## Runtime component bindings

`createComponent` and `TestBed.createComponent` accept `inputBinding`, `outputBinding`, and `twoWayBinding` (`20.0.0`). Directives applied at runtime may have their own binding lists:

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
    {type: HasColor, bindings: [inputBinding('color', () => 'red')]},
  ],
});

const fixture = TestBed.createComponent(MyCheckbox, {
  bindings: [inputBinding('isChecked', isChecked)],
});
```

`NgComponentOutlet` accepts an `EnvironmentInjector` so its dynamic component can resolve an isolated provider set:

```html
<ng-container
  *ngComponentOutlet="componentType; environmentInjector: myEnvironmentInjector">
</ng-container>
```

## Zoneless defaults (`21-platform-guides`)

Angular 21 applications are zoneless without an opt-in provider. Remove `provideZoneChangeDetection()`, delete `zone.js` and `zone.js/testing` from build and test polyfills, and uninstall `zone.js`. Angular 20 instead opts in with `provideZonelessChangeDetection()`.

Zoneless change detection is scheduled after:

- `markForCheck()`;
- `ComponentRef.setInput()`;
- an update to a signal read in a template;
- a bound host or template listener; or
- attachment of a view already marked dirty.

OnPush is recommended but not required for that contract. A default-strategy component updates if it uses a recognized notification. Be careful when an OnPush library host creates a user component that still depends on ZoneJS.

Under zoneless operation, `NgZone.onMicrotaskEmpty`, `onUnstable`, and `onStable` never emit, and `NgZone.isStable` is always true. Use `afterNextRender` or `afterEveryRender` for render timing and `MutationObserver` or another DOM API for state waits. `NgZone.run()` and `runOutsideAngular()` remain useful in libraries that support both modes.

Reactive Forms calls such as `setValue()`, `patchValue()`, and `FormArray.push()` update state and observables but do not notify zoneless change detection. Bridge a form observable to a template-read signal or `markForCheck()`.

## OnPush default

Starting in v22, omitted component `changeDetection` means OnPush (`22.0.0`). The former default strategy is named `ChangeDetectionStrategy.Eager`:

```ts
@Component({
  selector: 'legacy-widget',
  template: `...`,
  changeDetection: ChangeDetectionStrategy.Eager,
})
export class LegacyWidget {}
```

Audit plain-field mutations and dynamic component boundaries after upgrading.

## Root and code-split services

`@Service()` is a concise replacement for `@Injectable({providedIn: 'root'})` for simple root singletons (`22.0.0`). Keep `@Injectable` when constructor injection or deeper provider configuration is required.

```ts
@Service()
export class DataStore {}
```

An auto-provided `@Service()` can be loaded on first use with `injectAsync`; `{prefetch: onIdle}` adds idle-time prefetching:

```ts
private exporter = injectAsync(() => import('./report-exporter'));

async export() {
  const exporter = await this.exporter();
  exporter.export();
}
```

## Runtime signal guards

`isSignal(value)` identifies any signal; `isWritableSignal(value)` narrows only writable signals (`signals-and-control-flow`). A computed signal passes the first and fails the second:

```ts
const count = signal(0);
const doubled = computed(() => count() * 2);

isSignal(count);               // true
isWritableSignal(count);       // true
isWritableSignal(doubled);     // false
```

## Core typing improvements

`SimpleChanges` is generic (`21.0.0`), enabling typed previous and current values. `KeyValuePipe` also accepts object types with optional keys.

## HTTP correctness fixes

`HttpHeaders.delete(name, value)` deletes exact values only (`21.2.20`); partial matches remain:

```ts
const headers = new HttpHeaders({'X-Mode': ['prod', 'production']});
const next = headers.delete('X-Mode', 'prod');
// next.getAll('X-Mode') is ['production']
```

Materializing a cloned `HttpHeaders` no longer compromises immutability. Always assign the object returned by a header operation. Root interceptors also run in terminal request chains, so backend-bound requests no longer skip root interception.

JSON responses are always decoded as UTF-8 (`22.1.2`), regardless of other response metadata.
