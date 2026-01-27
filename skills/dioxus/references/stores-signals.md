# Stores: Nested Reactivity

Stores extend signals with **granular path-based subscriptions** for nested data structures.

## When to Use

| Feature | Signal | Store |
|---------|--------|-------|
| Mutability | Mutable | Mutable |
| Granularity | Single value | Per-field |
| Use case | Scalar state | Nested structures |
| Subscriptions | Simple HashSet | Tree structure |
| Performance | O(1) update | O(path) update |

**Use Stores when**: You have nested data and want to re-render only components that access specific fields.

## Basic Usage

```rust
#[derive(Store, Clone)]
struct TodoItem {
    checked: bool,
    contents: String,
}

let store = Store::new(TodoItem {
    checked: false,
    contents: "Buy milk".into(),
});

// Subscribe only to `checked` field
let checked = store.checked();
rsx! { input { checked: checked.read() } }

// Changing `contents` won't re-render the above component
store.contents().set("Buy eggs".into());
```

## Store Derive Macro

```rust
#[derive(Store)]
struct TodoItem {
    checked: bool,
    contents: String,
}

// Generates:
pub trait TodoItemStoreExt<__Lens> {
    fn checked(self) -> Store<bool, __Lens::MappedSignal>;
    fn contents(self) -> Store<String, __Lens::MappedSignal>;
    fn transpose(self) -> TodoItemStoreTransposed;
}

pub struct TodoItemStoreTransposed {
    pub checked: Store<bool>,
    pub contents: Store<String>,
}
```

## Enum Support

```rust
#[derive(Store)]
enum Status {
    Loading,
    Ready(String),
    Error(String),
}

// Generates:
fn is_loading(self) -> bool;
fn ready(self) -> Option<Store<String, ...>>;
fn transpose(self) -> StatusStoreTransposed;
```

## Architecture

### Store Structure

```
Store<T, Lens>
└── selector: SelectorScope<Lens>
    ├── subscriptions: StoreSubscriptions
    ├── path: TinyVec<u16>
    └── value: Lens
```

### Subscription Tree

```
StoreSubscriptions
└── root: SelectorNode
    ├── subscribers: HashSet<ReactiveContext>
    └── children: HashMap<PathKey, SelectorNode>
        └── [0] → SelectorNode
        └── [1] → SelectorNode
```

### Path Tracking

```rust
let store = Store::new(vec![a, b, c]);
let item_1 = store[1];    // path = [1]
let field = item_1.name;  // path = [1, field_hash]

// Writing store[1].name only marks dirty:
// - subscribers at path [1]
// - subscribers at path [1, field_hash]
// - NOT path [0] or [2]
```

## Memory Model

1. Values stored in per-scope storage singletons
2. Only pointers (GenerationalBox) in components
3. Owner drops when scope dies
4. Generation checking on each access
5. Arc+Mutex for subscribers, Rc+RefCell for ownership

## Comparison with Signals

**Signal**: All readers notified on any change
```rust
let signal = use_signal(|| MyStruct { a: 1, b: 2 });
// Changing signal.a re-renders ALL components reading the signal
```

**Store**: Only path-specific readers notified
```rust
let store = Store::new(MyStruct { a: 1, b: 2 });
let a = store.a(); // Component A subscribes to path [a]
let b = store.b(); // Component B subscribes to path [b]
// Changing store.a() only re-renders Component A
```

## Key Traits

```rust
pub trait Readable {
    type Target;
    type Storage;
    fn try_read_unchecked(&self) -> Result<ReadableRef<T>>;
    fn try_peek_unchecked(&self) -> Result<ReadableRef<T>>;
    fn subscribers(&self) -> Subscribers;
}

pub trait Writable: Readable {
    type WriteMetadata;
    fn try_write_unchecked(&self) -> Result<WritableRef<T>>;
}
```

Stores implement both traits with path-aware subscription management.

## Reactivity Gotchas

### Memos/Signals in Attributes

Passing a `Memo` or computed value directly to an attribute may not create proper reactive subscriptions. Prefer **direct signal reads** in RSX:

```rust
// ❌ May not subscribe properly - attribute won't update
let computed_style = use_memo(move || format!("color: {}", color()));
rsx! { div { style: computed_style } }

// ✅ Direct signal read in RSX - proper subscription
rsx! { div { style: format!("color: {}", color()) } }
```

### CSS-in-RSX for Reactive Styles

For reactive styles, use individual CSS properties as RSX attributes instead of style strings:

```rust
// ❌ Style string with memo - subscription issues
let style = use_memo(move || format!("font-weight: {}", if bold() { "bold" } else { "normal" }));
rsx! { p { style: style } }

// ✅ Individual CSS properties with direct signal reads
rsx! {
    p {
        font_weight: if bold() { "bold" } else { "normal" },
        font_style: if italic() { "italic" } else { "normal" },
        text_align: "{align}",
    }
}
```

This ensures each property subscribes to its signals and the component re-renders correctly.
