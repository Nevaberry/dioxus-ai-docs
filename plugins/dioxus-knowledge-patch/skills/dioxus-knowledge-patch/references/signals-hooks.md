# Signals and Hooks

## Signals (0.5+)

`Signal<T>` is always `Copy` (via generational-box). Auto-subscribes when read in component body.

```rust
let count = use_signal(|| 0); // Signal<i32>, Copy
count.read(); // {code}i32
count.write(); // {code}mut i32
count += 1; // shorthand for *count.write() += 1
count.set(5); // replace value

// Only re-renders components that READ the signal (not event handlers)
```

### Global Signals

App-wide state accessible from any component:

```rust
static THEME: GlobalSignal<Theme> = GlobalSignal::new(|| Theme::Dark);

fn Settings() -> Element {
    let theme = THEME(); // reads global
    rsx! { button { onclick: move |_| *THEME.write() = Theme::Light, "Light" } }
}
```

### peek() vs read()

- `.read()` - subscribes component, re-renders on change
- `.peek()` - reads without subscribing (no re-render)

```rust
let count = use_signal(|| 0);
count.read(); // component re-renders when count changes
count.peek(); // just get value, no subscription
```

### Mapped Signals

Derive read-only views with `.map()`:

```rust
let user = use_signal(|| User { name: "Alice".into(), age: 30 });
let name = user.map(|u| &u.name);  // MappedSignal<String>
rsx! { "{name}" }  // only re-renders if name changes
```

### WritableResultExt (0.7.4+)

Mutable access to `Writable<Result<T, E>>` without intermediate bindings:

```rust
let data: Signal<Result<User, Error>> = use_signal(|| Ok(default_user()));

// Get mutable ref to whichever variant the Result holds
let result = data.as_mut(); // Result<WritableRef<User>, WritableRef<Error>>

// Unwrap directly (panics on Err)
let user = data.unwrap_mut(); // WritableRef<User>
```

Mirrors `ReadableResultExt` on the read side and follows the same pattern as `WritableOptionExt`.

## Stores (0.7+)

New primitive for complex/nested data. Derive `Store` to get fine-grained reactivity:

```rust
#[derive(Store)]
struct AppState {
    users: BTreeMap<String, User>,
}

#[component]
fn UserList(state: Store<AppState>) -> Element {
    let users = state.users();  // Store<BTreeMap<...>>
    rsx! {
        for (id, user) in users.iter() {
            UserRow { key: "{id}", user }  // only re-renders changed items
        }
    }
}
```

### SyncStore (0.7.2+)

Thread-safe stores for multi-threaded scenarios:

```rust
use dioxus_stores::{SyncStore, use_store_sync};

let store: SyncStore<MyState> = use_store_sync(|| MyState::default());
// Can be sent across threads (Send + Sync)
```

## Hooks Reference

### use_memo - Memoized Computations

Recomputes only when dependencies change:

```rust
let count = use_signal(|| 0);
let doubled = use_memo(move || count() * 2); // only recomputes when count changes
rsx! { "{doubled}" }
```

### use_effect - Side Effects

Runs after render when dependencies change:

```rust
let id = use_signal(|| 1);
use_effect(move || {
    // Runs when `id` changes
    println!("ID changed to {}", id());
});
```

### use_resource - Async Data Fetching

Manages async state with automatic re-fetching:

```rust
let id = use_signal(|| 1);
let user = use_resource(move || async move {
    fetch_user(id()).await
});

match &*user.read() {
    Some(Ok(user)) => rsx! { "{user.name}" },
    Some(Err(e)) => rsx! { "Error: {e}" },
    None => rsx! { "Loading..." },
}

// Manual controls
user.restart();  // Re-fetch
user.cancel();   // Cancel pending
user.clear();    // Clear cached value
```

### use_coroutine - Long-Lived Async Tasks

For background tasks that outlive renders, with optional channel:

```rust
let chat = use_coroutine(|mut rx: UnboundedReceiver<String>| async move {
    while let Some(msg) = rx.next().await {
        send_to_server(msg).await;
    }
});

rsx! {
    button { onclick: move |_| chat.send("Hello".into()), "Send" }
}
```

### use_callback - Memoized Event Handlers

Prevents unnecessary closure recreation:

```rust
let onclick = use_callback(move |_| {
    // This closure is memoized
    do_something();
});
```

### use_future - Run Once on Mount

```rust
fn DataLoader() -> Element {
    let data = use_signal(|| None);

    use_future(move || async move {
        let result = fetch_initial_data().await;
        data.set(Some(result));
    });

    // renders...
}
```

## Context API

Share state without prop drilling:

```rust
// Provide context (parent)
#[component]
fn App() -> Element {
    use_context_provider(|| Signal::new(Theme::Dark));
    rsx! { Child {} }
}

// Consume context (any descendant)
fn Child() -> Element {
    let theme: Signal<Theme> = use_context();
    rsx! { "Theme: {theme:?}" }
}
```

## Spawn and Tasks

### spawn() - Async Tasks

Run async code from event handlers:

```rust
fn Uploader() -> Element {
    let status = use_signal(|| "Ready");

    rsx! {
        button {
            onclick: move |_| {
                spawn(async move {
                    status.set("Uploading...");
                    upload_file().await;
                    status.set("Done!");
                });
            },
            "{status}"
        }
    }
}
```

### Task Control Methods

Spawned tasks return a `Task` handle with control methods:

```rust
let task = spawn(async move {
    // long-running work
});

task.cancel(); // Stop and remove task
task.pause(); // Suspend polling (task stays in memory)
task.resume(); // Resume paused task
task.wake(); // Manually wake a sleeping task
```

## Reactivity Gotchas

### Memos in Attributes Don't Subscribe Properly

Passing a `Memo` or computed value directly to an attribute may not create reactive subscriptions:

```rust
// BAD: Attribute won't update when color changes
let computed_style = use_memo(move || format!("color: {}", color()));
rsx! { div { style: computed_style } }

// GOOD: Direct signal read in RSX - proper subscription
rsx! { div { style: format!("color: {}", color()) } }
```

### Use Individual CSS Properties for Reactive Styles

Style strings with memos have subscription issues. Use individual CSS properties instead:

```rust
// BAD: Style string with memo - won't update
let style =
    use_memo(move || format!("font-weight: {}", if bold() { "bold" } else { "normal" }));
rsx! { p { style: style } }

// GOOD: Individual CSS properties with direct signal reads
rsx! {
    p {
        font_weight: if bold() { "bold" } else { "normal" },
        font_style: if italic() { "italic" } else { "normal" },
        text_align: "{align}",
    }
}
```

### Thread-Locals Reset on Hot-Patch

Thread-local variables in your crate reset to initial values when Subsecond applies a patch. Store state in signals/stores instead:

```rust
// BAD: Resets on hot-patch
thread_local! { static COUNTER: Cell<i32> = Cell::new(0); }

// GOOD: Survives hot-patches
static COUNTER: GlobalSignal<i32> = GlobalSignal::new(|| 0);
```
