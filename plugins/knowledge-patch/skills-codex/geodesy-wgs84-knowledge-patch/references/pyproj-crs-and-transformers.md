# pyproj CRS and Transformers

## Contents

- [CF and coordinate-system export](#cf-and-coordinate-system-export)
- [Dimensional promotion](#dimensional-promotion)
- [Bound and compound CRS inspection](#bound-and-compound-crs-inspection)
- [Authority matching and serialization](#authority-matching-and-serialization)
- [Transformer construction and selection](#transformer-construction-and-selection)
- [Transformation execution](#transformation-execution)

## CF and coordinate-system export

`CRS.to_cf()` returns a CF 1.8 grid-mapping dictionary. `CRS.cs_to_cf()` returns a list of CF 1.8 coordinate-variable dictionaries for every coordinate system in the CRS. Keep grid mapping and axes separate.

Use `to_cf(errcheck=True)` to warn about ignored parameters. When rebuilding with `CRS.from_cf()`, pass `ellipsoidal_cs`, `cartesian_cs`, and `vertical_cs` as applicable so axis definitions are not treated as part of the grid mapping alone.

```python
from pyproj import CRS

crs = CRS.from_epsg(32632)
grid_mapping = crs.to_cf(errcheck=True)
coordinate_axes = crs.cs_to_cf()
rebuilt = CRS.from_cf(
    grid_mapping,
    ellipsoidal_cs=crs.geodetic_crs.coordinate_system,
    cartesian_cs=crs.coordinate_system,
)
```

## Dimensional promotion

`CRS.to_3d()` adds an upward ellipsoidal-height axis in metres. It does not attach an orthometric-height datum or geoid model. `to_3d()` is available since pyproj 3.1; `to_2d()` was added in pyproj 3.6 to remove the extra dimension where meaningful. Both accept an optional replacement name.

```python
horizontal_3d = CRS.from_epsg(4326).to_3d(name="WGS 84 3D")
horizontal_2d = horizontal_3d.to_2d()
```

## Bound and compound CRS inspection

For a bound CRS, `axis_info` and the geocentric, geographic, projected, and vertical predicates inspect its source CRS.

For a compound CRS, axes come from its components and the type predicates search those components. More than one predicate can be true. `utm_zone` likewise looks through projected, bound, and compound CRSs instead of only the top-level type.

```python
from pyproj.crs import CompoundCRS

compound = CompoundCRS(
    "WGS 84 plus EGM2008 height",
    [CRS.from_epsg(4326), CRS.from_epsg(3855)],
)
assert compound.is_geographic and compound.is_vertical
```

## Authority matching and serialization

### Authority matches

`to_authority()` and `to_epsg()` return the best database match at a default minimum confidence of 70. `list_authority()` returns all qualifying `AuthorityMatchInfo` records.

A bound CRS may have no direct authority match even when `source_crs` does. The source code identifies only that source CRS; the bound CRS remains unequal because it also includes a hub CRS and an operation.

```python
bound = CRS("+proj=geocent +datum=WGS84 +towgs84=0,0,0")
assert bound.to_epsg() is None
assert bound.source_crs.to_epsg() == 4978
assert bound != CRS.from_epsg(4978)
```

### Geographic constructor default

`GeographicCRS()` defaults its datum to `urn:ogc:def:ensemble:EPSG::6326`, the WGS 84 ensemble. Do not rely on that zero-argument default for a realization-specific WGS 84 CRS. Supply a datum accepted by `Datum.from_user_input()` and, when needed, an explicit ellipsoidal coordinate system.

```python
from pyproj.crs import GeographicCRS

wgs84_ensemble = GeographicCRS()
```

### Strings, WKT, and PROJJSON

`CRS.srs` reflects the string form of the construction input. `CRS.to_string()` first attempts an authority string and falls back to that input form. Neither is a canonical equivalence key.

Conversion to a PROJ string or parameter dictionary can lose CRS information. `to_wkt()` defaults to WKT2:2019. Since pyproj 3.6, `output_axis_rule=True` forces axis clauses on, `False` forces them off, and `None` leaves them format-dependent.

```python
wkt = crs.to_wkt(version="WKT2_2019", output_axis_rule=True)
projjson = crs.to_json_dict()
```

## Transformer construction and selection

### Authority filtering

With `Transformer.from_crs()`, omitting `authority` applies the `authority_to_authority_preference` restrictions associated with the source and target CRS authorities. Pass `authority="any"` to search without those restrictions, or a namespace such as `"EPSG"` to use operations from only that authority.

```python
from pyproj import Transformer

transformer = Transformer.from_crs(
    "EPSG:4269", "EPSG:3438", authority="EPSG", allow_ballpark=False
)
```

### `from_pipeline()` inputs

Despite its name, `Transformer.from_pipeline()` accepts all of the following:

- PROJ strings, WKT, and PROJJSON.
- Authority operation codes and URNs.
- Concatenated-operation URNs.
- Operation names.

Names need not be unique, so pyproj uses heuristics to choose a match. Use a code or URN when the exact operation matters.

```python
operation = Transformer.from_pipeline("EPSG:1671")
```

### Last-used operation

Since pyproj 3.4, `get_last_used_operation()` returns the operation used by the preceding transform call as another `Transformer`; it requires PROJ 9.1 or newer. Inspect it to learn the concrete runtime selection rather than relying only on the initial candidate description.

```python
transformer.transform(x, y, errcheck=True)
used = transformer.get_last_used_operation()
print(used.description)
```

### Supersession and thread safety

`TransformerGroup` excludes superseded operations by default. `allow_superseded=True` admits superseded operations but not deprecated ones. `CoordinateOperation` and `Transformer` objects returned by a group are not thread-safe; do not share them concurrently.

```python
from pyproj.transformer import TransformerGroup

group = TransformerGroup(source_crs, target_crs, allow_superseded=True)
```

## Transformation execution

### Error handling

Both `transform()` and `itransform()` default to `errcheck=False`, returning `inf` for transformation errors instead of raising. Set `errcheck=True` when failures must be explicit.

```python
x2, y2 = transformer.transform(x1, y1, errcheck=True)
```

### In-place arrays

`transform(..., inplace=True)` writes into input arrays only when they are C-order and double precision. Other layouts or data types fail rather than providing a general zero-copy path.

```python
import numpy

x = numpy.asarray(x, dtype=numpy.float64, order="C")
y = numpy.asarray(y, dtype=numpy.float64, order="C")
x2, y2 = transformer.transform(x, y, inplace=True, errcheck=True)
```

### Streamed time ordinate

`Transformer.itransform()` treats three-component points as `(x, y, z)` unless `time_3rd=True`; with that flag, the third component is time. Set it for lazy 3-tuples passed through a time-dependent operation.

```python
for x2, y2, epoch2 in transformer.itransform(
    points, time_3rd=True, errcheck=True
):
    ...
```
