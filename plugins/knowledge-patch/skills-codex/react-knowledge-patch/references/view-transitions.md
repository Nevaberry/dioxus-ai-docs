# View Transitions

The Canary View Transition behavior below is attributed to batch `19.2-guide`.

## Activate boundaries through transition-driven work

`<ViewTransition>` and `addTransitionType` are available in the Canary channel and currently work only in the DOM. React owns the underlying `document.startViewTransition()` call.

A normal synchronous `setState` does not activate a boundary. Activation can be driven by `startTransition` or `useTransition`, `useDeferredValue`, or a Suspense reveal.

```jsx
<ViewTransition enter="slide-in" exit="slide-out">
  {show && <Panel />}
</ViewTransition>

startTransition(() => setShow(value => !value));
```

React classifies activation as `enter`, `exit`, `update`, or `share`. For `enter` and `exit`, the boundary must appear before any host DOM wrapper in the inserted or removed subtree. An Activity becoming visible or hidden during a Transition also activates `enter` or `exit` while preserving its state.

## Select classes by trigger and type

The `default`, `enter`, `exit`, `update`, and `share` props accept:

- `"auto"`
- `"none"`
- a view-transition class
- an object keyed by types registered with `addTransitionType`

`default="none"` disables every trigger that is not specified separately. Style transition classes through class selectors such as `::view-transition-old(.slide-left)` instead of assigning manual browser transition names.

```jsx
<ViewTransition
  default="none"
  share={{ forward: "slide-left", back: "slide-right" }}
>
  <Page />
</ViewTransition>

startTransition(() => {
  addTransitionType("forward");
  navigate(nextUrl);
});
```

## Pair shared elements with unique names

Set `name` only to pair different mounted and removed trees as a shared-element transition. Names must be unique across all simultaneously mounted boundaries.

A matching removed and inserted pair in one Transition activates `share`. Shared activation takes precedence over `enter` and `exit`.

## Clean up imperative animations

`onEnter`, `onExit`, `onUpdate`, and `onShare` receive a transition instance and an array of transition types. The instance exposes its `name` and the `old`, `new`, `group`, and `imagePair` pseudo-elements.

Return a cleanup function from every handler so an interrupted transition cancels its Web Animations work:

```jsx
<ViewTransition
  onEnter={(instance, types) => {
    const animation = instance.new.animate(
      [{ opacity: 0 }, { opacity: 1 }],
      { duration: types.includes("fast") ? 150 : 300 },
    );
    return () => animation.cancel();
  }}
>
  <Panel />
</ViewTransition>
```

## Integrate routers without deadlock

React waits for a pending Navigation before measuring a transition. A router that blocks Navigation on React must unblock it in `useLayoutEffect`; waiting for `useEffect` creates a deadlock.

Transitions started from legacy `popstate` must finish synchronously, so React skips their animations. A router needs the Navigation API to animate browser back navigation.
