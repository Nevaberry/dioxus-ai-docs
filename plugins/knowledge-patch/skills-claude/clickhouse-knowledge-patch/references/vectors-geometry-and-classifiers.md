# Vectors, geometry, and classifiers

Use this reference for quantized vector storage and search, embedding generation, geometry intersections, vector tiles, and dictionary-backed Naive Bayes classification.

## QBit storage

### Int8 vectors

`QBit` accepts `Int8` elements for quantized vector storage. These columns can be searched with the transposed `L2Distance` and cosine-distance functions. Keep the quantization scheme consistent between stored values and query vectors.

### Strided dimensions

```text
QBit(T, dimension, stride)
```

The strided form stores dimension groups in separate streams. Transposed distance functions accept `used_dims` as a fourth argument so a search can read only an initial dimension subset. This supports coarse-to-fine pipelines in which a smaller prefix prunes candidates before a fuller comparison.

`used_dims` selects an initial subset, not an arbitrary mask. Design the transform and dimension order so early dimensions provide useful discrimination.

## Transposed and quantized distance functions

### Approximate inner products

`dotProductTransposed`, also named `scalarProductTransposed`, computes an approximate inner product between a `QBit` column and a reference vector.

For Lloyd-Max codes produced by `quantizeBFloat16ToInt8`, these functions operate on `QBit(Int8)` and dequantize stored codes during comparison:

- `cosineDistanceTransposedQuantized`
- `L2DistanceTransposedQuantized`
- `dotProductTransposedQuantized`

The quantized functions trade precision for storage and scan efficiency. Measure recall against an unquantized or reranked reference path for the target data distribution.

### Decode individual components

`dequantizeInt8ToBFloat16(code)` converts one `Int8` scalar code back to a `BFloat16` embedding component:

```sql
SELECT dequantizeInt8ToBFloat16(107::Int8);
```

This helper decodes the scalar representation; it does not by itself reconstruct a complete vector pipeline or restore information lost during quantization.

## Randomized Hadamard transforms

`randomHadamardTransform(vector[, seed[, output_dims]])` applies a deterministic, norm-preserving float-vector rotation. A fixed seed produces a repeatable transform. Supplying `output_dims` truncates the rotated output to perform a random projection before quantization.

Store or otherwise stabilize the chosen seed and output dimension with the data pipeline. Query vectors must undergo the compatible transform before comparison with transformed stored vectors.

## Experimental embedding generation

`aiEmbed(text)` calls an embedding endpoint configured through a named collection. The collection supplies these fields:

```text
provider = 'openai'
endpoint = '...'
model = '...'
api_key = '...'
```

Enable the feature and select the credential collection explicitly:

```sql
SET allow_experimental_ai_functions = 1;
SET ai_function_credentials = 'embedding_credentials';

SELECT aiEmbed('text to embed');
```

Keep the API key server-side, restrict access to the collection, and account for remote latency, rate limits, cost, and non-deterministic service availability in query design.

## Naive Bayes dictionaries

`naiveBayesClassifier` assets must be recreated as dictionaries using the `NAIVE_BAYES` layout. Populate them from pre-aggregated per-class n-gram counts. XML configuration that points to serialized `.bin` files is unsupported.

The related helpers are:

- `naiveBayesNgrams` for n-gram preparation;
- `naiveBayesClassifierWithProb` for a classification with its probability;
- `naiveBayesClassifierWithAllProbs` for probabilities across classes.

Plan the migration as data reconstruction, not as a path rewrite from the old binary file, because the supported representation and loading mechanism changed.

## Geometry intersections

`geometryIntersectCartesian` and `geometryIntersectSpherical` accept any supported geometry type, including the generic `Geometry` type. The two arguments may have different concrete geometry types.

Choose Cartesian or spherical semantics based on the coordinate domain. The wider type acceptance does not make Cartesian operations appropriate for longitude/latitude data.

## Mapbox Vector Tiles

Three functions form the core tile pipeline:

- `MVTBoundingBox(z, x, y)` returns geographic bounds for filtering source data.
- `MVTEncodeGeom` projects longitude/latitude geometry into tile pixel space.
- `MVTEncode` aggregates encoded geometries into a binary vector tile.

Point, line, and polygon geometry are supported. Filter by the tile bounds before encoding, then return the aggregate as binary output rather than displaying it directly in a terminal.
