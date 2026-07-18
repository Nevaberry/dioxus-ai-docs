---
name: angular-knowledge-patch
description: Angular
license: MIT
version: 22.0.0
metadata:
  author: Nevaberry
---

# Angular Knowledge Patch

Use this skill when writing, reviewing, upgrading, or debugging modern Angular applications. Start with the breaking changes and defaults below, then open the topic reference that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [Compatibility, security, and releases](references/compatibility-security-and-releases.md) | Supported Node.js, TypeScript, and RxJS combinations; browser policy; support lifecycle; update hops; CSP and security changes |
| [Core reactivity](references/core-reactivity.md) | Resources, effects, runtime bindings, zoneless change detection, services, signals, and core typing changes |
| [Signal Forms](references/signal-forms.md) | Field trees, schemas, validation, submission, custom controls, and Material/Aria integration |
| [SSR, hydration, and routing](references/ssr-hydration-and-routing.md) | Hybrid rendering, server routes, incremental hydration, pending work, transfer cache, engines, and router lifecycle |
| [Templates and animations](references/templates-and-animations.md) | Template syntax, diagnostics, CSS enter/leave animation, defer triggers, and host-directive matching |
| [Testing and tooling](references/testing-and-tooling.md) | Vitest, migrations, HMR, compiler checks, CLI tools, build changes, and removed test APIs |
| [UI, platform, and DevTools](references/ui-platform-and-devtools.md) | Angular Aria, Material, CDK, locale data, profiling, and debugging visualizations |

## Breaking changes and defaults

### Components default to OnPush

An omitted `changeDetection` now means `OnPush`. Use the renamed eager strategy only for a component that truly requires full eager checking:

```ts
@Component({
  selector: 'legacy-widget',
  template: `...`,
  changeDetection: ChangeDetectionStrategy.Eager,
})
export class LegacyWidget {}
```

Audit code that mutates plain fields without a recognized notification. Prefer signals, `markForCheck()`, `ComponentRef.setInput()`, template/host listeners, or attachment of an already-dirty view.

### New applications are zoneless

Do not add ZoneJS as a reflex. Remove stale `provideZoneChangeDetection()` overrides, `zone.js` polyfills, and the package when migrating an application to the zoneless default. `NgZone` stability events do not report render timing under zoneless operation; use `afterNextRender`, `afterEveryRender`, or a DOM observer.

Reactive Forms mutations emit through form observables but do not themselves schedule a zoneless refresh. Bridge the relevant observable to a template-read signal or call `markForCheck()`.

For server rendering, register application-owned asynchronous work with `PendingTasks`; router navigations and `HttpClient` calls are already registered.

### Use the current server-route contract

Server route paths are slashless. Configure `renderMode`, and use `getPrerenderParams` for parameterized prerendering. Call `inject()` synchronously before any `await` in that callback.

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

The older `mode` and `getPrerenderPaths` names belong only to the preview contract. See the SSR reference before changing hybrid rendering or redirect behavior.

### Removed and deprecated integrations

- The built-in Protractor builder and Hammer.js integration are gone.
- Experimental Jest and Web Test Runner integrations are deprecated; retained Jest suites need a community integration.
- Webpack-based Angular builders and `@ngtools/webpack` are deprecated.
- `TestBed.getFixture()` is now `TestBed.getLastFixture()`.
- `ChangeDetectorRef.checkNoChanges()` is removed; use fixture-level test APIs.

### Security behavior is stricter

Treat SVG animation URL attributes and `object[data]` as security-sensitive URL contexts. Translations cannot target `iframe src`; translated form attributes and translated interpolated bindings are sanitized. Do not bypass these checks to preserve old behavior.

## High-value APIs

### Choose the right resource primitive

Use `resource` for asynchronous reads driven by reactive parameters. Returning `undefined` from `params` leaves it idle; changing parameters aborts the previous load.

```ts
const user = resource({
  params: () => id() ? {id: id()} : undefined,
  loader: ({params, abortSignal}) =>
    fetch(`/api/users/${params.id}`, {signal: abortSignal})
      .then(response => response.json()),
});
```

Check `hasValue()` before `value()` because `value()` throws in the error state. `reload()` keeps the prior value with `reloading` status; `set()` and `update()` mark the value `local`.

Use:

- `httpResource` for `HttpClient`-backed reads with interceptors, cancellation, testing support, response-type helpers, and optional parsing.
- `rxResource` when an Observable loader should publish each emission.
- `stream` when a resource source publishes a signal of `{value}` or `{error}` items.
- `resourceFromSnapshots` when transforming a resource's snapshot signal while preserving the resource interface.

Keep mutation commands out of read resources. To submit explicitly, copy draft state into the signal used by `params`; reads performed only inside `loader` do not become reload dependencies.

### Put DOM work after rendering

Signal writes are allowed in `effect`; the old write opt-in is unnecessary. Root effects run before component checks and view effects run before their component is checked. Use `afterRenderEffect` for DOM- or query-dependent work.

```ts
afterRenderEffect({
  earlyRead: () => host().nativeElement.getBoundingClientRect(),
  write: rect => {
    host().nativeElement.style.height = `${rect().width}px`;
  },
});
```

Available phases are `earlyRead`, `write`, `mixedReadWrite`, and `read`; each later phase receives the prior phase result as a signal. The callback is client-only and can still run before its component hydrates.

### Build forms from writable model signals

Signal Forms turn a writable model signal into a callable typed field tree:

```ts
model = signal({email: '', password: ''});
loginForm = form(this.model, path => required(path.email));
```

```html
<input [formField]="loginForm.email" />
```

Every bindable field must exist in the initial model. Prefer empty leaf values over absent optional properties or `null` object branches. Track array fields by field identity so their interaction and validation state survive reordering.

Schemas support built-in, custom, cross-field, HTTP, asynchronous, and Standard Schema validation, plus reactive disabled, hidden, and readonly rules. Read the forms reference before implementing arrays, submission, reset, custom controls, or validation timing.

### Use native CSS enter and leave animation

For insertion and removal, attach classes with `animate.enter` and `animate.leave` instead of introducing the legacy animation DSL:

```html
@if (shown()) {
  <div animate.enter="enter" animate.leave="leave">Content</div>
}
```

Nested leave animations can run within the same component boundary.

### Prefer Angular Aria for headless interactions

`@angular/aria` provides unstyled directives for keyboard behavior, focus, ARIA state, screen-reader support, and RTL navigation. It covers autocomplete, listbox, select, multiselect, combobox, menu, menubar, toolbar, accordion, tabs, tree, and grid patterns. Keep markup, styling, and application behavior in the app.

### Use runtime bindings without wrappers

`createComponent` and `TestBed.createComponent` accept `inputBinding`, `outputBinding`, and `twoWayBinding`. Runtime-applied directives can have their own binding lists. `NgComponentOutlet` can receive an `EnvironmentInjector` for an isolated provider scope.

### Use lazy global services intentionally

Use `@Service()` as the concise root-singleton form when no deeper provider configuration or constructor injection is required. Such a service can be code-split with `injectAsync` and optionally prefetched on idle.

```ts
private exporter = injectAsync(() => import('./report-exporter'));
```

## Testing defaults

New projects use Vitest with a Node DOM emulator. `ng test` watches by default. Configure global Angular providers through a default-exported `providersFile`; use `setupFiles` for general initialization. Real-browser execution supports the Playwright or WebdriverIO Vitest providers.

Prefer `await fixture.whenStable()` in zoneless tests. Repeated unconditional `fixture.detectChanges()` can conceal missing change notifications; exhaustive no-change checks can expose them.

The CLI owns important portions of the Vitest configuration even when `runnerConfig` points to a custom file. Read the testing reference for target options, browser naming, migration limitations, and output files.

## Upgrade checklist

1. Match Angular, Node.js, TypeScript, and RxJS using the exact compatibility row for the destination minor line.
2. Move across majors one at a time with `ng update`, and ensure the destination is still supported.
3. Run the supplied migrations, including strict template checking and replacements for deprecated router-testing or styling constructs.
4. Re-test locale-sensitive output, URL sanitization, translated attributes, server redirects, and hydration transfer caching.
5. Verify zoneless notifications, pending SSR tasks, OnPush assumptions, and unit tests without relying on forced detection.
6. Replace removed integrations and plan exits from deprecated test and build tooling.

Preview APIs can change outside the normal deprecation guarantees. Confirm their current signatures before adopting them in long-lived libraries.
