# Aggregation, queries, and search

## Geospatial index key generation

In 8.2, when a document contains both GeoJSON and legacy numeric coordinates, geospatial index
generation gives GeoJSON precedence. Rebuild affected indexes and verify queries when existing
index keys relied on legacy numeric coordinates appearing first.

## Server-time expression

`$currentDate` is an aggregation expression that returns the current time on the server:

```javascript
db.events.aggregate([
  { $project: { observedAt: { $currentDate: {} } } }
])
```

Use it when server time, rather than client-side timestamp construction, is required.

## Array accumulators

MongoDB 8.1 added `$concatArrays` and `$setUnion` as aggregation accumulators. They can collect
all arrays for a group or collect their distinct values directly:

```javascript
db.events.aggregate([
  {
    $group: {
      _id: "$tenant",
      all: { $concatArrays: "$values" },
      unique: { $setUnion: "$values" }
    }
  }
])
```

## Nullable and missing `$merge` keys

From 8.1, a field named by `$merge.on` may be missing or `null` when the supporting index is
non-sparse. A sparse supporting index does not enable this behavior. Check the index definition,
not only the pipeline, before relying on a nullable merge key.

## Cluster catalog aggregation

The 8.1 `$listClusterCatalog` stage exposes cluster catalog information through aggregation:

```javascript
db.aggregate([{ $listClusterCatalog: {} }])
```

This is a database-level aggregation, rather than a collection aggregation.

## Query-setting comments

`setQuerySettings` accepts comments from MongoDB 8.1 and 8.0.4. Attach an operational reason so
it remains associated with the query setting.

## Search explain and indexes on views

From 8.1, explain results include execution statistics for `$search`, `$searchMeta`, and
`$vectorSearch`.

Search-index create, update, drop, and list operations also work on standard views, provided the
view pipeline contains only these eligible transformations:

- `$addFields`;
- `$set`; or
- `$match` wrapping `$expr`.

An eligible view can then run the corresponding search stages. Do not assume an arbitrary view
pipeline supports search indexes.

## Trim expressions

Starting in 8.2.8, the `chars` string for `$trim`, `$ltrim`, and `$rtrim` has a 4096-character
limit. Reject or shorten a generated character set before executing the pipeline.
