# View Transitions

## Activate Canary DOM transitions through React

In `19.2-guide`, `<ViewTransition>` and `addTransitionType` are Canary APIs and
work only in the DOM. React owns the underlying
`document.startViewTransition()` call. An ordinary synchronous `setState`
does not activate a boundary. Activation can come from an update driven by
`startTransition` or `useTransition`, `useDeferredValue`, or a Suspense reveal:

```jsx
<ViewTransition enter="slide-in" exit="slide-out">
  {show && <Panel />}
</ViewTransition>

startTransition(() => setShow(value => !value));
```

React classifies activation as `enter`, `exit`, `update`, or `share`. For
enter and exit, place the boundary before any host DOM wrapper in the inserted
or removed subtree. An Activity becoming visible or hidden during a
Transition also activates enter or exit while retaining its state.

## Select classes by trigger and type

In `19.2-guide`, the `default`, `enter`, `exit`, `update`, and `share` props
accept one of:

- `"auto"`
- `"none"`
- a view-transition class
- an object keyed by types registered with `addTransitionType`

`default="none"` disables every unspecified trigger. Style the transition
with class selectors such as `::view-transition-old(.slide-left)` instead of
manually assigning browser transition names.

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

## Pair shared elements carefully

Set `name` only to pair different mounted and removed trees as a shared
element transition (`19.2-guide`). Names must be unique among every boundary
mounted at the same time. A matching removed and inserted pair within one
Transition activates `share`, which takes precedence over `enter` and `exit`.

## Clean up imperative animations

In `19.2-guide`, `onEnter`, `onExit`, `onUpdate`, and `onShare` receive two
arguments: an instance and an array of transition types. The instance exposes
the `old`, `new`, `group`, and `imagePair` pseudo-elements plus its `name`.
Return cleanup from each handler so interrupted Web Animations are cancelled:

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

## Unblock routers before measurement

React waits for a pending Navigation before measuring the transition
(`19.2-guide`). A router that blocks Navigation on React must unblock it in
`useLayoutEffect`; waiting for `useEffect` deadlocks transition measurement.

Transitions started from legacy `popstate` must finish synchronously, so React
skips their animations. A router needs the Navigation API to animate browser
back navigation.
