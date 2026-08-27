# Grid traversal and index operations

## Pentagon-safe hollow rings

`gridRing` (since 4.3.0) returns the hollow ring of cells at exactly grid
distance `k` from an origin.

Unlike `gridRingUnsafe`, it survives pentagon distortion by falling back to a
more memory-intensive algorithm.

```js
const ring = h3.gridRing('85283473fffffff', 1);
```

### Binding names

| Binding | API |
| --- | --- |
| JavaScript | `gridRing` |
| Java | `gridRing` |
| Python | `grid_ring` |
| Go | `Cell.GridRing` |
| DuckDB | `h3_grid_ring` |
| CLI | `h3 gridRing -c <cell> -k <distance>` |

### C allocation

Allocate a zeroed output array using `maxGridRingSize`, then call:

```c
H3Error err = gridRing(origin, k, out);
```

The maximum can exceed the actual ring size. Unused entries may remain zero, so
do not treat zero slots as H3 cells.

## Resolution-digit inspection

`getIndexDigit` (since 4.4.0) retrieves a resolution digit from a cell, directed
edge, or vertex. Digit positions begin at 1 for resolution 1.

For a valid cell, asking for a position beyond the cell's resolution returns the
unused digit value `7`.

```js
const digit = h3.getIndexDigit('85283473fffffff', 2); // 7
```

C signature:

```c
H3Error getIndexDigit(H3Index h, int res, H3Index *out);
```

Binding names:

| Binding | API |
| --- | --- |
| JavaScript | `getIndexDigit` |
| Java | `getIndexDigit` |
| Python | `get_index_digit` |
| Go | `cell.IndexDigit(res)` |
| DuckDB | `h3_get_index_digit` |
| CLI | `h3 getIndexDigit -c <index> -r <res>` |

## Explicit cell construction

`constructCell` (since 4.4.0) is the inverse of inspecting a cell's resolution,
base-cell number, and digits. It constructs a valid cell from a base cell and
resolution-ordered digits.

JavaScript can infer the resolution from the digit count or accept an explicit
resolution:

```js
const cell = h3.constructCell(73, [1, 2, 3], 3);
// '839253fffffffff'
```

### C contract and errors

The C call is `constructCell(res, baseCellNumber, digits, out)`.

The accepted domains and errors are:

| Component | Domain | Error |
| --- | --- | --- |
| Resolution | 0–15 | `E_RES_DOMAIN` |
| Base cell | 0–121 | `E_BASE_CELL_DOMAIN` |
| Each digit | 0–6 | `E_DIGIT_DOMAIN` |

At resolution 0, `digits` may be `NULL`.

For a pentagon cell, digit `1` is deleted when it is the first nonzero digit
after leading zeroes. Attempting to construct that sequence returns
`E_DELETED_DIGIT`.

### Binding availability

| Binding | API |
| --- | --- |
| JavaScript | `constructCell`, with inferred or explicit resolution |
| Java | `constructCell`; `constructCellAddress` for a string result |
| DuckDB | `h3_construct_cell`; `h3_construct_cell_string`, with optional explicit resolution |
| CLI | `h3 constructCell -b <base> -d <digits> [-r <resolution>]` |

Python and Go may not expose this API. Check the installed binding instead of
transliterating a name from another language.

The C symbols `H3_INDEX_INVALID` and `H3_ERROR_END` were also introduced in
4.4.0.

## Mode-agnostic validation

`isValidIndex` (since 4.4.0) accepts any supported H3 mode. It returns true for
a valid cell, directed edge, or vertex:

```c
int isValidIndex(H3Index h);
```

Java exposes it for numeric and string indexes. DuckDB exposes
`h3_is_valid_index`. It may not be available in JavaScript, Python, or Go.

## Directed-edge reversal

`reverseDirectedEdge` (since 4.5.0) returns the same directed edge with its
origin and destination swapped.

```js
h3.reverseDirectedEdge('115283473fffffff');
// '115283477fffffff'
```

C reports an error when the input is not a valid directed edge:

```c
H3Error reverseDirectedEdge(H3Index edge, H3Index *out);
```

| Binding | API |
| --- | --- |
| JavaScript | `reverseDirectedEdge` |
| Java | `reverseDirectedEdge` |
| Python | `reverse_directed_edge` |
| Go | `edge.Reverse()` |
| DuckDB | `h3_reverse_directed_edge` |
| CLI | `h3 reverseDirectedEdge -e <edge>` |

## Bidirectional paths

`gridPathCells` supports paths with endpoints supplied in either direction
(since 4.5.0). Do not reorder endpoints solely to satisfy an assumed
directional limitation.
