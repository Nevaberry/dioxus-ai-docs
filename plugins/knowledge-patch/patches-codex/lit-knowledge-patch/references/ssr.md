# Server-Side Rendering

## Migrate custom element renderers

Lit SSR 4.0 replaces generator use throughout the `ElementRenderer` interface
with a thunk/trampoline pattern. This is a breaking interface change.

Before upgrading, locate every custom renderer that implements or extends the
3.x interface. Port it to the new thunk/trampoline contract and run focused
SSR tests. A renderer that merely compiled against the generator-based
interface should not be assumed to work after the dependency change.

The `ssr-3.3-4.x` guidance also includes lifecycle, DOM-shim, and dependency
changes that may surface in the same upgrade.

## Opt into lifecycle callbacks

Lit SSR 3.3 adds event handling and can invoke `connectedCallback()` during
SSR. Enable the callback globally before rendering:

```js
globalThis.litSsrCallConnectedCallback = true;
```

The flag changes lifecycle behavior, so set it during server initialization
rather than midway through a render. Audit connected callbacks for browser
globals and side effects before opting in.

Starting in SSR 4.1, `LitElementRenderer` also exposes configuration that can:

- Disable SSR.
- Call `connectedCallback()` on `LitElement` subclasses.

Use renderer configuration when behavior needs to be scoped through the
renderer rather than controlled solely by the global flag.

## Use the expanded DOM shim

SSR 4.1 expands the DOM shim with:

- `ShadowRoot`.
- `document` in event paths.
- `MutationObserver`.
- `ResizeObserver`.
- `IntersectionObserver`.

Components that reference these browser APIs while server-rendering can run
against the shim implementations. Remove local stand-ins only after verifying
that the shim's behavior satisfies the component's needs; availability does
not guarantee that browser-specific layout or visibility assumptions are
meaningful during SSR.

Event tests should account for `document` now appearing in event paths.

## Manage Node typings explicitly

In SSR 4.0, `@types/node` becomes a ranged peer dependency. The SSR package no
longer forces a potentially conflicting Node typings version into the
consumer's dependency graph.

Ensure the consuming project provides a compatible `@types/node` version when
TypeScript checks server code. If an upgrade reveals missing Node globals or
types, inspect peer-dependency installation and the project's TypeScript
`types` configuration before adding casts.

## Upgrade checklist

1. Port custom `ElementRenderer` implementations before adopting SSR 4.0.
2. Verify that the application supplies compatible Node typings.
3. Decide whether server rendering should invoke `connectedCallback()`.
4. Audit lifecycle callbacks for server-safe behavior.
5. Revisit local DOM shims when adopting SSR 4.1.
6. Test event paths and all observer-dependent components on the server.

