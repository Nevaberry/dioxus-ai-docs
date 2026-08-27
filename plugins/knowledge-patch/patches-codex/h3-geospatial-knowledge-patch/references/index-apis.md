# Index Inspection, Construction, and Validation

## Resolution-digit inspection (since 4.4.0)

`getIndexDigit` retrieves a resolution digit from a cell, directed edge, or
vertex. Resolution positions are one-based: position `1` is the resolution-1
digit. For a valid cell, positions beyond its resolution return the unused
digit value `7`.

```js
const digit = h3.getIndexDigit("85283473fffffff", 2); // 7
```

The C function writes its result to an `H3Index` output pointer:

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

## Explicit cell construction (since 4.4.0)

`constructCell` reverses the usual resolution, base-cell, and resolution-digit
inspection: it builds a valid cell from those components. JavaScript can infer
the resolution from the digit count or accept it explicitly.

```js
const cell = h3.constructCell(73, [1, 2, 3], 3);
// "839253fffffffff"
```

### C contract

Call `constructCell(res, baseCellNumber, digits, out)`.

Inputs and errors:

| Input condition | Result |
| --- | --- |
| Resolution outside `0` through `15` | `E_RES_DOMAIN` |
| Base cell outside `0` through `121` | `E_BASE_CELL_DOMAIN` |
| Any of the `res` digits outside `0` through `6` | `E_DIGIT_DOMAIN` |
| Pentagon would use digit `1` as its first nonzero digit after leading zeroes | `E_DELETED_DIGIT` |

At resolution 0, `digits` may be `NULL`.

This API addition also provides the C symbols `H3_INDEX_INVALID` and
`H3_ERROR_END`.

### Other bindings

- Java provides `constructCell` and string-returning
  `constructCellAddress`.
- DuckDB provides `h3_construct_cell` and `h3_construct_cell_string`; both
  permit an optional explicit resolution.
- The CLI form is
  `h3 constructCell -b <base> -d <digits> [-r <resolution>]`.
- Python and Go may not expose this API.

## Mode-agnostic validation (since 4.4.0)

`isValidIndex` returns true for a valid index in any supported H3 mode: cell,
directed edge, or vertex.

```c
int isValidIndex(H3Index h);
```

Java accepts numeric or string indexes. DuckDB exposes
`h3_is_valid_index`. JavaScript, Python, and Go may not expose this
mode-agnostic validator.
