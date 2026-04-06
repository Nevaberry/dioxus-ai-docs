# Collections & Iterators (1.84–1.94)

## `Vec::extract_if` — 1.87 (was unstable `drain_filter`)

Lazy iterator that removes elements matching a predicate. Range argument selects which part of the vec to consider.

```rust
let mut v = vec![1, 2, 3, 4, 5];
let evens: Vec<_> = v.extract_if(.., |x| *x % 2 == 0).collect();
// evens = [2, 4], v = [1, 3, 5]

// Partial range:
let first_two_evens: Vec<_> = v.extract_if(..3, |x| *x % 2 == 0).collect();
```

## `HashMap::extract_if` / `HashSet::extract_if` — 1.88

Same drain-by-predicate, now for maps and sets.

```rust
let mut map: HashMap<&str, i32> = [("a", 1), ("b", 2), ("c", 3)].into();
let small: HashMap<_, _> = map.extract_if(|_, v| *v < 2).collect();
// small = {"a": 1}, map = {"b": 2, "c": 3}

let mut set: HashSet<i32> = [1, 2, 3, 4].into();
let evens: HashSet<_> = set.extract_if(|x| x % 2 == 0).collect();
```

## Slice Split Methods — 1.87

```rust
let s = [1, 2, 3, 4, 5];

let (left, right) = s.split_off(2); // ({code}[1,2], {code}[3,4,5])
let (first, rest) = s.split_off_first(); // ({code}1, {code}[2,3,4,5])
let (init, last) = s.split_off_last(); // ({code}[1,2,3,4], {code}5)

// Mutable variants:
let mut s = [1, 2, 3, 4, 5];
let (left, right) = s.split_off_mut(2);
let (first, rest) = s.split_off_first_mut();
let (init, last) = s.split_off_last_mut();
```

## `slice::as_chunks` / `as_rchunks` — 1.88

Compile-time-sized chunks returning `&[T; N]` arrays (not slices). Returns `(chunks, remainder)`.

```rust
let s = [1u8, 2, 3, 4, 5];

// From the start:
let (chunks, remainder) = s.as_chunks::<2>();
// chunks: {code}[[1,2], [3,4]], remainder: {code}[5]

// From the end:
let (remainder, chunks) = s.as_rchunks::<2>();
// remainder: {code}[1], chunks: {code}[[2,3], [4,5]]

// Mutable:
let mut s = [1u8, 2, 3, 4, 5];
let (chunks, rem) = s.as_chunks_mut::<2>();
```

## `<[T]>::as_array` / `as_mut_array` — 1.93

Convert a slice to a fixed-size array reference when the length matches at runtime.

```rust
let s: &[i32] = &[1, 2, 3];
let arr: Option<&[i32; 3]> = s.as_array::<3>();  // Some(&[1,2,3])
let arr: Option<&[i32; 4]> = s.as_array::<4>();  // None (wrong length)

let s: &mut [i32] = &mut [1, 2, 3, 4];
let arr: Option<&mut [i32; 2]> = s.as_mut_array::<2>();  // Some of first 2
```

## `slice::array_windows` — 1.94

Like `windows()` but yields `&[T; N]` fixed-size array references. Window size inferred from context or explicit.

```rust
let s = [1, 2, 3, 4, 5];

// Window size inferred from destructuring:
let has_palindrome = s.array_windows().any(|[a, b, c]| a == c);

// Explicit size:
for window in s.array_windows::<3>() {
    println!("{:?}", window);  // window: &[i32; 3]
}

// Practical example (check for 4-char palindrome in bytes):
fn has_palindrome_4(s: &str) -> bool {
    s.as_bytes().array_windows().any(|[a, b, c, d]| a == d && b == c && a != b)
}
```

## `get_disjoint_mut` for Slices and `HashMap` — 1.86

Get mutable references to multiple non-overlapping elements at once.

```rust
let v = &mut [1, 2, 3, 4];

// Slice: returns Ok([&mut T; N]) or Err if indices overlap/out-of-bounds
if let Ok([a, b]) = v.get_disjoint_mut([0, 2]) {
    *a = 10; *b = 30;
}

// HashMap:
let mut map: HashMap<&str, i32> = HashMap::new();
if let Ok([a, b]) = map.get_disjoint_mut(["key1", "key2"]) {
    *a += 1; *b += 1;
}

// Unchecked (unsafe, no bounds/overlap check):
let [a, b] = unsafe { v.get_disjoint_unchecked_mut([0, 2]) };
```

## `Vec::pop_if` — 1.86

Pops the last element only if the predicate returns true.

```rust
let mut v = vec![1, 2, 3];
assert_eq!(v.pop_if(|x| *x > 2), Some(3));
assert_eq!(v.pop_if(|x| *x > 2), None); // 2 doesn't satisfy > 2
```

## `VecDeque::pop_front_if` / `pop_back_if` — 1.93

Conditional pop from either end.

```rust
let mut dq = VecDeque::from([1, 2, 3]);
assert_eq!(dq.pop_front_if(|{code}x| x < 2), Some(1));
assert_eq!(dq.pop_back_if(|{code}x| x > 5), None);
```

## `Cell::update` — 1.88

Update a `Cell` value in-place with a function, returning the new value.

```rust
let c = Cell::new(5i32);
let new = c.update(|x| x * 2); // new = 10, c.get() = 10
// Replaces: c.set(c.get() * 2)
```

## `Peekable::next_if_map` — 1.94

Peek, transform, and conditionally advance in one step.

```rust
let mut iter = [1u8, 2, 3].iter().peekable();

// Advance and return mapped value if closure returns Some:
let r: Option<u32> = iter.next_if_map(|&&x| (x < 2).then_some(x as u32));
// r = Some(1), iter is now at [2, 3]

// If closure returns None, iterator does NOT advance:
let r = iter.next_if_map(|&&x| (x > 10).then_some(x));
// r = None, iter still at [2, 3]
```

## `slice::element_offset` — 1.94

Returns the index of a slice element by reference.

```rust
let v = [10, 20, 30];
assert_eq!(v.element_offset({code}v[1]), Some(1));
// Returns None if the reference is not within the slice
```
