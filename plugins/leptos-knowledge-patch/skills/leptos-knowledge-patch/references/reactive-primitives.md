# Reactive Primitives

Signals, stores, guards, and context APIs new in 0.7+.

## Read/Write Guards (0.7+)

No-clone signal access via guard types (similar to lock guards):

```rust
let data = RwSignal::new(vec![42; 1000]);
let other = RwSignal::new(vec![13; 2]);

// 0.6.x: clones both Vecs
let bad = move || data.get().len() + other.get().len();

// 0.7+: no clone, returns guard
let good = move || data.read().len() + other.read().len();

// Mutable guard
data.write().push(99);
```

Warning: guards must not be held long-term (deadlock/panic risk), same as any lock guard.

## Arc Signal Variants (0.7+)

New `ArcRwSignal<T>`, `ArcReadSignal<T>`, `ArcWriteSignal<T>` — `Clone` (not `Copy`), reference-counted. Fixes memory leak problem with nested signals in 0.6.x:

```rust
let arc_sig = ArcRwSignal::new(vec![1, 2, 3]);
let copy_sig: RwSignal<_> = arc_sig.clone().into();
```

### Conversions (0.8.9+)

`From<RwSignal<T>>`, `From<ReadSignal<T>>`, `From<Memo<T>>` all implemented for `ArcSignal<T>`.

## signal.into_inner() (0.7.1+)

Consume a signal and retrieve its inner value:

```rust
let sig = RwSignal::new(42);
let val: i32 = sig.into_inner();
```

## Context APIs (0.7.1+)

Two new referential context functions that avoid cloning:

```rust
// Access context by reference (no clone)
with_context::<MyCtx, _, _>(|ctx| ctx.some_field.clone());

// Mutate context in place
update_context::<MyCtx, _>(|ctx| ctx.counter += 1);
```

These complement existing `use_context`/`provide_context`.

## Reactive Stores (0.7+)

`Store<T>` for deeply nested reactive data without signals-inside-signals. Each field is independently reactive:

```rust
#[derive(Store)]
struct AppState {
    user: User,
    settings: Settings,
}
// Updating settings does NOT trigger effects watching user
```

### Store Improvements Timeline

| Version | Feature |
|---|---|
| 0.7.1 | `IntoSplitSignal` for `Field`, `PatchField` for `usize`, nested keyed field fixes |
| 0.7.3 | `Default` and `Dispose` for `Store`, `From<ArcStore<T>>` for `Store<T>` |
| 0.7.5 | Custom patch support, recursive store node unboxing |
| 0.8.1 | `PartialEq`/`Eq` for `Store` |
| 0.8.8 | `Derive Patch` works with generic type arguments |
| 0.8.11 | `AtIndex` ancestor tracking fixed, keyed store field patching fixes |
| 0.8.15 | Unkeyed paths for all store patching (reactivity bug class fixed) |
| 0.8.16 | Variable-keyed collections, keyed subfield parent tracking |
| 0.8.17 | Keyed patching for store fields (fine-grained diffing like `<For>`) |

### IntoClass for Store Fields

Store fields implement `IntoClass`, so they can be used directly in `class:` syntax.

## Resource .await with Suspend (0.7+)

Resources can be `.await`ed inside async blocks within `<Suspense/>` via `Suspend::new()`:

```rust
let user = Resource::new(|| (), |_| fetch_user());
let posts = Resource::new(
    move || user.get(),
    move |_| async move {
        let user = user.await?;
        get_posts(user).await
    },
);

view! {
    <Suspense fallback=|| "Loading...">
        {move || Suspend::new(async move {
            match user.await {
                Ok(u) => view! { <p>{u.name}</p> }.into_any(),
                Err(_) => view! { <p>"Error"</p> }.into_any(),
            }
        })}
    </Suspense>
}
```

In 0.8+, `Suspend::new()` accepts any `IntoFuture`, not just `Future`.

### Resource.write() (0.8.3+)

`Resource::write()` and related mutation functions were added (previously missing).

### LocalResource::refetch() (0.7.4+)

Both `LocalResource` and `ArcLocalResource` gained a `refetch()` method to programmatically trigger re-fetch independent of signal changes.

### LocalResource API Cleanup (0.8.0)

`LocalResource` no longer exposes `SendWrapper` in its API. Remove `.as_deref()` etc. from calling code.

### Resource Tracking Fix (0.8.3)

The async block inside a `Resource` no longer tracks reactivity — only the source closure signals are tracked. This was a significant correctness fix.

## MappedSignal (0.8.0+)

- `From<MappedSignal<T>>` for `Signal<T>`
- `Copy`/`Clone` derives
- `.map()` and `.and_then()` added to `LocalResource`

## Signal Deserialize (0.8.16+)

`Signal<T>` implements `Deserialize` — deserialize directly into a signal type.

## Callback Improvements

| Version | Feature |
|---|---|
| 0.7.5 | `Callback::matches` and `UnsyncCallback::matches` for identity comparison |
| 0.8.0 | `Callback` types implement `Dispose`; `Callable` gets `try_run` |

## Immediate Effect Batching (0.8.11+)

```rust
effect::immediate::batch(|| {
    // Multiple signal updates here are batched
});
```

## Owner::parent() (0.8.10+)

Access the parent owner from a child context:

```rust
let parent = Owner::parent();
```

## Runtime Deadlock Warning (0.8.16+)

A runtime warning is now issued when you update a signal while a read guard is still active.
