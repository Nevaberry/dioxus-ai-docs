# Grid Traversal and Directed Edges

## Pentagon-safe hollow rings (since 4.3.0)

`gridRing` returns the hollow ring of cells at exactly grid distance `k` from
an origin. Unlike `gridRingUnsafe`, it remains usable when traversal encounters
pentagon distortion: it falls back to a more-memory-intensive algorithm.

```js
const ring = h3.gridRing("85283473fffffff", 1);
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

### C output allocation

Use `maxGridRingSize` to size a zeroed output array, then call
`gridRing(origin, k, out)`.

The maximum-sized allocation can be larger than the actual ring. Unused
entries can therefore remain zero; callers that iterate the entire allocation
must account for those entries.

## Bidirectional grid paths (since 4.5.0)

`gridPathCells` supports paths with its endpoints supplied in either
direction. Code does not need to normalize or reject the reverse ordering
solely to obtain a path.

## Directed-edge reversal (since 4.5.0)

`reverseDirectedEdge` preserves the pair of adjacent cells while swapping the
edge origin and destination.

```js
h3.reverseDirectedEdge("115283473fffffff");
// "115283477fffffff"
```

In C, the function returns an error if its input is not a valid directed edge:

```c
H3Error reverseDirectedEdge(H3Index edge, H3Index *out);
```

Binding names:

| Binding | API |
| --- | --- |
| JavaScript | `reverseDirectedEdge` |
| Java | `reverseDirectedEdge` |
| Python | `reverse_directed_edge` |
| Go | `edge.Reverse()` |
| DuckDB | `h3_reverse_directed_edge` |
| CLI | `h3 reverseDirectedEdge -e <edge>` |
