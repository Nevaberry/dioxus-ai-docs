---
name: react-knowledge-patch
description: React
license: MIT
version: "19.2.0"
metadata:
  author: Nevaberry
---

# React Knowledge Patch

Use the quick references below for implementation decisions, then open the linked topic file for complete constraints and edge cases.

## Index

| Reference | Topics |
|---|---|
| [Activity and Effect Events](references/activity-and-effects.md) | Hidden UI, pre-rendering, hydration, DOM side effects, `useEffectEvent` |
| [Compiler and lint](references/compiler-and-lint.md) | Compiler dependency tracking, Hooks ESLint v6, starter defaults, upgrade policy |
| [React 19 migration](references/react-19-migration.md) | Generated IDs, CSP nonces, maintained patch levels |
| [Security](references/security.md) | RSC request-decoding vulnerabilities, framework remediation, React Native exception |
| [Server rendering](references/server-rendering.md) | `cacheSignal`, partial pre-rendering, resume APIs, streams, Suspense reveal batching |
| [Tooling and platforms](references/tooling-and-platforms.md) | Performance Tracks, Fragment refs, React Native 0.82, Virtual View |
| [View Transitions](references/view-transitions.md) | Canary activation, classes, types, shared elements, events, router integration |

## Critical: patch RSC deployments

Applications with an RSC-capable framework, bundler, or plugin can be vulnerable even if application code declares no Server Functions. Update these together:

```sh
npm install react@latest react-dom@latest \
  react-server-dom-webpack@latest
```

Substitute the installed `react-server-dom-*` transport, and also update the framework or RSC plugin that integrates it. Initial fixes were followed by additional denial-of-service and source-exposure fixes, so target the latest patched release rather than an initial fixed version. Hosting mitigations are not a substitute.

Client-only applications with no RSC-capable integration are unaffected. React Native monorepos have narrower remediation rules; read [Security](references/security.md) before changing their React versions.

## Breaking configuration and output changes

### Hooks ESLint v6

The `recommended` preset is now an ESLint flat-config preset:

```js
import reactHooks from "eslint-plugin-react-hooks";

export default [reactHooks.configs.recommended];
```

For an eslintrc project, select the legacy preset explicitly:

```yaml
extends:
  - plugin:react-hooks/recommended-legacy
```

Remove `eslint-plugin-react-compiler`; compiler linting lives in `eslint-plugin-react-hooks@latest` and does not require the compiler package to be installed.

### Generated IDs

The default `useId` prefix is now `_r_`. It replaces the earlier `:r:` and `«r»` forms, making IDs valid as `view-transition-name` values and XML 1.0 names. Update snapshots or logic that exposes generated IDs; do not depend on the exact generated text.

### React Native 0.82

React Native 0.82 supports only the New Architecture. An application upgrading to it cannot retain the legacy architecture. Hermes V1 support is experimental, not a stable runtime recommendation.

## Activity: preserve and prepare hidden UI

Use `<Activity>` when hidden content should keep component and DOM state or prepare likely navigation targets:

```jsx
<Activity mode={activeTab === "posts" ? "visible" : "hidden"}>
  <Posts />
</Activity>
```

In `hidden` mode, React:

- keeps component and DOM state;
- hides retained DOM with `display: none`;
- cleans up Effects and recreates them on reveal;
- processes updates at low priority; and
- can warm Suspense data, `lazy` code, or a cached Promise consumed with `use`.

Fetching initiated inside an Effect does not run while initially hidden. Retained `<video>`, `<audio>`, or `<iframe>` elements can continue browser-owned behavior after Effect cleanup, so cleanup must stop that behavior explicitly.

During SSR, an initially hidden Activity is omitted from the response and rendered on the client while visible content hydrates. A visible Activity remains in HTML and creates a selective-hydration boundary, which can isolate slow hydration even if it never becomes hidden.

## Effect Events: latest values without dependencies

`useEffectEvent` callbacks read the latest committed props and state without adding those values to an Effect dependency list:

```jsx
const onConnected = useEffectEvent(() => {
  showNotification("Connected", theme);
});

useEffect(() => {
  const connection = connect(roomId, onConnected);
  return () => connection.disconnect();
}, [roomId]);
```

The callback intentionally changes identity on every render. Do not place it in a dependency array, call it during render or from an ordinary event handler, or pass it to another component or Hook. Call it only from an Effect or another Effect Event local to the same component. `useEffect`, `useLayoutEffect`, and `useInsertionEffect` may call it.

## Partial pre-rendering

`prerender` can return a cacheable or immediately served `prelude` plus reusable `postponed` state. Persist that state and resume the same tree later for dynamic content:

```jsx
import { resume } from "react-dom/server";
import { prerender } from "react-dom/static";

const controller = new AbortController();
const { prelude, postponed } = await prerender(<App />, {
  signal: controller.signal,
});

await savePostponedState(postponed);
const stream = await resume(
  <App />,
  await getPostponedState(request),
);
```

Choose the continuation by output target:

| Goal | Web Stream | Node stream |
|---|---|---|
| Resume dynamic output | `resume` | `resumeToPipeableStream` |
| Finish as static HTML | `resumeAndPrerender` | `resumeAndPrerenderToNodeStream` |

Node supports the Web Streams APIs, but the Node-stream variants are faster there. Web Streams also do not provide compression by default.

## Cancel work at the RSC cache boundary

`cacheSignal()` is RSC-only. It returns a signal that aborts when the surrounding `cache()` lifetime ends because rendering completed, aborted, or failed:

```jsx
import { cache, cacheSignal } from "react";

const dedupedFetch = cache(fetch);

async function Component() {
  await dedupedFetch(url, { signal: cacheSignal() });
  return null;
}
```

Pass the signal to cancellable work so work whose result can no longer enter the cache stops consuming resources.

## Adopt the compiler deliberately

Compiler 1.0 tracks optional-chain accesses and indexed reads directly:

```jsx
const selectedName = users[selected]?.profile?.name;
```

New Expo projects on SDK 54 or newer enable the compiler by default. Vite and Next.js expose compiler-enabled starter choices instead. Compiler releases can change memoization boundaries and reveal latent Rules-of-React violations through changed Effect dependency behavior. Without strong end-to-end coverage, pin an exact version and test upgrades manually:

```sh
npm install --save-dev --save-exact babel-plugin-react-compiler@1.0.0
```

## View Transitions are Canary and DOM-only

React owns `document.startViewTransition()`. A synchronous `setState` does not activate a `<ViewTransition>` boundary; use a Transition-driven update, `useDeferredValue`, or a Suspense reveal:

```jsx
<ViewTransition enter="slide-in" exit="slide-out">
  {show && <Panel />}
</ViewTransition>

startTransition(() => setShow(value => !value));
```

React classifies activation as `enter`, `exit`, `update`, or `share`. Shared elements require matching, unique `name` values across removed and inserted trees. Type-specific classes use `addTransitionType`; imperative event handlers must return cleanup that cancels interrupted animation work.

Routers must unblock a pending Navigation in `useLayoutEffect`; waiting for `useEffect` deadlocks transition measurement. Animating browser back navigation requires the Navigation API because legacy `popstate` transitions must finish synchronously and are skipped.

## Diagnose rendering performance

Chrome DevTools performance profiles now receive React Scheduler and Components tracks. Use them to correlate update priorities and scheduling delays with component render, mount, and Effect work before adding custom instrumentation.

Streaming SSR may briefly hold completed Suspense boundaries so nearby boundaries reveal together. React abandons the delay when it could harm metrics such as the 2.5-second LCP threshold, so never depend on every boundary being batched.
