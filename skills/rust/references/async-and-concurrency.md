# Async and Concurrency

## Async Closures

Syntax `async || {}` for closures returning futures. Captures variables properly unlike `|| async {}`.

```rust
let mut data = vec![];
let closure = async || {
    data.push(fetch_value().await);
};
closure().await;
```

New traits: `AsyncFn`, `AsyncFnMut`, `AsyncFnOnce`.

```rust
async fn call_twice<F: AsyncFnMut()>(f: F) {
    f().await;
    f().await;
}
```

## `Once::wait` and `OnceLock::wait`

Block until initialization completes (by any thread).

```rust
use std::sync::OnceLock;

static CONFIG: OnceLock<Config> = OnceLock::new();

// Thread 1: initializes
CONFIG.set(load_config()).unwrap();

// Thread 2: waits for initialization
let config = CONFIG.wait();  // Blocks until set() completes
```

## `RwLockWriteGuard::downgrade`

Downgrade write lock to read lock without releasing.

```rust
use std::sync::RwLock;

let lock = RwLock::new(5);
let mut write_guard = lock.write().unwrap();
*write_guard = 10;

// Downgrade - no other writers can sneak in
let read_guard = write_guard.downgrade();
```

## `AtomicPtr` Arithmetic

Atomic pointer arithmetic operations.

```rust
use std::sync::atomic::{AtomicPtr, Ordering};

let mut data = [1, 2, 3, 4, 5];
let ptr = AtomicPtr::new(data.as_mut_ptr());

ptr.fetch_ptr_add(2, Ordering::SeqCst);  // Advance by 2 elements
ptr.fetch_ptr_sub(1, Ordering::SeqCst);  // Retreat by 1 element
ptr.fetch_byte_add(4, Ordering::SeqCst); // Add 4 bytes

// Bitwise operations for pointer tagging
ptr.fetch_or(0x1, Ordering::SeqCst);   // Set low bit
ptr.fetch_and(!0x1, Ordering::SeqCst); // Clear low bit
```

## File Locking

Cross-platform advisory file locking.

```rust
use std::fs::File;

let file = File::open("data.txt")?;

file.lock()?;           // Exclusive lock (blocks)
file.lock_shared()?;    // Shared lock (multiple readers)
file.unlock()?;

// Non-blocking variants
match file.try_lock() {
    Ok(()) => { /* got lock */ }
    Err(e) if e.kind() == io::ErrorKind::WouldBlock => { /* locked */ }
    Err(e) => return Err(e),
}
```
