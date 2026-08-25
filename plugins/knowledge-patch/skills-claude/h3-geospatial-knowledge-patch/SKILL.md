---
name: h3-geospatial-knowledge-patch
description: H3
version: 4.5.0
license: MIT
metadata:
  author: Nevaberry
---


# H3 Geospatial

Load this skill when implementing or reviewing H3 polygon conversion, grid
traversal, index construction or inspection, directed-edge handling, command-line
automation, or native-library integration.

Check the project's H3 version and binding before applying an API name. Equivalent
operations often have different names, argument shapes, return types, and
availability across C, JavaScript, Java, Python, Go, DuckDB, and the `h3` CLI.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/polygon-conversion.md](references/polygon-conversion.md) | Experimental polygon containment, binding names, C allocation, conversion errors, cleanup |
| [references/traversal-and-indexes.md](references/traversal-and-indexes.md) | Pentagon-safe rings, digit inspection, cell construction, validation, paths, directed edges |
| [references/cli-and-build-integration.md](references/cli-and-build-integration.md) | Scriptable CLI, region input/output, CMake install layout, pkg-config |

## Quick reference

### Handle polygon-conversion failures explicitly

`cellsToLinkedMultiPolygon` has deterministic failure categories:

- invalid cells return `E_CELL_INVALID`;
- cells at mixed resolutions return `E_RES_MISMATCH`;
- duplicate cells return `E_DOMAIN`.

Do not depend on partially produced or undefined output for these cases. Validate
or propagate the returned `H3Error`.

`destroyLinkedMultiPolygon` is idempotent. Cleanup code may safely call it twice,
which makes a single cleanup path practical after either success or failure.

### Do not assume grid paths are directional

`gridPathCells` accepts endpoints in either direction. Code does not need to
preorder a pair merely to make the path operation succeed.

### Prefer safe rings around pentagons

Use `gridRing` when pentagon distortion may be encountered. It returns cells at
exactly distance `k` and falls back to a more memory-intensive algorithm when the
fast unsafe algorithm cannot continue.

```js
const ring = h3.gridRing('85283473fffffff', 1);
```

Use `gridRingUnsafe` only when its pentagon failure behavior is acceptable.

In C:

1. Allocate a zeroed `H3Index` array sized by `maxGridRingSize`.
2. Call `gridRing(origin, k, out)`.
3. Ignore zero entries left when the actual ring is smaller than the maximum.

See [references/traversal-and-indexes.md](references/traversal-and-indexes.md)
for binding and CLI names.

### Reverse directed edges directly

Use `reverseDirectedEdge` to swap a directed edge's origin and destination:

```js
const reversed = h3.reverseDirectedEdge('115283473fffffff');
// '115283477fffffff'
```

The C API reports an error if its input is not a valid directed edge:

```c
H3Error reverseDirectedEdge(H3Index edge, H3Index *out);
```

Other binding names are Java `reverseDirectedEdge`, Python
`reverse_directed_edge`, Go `edge.Reverse()`, DuckDB
`h3_reverse_directed_edge`, and CLI
`h3 reverseDirectedEdge -e <edge>`.

### Choose polygon containment deliberately

`polygonToCellsExperimental` provides a memory-efficient polygon fill and four
containment rules:

| C flag | Value | Selection rule |
| --- | ---: | --- |
| `CONTAINMENT_CENTER` | 0 | Cell center is inside |
| `CONTAINMENT_FULL` | 1 | Entire cell is inside |
| `CONTAINMENT_OVERLAPPING` | 2 | Cell overlaps the polygon |
| `CONTAINMENT_OVERLAPPING_BBOX` | 3 | Cell bounding box overlaps |

JavaScript selects the flag from `POLYGON_TO_CELLS_FLAGS`:

```js
const polygon = [
  [37.813319, -122.408987],
  [37.719806, -122.354474],
  [37.815157, -122.479877]
];

const cells = h3.polygonToCellsExperimental(
  polygon,
  7,
  h3.POLYGON_TO_CELLS_FLAGS.containmentOverlapping
);
```

Python and DuckDB use the strings `center`, `full`, `overlap`, and
`bbox_overlap`; `center` is the default.

For C, use the same polygon, resolution, and flags for the size and fill calls.
Allocate a zeroed array before filling it:

```c
H3Error maxPolygonToCellsSizeExperimental(
    const GeoPolygon *polygon, int res, uint32_t flags, int64_t *out
);
H3Error polygonToCellsExperimental(
    const GeoPolygon *polygon, int res, uint32_t flags,
    int64_t size, H3Index *out
);
```

The C size helper is not exposed in the JavaScript, Java, Python, Go, or DuckDB
bindings. See
[references/polygon-conversion.md](references/polygon-conversion.md) before
porting code between bindings.

### Inspect and construct indexes

`getIndexDigit(index, res)` reads the digit for a resolution position from a
cell, directed edge, or vertex. Positions start at 1 for resolution 1. For a
valid cell, a position beyond the cell's resolution returns unused digit `7`.

```js
const digit = h3.getIndexDigit('85283473fffffff', 2); // 7
```

`constructCell` performs the inverse operation for cells: supply a base-cell
number and resolution-ordered digits. JavaScript can infer the resolution from
the digit count or accept it explicitly.

```js
const cell = h3.constructCell(73, [1, 2, 3], 3);
// '839253fffffffff'
```

In C, validate these domains or handle their exact errors:

- resolution `0` through `15`, otherwise `E_RES_DOMAIN`;
- base cell `0` through `121`, otherwise `E_BASE_CELL_DOMAIN`;
- each digit `0` through `6`, otherwise `E_DIGIT_DOMAIN`;
- a pentagon's first nonzero digit after leading zeroes cannot be `1`;
  that deleted subsequence returns `E_DELETED_DIGIT`.

At resolution 0, the C `digits` pointer may be `NULL`.

Use `isValidIndex` when a value may be any supported H3 mode. It recognizes
valid cells, directed edges, and vertices, unlike mode-specific validators.

Availability is binding-dependent. Consult
[references/traversal-and-indexes.md](references/traversal-and-indexes.md) for
the complete binding matrix and C signatures.

### Automate region operations with the CLI

The `h3` executable is suitable for shell scripts. For polygon input, use:

- `-p` for an inline polygon;
- `-i <file>` for a file;
- `-i --` for standard input.

```sh
h3 polygonToCells \
  -r 7 \
  -p '[[37.813319,-122.408987],[37.719806,-122.354474],[37.815157,-122.479877]]' \
  -f newline
```

`polygonToCells` requires a resolution from 0 through 15 and emits JSON or
newline output. Experimental polygon functions are not available through the
CLI.

### Integrate the native library

Set `CMAKE_INSTALL_LIBDIR` when packaging H3 into a nondefault library
directory:

```sh
cmake -S . -B build -DCMAKE_INSTALL_LIBDIR=lib64
```

For compiler and linker flags, query the installed `h3.pc`:

```sh
pkg-config --cflags --libs h3
```

See
[references/cli-and-build-integration.md](references/cli-and-build-integration.md)
for the complete command inventory and installation details.
