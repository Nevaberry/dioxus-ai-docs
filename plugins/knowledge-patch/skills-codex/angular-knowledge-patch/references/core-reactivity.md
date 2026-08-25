# Core Reactivity, Components, and Change Detection

## Resource lifecycle

`resource` takes reactive `params` and an asynchronous `loader`. Returning
`undefined` from `params` leaves it idle. A parameter change aborts an active
load and passes the loader an `AbortSignal`. Guard `value()` with `hasValue()`
because it throws in the error state. `reload()` preserves the old value with
status `reloading`; `set()` and `update()` produce status `local`.
(`19-guides`)

```ts
const user = resource({
  params: () => id() ? {id: id()} : undefined,
  loader: ({params, abortSignal}) =>
    fetch(`/api/users/${params.id}`, {signal: abortSignal})
      .then(response => response.json()),
});
```

Every resource exposes a `snapshot` signal containing its status and either a
value or error. Transform it with signal APIs, then use `resourceFromSnapshots`
to retain the `Resource` interface—for example, to keep a previous value during
a parameter-driven reload. (`19-guides`)

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

With `provideHttpClient()` configured, `httpResource` issues requests eagerly,
reruns when a signal read by its request changes, cancels the prior request, and
retains interceptors and the HTTP testing backend. Use it for reads, not
mutations. JSON is the default; `.text()`, `.blob()`, and `.arrayBuffer()` select
other response types, and `parse` validates and determines `value()`'s type.
(`19-guides`)

```ts
const user = httpResource(() => `/api/users/${id()}`, {
  parse: UserSchema.parse,
});
```

`rxResource` accepts an Observable loader and publishes every emission
(`19.0.0`). A resource can instead supply `stream`; it resolves to a signal of
`ResourceStreamItem<T>`, and each update publishes `{value}` or `{error}`
(`20.0.0`).

```ts
const item = signal<{value: string[]}>({value: []});
const messages = resource({stream: () => Promise.resolve(item)});

socket.onmessage = event => {
  item.update(({value}) => ({value: [...value, event.data]}));
};
```

The `resource` and `httpResource` APIs are stable in Angular 22 (`22.0.0`).

## Submission-gated reads

Do not let live input trigger command-like requests. Keep draft text in one
signal and copy it into the signal used by `resource.params` only on submission.
A signal read only inside `loader`, such as a session ID, supplies its current
value without becoming a reload dependency. (`strategy-ai-and-news`)

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

## Effects and post-render work

Signal writes are allowed in `effect`; the old `allowSignalWrites` opt-in is
gone. Effects no longer run as independently queued microtasks: root effects run
before all component checks and view effects before their component is checked.
This can make `toObservable()` over input signals emit earlier. Move post-check
DOM or query work to `afterRenderEffect`. (`19-guides`)

`afterRenderEffect` runs after DOM commits. Its ordered phases are `earlyRead`,
`write`, `mixedReadWrite`, and `read`; a later phase receives the preceding
result as a signal, and an unphased callback defaults to `mixedReadWrite`. It is
client-only and can run before its component hydrates. (`19-guides`)

```ts
afterRenderEffect({
  earlyRead: () => host().nativeElement.getBoundingClientRect(),
  write: rect => {
    host().nativeElement.style.height = `${rect().width}px`;
  },
});
```

## Zoneless notification contract

Angular 21 applications are zoneless without an opt-in provider. Remove
`provideZoneChangeDetection()`, `zone.js` and `zone.js/testing` polyfills, and
the package. Angular 20 applications opt in with
`provideZonelessChangeDetection()`. (`21-platform-guides`)

Zoneless change detection is scheduled by `markForCheck()`,
`ComponentRef.setInput()`, a template-read signal update, a bound host or
template listener, or attaching an already-dirty view. `OnPush` is recommended,
not required, but an `OnPush` library host can prevent dynamically created user
components that still depend on ZoneJS from refreshing. (`21-platform-guides`)

`NgZone.onMicrotaskEmpty`, `onUnstable`, and `onStable` do not emit under
zoneless operation, and `NgZone.isStable` stays true. Use `afterNextRender` or
`afterEveryRender` for render timing and `MutationObserver` for DOM waits.
`NgZone.run()` and `runOutsideAngular()` remain compatible and should stay in
libraries that also support ZoneJS applications. (`21-platform-guides`)

Reactive Forms mutations such as `setValue()`, `patchValue()`, and
`FormArray.push()` update state and observables but do not schedule a zoneless
view refresh. Bridge a forms observable to `markForCheck()` or to a signal read
by the template. (`21-platform-guides`)

## Component defaults and dynamic creation

An unspecified component `changeDetection` now means `OnPush`. Use
`ChangeDetectionStrategy.Eager`, the renamed prior default, only when eager
checking is required. (`22.0.0`)

```ts
@Component({
  selector: 'legacy-widget',
  template: `...`,
  changeDetection: ChangeDetectionStrategy.Eager,
})
export class LegacyWidget {}
```

`createComponent` and `TestBed.createComponent` accept `inputBinding`,
`outputBinding`, and `twoWayBinding`, plus directives whose entries can have
their own bindings. Tests therefore need no wrapper component solely to bind an
input. (`20.0.0`)

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
```

`NgComponentOutlet` accepts an `EnvironmentInjector`, allowing its component to
resolve an isolated provider set (`20.0.0`). `Router.currentNavigation` is a
`Signal<Navigation | null>` for reactive access to an in-progress navigation
(`20.0.0`).

## Services and signal typing

`@Service()` is the concise form of `@Injectable({providedIn: 'root'})` for most
global singletons. Keep `@Injectable` for deeper provider configuration or
constructor injection. `injectAsync` lazily loads an auto-provided `@Service()`
and returns an asynchronous accessor; `{prefetch: onIdle}` enables idle-time
prefetching. (`22.0.0`)

```ts
@Service()
export class DataStore {}

private exporter = injectAsync(() => import('./report-exporter'));
```

Use `isSignal(value)` to detect any signal and `isWritableSignal(value)` to
narrow to writable signals. A computed signal passes only `isSignal`.
(`signals-and-control-flow`)

## Core typing changes

`SimpleChanges` is generic, providing typed previous and current values.
`KeyValuePipe` accepts object types with optional keys. (`21.0.0`)
