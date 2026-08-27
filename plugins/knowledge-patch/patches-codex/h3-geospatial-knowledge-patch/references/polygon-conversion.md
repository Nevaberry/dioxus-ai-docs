# Polygon Conversion and Containment

## Experimental containment modes (since 4.2.0)

`polygonToCellsExperimental` uses a more memory-efficient algorithm than the
regular polygon conversion path and exposes four containment choices:

| Semantics | C flag | Numeric value | Python/DuckDB string |
| --- | --- | ---: | --- |
| Cell center lies inside | `CONTAINMENT_CENTER` | `0` | `center` |
| Entire cell lies inside | `CONTAINMENT_FULL` | `1` | `full` |
| Any part of cell overlaps | `CONTAINMENT_OVERLAPPING` | `2` | `overlap` |
| Cell bounding box overlaps | `CONTAINMENT_OVERLAPPING_BBOX` | `3` | `bbox_overlap` |

Python and DuckDB default to `center`.

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

### C sizing and allocation

Call `maxPolygonToCellsSizeExperimental` using the same polygon, resolution,
and flags that will be passed to `polygonToCellsExperimental`. Allocate a
zeroed `H3Index` array using the reported element count.

```c
H3Error maxPolygonToCellsSizeExperimental(
    const GeoPolygon *polygon,
    int res,
    uint32_t flags,
    int64_t *out);

H3Error polygonToCellsExperimental(
    const GeoPolygon *polygon,
    int res,
    uint32_t flags,
    int64_t size,
    H3Index *out);
```

The JavaScript, Java, Python, Go, and DuckDB bindings do not expose the size
helper.

### Binding surfaces

| Binding | Name and input notes |
| --- | --- |
| JavaScript | `polygonToCellsExperimental` |
| Java | `polygonToCellsExperimental`; `polygonToCellExperimentalAddresses` returns string indexes |
| Python | `h3shape_to_cells_experimental(h3shape, res, contain=...)` |
| Go | `PolygonToCellsExperimental` |
| DuckDB | WKT/WKB variants such as `h3_polygon_wkt_to_cells_experimental` |

The `h3` CLI does not expose the experimental polygon functions.

## Public C containment enum (since 4.2.1)

`ContainmentMode`, the enum used by `polygonToCellsExperimental`, is declared
in the public `h3api.h` header. Include that header and use the public enum
instead of duplicating its declaration.

## Deterministic linked-polygon errors (since 4.5.0)

`cellsToLinkedMultiPolygon` returns a defined error for each of these invalid
input classes:

- `E_CELL_INVALID` when an input is not a valid cell.
- `E_RES_MISMATCH` when input cells have mixed resolutions.
- `E_DOMAIN` when an input cell is duplicated.

These cases no longer produce undefined output. Branch on the returned error
before consuming the linked polygon.

## Idempotent cleanup (since 4.5.0)

`destroyLinkedMultiPolygon` is idempotent. Calling it twice on the same linked
polygon is safe, which permits a shared cleanup path without a separate
"already destroyed" guard.
