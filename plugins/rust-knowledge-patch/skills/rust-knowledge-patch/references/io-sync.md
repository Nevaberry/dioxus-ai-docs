# I/O, Sync & Concurrency (1.85–1.94)

## Anonymous Pipes (1.87)

`std::io::pipe()` creates an anonymous pipe. Integrates with `Command` via `From<PipeReader/PipeWriter> for Stdio`:

```rust
use std::process::Command;
use std::io::Read;

let (mut recv, send) = std::io::pipe()?;
let mut child = Command::new("my-cmd")
    .stdout(send.try_clone()?)
    .stderr(send) // combine stdout+stderr into one pipe
    .spawn()?;
let mut output = Vec::new();
recv.read_to_end(&mut output)?;
child.wait()?;
```

## File Locking (1.89)

Cross-platform advisory file locking:

```rust
use std::fs::File;
let f = File::open("data.lock")?;
f.lock()?; // exclusive, blocks until acquired
f.lock_shared()?; // shared read lock, blocks
f.try_lock()?; // exclusive, returns Err if already locked
f.try_lock_shared()?;
f.unlock()?;
```

## `Once::wait` / `OnceLock::wait` (1.86)

Block until a `Once` has completed or an `OnceLock` is initialized:

```rust
use std::sync::OnceLock;
static CONFIG: OnceLock<String> = OnceLock::new();
// In reader thread: blocks until another thread calls CONFIG.set(...)
let val: &String = CONFIG.wait();
```

## `RwLockWriteGuard::downgrade` (1.92)

Atomically downgrade a write lock to a read lock without releasing:

```rust
use std::sync::RwLock;
let lock = RwLock::new(1);
let mut write = lock.write().unwrap();
*write = 2;
let read = std::sync::RwLockWriteGuard::downgrade(write); // no gap where lock is unheld
assert_eq!(*read, 2);
```

## `DerefMut` for `LazyCell` / `LazyLock` (1.89)

`LazyCell` and `LazyLock` now implement `DerefMut`, allowing mutation of the lazily-initialized value.

## `LazyCell::get()` / `LazyLock::get()` (1.94)

Check if initialized without forcing initialization:

```rust
use std::cell::LazyCell;
let lazy = LazyCell::new(|| expensive_init());
assert!(lazy.get().is_none()); // not yet initialized
let _ = *lazy; // forces init
assert!(lazy.get().is_some());
```

## `LazyCell::force_mut()` / `LazyLock::force_mut()` (1.94)

Force initialization and get mutable reference.

## `Peekable::next_if_map` (1.94)

Peek and consume if mapping function returns `Some`, combining `next_if` + map.

## `Waker::noop()` (1.85)

Returns a no-op waker for testing async code without a full runtime.

## `Cell::update(f)` (1.88)

Apply a function to the cell's value in-place:

```rust
use std::cell::Cell;
let c = Cell::new(5);
c.update(|x| x + 1);
assert_eq!(c.get(), 6);
```

## `Cell::as_array_of_cells` (1.91)

```rust
let cell: &Cell<[i32; 3]> = &Cell::new([1, 2, 3]);
let cells: &[Cell<i32>; 3] = Cell::as_array_of_cells(cell);
```

## `hint::select_unpredictable(cond, a, b)` (1.88)

Branchless select hint for performance-critical code.
