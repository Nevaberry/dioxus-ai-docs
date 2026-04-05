# Storage

## Vector Buckets (Alpha)

Supabase Storage now has specialized vector buckets for storing, indexing, and querying embeddings with similarity search. Accessed via `supabase.storage.vectors` namespace.

**Create bucket and index:**

```typescript
// Create a vector bucket
await supabase.storage.vectors.createBucket('embeddings');

// Create an index (dimension must match your embedding model)
const bucket = supabase.storage.vectors.from('embeddings');
await bucket.createIndex({
  indexName: 'documents-openai',
  dataType: 'float32',
  dimension: 1536,
  distanceMetric: 'cosine', // 'cosine' | 'euclidean' | 'l2' — immutable after creation
});
```

**Store vectors:**

```typescript
const index = supabase.storage.vectors.from('embeddings').index('documents-openai')

await index.putVectors({
  vectors: [
    {
      key: 'doc-1',
      data: { float32: [0.1, 0.2, 0.3 /* ... */] },
      metadata: { title: 'My Document', category: 'docs' },
    },
  ],
})
```

**Similarity search with metadata filtering:**

```typescript
const { data } = await index.queryVectors({
  queryVector: { float32: queryEmbedding },
  topK: 10,
  filter: { category: 'electronics', price: { $lte: 500 } },
  returnDistance: true,
  returnMetadata: true,
});
// data.vectors[].key, .distance, .metadata
```

**Other operations:** `getVectors({ keys })`, `listVectors({ maxResults, nextToken })`, `deleteVectors({ keys })`. Manage indexes with `listIndexes()`, `getIndex(name)`, `deleteIndex(name)`.

**SQL access via S3 Vector Wrapper** — query vector buckets from Postgres using the `<===>` distance operator and `embd_distance()` function:

```sql
SELECT key, metadata->>'title', embd_distance(data) as distance
FROM s3_vectors.documents_openai
WHERE data <==> '[0.1, 0.2, ...]'::embd
ORDER BY embd_distance(data) ASC
LIMIT 5;
```

Supports JOINs with relational tables for hybrid search. Limits: max 4096 dimensions, 1000 vectors per batch, 10 indexes per bucket, 10 buckets per project.

## Analytics Buckets (Alpha)

Store large datasets for analytics using Apache Iceberg table format, separate from your transactional Postgres database. Analytics buckets are S3-backed and designed for data warehousing, historical archiving, and complex aggregations.

Query from Postgres via the Iceberg Foreign Data Wrapper:

```sql
-- After connecting via Dashboard (Analytics Bucket -> Query with Postgres)
SELECT
  event_id,
  event_name,
  event_timestamp
FROM
  analytics.events
ORDER BY
  event_timestamp DESC
LIMIT
  1000;

-- Joins with transactional data work
SELECT
  e.event_id,
  u.user_email
FROM
  analytics.events e
  JOIN public.users u ON e.user_id = u.id;
```

Also queryable via DuckDB, Apache Spark, and PyIceberg using S3 credentials. Limits: 2 buckets/project, 10 namespaces/bucket, 10 tables/namespace.
