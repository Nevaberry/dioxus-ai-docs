# Topology

Batch attribution: `3.5.0` and `3.6.0`.

## Compare TopoGeometry values explicitly

`TopoGeometry <> TopoGeometry` is ambiguous. Reproduce the former structural
comparison by testing every identifying component and the type:

```sql
id(tg1) <> id(tg2)
OR topology_id(tg1) <> topology_id(tg2)
OR layer_id(tg1) <> layer_id(tg2)
OR type(tg1) <> type(tg2)
```

Do not substitute geometry's explicit `<>` operator; it addresses geometry
inequality, not TopoGeometry overload ambiguity.

## Load geometry and share sequences

- Different topologies can share sequences.
- Use the new `postgis_topology` function `TopoGeo_LoadGeometry` to load
  geometry into a topology.

## Upgrade domains and identifiers

Topology domains can be upgraded. Functions formerly restricted to `integer`
identifiers were replaced by `bigint` forms that accept both `integer` and
`bigint` inputs. During extension upgrades, inspect dependent objects and
overload resolution instead of assuming the replacement is invisible.

## Repair corrupt TopoGeometry columns

Upgrading `postgis_topology` through 3.6.0 can corrupt existing TopoGeometry
columns. After installing a release containing the repair function, repair
every registered column:

```sql
SELECT topology.FixCorruptTopoGeometryColumn(
         schema_name, table_name, feature_column
       )
FROM topology.layer;
```

Use `topology.layer` as the registry so the repair covers every known feature
column.

## Inspect size and control precision

- Use `TotalTopologySize` to report the total size of a topology.
- Use `ValidateTopologyPrecision` to detect precision problems.
- Use `MakeTopologyPrecise` to repair or enforce topology precision.

Validate before repairing when the operational workflow needs an explicit
problem report or review boundary.

## Replace a topology during import

Pass `--drop-topology` to `pgtopo_import` when the import should remove an
existing target topology before loading the replacement.
