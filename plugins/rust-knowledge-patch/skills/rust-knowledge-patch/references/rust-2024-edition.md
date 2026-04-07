# Rust 2024 Edition

Stabilized in Rust 1.85.0 (2025-02-20). Enable with `edition = "2024"` in `Cargo.toml`. Migrate with `cargo fix --edition`.

## Breaking Changes from 2021

### `extern` blocks require `unsafe`

```rust
// 2021
extern "C" {
    fn foo();
}

// 2024
unsafe extern "C" {
    fn foo();
    safe fn bar(); // opt-in: callable without unsafe block
}
```

### Link attributes require `unsafe(...)` wrapper

```rust
// 2021
#[no_mangle]
#[export_name = "my_fn"]
#[link_section = ".text"]
pub extern "C" fn my_fn() {}

// 2024
#[unsafe(no_mangle)]
#[unsafe(export_name = "my_fn")]
#[unsafe(link_section = ".text")]
pub extern "C" fn my_fn() {}
```

### `unsafe fn` bodies require explicit `unsafe {}`

The lint `unsafe_op_in_unsafe_fn` is now warn-by-default in 2021, and an error in 2024.

```rust
// 2024: unsafe operations inside unsafe fn still need a block
unsafe fn helper() {
    unsafe {
        some_unsafe_op();
    }
}
```

### References to `static mut` are hard errors

Use `&raw const`/`&raw mut` instead (safe since 1.84).

```rust
static mut GLOBAL: u32 = 0;

// 2021: warned
// 2024: hard error
let _r = &GLOBAL;

// Fix: use raw refs (safe in 2024)
let r = &raw const GLOBAL;
let r = &raw mut GLOBAL;
```

### `std::env::set_var` / `remove_var` are now `unsafe`

```rust
// 2024
unsafe {
    std::env::set_var("KEY", "val");
}
unsafe {
    std::env::remove_var("KEY");
}
```

### `gen` is a reserved keyword

Can no longer be used as an identifier.

### `impl Trait` in return position captures all in-scope lifetimes

```rust
// 2021: only captures what's needed
fn foo<'a>(x: &'a str) -> impl Display { x }

// 2024: captures 'a by default
fn foo<'a>(x: &'a str) -> impl Display { x }

// 2024: restrict explicitly with use<>
fn foo<'a>(x: &'a str) -> impl Display + use<'a> { x }
fn bar() -> impl Display + use<> { "static" }  // captures nothing
```

### `Future` and `IntoFuture` added to prelude

May cause name conflicts if you define local `Future`/`IntoFuture` types.

---

## Let Chains — Stabilized in 1.88 (2024 Edition only)

Chain `let` bindings with `&&` inside `if`/`while`. Each binding is in scope for subsequent conditions.

```rust
if let Channel::Stable(v) = release_info()
    && let Semver { major, minor, .. } = v
    && major == 1
    && minor == 88
{
    println!("let chains stabilized here");
}

while let Some(x) = iter.next() && x < 10 {
    process(x);
}

// Combining with regular bool expressions:
if let Some(user) = db.get(id)
    && user.is_active()
    && let Some(role) = user.role()
{
    grant_access(role);
}
```

---

## `&raw const` / `&raw mut` — Safe since 1.84

Taking a raw reference through a pointer dereference no longer requires `unsafe`:

```rust
let p: *const i32 = &42;
let r = &raw const *p;  // was unsafe before 1.84, now safe

// Key use case: safely reference static mut
static mut COUNTER: u32 = 0;
let r: *const u32 = &raw const COUNTER;  // safe
```
