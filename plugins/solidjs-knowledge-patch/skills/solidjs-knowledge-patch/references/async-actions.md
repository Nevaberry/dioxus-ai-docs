# Async Data and Actions

## Async Computations (2.0)

`createResource` is removed. Any computation can return a Promise or AsyncIterable and the reactive graph handles suspension automatically.

```tsx
// 1.x
const [user] = createResource(id, fetchUser);

// 2.0 -- just use createMemo with an async function
const user = createMemo(() => fetchUser(id()));
```

Consumers read the accessor normally. If not ready, the graph suspends -- wrap in `<Loading>` to control fallback UI:

```tsx
function Profile() {
  return <div>{user().name}</div>; // suspends if not ready
}

<Loading fallback={<Spinner />}>
  <Profile />
</Loading>;
```

### Derived store with async

```tsx
const [items] = createStore(() => api.listItems(), []);
// items is reactive; Loading boundary handles the pending state
```

## Loading (replaces Suspense)

`Loading` is the boundary for async computations. Shows `fallback` while async values in its subtree are not ready.

```tsx
<Loading fallback={<Spinner />}>
  <UserProfile id={params.id} />
</Loading>;
```

Key behavior: `Loading` covers **initial readiness** only. After the subtree has rendered once, subsequent revalidation does NOT kick you back into the fallback. Use `isPending` for "refreshing" indicators.

Nested `Loading` boundaries control where loading UI appears:

```tsx
<Loading fallback={<PageSkeleton />}>
  <Header />
  <Loading fallback={<ContentSkeleton />}>
    <Content />
  </Loading>
</Loading>;
```

## isPending (stale-while-revalidating)

`isPending(fn)` returns true when `fn` has pending async work **and** a usable stale value exists. It is **false during initial Loading fallback** (no stale value yet).

```tsx
const users = createMemo(() => fetchUsers());
const posts = createMemo(() => fetchPosts());

const listPending = () => isPending(() => users() || posts());

return (
  <>
    <Show when={listPending()}>
      <RefreshingIndicator />
    </Show>
    <Loading fallback={<Spinner />}>
      <List users={users()} posts={posts()} />
    </Loading>
  </>
);
```

## latest(fn)

Reads the in-flight value during transitions. Falls back to stale if next value is not available.

```tsx
const [userId, setUserId] = createSignal(1);
const user = createMemo(() => fetchUser(userId()));

const latestUserId = () => latest(userId);
```

## Transitions

Transitions are a built-in scheduling concept in 2.0. `startTransition` and `useTransition` are removed. Multiple transitions can be in flight simultaneously. Pending state is observable via `isPending`.

## action() for Mutations

`action()` wraps a generator (or async generator) for mutations. It coordinates optimistic writes, async work, and refreshes.

```tsx
const [todos, setOptimisticTodos] = createOptimisticStore(
  () => api.getTodos(),
  [],
);

const addTodo = action(function* (todo) {
  // 1. Optimistic write
  setOptimisticTodos((todos) => {
    todos.push(todo);
  });

  // 2. Async work
  yield api.addTodo(todo);

  // 3. Refresh derived reads
  refresh(todos);
});
```

Async generator form (better TS ergonomics):

```tsx
const saveTodo = action(async function* (todo) {
  setOptimisticTodos((todos) => {
    todos.push(todo);
  });
  const res = await api.addTodo(todo);
  yield; // resume in same transition context
  refresh(todos);
  return res;
});
```

## refresh()

Explicitly recompute derived reads after a mutation. Two forms:

```tsx
// Thunk form: re-run expression
refresh(() => query.user(id()));

// Refreshable form: recompute a derived store/projection
const [todos] = createStore(() => api.getTodos(), []);
refresh(todos);
```

## createOptimistic (signal)

Like `createSignal`, but writes are optimistic -- values revert when the transition completes.

```tsx
const [name, setName] = createOptimistic('Alice');

const updateName = action(function* (next) {
  setName(next); // optimistic, reverts on settle
  yield api.saveName(next);
});
```

## createOptimisticStore

Store analogue for optimistic updates. Commonly derives from a source getter.

```tsx
const [todos, setOptimisticTodos] = createOptimisticStore(
  () => api.getTodos(),
  [],
);

const addTodo = action(function* (todo) {
  setOptimisticTodos((s) => {
    s.push(todo);
  }); // optimistic
  yield api.addTodo(todo);
  refresh(todos); // recompute from server
});
```

## Removals

| Removed | Replacement |
|---------|-------------|
| `createResource` | Async `createMemo` / `createStore(fn)` + `Loading` |
| `useTransition` / `startTransition` | Built-in transitions; use `Loading`, `isPending`, actions |
| `.loading` flag on resources | `isPending(fn)` |
