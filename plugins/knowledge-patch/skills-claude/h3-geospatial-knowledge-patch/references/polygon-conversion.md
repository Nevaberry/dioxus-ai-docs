# Polygon conversion and linked polygon output

## Experimental containment modes

`polygonToCellsExperimental` (since 4.2.0) uses a more memory-efficient
algorithm and supports four ways to decide whether a cell belongs in the
result.

| Semantic mode | C flag | Numeric value | Python and DuckDB value |
| --- | --- | ---: | --- |
| Cell center inside | `CONTAINMENT_CENTER` | 0 | `center` |
| Cell fully inside | `CONTAINMENT_FULL` | 1 | `full` |
| Any cell overlap | `CONTAINMENT_OVERLAPPING` | 2 | `overlap` |
| Cell bounding-box overlap | `CONTAINMENT_OVERLAPPING_BBOX` | 3 | `bbox_overlap` |

`center` is the default for the Python and DuckDB bindings.

JavaScript example:

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

### Binding names

| Binding | API |
| --- | --- |
| JavaScript | `polygonToCellsExperimental` |
| Java | `polygonToCellsExperimental`; `polygonToCellExperimentalAddresses` for string indexes |
| Python | `h3shape_to_cells_experimental(h3shape, res, contain=...)` |
| Go | `PolygonToCellsExperimental` |
| DuckDB | WKT/WKB variants such as `h3_polygon_wkt_to_cells_experimental` |

The experimental polygon functions are not exposed through the `h3` CLI.

## C allocation contract

The C API is a two-call operation:

```c
H3Error maxPolygonToCellsSizeExperimental(
    const GeoPolygon *polygon,
    int res,
    uint32_t flags,
    int64_t *out
);

H3Error polygonToCellsExperimental(
    const GeoPolygon *polygon,
    int res,
    uint32_t flags,
    int64_t size,
    H3Index *out
);
```

Call `maxPolygonToCellsSizeExperimental` first. Use exactly the same polygon,
resolution, and flags for the fill operation. Allocate a zeroed `H3Index` array
with the returned element count, then pass both the count and array to
`polygonToCellsExperimental`.

The size helper is C-specific. JavaScript, Java, Python, Go, and DuckDB do not
expose it.

`ContainmentMode`, the enum used by this API, is publicly declared in
`h3api.h` (since 4.2.1). C consumers should include the public header rather
than duplicate the enum declaration.

## Linked multi-polygon error handling

`cellsToLinkedMultiPolygon` reports deterministic input failures (since 4.5.0):

| Condition | Error |
| --- | --- |
| An input cell is invalid | `E_CELL_INVALID` |
| Input cells have mixed resolutions | `E_RES_MISMATCH` |
| The input contains a duplicate cell | `E_DOMAIN` |

Check the returned error before consuming the linked structure. These cases no
longer need to be treated as unspecified-output scenarios.

## Cleanup

`destroyLinkedMultiPolygon` is idempotent (since 4.5.0). Calling it twice on the
same linked polygon is safe, so error and success paths can converge on one
cleanup routine.
