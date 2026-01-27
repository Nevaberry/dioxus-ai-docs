# Pointers and Memory

## Trait Upcasting

Trait objects can be coerced to supertrait objects automatically.

```rust
trait Base { fn base_method(&self); }
trait Derived: Base { fn derived_method(&self); }

fn use_base(obj: &dyn Base) { obj.base_method(); }

fn example(obj: &dyn Derived) {
    use_base(obj);  // Automatic upcasting
}
```

Works with any pointer type: `&dyn`, `Box<dyn>`, `Arc<dyn>`, `*const dyn`.

Useful with `Any` for downcasting:

```rust
use std::any::Any;
trait MyTrait: Any {}

fn downcast(obj: &dyn MyTrait) -> Option<&ConcreteType> {
    let any: &dyn Any = obj;  // Upcast
    any.downcast_ref()
}
```

## Unsigned Pointer Offset Methods

Return `usize` instead of `isize`.

```rust
let arr = [1, 2, 3, 4, 5];
let p1 = arr.as_ptr();
let p2 = unsafe { p1.add(3) };

let offset: usize = unsafe { p2.offset_from_unsigned(p1) };
assert_eq!(offset, 3);
```

## `NonNull` Provenance Methods

Pointer provenance control for `NonNull`.

```rust
use std::ptr::NonNull;

// From reference (preserves provenance)
let x = 42;
let ptr: NonNull<i32> = NonNull::from_ref(&x);
let ptr_mut: NonNull<i32> = NonNull::from_mut(&mut x);

// Without provenance (for integer-to-pointer casts)
let ptr = NonNull::<i32>::without_provenance(0x1000.try_into().unwrap());

// Expose/restore provenance for round-tripping
let addr = ptr.expose_provenance();
let restored = NonNull::<i32>::with_exposed_provenance(addr);
```

## `MaybeUninit` Slice Methods

Safe operations on slices of `MaybeUninit`.

```rust
use std::mem::MaybeUninit;

let mut uninit: [MaybeUninit<u32>; 4] = MaybeUninit::uninit_array();

// Write data
let source = [1u32, 2, 3, 4];
uninit.write_copy_of_slice(&source);  // For Copy types
// uninit.write_clone_of_slice(&source);  // For Clone types

// Get references after initialization
let init: &[u32] = unsafe { uninit.assume_init_ref() };
let init_mut: &mut [u32] = unsafe { uninit.assume_init_mut() };

// Drop in place
unsafe { uninit.assume_init_drop() };
```

## Zeroed Smart Pointer Constructors

Create zero-initialized smart pointers efficiently (avoids stack allocation).

```rust
use std::mem::MaybeUninit;

let boxed: Box<MaybeUninit<[u8; 1024]>> = Box::new_zeroed();
let boxed: Box<[u8; 1024]> = unsafe { boxed.assume_init() };

let slice: Box<[MaybeUninit<u32>]> = Box::new_zeroed_slice(100);

// Same for Rc and Arc
let rc: Rc<MaybeUninit<[u8; 1024]>> = Rc::new_zeroed();
let arc: Arc<MaybeUninit<[u8; 1024]>> = Arc::new_zeroed();
```

## Null Pointer Debug Assertions

Debug builds catch null pointer dereferences at runtime, even through complex code paths.

## Dangling Raw Pointer Lint

Warn-by-default lint catches returning pointers to local variables.

```rust
fn bad() -> *const u8 {
    let x = 0;
    &x  // Warning: dangling pointer
}

fn good(x: &u8) -> *const u8 {
    x  // OK: caller controls lifetime
}
```
