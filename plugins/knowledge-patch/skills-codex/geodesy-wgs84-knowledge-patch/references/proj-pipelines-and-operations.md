# PROJ Pipelines and Operation Selection

## Contents

- [Pipeline construction](#pipeline-construction)
- [Grid transformations](#grid-transformations)
- [Dynamic coordinates and metadata](#dynamic-coordinates-and-metadata)
- [Operation discovery and fallback](#operation-discovery-and-fallback)
- [Vertical and compound CRS behavior](#vertical-and-compound-crs-behavior)
- [Projection and factor capabilities](#projection-and-factor-capabilities)

## Pipeline construction

### Scope and validation

`+proj=pipeline` requires at least one `+step`. Parameters before the first step are global and copied into every step. Adjacent output and input units must match, and the pipeline must retain a usable forward path.

An inline `+proj=pipeline` cannot itself be a step. Reference the nested pipeline through an init file when nesting is required.

```text
+proj=pipeline +ellps=GRS80
+step +proj=merc
+step +proj=axisswap +order=2,1
```

### Direction-specific steps

`+inv` reverses one operation. `+omit_fwd` and `+omit_inv` skip a step only when the whole pipeline is evaluated in the named direction. Combine them with `push` and `pop` when a vertical correction needs temporary horizontal coordinates in the grid’s interpolation CRS while the original horizontal values must be restored in both directions.

```text
+proj=pipeline
+step +proj=unitconvert +xy_in=deg +xy_out=rad
+step +proj=push +v_1 +v_2
+step +proj=hgridshift +grids=nvhpgn.gsb +omit_inv
+step +proj=vgridshift +grids=g1999u05.gtx +multiplier=1
+step +inv +proj=hgridshift +grids=nvhpgn.gsb +omit_fwd
+step +proj=pop +v_1 +v_2
+step +proj=unitconvert +xy_in=rad +xy_out=deg
```

### Temporal units

`unitconvert` can convert the fourth coordinate through `t_in` and `t_out`. Bracket a time-dependent Helmert step that expects decimal years with GPS-week-to-decimal-year and reverse conversions instead of rewriting timestamps outside the pipeline.

```text
+proj=unitconvert +t_in=gps_week +t_out=decimalyear
```

## Grid transformations

### Geoid interpolation CRS and operation order

PROJ 9.1 added `+geoid_crs=horizontal_crs` and `+geoid_crs=WGS84` for `+geoidgrids`:

- With `horizontal_crs`, apply the vertical grid before a source-horizontal-datum shift to WGS 84.
- With `WGS84`, apply the horizontal shift first. This is also the default when omitted in PROJ 6 and newer.
- Before PROJ 6, omission implied the horizontal CRS.

Set the choice explicitly in portable definitions.

```text
+proj=longlat +ellps=GRS80 +nadgrids=foo.gsb +geoidgrids=bar.gtx \
  +geoid_crs=horizontal_crs +type=crs
```

### Ordered fallback

Comma-separated `+nadgrids` entries are tried in order; the first grid that contains the point wins even in overlaps. A missing file normally fails the transformation. Prefix an optional filename with `@` to continue the search. A final `null` grid provides a worldwide zero shift outside every real grid and suppresses the usual out-of-coverage error, so use it only deliberately.

```text
+nadgrids=@regional-highres.gsb,national.gsb,null
```

### Projected and specialized grid shifts

Since PROJ 9.4, `+proj=gridshift` can consume a grid referenced in a projected CRS and apply `easting_offset` and `northing_offset`. Do not treat its nodes or offsets as geographic angular values.

PROJ 7 added `+proj=xyzgridshift` for geocentric translations by grid interpolation. PROJ 7.2 added `+proj=tinshift` for triangulation-based transformations; PROJ 8.2 added a closest-triangle fallback for points outside all TIN triangles. PROJ 9.6 added EPSG JSON TIN methods for Cartesian grid offsets and vertical offsets.

PROJ 9.6 also maps EPSG “Vertical Offset by Grid Interpolation (asc)” to `vgridshift` and supports full-matrix coordinate-frame rotation methods for geocentric and geographic-2D coordinates.

## Dynamic coordinates and metadata

### Coordinate metadata and point motion

PROJ 9.2 added the WKT:2019 `COORDINATEMETADATA` construct, the ISO 19111 `CoordinateMetadata` class, and PROJJSON 0.6 support. PROJ 9.4 added `PointMotionOperation` transformations that change coordinate epoch, initially for Canadian NAD83(CSRS). Represent epoch as metadata when possible instead of only as an unlabeled fourth ordinate.

PROJ 9.5 added `proj_coordoperation_requires_per_coordinate_input_time()` and the `PROJ_ERR_COORD_TRANSFM_MISSING_TIME` error. PROJ 9.6 makes `projinfo` report whether an operation is time-dependent. PROJ 9.5.1 fixed static coordinate-frame Helmert operations being incorrectly classified as time-dependent.

### Deformation time behavior

Temporal horizontal and vertical grid shifts have existed since PROJ 5.1. For `deformation`, PROJ 5.2 evaluates a coordinate with no supplied time at `+t_epoch`. PROJ 6 removed `+t_obs` and replaced it with `+dt`. PROJ 7.1 added `+proj=defmodel` for multi-component time-based deformation models.

Omitting coordinate time can therefore intentionally or accidentally evaluate a model at its reference epoch.

### Bundled frame and geoid operations

PROJ 9.5 added `data/ITRF2020`, containing ITRF2020-to-other-frame transformations and ITRF2020 plate-motion models. PROJ 9.6 replicated the EGM2008 grid transformation record for named WGS 84 realizations and improved operation creation between ETRF realizations and between WGS 84 realizations.

## Operation discovery and fallback

### Authority CRSs versus legacy strings

From PROJ 6 onward, `cs2cs` transformations built from authority CRS identifiers use late binding and are not forced through WGS 84. Expanded legacy PROJ strings containing `+towgs84`, `+nadgrids`, or `+geoidgrids` generally preserve the older WGS-84-pivot behavior and can yield a different operation.

In the PROJ 4/5 framework, inverse horizontal grid correction applies the correction grid verbatim instead of solving its nonlinear inverse.

### Candidate fallback and strict selection

Since PROJ 6.3, `proj_trans()` may retry another candidate when the preferred operation fails for a coordinate. PROJ 9.2 added `ONLY_BEST=YES` and `cs2cs --only-best`. Strict mode fails when the preferred operation cannot be instantiated, including when its required grid is unavailable, rather than silently choosing a lesser operation.

Candidate controls include:

- `projinfo --hide-ballpark` since PROJ 7.1.
- `cs2cs --area`, `--bbox`, and `--authority` since PROJ 8.0.
- `projinfo --accuracy` since PROJ 8.0.

Set them explicitly when a workflow depends on a particular extent, authority, or accuracy.

### Longitude and celestial-body overrides

PROJ 9.0 added an option to `proj_create_crs_to_crs_from_pj()` that forces `+over` on generated operations; the operation property is `FORCE_OVER`. Use it when longitude continuity outside the usual wrap range is intentional.

PROJ 9.2 added `PROJ_IGNORE_CELESTIAL_BODY=YES`, which relaxes celestial-body matching so non-Earth ellipsoids can be matched across bodies. Enable it only for intentional planetary work; the normal check prevents nonsensical cross-body operations.

## Vertical and compound CRS behavior

### Vertical chains

The PROJ 9.8.1 operation factory can chain vertical transformations through an intermediate same-datum vertical CRS. For example, `EPSG:5705` Baltic 1977 height to `EPSG:5706` Caspian depth can route through Caspian height. Older versions may fail to find that chain.

PROJ 9.8.0 added Canadian vertical references for MTM with CGVD2013 and UTM with CGVD28 at epochs 1997, 2002, and 2010. Definitions requiring those exact horizontal/vertical/epoch combinations need the newer database records rather than an unqualified CGVD label.

### Ensemble null operations

Since PROJ 9.1, the database generates null transformations between a geodetic or vertical datum ensemble and its members. That zero operation reflects ensemble-selection behavior; it does not prove all member realizations are physically identical at every epoch.

### Two-dimensional targets

PROJ 9.1 stopped applying a vertical transformation from a compound source to a 2D target and added `cs2cs --3d` for a three-dimensional workflow. Do not expect a supplied height to transform merely because the source CRS is compound when the requested target is 2D.

### Compound input and WKT behavior

Since PROJ 7.1, `createFromUserInput()` accepts named compound CRSs such as `WGS 84 + EGM96 height`. Since PROJ 8.1, it also parses compound identifiers with different authorities, such as `ESRI:103668+EPSG:5703`.

The PROJ 9.7 WKT2 parser recognizes `DEFININGTRANSFORMATION` syntax but ignores its contents. Do not treat the node as proof that PROJ will instantiate or apply its embedded transformation.

## Projection and factor capabilities

### Exact auxiliary latitudes

PROJ 9.7.0 implemented uniform auxiliary-latitude conversions and changed `aea`, `cea`, `laea`, `eqearth`, `healpix`, and `rhealpix` to exact authalic-to-geographic latitude conversion. Results need not be bit-identical to PROJ 9.6 and earlier.

### Projection factors

Since PROJ 8.2, `proj_factors()` accepts a projected CRS rather than only a raw projection operation. PROJ 9.3 extended support to projected CRSs with non-metre units and northing/easting axis order. Do not pre-normalize such CRSs merely to obtain factors.

### Additional projection methods

- PROJ 9.4 added `+proj=mod_krovak` for the Modified Krovak method used by S-JTSK/05.
- PROJ 9.5 added Local Orthographic and an inverse for ISEA.
- PROJ 9.8 added the ellipsoidal Equidistant Cylindrical method identified as EPSG:1028.
