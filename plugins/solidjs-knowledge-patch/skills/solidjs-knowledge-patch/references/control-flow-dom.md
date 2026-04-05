# Control Flow and DOM

## For (unified list rendering)

`Index` is removed. `For` handles both keyed and index-based rendering. Children receive **accessors** for both item and index.

```tsx
// Keyed by identity (default)
<For each={todos()}>
  {(todo, i) => <TodoRow todo={todo()} index={i()} />}
</For>

// Index-style (reuse by position, replaces Index)
<For each={todos()} keyed={false}>
  {(todo, i) => <TodoRow todo={todo()} index={i()} />}
</For>

// Custom key function
<For each={todos()} keyed={(t) => t.id}>
  {(todo) => <TodoRow todo={todo()} />}
</For>

// Fallback
<For each={todos()} fallback={<EmptyState />}>
  {(todo) => <TodoRow todo={todo()} />}
</For>
```

## Repeat (range/count rendering)

No list diffing. For skeletons, numeric ranges, windowed UIs.

```tsx
// 10 items: 0..9
<Repeat count={10}>{(i) => <Item index={i} />}</Repeat>

// Offset
<Repeat count={visibleCount()} from={start()}>
  {(i) => <Row index={i} />}
</Repeat>

// Fallback when count is 0
<Repeat count={items.length} fallback={<EmptyState />}>
  {(i) => <div>{items[i]}</div>}
</Repeat>
```

## Show

Function children receive a narrowed accessor:

```tsx
<Show when={user()} fallback={<Login />}>
  {(u) => <Profile user={u()} />}
</Show>

// Keyed form (identity-based switching)
<Show when={user()} keyed>
  {(u) => <Profile user={u()} />}
</Show>
```

## Switch / Match

First matching branch wins:

```tsx
<Switch fallback={<NotFound />}>
  <Match when={route() === 'home'}>
    <Home />
  </Match>
  <Match when={route() === 'profile'}>
    <Profile />
  </Match>
</Switch>;
```

## Loading (replaces Suspense)

Async boundary for initial readiness:

```tsx
<Loading fallback={<Spinner />}>
  <UserProfile id={params.id} />
</Loading>;
```

## Errored (replaces ErrorBoundary)

Callback form receives error and reset function:

```tsx
<Errored
  fallback={(err, reset) => (
    <div>
      <p>Something went wrong.</p>
      <pre>{String(err)}</pre>
      <button onClick={reset}>Retry</button>
    </div>
  )}
>
  <Page />
</Errored>;
```

## DOM: Attributes Over Properties (2.0)

Solid 2.0 follows HTML standards by default:

- Built-in attributes are set as **attributes** (not magically mapped to properties), generally lowercase
- Boolean attributes use presence/absence: `muted={true}` adds, `muted={false}` removes
- `attr:` and `bool:` namespaces are removed
- `oncapture:` is removed

```tsx
<video muted={true} />
<video muted={false} />

// When the platform requires a string value:
<some-element enabled="true" />
```

Exceptions: `value`, `selected`, `checked`, `muted` continue to be handled as props where needed. Event handlers remain camelCase (`onClick`).

## Enhanced class Prop (2.0)

`classList` is removed. `class` now accepts string, object, or array:

```tsx
// String
<div class="card" />

// Object (classList replacement)
<div class={{ active: isActive(), disabled: isDisabled() }} />

// Array (clsx-style composition)
<div class={['card', props.class, { active: isActive() }]} />
```

## Directives via ref (2.0)

`use:` directive namespace is removed. Use `ref` with directive factories:

```tsx
// 1.x
<input use:autofocus />
<button use:tooltip={{ content: 'Save' }} />

// 2.0
<input ref={autofocus} />
<button ref={tooltip({ content: 'Save' })} />

// Multiple directives via array
<button ref={[autofocus, tooltip({ content: 'Save' })]} />
```

### Two-phase directive pattern

Recommended: owned setup phase (reactive primitives) + unowned apply phase (DOM writes).

```tsx
function titleDirective(source) {
  // Setup phase (owned): create subscriptions
  let el;
  createEffect(source, (value) => {
    if (el) el.title = value;
  });

  // Apply phase (unowned): receives element, performs DOM writes
  return (nextEl) => {
    el = nextEl;
    el.title = source();
  };
}

// Usage
<button ref={titleDirective(() => props.title)} />;
```

## Removals

| Removed | Replacement |
|---------|-------------|
| `Index` | `<For keyed={false}>` |
| `Suspense` | `Loading` |
| `ErrorBoundary` | `Errored` |
| `classList` | `class` with object/array |
| `use:` directives | `ref={directive(opts)}` / `ref={[a, b]}` |
| `attr:` / `bool:` | Standard attribute behavior |
| `oncapture:` | Removed |
| `createMutable` | `@solidjs/signals` or primitives layer |
