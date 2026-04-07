# pyproj Advanced Patterns

## UTM Zone Lookup

```python
from pyproj import CRS
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info

utm_list = query_utm_crs_info(
    datum_name="WGS 84",
    area_of_interest=AreaOfInterest(
        west_lon_degree=-93.58, south_lat_degree=42.03,
        east_lon_degree=-93.58, north_lat_degree=42.03,
    ),
)
utm_crs = CRS.from_epsg(utm_list[0].code)
```

## 3D CRS Promotion

Promote 2D CRS to 3D for proper height handling:

```python
from pyproj import CRS, Transformer

t = Transformer.from_crs(CRS("EPSG:4326").to_3d(), CRS("EPSG:2056").to_3d(), always_xy=True)
```

## TransformerGroup

Explore available transformations and check for missing grids:

```python
from pyproj.transformer import TransformerGroup

tg = TransformerGroup("EPSG:4326", "EPSG:2964")
tg.best_available                    # True if best transform is available
tg.unavailable_operations[0].grids   # missing grid files
```

## Pipeline and EPSG Operation Transforms

```python
from pyproj import Transformer

# From EPSG operation code
t = Transformer.from_pipeline("EPSG:1671")

# From PROJ pipeline string
t = Transformer.from_pipeline("+proj=pipeline +step +proj=cart ...")
```

## 4D Epoch Transforms

For time-dependent frame conversions (e.g., ITRF2014 → ETRF2014):

```python
t = Transformer.from_crs(7789, 8401)
t.transform(xx=3496737.27, yy=743254.45, zz=5264462.96, tt=2019.0)
```

## Geodesic Calculations

```python
from pyproj import Geod

geod = Geod(ellps="WGS84")
total_length = geod.line_length(lons, lats)               # metres
area, perim = geod.polygon_area_perimeter(lons, lats)     # m², m
```

### Shapely Integration

```python
geod.geometry_length(shapely_linestring)                   # metres
geod.geometry_area_perimeter(shapely_polygon)              # m², m
```
