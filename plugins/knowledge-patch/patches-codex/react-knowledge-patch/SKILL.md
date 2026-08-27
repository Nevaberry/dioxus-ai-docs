---
name: react-knowledge-patch
description: React
version: "19.2.0"
license: MIT
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

Applications with an RSC-capable framework, bundler, or plugin can be vulnerable even when application code declares no Server Functions. Update React, React DOM, the installed RSC transport, and its framework or plugin integration together:

```sh
npm install react@latest react-dom@latest \
  react-server-dom-webpack@latest
```

Substitute the installed `react-server-dom-*` transport. Initial fixes were followed by denial-of-service and source-exposure fixes, so target the latest patched release rather than an initial fixed version. Hosting mitigations are not a substitute.

Client-only applications with no RSC-capable integration are unaffected. React Native monorepos have narrower remediation rules; read [Security](references/security.md) before changing their React versions.

## Migrate lint configuration deliberately

Hooks ESLint v6 changed the `recommended` preset to an ESLint flat-config preset. Existing eslintrc projects must select its legacy equivalent explicitly:

```yaml
extends:
  - plugin:react-hooks/recommended-legacy
```

Remove `eslint-plugin-react-compiler` and use `eslint-plugin-react-hooks@latest`. Compiler-powered linting now lives in the Hooks plugin and does not require the compiler package to be installed.

## Do not depend on generated ID text

The default `useId` prefix is `_r_`, replacing the earlier `:r:` and `«r»` forms. The new IDs are valid `view-transition-name` values and XML 1.0 names. Update snapshots or logic that exposes generated IDs instead of relying on their exact text.

## Plan React Native 0.82 as a one-way architecture upgrade

React Native 0.82 supports only the New Architecture. An application upgrading to it cannot retain the legacy architecture. Hermes V1 support is experimental, not a stable runtime recommendation.

## Preserve and prepare hidden UI with Activity

Use `<Activity>` when hidden content should retain component and DOM state or prepare likely navigation targets:

```jsx
<Activity mode={activeTab === "posts" ? "visible" : "hidden"}>
  <Posts />
</Activity>
```

In `hidden` mode, React hides retained DOM with `display: none`, cleans up Effects, recreates them on reveal, and processes the children at low priority. This can warm Suspense data, `lazy` code, or a cached Promise consumed with `use`; fetching initiated inside an Effect does not run while initially hidden.

Retained `<video>`, `<audio>`, and `<iframe>` elements can continue browser-owned behavior after Effect cleanup, so cleanup must stop that behavior explicitly.

During SSR, an initially hidden Activity is omitted from the response and rendered on the client while visible content hydrates. A visible Activity stays in the HTML and creates a selective-hydration boundary that can isolate slow hydration.

## Read latest values with Effect Events

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

The callback intentionally changes identity on every render. Do not put it in a dependency array, call it during render or from an ordinary event handler, or pass it to another component or Hook. Call it only from an Effect or another Effect Event local to the same component. `useEffect`, `useLayoutEffect`, and `useInsertionEffect` may call it.

## Resume partially pre-rendered trees

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

Prefer Node-stream variants on Node because they are faster there; Web Streams also do not provide compression by default.

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

New Expo projects on SDK 54 or newer enable the compiler by default. Vite and Next.js expose compiler-enabled starter choices instead.

Compiler releases can change memoization boundaries and reveal latent Rules-of-React violations through changed Effect dependency behavior. Without strong end-to-end coverage, pin an exact version and test upgrades manually:

```sh
npm install --save-dev --save-exact babel-plugin-react-compiler@1.0.0
```

## Activate View Transitions through React Transitions

`<ViewTransition>` and `addTransitionType` are Canary, DOM-only APIs. React owns `document.startViewTransition()`. A synchronous `setState` does not activate a boundary; use a Transition-driven update, `useDeferredValue`, or a Suspense reveal:

```jsx
<ViewTransition enter="slide-in" exit="slide-out">
  {show && <Panel />}
</ViewTransition>

startTransition(() => setShow(value => !value));
```

React classifies activation as `enter`, `exit`, `update`, or `share`. Shared elements require matching, unique `name` values across removed and inserted trees. Type-specific classes use `addTransitionType`; imperative event handlers must return cleanup that cancels interrupted animation work.

Routers must unblock a pending Navigation in `useLayoutEffect`; waiting for `useEffect` deadlocks transition measurement. Animating browser back navigation requires the Navigation API because legacy `popstate` transitions must finish synchronously and are skipped.

## Diagnose rendering performance first

Chrome DevTools performance profiles receive React Scheduler and Components tracks. Use them to correlate update priorities and scheduling delays with component render, mount, and Effect work before adding custom instrumentation.

Streaming SSR may briefly hold completed Suspense boundaries so nearby boundaries reveal together. React abandons the delay when it could harm metrics such as the 2.5-second LCP threshold, so never depend on every boundary being batched.
