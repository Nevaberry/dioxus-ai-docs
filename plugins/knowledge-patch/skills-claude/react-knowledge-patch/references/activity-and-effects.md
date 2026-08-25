# Activity and Effect Events

## Prepare hidden UI with Activity

Since `19.2-guide`, an initially hidden `<Activity>` renders its children at
low priority without mounting their Effects:

```jsx
<Activity mode={activeTab === "posts" ? "visible" : "hidden"}>
  <Posts />
</Activity>
```

Hidden children retain component state and DOM state. React cleans up their
Effects while they are hidden and recreates the Effects when they become
visible. The low-priority render can warm Suspense-enabled data, `lazy` code,
or a cached Promise read with `use`. A fetch started by an Effect does not run
while the tree is initially hidden because that Effect is not mounted.

### Hydration behavior

For SSR, React omits an initially hidden Activity from the response. React
client-renders that content while the visible page hydrates. A visible
Activity remains in the server HTML but creates a selective-hydration
boundary whose contents are deprioritized until needed. An Activity that is
always visible can therefore isolate slower hydration work.

### Clean up browser-owned behavior

Hidden Activity content uses `display: none` but keeps its DOM. Effect cleanup
does not necessarily stop browser-owned behavior in retained `<video>`,
`<audio>`, or `<iframe>` elements. Explicitly stop that behavior in the Effect
cleanup. Apart from retained component and DOM state, treat hidden children as
unmounted when managing side effects.

## Keep Effect Events local

Since `19.2-guide`, `useEffectEvent` returns a callback that reads the latest
committed props and state without making those values dependencies of the
Effect that invokes it:

```jsx
const onConnected = useEffectEvent(() => {
  showNotification("Connected", theme);
});

useEffect(() => {
  const connection = connect(roomId, onConnected);
  return () => connection.disconnect();
}, [roomId]);
```

The returned callback intentionally has a new identity on every render:

- Do not put it in an Effect dependency array.
- Do not call it during render or from an ordinary event handler.
- Do not pass it to another component or Hook.
- Call it only from an Effect or another Effect Event in the same component.

`useEffect`, `useLayoutEffect`, and `useInsertionEffect` can invoke Effect
Events. A custom Hook can wrap an incoming callback in its own
`useEffectEvent`, keeping that event local to the custom Hook's Effect.
