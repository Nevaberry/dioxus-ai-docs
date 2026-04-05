# Collections & Iterators (1.85–1.94)

## `get_disjoint_mut` (1.86)

Safely get multiple mutable references to distinct elements simultaneously:

```rust
let v = &mut [1, 2, 3];
let [a, b] = v.get_disjoint_mut([0, 2]).unwrap();
*a = 10; *b = 30;

// Also works with ranges and on HashMap
use std::collections::HashMap;
let mut map = HashMap::from([("a", 1), ("b", 2)]);
let [a, b] = map.get_disjoint_mut(["a", "b"]).unwrap();
*a = 10;
```

## `Vec::pop_if` (1.86)

Conditionally pop the last element:

```rust
let mut v = vec![1, 2, 3];
let popped = v.pop_if(|&mut x| x > 2); // Some(3)
let not_popped = v.pop_if(|&mut x| x > 5); // None
```

## `Vec::extract_if` (1.87)

Stable replacement for `drain_filter`. Removes and yields elements matching a predicate:

```rust
let mut v = vec![1, 2, 3, 4, 5];
let evens: Vec<_> = v.extract_if(.., |x, _| *x % 2 == 0).collect();
// evens = [2, 4], v = [1, 3, 5]
```

Note: takes a **range** as first argument (use `..` for the whole vec).

## `HashMap::extract_if` / `HashSet::extract_if` (1.88)

Same pattern for maps and sets:

```rust
let mut map = HashMap::from([("a", 1), ("b", 2), ("c", 3)]);
let extracted: HashMap<_, _> = map.extract_if(|_, v| *v > 1).collect();
```

## `VecDeque::pop_front_if` / `pop_back_if` (1.93)

Conditional pop for deques:

```rust
let mut dq = std::collections::VecDeque::from([1, 2, 3]);
let popped = dq.pop_front_if(|&mut x| x < 2); // Some(1)
let nope = dq.pop_back_if(|&mut x| x > 5);    // None
```

## `array_windows` (1.94)

Slice method returning fixed-size array windows (vs dynamic `windows(n)`). Window size can be inferred:

```rust
let data = &[1, 2, 3, 4, 5];
let diffs: Vec<_> = data.array_windows().map(|&[a, _, b]| b - a).collect();

fn has_abba(s: &str) -> bool {
    s.as_bytes()
        .array_windows()
        .any(|[a1, b1, b2, a2]| (a1 != b1) && (a1 == a2) && (b1 == b2))
}
```

## `<[T]>::as_chunks::<N>()` (1.88)

View slice as array chunks with remainder:

```rust
let slice = &[1, 2, 3, 4, 5];
let (chunks, remainder): (&[[i32; 2]], &[i32]) = slice.as_chunks::<2>();
// chunks = &[[1, 2], [3, 4]], remainder = &[5]
```

Also: `as_chunks_mut::<N>()` for mutable version.

## `<[T]>::as_array::<N>()` / `as_array_mut` (1.93)

Try to convert a slice reference to a fixed-size array reference:

```rust
let slice: &[u8] = &[1, 2, 3, 4];
let arr: Option<&[u8; 4]> = slice.as_array::<4>(); // Some(&[1, 2, 3, 4])
let nope: Option<&[u8; 5]> = slice.as_array::<5>(); // None
```

Also available on `*const [T]` and `*mut [T]` raw pointers.

## `<[T]>::element_offset` (1.94)

Given a reference to an element within a slice, returns its index:

```rust
let v = &[10, 20, 30];
let elem = &v[1];
assert_eq!(v.element_offset(elem), Some(1));
```

## Tuple `FromIterator` / `Extend` (1.85, Arity 1–12)

`collect()` can fan out into multiple collections from tuple iterators:

```rust
let (v, d): (Vec<_>, VecDeque<_>) = (0..5).map(|i| (i, i * 2)).collect();
// Also works for 3-tuples, 4-tuples, ... up to 12
```

## `core::iter::chain(a, b)` (1.91)

Free function equivalent of `a.chain(b)`.

## `core::array::repeat::<N>(value)` (1.91)

Create `[T; N]` from a `Clone` value (like `[val; N]` but works with non-`Copy` types):

```rust
let arr: [String; 3] = core::array::repeat(String::from("hello"));
```

## Behavior Change: `iter::Repeat` (1.92)

`iter::Repeat::last()` and `.count()` now **panic** instead of looping infinitely.
