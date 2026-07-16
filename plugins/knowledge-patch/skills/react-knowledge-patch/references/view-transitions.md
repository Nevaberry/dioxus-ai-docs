# View Transitions

The `<ViewTransition>` and `addTransitionType` APIs described by `19.2-guide` are available in the Canary channel and currently target only the DOM.

## Activation

React owns the underlying `document.startViewTransition()` call. Do not call it around React updates yourself.

A normal synchronous `setState` does not activate a boundary. These update sources can activate View Transitions:

- `startTransition`;
- `useTransition`;
- `useDeferredValue`; and
- a Suspense reveal.

```jsx
<ViewTransition enter="slide-in" exit="slide-out">
  {show && <Panel />}
</ViewTransition>

startTransition(() => {
  setShow(value => !value);
});
```

React classifies each activation as `enter`, `exit`, `update`, or `share`.

For `enter` and `exit`, place the `<ViewTransition>` boundary before any host DOM wrapper in the inserted or removed subtree:

```jsx
// The boundary directly observes insertion and removal.
{show && (
  <ViewTransition enter="slide-in" exit="slide-out">
    <section>...</section>
  </ViewTransition>
)}
```

When an Activity becomes visible or hidden during a Transition, it activates `enter` or `exit` while preserving the Activity subtree's state.

## Classes and transition types

The `default`, `enter`, `exit`, `update`, and `share` props accept:

- `"auto"`;
- `"none"`;
- one view-transition class name; or
- an object whose keys are types registered with `addTransitionType`.

`default="none"` disables every trigger that is not configured explicitly.

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

Style the class through its view-transition pseudo-elements:

```css
::view-transition-old(.slide-left) {
  animation-name: leave-left;
}

::view-transition-new(.slide-left) {
  animation-name: enter-left;
}
```

Do not implement class-based transitions by manually assigning browser view-transition names.

## Shared elements

Set `name` only when pairing different mounted and removed trees as one shared element:

```jsx
<ViewTransition name={`photo-${photo.id}`} share="photo-morph">
  <img src={photo.src} alt="" />
</ViewTransition>
```

Every `name` must be unique among all simultaneously mounted View Transition boundaries. A matching removed and inserted pair within one Transition activates `share`; `share` takes precedence over `enter` and `exit` for that pair.

## Imperative event handlers

`onEnter`, `onExit`, `onUpdate`, and `onShare` receive:

1. an instance with `old`, `new`, `group`, and `imagePair` pseudo-elements plus its `name`; and
2. an array of active transition types.

Use the pseudo-elements with the Web Animations API when class-based animation is insufficient:

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

Return a cleanup function from every handler so interrupted animations and other imperative work are cancelled.

## Router integration

React waits for a pending Navigation before measuring a transition. If a router blocks that Navigation on React, it must unblock in `useLayoutEffect`. Waiting for `useEffect` creates a deadlock because measurement waits for navigation while navigation waits for an Effect that cannot run.

Transitions initiated by legacy `popstate` must finish synchronously, so React skips their animations. A router needs the Navigation API to animate browser back navigation.
