# Activity and Effect Events

The Activity and Effect Event behavior below is attributed to batch `19.2-guide`.

## Pre-render and hydrate with Activity

An initially hidden `<Activity>` renders its children at low priority without mounting their Effects. It can warm Suspense-enabled data, `lazy` code, or a cached Promise read with `use`; a fetch started from an Effect does not run while the Activity is initially hidden.

```jsx
<Activity mode={activeTab === "posts" ? "visible" : "hidden"}>
  <Posts />
</Activity>
```

Hidden children retain component and DOM state. React cleans up their Effects while hidden and recreates those Effects when the Activity is revealed.

Server rendering depends on the initial mode:

- A hidden Activity is omitted from the response and client-rendered while the visible page hydrates.
- A visible Activity remains in the HTML, but forms a selective-hydration boundary whose contents are deprioritized until needed. An always-visible Activity can therefore isolate slower hydration work.

## Clean up DOM-owned behavior

Hidden Activity content uses `display: none` and retains its DOM. Browser-owned behavior in `<video>`, `<audio>`, and `<iframe>` elements can continue after React cleans up Effects. Components that use these elements must stop that behavior explicitly in Effect cleanup. Apart from retained component and DOM state, treat hidden Activity children conceptually as unmounted.

## Keep Effect Events local

`useEffectEvent` returns a callback that reads the latest committed props and state without turning those values into Effect dependencies.

```jsx
const onConnected = useEffectEvent(() => {
  showNotification("Connected", theme);
});

useEffect(() => {
  const connection = connect(roomId, onConnected);
  return () => connection.disconnect();
}, [roomId]);
```

The returned callback intentionally changes identity on every render. Follow all of these constraints:

- Do not put it in a dependency array.
- Do not call it during render or from an ordinary event handler.
- Do not pass it to another component or Hook.
- Call it only from an Effect or another Effect Event in the same component.

`useEffect`, `useLayoutEffect`, and `useInsertionEffect` may call Effect Events. A custom Hook can wrap a callback it receives in its own `useEffectEvent`, keeping that event local to the custom Hook's Effect.
