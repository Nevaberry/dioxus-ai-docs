# Reactivity, Resources, and Stores

## Reference-counted signals

`ArcRwSignal`, `ArcReadSignal`, and related `Arc*` types release their storage
through reference counting (since 0.7.0). Their handles are `Clone`, not
`Copy`. Prefer them for dynamically nested signals whose lifetimes cannot be
managed by explicit arena disposal. Convert them to arena-backed `RwSignal`
and related types when a copyable handle is useful and arena ownership fits.

## Read and write guards

Use `.read()` and `.write()` to access a signal without cloning the value and
without a `.with()` or `.update()` closure:

```rust
let values = RwSignal::new(vec![1, 2, 3]);
let len = values.read().len();
values.write().push(4);
```

Keep each guard short-lived. Accessing the same reactive value again while a
guard is retained can deadlock or panic. Resource values also provide
`.write()` and related guarded mutation methods (since 0.8.0).

## Awaitable resources and Suspense

A `Resource` is directly awaitable (since 0.7.0), including from another
resource. It is no longer necessary to expose every dependent operation as
manual handling of `Option<T>`. Keep explicit dependency reads where hydration
needs them:

```rust
let user = Resource::new(|| (), |_| async { 42 });
let posts = Resource::new(
    move || user.get(), // explicit dependency for hydration
    move |_| async move { user.await + 1 },
);
```

Wrap an asynchronous child in `Suspend::new(...)` when rendering it beneath
`Suspense`:

```rust
view! {
    <Suspense>
        {move || Suspend::new(async move { posts.await.to_string() })}
    </Suspense>
}
```

## Automatic batching

The standalone `batch` function was removed (since 0.7.0). All reactive
updates automatically receive the behavior that formerly required an explicit
`batch(...)` call. Remove wrappers rather than recreating a local batching
helper.

## Signal conversions and serialization

In 0.7.0, `Signal<T>` stopped automatically implementing `From<Fn() -> T>`,
so closure conversion required `Signal::derive(...)`. Compatible closures
once again implement conversion into `Signal<T>`, `ArcSignal<T>`,
`Callback<T, _>`, and similar types (since 0.8.0), while the explicit form
remains valid:

```rust
let explicit = Signal::derive(move || count.get() * 2);
let converted: Signal<i32> = (move || count.get() * 2).into();
```

`Signal<T>` also implements `From<T>`, so it can represent a plain or reactive
value in places that formerly used `MaybeSignal<T>`. It implements Serde
`Deserialize` when `T` is deserializable, allowing application data to decode
directly into a signal.

## Local resource and action values

`LocalResource` no longer exposes `SendWrapper` in returned values (since
0.8.0). Remove wrapper-oriented calls such as `.as_deref()` and use the value
directly. Actions likewise no longer expose `SendOption` through their public
API.

## Deeply reactive stores

`#[derive(Store)]` turns ordinary nested data into a deeply reactive store
(since 0.7.0). The derive generates field-level getters and setters so an
update to one field does not notify effects that track only a sibling field;
this avoids signals nested inside signals.

Variable keyed collections are supported (since 0.8.0), so keyed reactivity
is not limited to collections with fixed shapes.
