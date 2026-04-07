# Standard Library Additions (1.84–1.94)

## Anonymous Pipes — 1.87

`std::io::pipe()` returns `(PipeReader, PipeWriter)`. Both implement `Read`/`Write` and convert to `Stdio`.

```rust
use std::io::{self, Read};
use std::process::Command;

let (mut recv, send) = io::pipe()?;
let mut child = Command::new("cmd")
    .stdout(send.try_clone()?)
    .stderr(send)
    .spawn()?;

let mut output = Vec::new();
recv.read_to_end(&mut output)?;  // read BEFORE wait to avoid blocking on full buffer
child.wait()?;
```

## Advisory File Locking — 1.89

New stdlib file locking without `fs2` crate. Advisory (not mandatory): other processes that don't use these calls can bypass locks.

```rust
use std::fs::File;

let f = File::open("data.txt")?;

f.lock()?; // exclusive lock — blocks until acquired
f.lock_shared()?; // shared (read) lock — blocks until acquired
f.try_lock()?; // non-blocking; returns Err if already locked
f.try_lock_shared()?;
f.unlock()?; // explicit unlock (also unlocked on drop)
```

## `OsStr::display()` / `OsString::display()` — 1.87

Display `OsStr`/`OsString` without `.to_string_lossy()`. Returns a lossily-decoded `Display` wrapper.

```rust
// Before:
println!("{}", path.file_name().unwrap().to_string_lossy());

// After:
println!("{}", path.file_name().unwrap().display());

// Works anywhere Display is accepted:
let s = format!("{}", some_os_string.display());
```

## `sync::Once::wait` / `OnceLock::wait` — 1.86

Block the current thread until `Once`/`OnceLock` has been initialized.

```rust
use std::sync::{OnceLock, Arc};
use std::thread;

let lock: Arc<OnceLock<String>> = Arc::new(OnceLock::new());
let lock2 = Arc::clone(&lock);

thread::spawn(move || {
    lock2.set("initialized".to_string()).ok();
});

let val: &String = lock.wait();  // blocks until set
println!("{val}");
```

## `RwLockWriteGuard::downgrade` — 1.92

Atomically downgrade a write lock to a read lock without releasing it. Eliminates the race window between `drop(write_guard)` and `lock.read()`.

```rust
use std::sync::{Arc, RwLock, RwLockWriteGuard};

let lock = Arc::new(RwLock::new(0u32));
let write = lock.write().unwrap();

// ... mutate data ...

// Atomically: release exclusive write, become shared read
let read = RwLockWriteGuard::downgrade(write);
println!("{}", *read);  // can read without reacquiring
```

## `LazyCell`/`LazyLock` New Methods — 1.94

`get()` returns `Option<&T>` without forcing initialization. `force_mut()` forces initialization and returns `&mut T`.

```rust
use std::cell::LazyCell;
use std::sync::LazyLock;

// Before first access, cell is uninitialized:
let mut cell: LazyCell<String> = LazyCell::new(|| "hello".into());
let _: Option<&String> = cell.get();  // None (not yet initialized)
let _ = *cell;                         // forces initialization
let _: Option<&String> = cell.get();  // Some("hello")

// Mutation after forced init:
let s: &mut String = LazyCell::force_mut(&mut cell);
s.push_str(" world");

// LazyLock has the same API (thread-safe):
let mut lock: LazyLock<String> = LazyLock::new(|| "hello".into());
let s = LazyLock::force_mut(&mut lock);
```

## `Result::flatten` — 1.89

Flatten `Result<Result<T, E>, E>` into `Result<T, E>`. Mirror of `Option::flatten`.

```rust
let r: Result<Result<i32, &str>, &str> = Ok(Ok(42));
assert_eq!(r.flatten(), Ok(42));

let r: Result<Result<i32, &str>, &str> = Ok(Err("inner"));
assert_eq!(r.flatten(), Err("inner"));

let r: Result<Result<i32, &str>, &str> = Err("outer");
assert_eq!(r.flatten(), Err("outer"));
```

## Path / OsStr Additions — 1.91

```rust
use std::path::{Path, PathBuf};

// file_prefix: strip ALL extensions (file_stem only strips the last)
Path::new("archive.tar.gz").file_prefix()  // Some("archive")
Path::new("archive.tar.gz").file_stem()    // Some("archive.tar")
Path::new(".hidden").file_prefix()         // Some(".hidden")

// add_extension: appends instead of replacing
let mut p = PathBuf::from("file.tar");
p.add_extension("gz");  // "file.tar.gz"
// set_extension would give: "file.gz"

// Non-mutating variant:
let p2 = PathBuf::from("file.tar").with_added_extension("gz");

// PartialEq with strings (new in 1.91):
assert!(Path::new("/tmp/foo") == "/tmp/foo");
assert!(PathBuf::from("/tmp/foo") == "/tmp/foo");
assert!(PathBuf::from("/tmp/foo") == String::from("/tmp/foo"));
```

## `Duration` Additions

```rust
// From 1.91: minute and hour constructors
Duration::from_mins(5)    // = Duration::from_secs(300)
Duration::from_hours(2)   // = Duration::from_secs(7200)

// From 1.93: u128 nanoseconds (avoids u64 overflow)
let nanos: u128 = u64::MAX as u128 + 1000;
let d = Duration::from_nanos_u128(nanos);
```

## `std::fmt::from_fn` — 1.93

Create a `Display`/`Debug`-implementing value from a closure, without defining a new type.

```rust
use std::fmt;

let val = fmt::from_fn(|f| write!(f, "hello {}", 42));
println!("{val}"); // "hello 42"
let s = format!("{val}"); // "hello 42"

// Useful for lazy formatting in log calls:
log::debug!("{}", fmt::from_fn(|f| expensive_format(f)));
```
