# Storage

## Vector Buckets (Alpha)

New bucket type for storing and querying vector embeddings at scale via `supabase.storage.vectors`. Alternative to pgvector — built on S3 storage, optimized for large-scale similarity search rather than low-latency transactional queries.

Create a vector bucket and index:

```typescript
// Create bucket
await supabase.storage.vectors.createBucket('embeddings');

// Create index (dimension must match your embedding model)
const bucket = supabase.storage.vectors.from('embeddings');
await bucket.createIndex({
  indexName: 'documents-openai',
  dataType: 'float32',
  dimension: 1536,
  distanceMetric: 'cosine', // 'cosine' | 'euclidean' | 'l2'
});
```

Store vectors with metadata:

```typescript
const index = supabase.storage.vectors.from('embeddings').index('documents-openai')

await index.putVectors({
  vectors: [
    {
      key: 'doc-1',
      data: { float32: [0.1, 0.2, 0.3 /* ... */] },
      metadata: { title: 'My Document', category: 'guide' },
    },
  ],
})
```

Query with similarity search and metadata filtering:

```typescript
const { data } = await index.queryVectors({
  queryVector: { float32: queryEmbedding },
  topK: 10,
  filter: {
    category: 'guide',
    price: { $lte: 500 },
  },
  returnDistance: true,
  returnMetadata: true,
});

// Results ranked by similarity (lowest distance = most similar)
data.vectors.forEach((v) => console.log(v.key, v.distance, v.metadata));
```

Other index operations:

```typescript
await index.getVectors({ keys: ['doc-1', 'doc-2'], returnMetadata: true });
await index.listVectors({ maxResults: 100, nextToken });
await index.deleteVectors({ keys: ['doc-1'] });
await bucket.listIndexes();
await bucket.deleteIndex('documents-openai');
```

**SQL access via S3 Vector Wrapper FDW** — query vector buckets from Postgres using the `<===>` distance operator and `embd_distance()` function:

```sql
SELECT key, metadata->>'title', embd_distance(data) as distance
FROM s3_vectors.documents_openai
WHERE data <==> '[0.1, 0.2, ...]'::embd
ORDER BY embd_distance(data) ASC
LIMIT 5;
```

Limits (alpha): max 10 buckets/project, 10 indexes/bucket, 4096 dimensions, 1000 vectors/batch.

## Analytics Buckets (Alpha)

New bucket type for large-scale analytical workloads using Apache Iceberg table format. Separates analytical queries from the transactional Postgres database.

Create analytics buckets via Dashboard or SDK. Populate with your own ingestion pipeline (ETL via Supabase is no longer supported). Query from Postgres via the Iceberg Foreign Data Wrapper:

```sql
-- After connecting via Dashboard (Analytics Bucket → Query with Postgres)
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

-- Join analytics data with transactional tables
SELECT
  e.event_name,
  u.user_email
FROM
  analytics.events e
  JOIN public.users u ON e.user_id = u.id
WHERE
  e.event_timestamp > NOW() - INTERVAL '7 days';
```

Also queryable externally via DuckDB, PyIceberg, or Apache Spark using S3 credentials from project settings.

Limits (alpha): 2 analytics buckets/project, 10 namespaces/bucket, 10 tables/namespace.
