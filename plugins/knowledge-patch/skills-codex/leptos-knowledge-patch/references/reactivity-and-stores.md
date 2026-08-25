# Reactivity, Resources, and Stores

## Reference-counted signals

`ArcRwSignal`, `ArcReadSignal`, and related `Arc*` primitives are `Clone`, not
`Copy` (since 0.7.0). Their storage is released through reference counting,
which makes them suitable for dynamically nested state that cannot be disposed
explicitly. Convert them to arena-backed `RwSignal` and related types when a
copyable handle is more useful.

## Read and write guards

Use `.read()` and `.write()` guards to access a signal without cloning the
value or wrapping work in `.with()` or `.update()` (since 0.7.0).

```rust
let values = RwSignal::new(vec![1, 2, 3]);
let len = values.read().len();
values.write().push(4);
```

Keep guards short-lived. Accessing the same reactive value again while one of
its guards is retained can deadlock or panic.

## Automatic batching

All reactive updates are automatically batched as of 0.7.0. The `batch`
function was removed, so delete explicit `batch(...)` wrappers during
migration.

## Awaitable resources

Await a `Resource` directly, including from inside another resource, instead
of always treating its value as `Option<T>` (since 0.7.0). Keep explicit
dependency tracking where hydration depends on it. Wrap asynchronous Suspense
children in `Suspend::new(...)`.

```rust
let user = Resource::new(|| (), |_| async { 42 });
let posts = Resource::new(
    move || user.get(),
    move |_| async move { user.await + 1 },
);

view! {
    <Suspense>
        {move || Suspend::new(async move { posts.await.to_string() })}
    </Suspense>
}
```

`Resource` also has `.write()` and related guarded mutation methods (since
0.8.0), so stored values can be mutated without replacing the full resource.

## Signal conversions

During the initial 0.7.0 migration, `Signal<T>` stopped implementing
`From<Fn() -> T>` and `Signal::derive(...)` was required. Conversion from a
compatible `Fn() -> T` was restored in 0.8.0 for `Signal<T>`, `ArcSignal<T>`,
`Callback<T, _>`, and similar types; `.into()` works again, while
`Signal::derive(...)` remains an explicit option.

```rust
let doubled: Signal<i32> = (move || count.get() * 2).into();
```

`Signal<T>` also implements `From<T>`, so it can carry either a plain or a
reactive value in places that previously used `MaybeSignal<T>` (since 0.7.0).
When `T` is deserializable, `Signal<T>` implements Serde `Deserialize` (since
0.8.0), allowing serialized application data to decode directly into a
signal.

## Deeply reactive stores

`#[derive(Store)]` builds field-level getters and setters for ordinary nested
data (since 0.7.0). Mutating one field does not notify effects that only track
a sibling, avoiding the need to place signals inside signals.

Variable keyed collections are supported as of 0.8.0, extending keyed
reactivity beyond fixed collection shapes.
