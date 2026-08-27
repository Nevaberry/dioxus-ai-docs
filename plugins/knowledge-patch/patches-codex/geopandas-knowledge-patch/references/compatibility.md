# Dependency Compatibility

## Runtime and core floors

GeoPandas 1.1.0 requires:

| Dependency | Minimum |
| --- | --- |
| Python | 3.10 |
| pandas | 2.0 |
| NumPy | 1.24 |
| pyproj | 3.5 |

Treat these as required installation constraints rather than optional test
targets.

## Tested optional floors

The minimum tested optional versions for GeoPandas 1.1.0 are:

| Optional dependency | Minimum tested version |
| --- | --- |
| Fiona | 1.8.21 |
| SciPy | 1.9 |
| matplotlib | 3.7 |
| mapclassify | 2.5 |
| folium | 0.12 |
| SQLAlchemy | 2.0 |

Older optional versions may work, but they are unsupported. Sparse boolean
output from `SpatialIndex.query` specifically requires SciPy.
