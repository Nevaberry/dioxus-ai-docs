# Collections

## `extract_if`

Drain elements matching a predicate, keeping others.

| Collection | Available |
|------------|-----------|
| `Vec` | Yes (with range parameter) |
| `LinkedList` | Yes |
| `HashMap` | Yes |
| `HashSet` | Yes |
| `BTreeMap` | Yes |
| `BTreeSet` | Yes |

```rust
let mut vec = vec![1, 2, 3, 4, 5, 6];
let evens: Vec<_> = vec.extract_if(.., |x| *x % 2 == 0).collect();
assert_eq!(evens, vec![2, 4, 6]);
assert_eq!(vec, vec![1, 3, 5]);

// Vec supports range parameter
let extracted: Vec<_> = vec.extract_if(1..4, |x| *x > 2).collect();

// HashMap
let mut map = HashMap::from([("a", 1), ("b", 2), ("c", 3)]);
let big: HashMap<_, _> = map.extract_if(|_k, v| *v > 1).collect();
```

## `pop_if` / `pop_front_if` / `pop_back_if`

Conditionally pop elements.

```rust
// Vec::pop_if
let mut vec = vec![1, 2, 3, 4];
let popped = vec.pop_if(|x| *x > 3);  // Some(4)
let none = vec.pop_if(|x| *x > 10);   // None

// VecDeque
let mut deque = VecDeque::from([1, 2, 3, 4, 5]);
deque.pop_front_if(|x| *x < 2);  // Some(1)
deque.pop_back_if(|x| *x > 4);   // Some(5)
```

## Disjoint Mutable Indexing

Safe simultaneous mutable access to multiple non-overlapping elements.

```rust
// Slices
let v = &mut [1, 2, 3, 4, 5];
let [a, b, c] = v.get_disjoint_mut([0, 2, 4]).unwrap();
*a = 10; *b = 30; *c = 50;

// HashMap
let mut map = HashMap::from([("a", 1), ("b", 2), ("c", 3)]);
let [x, y] = map.get_disjoint_mut(["a", "c"]).unwrap();
```

Returns `Err` if indices overlap or are out of bounds.

## Tuple Collection

`collect()` into multiple collections simultaneously (arity 1-12).

```rust
let (evens, odds): (Vec<_>, Vec<_>) =
    (0..10).map(|i| (i * 2, i * 2 + 1)).collect();

let (a, b, c): (Vec<_>, Vec<_>, Vec<_>) =
    data.into_iter().map(|x| (x.a, x.b, x.c)).collect();
```

## `btree_map::Entry::insert_entry`

Insert and get the entry in one operation.

```rust
let mut map: BTreeMap<&str, i32> = BTreeMap::new();
let entry = map.entry("key").insert_entry(42);
assert_eq!(entry.get(), &42);
*entry.into_mut() = 100;
```

## `core::iter::chain`

Free function alternative to `Iterator::chain`.

```rust
use std::iter::chain;
let chained: Vec<_> = chain(&[1, 2], &[3, 4]).collect();
```

## `core::array::repeat`

Create array by repeating a value.

```rust
use std::array::repeat;
let zeros: [i32; 5] = repeat(0);
```

## `Cell::as_array_of_cells`

View `Cell<[T; N]>` as `&[Cell<T>; N]`.

```rust
use std::cell::Cell;
let cell: Cell<[i32; 3]> = Cell::new([1, 2, 3]);
let cells: &[Cell<i32>; 3] = cell.as_array_of_cells();
cells[1].set(20);
```

## `Cell::update`

Update in place with a function.

```rust
let counter = Cell::new(0);
counter.update(|x| x + 1);
```
