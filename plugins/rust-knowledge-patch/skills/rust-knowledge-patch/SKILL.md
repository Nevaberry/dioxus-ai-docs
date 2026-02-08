---
name: rust-knowledge-patch
description: This skill should be used when writing Rust code, using async closures, let chains, Edition 2024 features, new collection methods like extract_if, integer arithmetic methods, or any Rust features from 2024-2026.
license: MIT
metadata:
  author: Nevaberry
  version: "1.93"
---

# Rust 1.85-1.93 Knowledge Patch

Claude's baseline knowledge covers Rust through 1.84. This skill provides features from 1.85 (Feb 2025) through 1.93 (Jan 2026).

## Quick Reference

### Edition 2024 (Major Changes)

| Change | Migration |
|--------|-----------|
| `unsafe extern "C" {}` | Add `unsafe` to extern blocks |
| `#[unsafe(no_mangle)]` | Wrap unsafe attrs in `unsafe()` |
| `unsafe {}` in unsafe fns | Explicit unsafe blocks required |
| `static mut` denied | Use atomics/sync primitives |
| `gen` reserved | Rename identifiers |
| `set_var`/`remove_var` unsafe | Wrap in `unsafe {}` |

**Let chains** (Edition 2024 only):
```rust
if let Some(x) = opt && x > 0 && let Some(y) = other { ... }
```

See `references/edition-2024.md` for full migration guide.

### Async

- **Async closures**: `async || {}` with `AsyncFn`, `AsyncFnMut`, `AsyncFnOnce` traits
- **`OnceLock::wait`**: Block until initialization completes
- **`RwLockWriteGuard::downgrade`**: Write → read lock without releasing

See `references/async-and-concurrency.md`.

### Collections

| Method | Types |
|--------|-------|
| `extract_if` | Vec, LinkedList, HashMap, HashSet, BTreeMap, BTreeSet |
| `pop_if` | Vec |
| `pop_front_if` / `pop_back_if` | VecDeque |
| `get_disjoint_mut` | slices, HashMap |
| `Cell::update` | Cell |

**Tuple collection**: `(Vec<_>, Vec<_>) = iter.map(\|x\| (a, b)).collect()`

See `references/collections.md`.

### Integers

| Method | Description |
|--------|-------------|
| `midpoint` | Exact midpoint without overflow |
| `is_multiple_of` | Divisibility check |
| `unbounded_shl/shr` | Return 0 on overflow |
| `cast_signed/unsigned` | Bit reinterpretation |
| `*_sub_signed` | Subtract signed from unsigned |
| `strict_*` | Panic on overflow (release too) |
| `carrying_*/borrowing_*` | Extended precision arithmetic |
| `unchecked_*` | UB on overflow (perf-critical) |

See `references/integers-and-arithmetic.md`.

### Slices & Arrays

- **Chunking**: `as_chunks`, `as_rchunks` → `(&[[T; N]], &[T])`
- **Conversion**: `slice.as_array::<N>()` → `Option<&[T; N]>`
- **Boundaries**: `str.ceil_char_boundary(n)`, `floor_char_boundary(n)`
- **Const**: `reverse`, `rotate_left`, `rotate_right`

See `references/slices-and-arrays.md`.

### Strings & Paths

- **`Path::file_prefix`**: Filename without ANY extensions
- **`PathBuf::add_extension`**: Add without replacing
- **`OsStr::display`**: Lossy UTF-8 display
- **`String::into_raw_parts`**: Decompose to `(ptr, len, cap)`

See `references/strings-and-paths.md`.

### Pointers & Memory

- **Trait upcasting**: `&dyn Derived` → `&dyn Base` automatic
- **`NonNull` provenance**: `from_ref`, `without_provenance`, `expose_provenance`
- **`MaybeUninit` slices**: `write_copy_of_slice`, `assume_init_ref`
- **Zeroed constructors**: `Box::new_zeroed()`, `Arc::new_zeroed()`

See `references/pointers-and-memory.md`.

### Assembly & SIMD

- **Safe `#[target_feature]`**: No unsafe needed for decorated fns
- **`asm!` labels**: Jump to Rust code blocks
- **`asm!` cfg**: `#[cfg(...)]` on individual lines
- **Naked functions**: `#[unsafe(naked)]` + `naked_asm!`

See `references/assembly-and-simd.md`.

### I/O

- **`io::pipe()`**: Cross-platform anonymous pipes
- **`File::lock/unlock`**: Advisory file locking
- **`i128/u128` in FFI**: No more warnings

See `references/io-and-process.md`.

### Misc

- **`Result::flatten`**: `Result<Result<T,E>,E>` → `Result<T,E>`
- **`fmt::from_fn`**: Display from closure
- **`Duration::from_mins/hours`**: Convenience constructors
- **Const `TypeId::of`**: Compile-time type IDs
- **Const float rounding**: `floor`, `ceil`, `round` in const

See `references/misc-apis.md`.

### Cargo

- **LLD default** (x86_64 Linux): Faster linking
- **`cargo publish --workspace`**: Multi-crate publishing
- **Auto cache cleaning**: 3mo network, 1mo local

See `references/cargo-and-tooling.md`.

## Reference Files

Detailed documentation in `references/`:

| File | Contents |
|------|----------|
| `edition-2024.md` | Full Edition 2024 migration guide |
| `async-and-concurrency.md` | Async closures, locks, atomics |
| `integers-and-arithmetic.md` | All integer methods |
| `collections.md` | extract_if, pop_if, disjoint_mut |
| `slices-and-arrays.md` | Chunking, conversion, const ops |
| `strings-and-paths.md` | Path/String APIs |
| `pointers-and-memory.md` | Upcasting, provenance, MaybeUninit |
| `assembly-and-simd.md` | asm!, target_feature, naked fns |
| `io-and-process.md` | Pipes, FFI, file locking |
| `misc-apis.md` | Floats, Duration, formatting, cfg |
| `cargo-and-tooling.md` | LLD, workspace publish, cache |
