---
name: h3-geospatial-knowledge-patch
description: H3
version: "4.5.0"
license: MIT
metadata:
  author: Nevaberry
---


# H3 Geospatial Compatibility Guide

Use this skill when implementing or reviewing H3 region conversion, grid
traversal, index construction, directed edges, validation, command-line
automation, or native-library packaging. Check the project's language binding
before assuming that a core C API has the same name or is exposed at all.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/polygon-conversion.md](references/polygon-conversion.md) | Experimental polygon containment, C allocation, binding-specific mode names, deterministic conversion errors, linked-polygon cleanup |
| [references/grid-traversal.md](references/grid-traversal.md) | Pentagon-safe rings, bidirectional paths, directed-edge reversal |
| [references/index-apis.md](references/index-apis.md) | Resolution-digit inspection, explicit cell construction, component errors, mode-agnostic validation |
| [references/cli-and-packaging.md](references/cli-and-packaging.md) | Scriptable CLI, region input/output, CMake install paths, pkg-config metadata |

## Compatibility changes to audit first

### Treat polygon conversion failures as defined outcomes

`cellsToLinkedMultiPolygon` reports distinct errors for three invalid inputs:

| Condition | C error |
| --- | --- |
| Invalid cell | `E_CELL_INVALID` |
| Cells at mixed resolutions | `E_RES_MISMATCH` |
| Duplicate cell | `E_DOMAIN` |

Handle these errors instead of relying on partially populated or undefined
output. Cleanup is simpler as well: `destroyLinkedMultiPolygon` is idempotent,
so a second call is safe.

### Do not assume grid paths are directional

`gridPathCells` accepts endpoints supplied in either direction. Avoid
application-side rejection or endpoint reordering that exists only to work
around one-way path behavior.

### Prefer the safe ring API around pentagons

`gridRing` returns cells at exactly distance `k` and falls back to a
more-memory-intensive algorithm when pentagon distortion prevents the fast
algorithm from succeeding. Use `gridRingUnsafe` only when its failure
characteristics are acceptable.

### Use the public containment type in C

`ContainmentMode` is part of `h3api.h`. C consumers should include the public
header and use the supported declaration rather than maintaining a local enum
copy.

## Experimental polygon containment

`polygonToCellsExperimental` uses a memory-efficient algorithm and supports
four interpretations of polygon containment:

| Meaning | C flag | Value | Python/DuckDB mode |
| --- | --- | ---: | --- |
| Cell center is inside | `CONTAINMENT_CENTER` | `0` | `center` |
| Cell is fully inside | `CONTAINMENT_FULL` | `1` | `full` |
| Any part of cell overlaps | `CONTAINMENT_OVERLAPPING` | `2` | `overlap` |
| Cell bounding box overlaps | `CONTAINMENT_OVERLAPPING_BBOX` | `3` | `bbox_overlap` |

`center` is the default in Python and DuckDB. Make the mode explicit when
boundary behavior matters.

```js
const polygon = [
  [37.813319, -122.408987],
  [37.719806, -122.354474],
  [37.815157, -122.479877],
];

const cells = h3.polygonToCellsExperimental(
  polygon,
  7,
  h3.POLYGON_TO_CELLS_FLAGS.containmentOverlapping,
);
```

### C allocation pattern

The C API does not allocate the output array. Call the size helper with exactly
the same polygon, resolution, and flags, then allocate a zeroed array and pass
its element count to `polygonToCellsExperimental`. Check the sizing call's
returned `H3Error` before allocating.

The size helper is not exposed by the JavaScript, Java, Python, Go, or DuckDB
bindings.

### Binding names

JavaScript uses `polygonToCellsExperimental`; Java also provides
`polygonToCellExperimentalAddresses` for string indexes. Python uses
`h3shape_to_cells_experimental`, Go uses `PolygonToCellsExperimental`, and
DuckDB has WKT/WKB variants such as `h3_polygon_wkt_to_cells_experimental`.

The scriptable CLI does not expose the experimental polygon functions.

## Pentagon-safe hollow rings

Use `gridRing` when the result must be the hollow ring at exactly distance `k`
and the origin or traversal may encounter pentagon distortion.

```js
const ring = h3.gridRing("85283473fffffff", 1);
```

Binding names are JavaScript and Java `gridRing`, Python `grid_ring`, Go
`Cell.GridRing`, DuckDB `h3_grid_ring`, and CLI
`h3 gridRing -c <cell> -k <distance>`.

In C, allocate a zeroed output array using `maxGridRingSize`, then call
`gridRing(origin, k, out)`. The maximum can exceed the actual ring size, so
unused entries can remain zero.

## Inspecting and constructing indexes

### Read a resolution digit

`getIndexDigit` reads a digit from a cell, directed edge, or vertex. Positions
start at `1` for resolution 1. For a valid cell, a position beyond the cell's
resolution returns the unused digit value `7`.

```js
const digit = h3.getIndexDigit("85283473fffffff", 2);
```

The C function writes the digit through an `H3Index *`:

```c
H3Error getIndexDigit(H3Index h, int res, H3Index *out);
```

### Construct a cell explicitly

`constructCell` is the inverse of inspecting a cell's resolution, base cell,
and digits. JavaScript can infer the resolution from the number of digits or
accept it explicitly.

```js
const cell = h3.constructCell(73, [1, 2, 3], 3);
// "839253fffffffff"
```

For C, enforce these domains before or while handling the returned error:

| Component | Valid input | Error |
| --- | --- | --- |
| Resolution | `0` through `15` | `E_RES_DOMAIN` |
| Base cell | `0` through `121` | `E_BASE_CELL_DOMAIN` |
| Each digit | `0` through `6` | `E_DIGIT_DOMAIN` |
| Pentagon first nonzero digit after leading zeroes | Must not be `1` | `E_DELETED_DIGIT` |

At resolution 0, C accepts `NULL` for `digits`. The C release also defines
`H3_INDEX_INVALID` and `H3_ERROR_END`.

Python and Go may not expose `constructCell`; consult the reference before
designing a cross-language interface.

### Validate any supported H3 mode

Use `isValidIndex` when an input may be a cell, directed edge, or vertex. It
validates all supported H3 modes, unlike a cell-only validator.

```c
int isValidIndex(H3Index h);
```

This API is available in Java for numeric and string indexes and in DuckDB as
`h3_is_valid_index`; it may not be exposed in JavaScript, Python, or Go.

## Reverse directed edges

`reverseDirectedEdge` returns the edge between the same cells with its origin
and destination swapped.

```js
h3.reverseDirectedEdge("115283473fffffff");
// "115283477fffffff"
```

In C, invalid directed-edge input produces an error:

```c
H3Error reverseDirectedEdge(H3Index edge, H3Index *out);
```

Other names are Java `reverseDirectedEdge`, Python `reverse_directed_edge`, Go
`edge.Reverse()`, DuckDB `h3_reverse_directed_edge`, and CLI
`h3 reverseDirectedEdge -e <edge>`.

## CLI and native packaging quick reference

The `h3` binary is intended for scripts. Region commands include
`polygonToCells`, `maxPolygonToCellsSize`, and `cellsToMultiPolygon`.
`polygonToCells` requires a resolution from 0 through 15 and can emit JSON or
newline-delimited output.

```sh
h3 polygonToCells -r 7 \
  -p '[[37.813319,-122.408987],[37.719806,-122.354474],[37.815157,-122.479877]]' \
  -f newline
```

Use `-p` for inline polygon input, `-i <file>` for a file, or `-i --` for
standard input.

For native installation, `CMAKE_INSTALL_LIBDIR` selects the library
destination:

```sh
cmake -S . -B build -DCMAKE_INSTALL_LIBDIR=lib64
```

Installed pkg-config metadata supports discovery of compiler and linker flags:

```sh
pkg-config --cflags --libs h3
```

## Implementation checklist

- Identify the exact binding before choosing an API name or return type.
- Choose polygon containment semantics explicitly when boundaries matter.
- In C, pair sizing helpers with zeroed, correctly sized output arrays.
- Prefer `gridRing` when pentagon distortion is possible.
- Handle construction and polygon-conversion errors by their specific codes.
- Use `isValidIndex` for mixed cells, directed edges, and vertices.
- Treat linked-polygon destruction as safe to repeat during cleanup.
- Use the scriptable CLI only for functions it actually exposes.
- Configure library paths through CMake and discover native flags with
  pkg-config rather than hard-coding platform paths.
