# Activity and Effect Events

The `19.2-guide` behavior described here covers preparing hidden UI, hydration boundaries, and Effect-local callbacks.

## Activity modes

`<Activity>` gives a subtree an explicit visibility mode:

```jsx
<Activity mode={activeTab === "posts" ? "visible" : "hidden"}>
  <Posts />
</Activity>
```

| Mode | DOM and state | Effects | Updates |
|---|---|---|---|
| `visible` | Shown and retained | Mounted | Normal priority |
| `hidden` | Retained and hidden with `display: none` | Cleaned up | Low priority |

Switching modes preserves component state and retained DOM. Revealing the subtree recreates its Effects.

## Preparing hidden content

An initially hidden Activity renders at low priority without mounting Effects. It can prepare work that begins during render, including:

- Suspense-enabled data;
- a `lazy` component's code; and
- a cached Promise read with `use`.

A fetch started by an Effect does not run while the Activity is initially hidden. Put preparatory work behind a Suspense-compatible render-time integration when it must warm in advance.

Useful cases include likely navigation destinations and views whose component or DOM state should survive hiding.

## Server rendering and hydration

An Activity's initial mode changes SSR behavior:

- A hidden Activity is omitted from the server response. React renders it on the client at low priority while the visible page hydrates.
- A visible Activity stays in the HTML but forms a selective-hydration boundary. React can deprioritize hydrating its contents until they are needed.

An always-visible Activity can therefore isolate slower hydration work without serving as a visibility toggle.

## Retained DOM side effects

Hidden Activity content should generally be treated as unmounted because its Effects are cleaned up. Its DOM remains, however, and element-owned browser behavior may continue. This matters for elements such as:

- `<video>`;
- `<audio>`; and
- `<iframe>`.

Use an Effect cleanup that explicitly pauses, stops, disconnects, or otherwise neutralizes the element-owned behavior:

```jsx
useEffect(() => {
  const player = videoRef.current;
  player.play();

  return () => {
    player.pause();
  };
}, []);
```

Do not assume that hiding the DOM or cleaning up React Effects automatically stops browser-owned work.

## Effect Events

`useEffectEvent` creates an Effect-local callback that reads the latest committed props and state. Values read by that callback do not need to become dependencies of the Effect that calls it:

```jsx
const onConnected = useEffectEvent(() => {
  showNotification("Connected", theme);
});

useEffect(() => {
  const connection = connect(roomId, onConnected);
  return () => connection.disconnect();
}, [roomId]);
```

The returned callback intentionally has a new identity on every render. Follow all of these constraints:

- Do not add it to an Effect dependency array.
- Do not call it during render.
- Do not call it from an ordinary event handler.
- Do not pass it to another component.
- Do not pass it to another Hook.
- Call it only from an Effect or another Effect Event in the same component.

`useEffect`, `useLayoutEffect`, and `useInsertionEffect` may call an Effect Event.

A custom Hook can keep a caller-provided callback current by wrapping it in its own Effect Event, provided the custom Hook calls that event only from its own Effect:

```jsx
function useConnection(roomId, onConnected) {
  const onConnectedEvent = useEffectEvent(onConnected);

  useEffect(() => {
    const connection = connect(roomId, onConnectedEvent);
    return () => connection.disconnect();
  }, [roomId]);
}
```
