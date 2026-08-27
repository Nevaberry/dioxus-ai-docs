# Reactivity, Resources, and Stores

## Reference-counted signals

`ArcRwSignal`, `ArcReadSignal`, and the other `Arc*` primitives are `Clone`,
not `Copy` (since 0.7.0). Their storage is released through reference
counting, which makes them appropriate for dynamically nested state that
cannot be explicitly disposed. Convert them to arena-backed `RwSignal` and
related types when copyable handles are more useful.

## Read and write guards

Signals expose `.read()` and `.write()` guards (since 0.7.0), avoiding value
cloning and closure-based `.with()` or `.update()` access.

```rust
let values = RwSignal::new(vec![1, 2, 3]);
let len = values.read().len();
values.write().push(4);
```

Keep every guard short-lived. Re-entering the same reactive value while a
guard remains alive can deadlock or panic.

## Thread-safe and local storage

Reactive primitives use `SyncStorage` by default and therefore require stored
data to be `Send + Sync` (since 0.7.0). For `Rc` or another thread-local value,
choose `LocalStorage` or a local constructor such as:

```rust
let local = RwSignal::new_local(std::rc::Rc::new("value"));
```

## Await resources

`Resource` can be awaited directly, including inside another resource (since
0.7.0). Keep manual dependency tracking when hydration requires it, and wrap
an asynchronous child with `Suspend::new(...)` beneath `<Suspense>`.

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

## Mutate resource values

`Resource` supplies `.write()` and related guarded mutation methods (since
0.8.0). Use them to mutate the stored value without cloning it, and apply the
same short guard-lifetime discipline used with signals.

## Signal conversions

During the 0.7.0 migration, `Signal<T>` gained `From<T>` so it could represent
either a plain or reactive value in place of `MaybeSignal<T>`. At that point,
closure conversion was removed and a closure had to use
`Signal::derive(...)`.

Closure conversions were restored in 0.8.0 for `Signal<T>`, `ArcSignal<T>`,
`Callback<T, _>`, and similar types. `Signal::derive(...)` remains valid, but
a compatible `Fn() -> T` may use `.into()` again:

```rust
let doubled: Signal<i32> = (move || count.get() * 2).into();
```

`Signal<T>` also implements Serde `Deserialize` when `T` does (since 0.8.0),
so serialized application data can decode directly into a signal.

## Deeply reactive stores

`#[derive(Store)]` turns nested data into a deeply reactive store with
field-level getters and setters (since 0.7.0). Updating one field does not
notify effects that track only a sibling field, avoiding signals nested inside
signals. Variable keyed collections are supported as of 0.8.0; keyed
reactivity is not restricted to fixed collection shapes.

## Thread-local wrapper cleanup

`LocalResource` no longer exposes `SendWrapper` in returned values (since
0.8.0). Remove wrapper-oriented calls such as `.as_deref()` and use the value
directly. Actions likewise no longer expose `SendOption` through their public
API.
