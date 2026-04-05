# Rust 2024 Edition (Stable in 1.85)

Migrate with `cargo fix --edition`.

## `unsafe extern` Blocks

All `extern` blocks must be `unsafe extern` in 2024 edition. Individual items can be marked `safe`:

```rust
unsafe extern "C" {
    safe fn strlen(s: *const std::ffi::c_char) -> usize;
    fn puts(s: *const std::ffi::c_char) -> i32; // unsafe by default
}
```

## Unsafe Attributes

`no_mangle`, `export_name`, and `link_section` must use `unsafe()` wrapper:

```rust
#[unsafe(no_mangle)]
pub extern "C" fn my_func() {}

#[unsafe(export_name = "my_symbol")]
pub fn foo() {}
```

## `unsafe_op_in_unsafe_fn` Warns by Default

Unsafe operations inside `unsafe fn` now require explicit `unsafe {}` blocks:

```rust
unsafe fn do_stuff(ptr: *const i32) -> i32 {
    unsafe { *ptr } // required in 2024 edition
}
```

## `static mut` References Denied

References to `static mut` are errors. Use raw pointers instead:

```rust
static mut COUNTER: u32 = 0;
// 2024: {code}COUNTER or {code}mut COUNTER is an error
// Use std::ptr::addr_of!(COUNTER) / addr_of_mut!(COUNTER) instead
```

## `std::env::set_var` / `remove_var` Are Unsafe

```rust
unsafe { std::env::set_var("KEY", "value") };
```

## Macro Fragment Changes

- `expr` fragment now also matches `const { }` blocks and `_`
- Use `expr_2021` fragment to preserve old behavior

## Reserved Keyword: `gen`

`gen` is reserved for future generator blocks. Rename any identifiers using this name.

## Prelude Additions

- `Future` and `IntoFuture` added to 2024 prelude
- `AsyncFn`, `AsyncFnMut`, `AsyncFnOnce` added to prelude in **all editions**

## `IntoIterator` for `Box<[T]>`

`Box<[T]>` now iterates by value (owned `T`), not by reference. This may break code that relied on iterating `&T`.

## Cargo: MSRV-Aware Resolver

The MSRV-aware dependency resolver is the default in 2024 edition. Cargo respects the `rust-version` field and avoids pulling deps that require a newer Rust than your MSRV.
