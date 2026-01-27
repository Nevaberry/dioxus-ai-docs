# Slices and Arrays

## Chunking Methods

Exact-size chunking with compile-time guarantees.

```rust
let data = [1, 2, 3, 4, 5, 6, 7, 8];

// as_chunks: split into fixed-size arrays
let (chunks, remainder): (&[[i32; 3]], &[i32]) = data.as_chunks();
// chunks = [[1,2,3], [4,5,6]], remainder = [7,8]

// as_rchunks: from the right
let (remainder, chunks): (&[i32], &[[i32; 3]]) = data.as_rchunks();
// remainder = [1,2], chunks = [[3,4,5], [6,7,8]]

// Mutable versions: as_chunks_mut, as_rchunks_mut
```

## Slice-to-Array Conversion

Try to view a slice as a fixed-size array.

```rust
let slice = &[1, 2, 3, 4, 5][..];

let arr: Option<&[i32; 5]> = slice.as_array();
assert_eq!(arr, Some(&[1, 2, 3, 4, 5]));

let arr: Option<&[i32; 3]> = slice.as_array();
assert!(arr.is_none());  // Length mismatch

// Mutable version
let slice = &mut [1, 2, 3][..];
if let Some(arr) = slice.as_mut_array::<3>() {
    arr[0] = 10;
}

// Also works on raw pointers
let ptr: *const [i32] = &[1, 2, 3][..];
let arr_ptr: Option<*const [i32; 3]> = ptr.as_array();
```

## Split Methods

```rust
// split_off_first / split_off_last
let slice = &mut [1, 2, 3, 4][..];
let (first, rest) = slice.split_off_first().unwrap();
let (last, init) = slice.split_off_last().unwrap();
```

## Character Boundary Methods

Find valid UTF-8 boundaries for safe slicing.

```rust
let s = "Hello, 世界!";

let ceil = s.ceil_char_boundary(8);   // 10 (start of '界')
let floor = s.floor_char_boundary(8); // 7 (start of '世')

// Safe truncation
let truncated = &s[..s.floor_char_boundary(10)];
assert_eq!(truncated, "Hello, 世");
```

## Const Operations

These work in const contexts:

```rust
// reverse
const fn reversed() -> [i32; 5] {
    let mut arr = [1, 2, 3, 4, 5];
    arr.reverse();
    arr
}

// rotate_left / rotate_right
const fn rotated() -> [i32; 5] {
    let mut arr = [1, 2, 3, 4, 5];
    arr.rotate_left(2);
    arr  // [3, 4, 5, 1, 2]
}
```
