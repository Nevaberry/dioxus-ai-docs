# Storage, AI, and Vectors

Use this reference for Storage uploads and S3, Analytics and Vector buckets, embeddings, CDN behavior, and encryption integrations.

## Supabase JS compatibility (`supabase-js-2.101.0`)

### Storage Analytics and Vector clients
`storage-js` adds Analytics and Vector APIs; the Analytics surface is named `StorageAnalyticsClient`, and its `from()` method follows the `{ data, error }` convention. Vector query responses use `vectors` rather than `matches`.

### Storage listing, downloads, and errors
Bucket listing supports pagination and sorting, including sorting in list V2. Downloads expose fetch parameters, and `StorageError` exposes `status` and `statusCode`.

## Embedding generation and refresh

### Queue-backed automatic embedding updates
The guide's reusable pattern defines generic `util.queue_embeddings` and `util.process_embeddings` helpers: row triggers put `{ id, schema, table, contentFunction, embeddingColumn }` jobs onto a `pgmq` queue, then `pg_cron` and `pg_net` send claimed batches to an Edge Function. Set the queue visibility timeout to the function timeout; the worker can connect through the built-in `SUPABASE_DB_URL`, delete only successful jobs, and leave failed or interrupted jobs to become visible for retry.

```sql
select pgmq.create('embedding_jobs');

create trigger embed_documents_on_insert
  after insert on documents
  for each row
  execute function util.queue_embeddings('embedding_input', 'embedding');

select cron.schedule(
  'process-embeddings',
  '10 seconds',
  $$ select util.process_embeddings(); $$
);
```

### Avoiding stale embeddings during regeneration
The generic worker requires an `id` primary key and a row-to-text content function, while an update trigger must watch every column that function reads. Existing vectors remain queryable during asynchronous regeneration unless a nullable embedding column is cleared first with a `before` row trigger; the guide's generic `util.clear_column` helper requires `hstore`.

```sql
create trigger clear_document_embedding_on_update
  before update of title, content
  on documents
  for each row
  execute function util.clear_column('embedding');
```

### Built-in Edge Function embeddings
The Edge Runtime can generate embeddings without an external inference API through `Supabase.ai.Session`; its built-in surface currently supports only `gte-small`. Keep the session at module scope so requests reuse it, and enable mean pooling and normalization for sentence embeddings used with dot-product distance.

```ts
const session = new Supabase.ai.Session('gte-small')
const embedding = await session.run(input, {
  mean_pool: true,
  normalize: true,
})
```

## Storage, S3, Analytics, and Vector APIs

### Analytics buckets are Iceberg warehouses
Private-alpha Analytics buckets store Parquet data behind an S3-compatible endpoint while a separate Iceberg REST Catalog manages namespaces, tables, schemas, partitions, and snapshots. Alpha defaults allow two Analytics buckets per project, ten namespaces per bucket, and ten tables per namespace.

```ts
await supabase.storage.analytics.createBucket('analytics-data')
```

### Analytics connections require two credential sets
Iceberg clients authenticate catalog requests to `/storage/v1/iceberg` with the project service key and data requests to `/storage/v1/s3` with generated S3 credentials. PyIceberg, Spark, and DuckDB can use those two endpoints; Postgres can query and join the tables through the Iceberg Foreign Data Wrapper.

```sh
curl 'https://<project-ref>.supabase.co/storage/v1/iceberg/v1/config?warehouse=<bucket>' \
  -H 'Authorization: Bearer <service-key>'
```

### Vector indexes have an immutable schema
An alpha Vector bucket contains indexes whose dimension, distance metric, and data type cannot be changed after creation; only `float32` is currently supported, with `cosine`, `euclidean`, or `l2` distance and at most 4,096 dimensions. Defaults allow ten Vector buckets per project and ten indexes per bucket.

```ts
const bucket = supabase.storage.vectors.from('embeddings')
await bucket.createIndex({
  indexName: 'documents',
  dataType: 'float32',
  dimension: 1536,
  distanceMetric: 'cosine',
})
```

### Vector records and similarity queries
Each vector has a string key, `data.float32`, and optional filterable metadata. `putVectors()` replaces an existing key, while queries rank the lowest distance first and can filter metadata before returning neighbors.

```ts
const index = bucket.index('documents')
await index.putVectors({ vectors: [
  { key: 'doc-1', data: { float32: embedding }, metadata: { category: 'guide' } },
] })

const { data } = await index.queryVectors({
  queryVector: { float32: queryEmbedding },
  topK: 5,
  filter: { category: 'guide' },
  returnDistance: true,
  returnMetadata: true,
})
```

The examples and index-creation guide batch writes at a maximum of 500 vectors, while the alpha limits table separately lists 1,000 vectors per insert/update request; use 500 as the conservative client batch until that contract converges.

### Vector buckets through Postgres
The S3 Vector Wrapper exposes an index as a foreign table with `key`, `data`, and `metadata`. SQL similarity search uses the sole `<===>` search operator with the `embd` type, and `embd_distance(data)` exposes the computed distance.

```sql
select key, metadata, embd_distance(data) as distance
from s3_vectors.documents
where data <==> '[0.1, 0.2, 0.3]'::embd
order by distance
limit 5;
```

### RLS-scoped S3 session credentials
Generated S3 access keys are server-only credentials with full cross-bucket access that bypasses RLS. To scope an S3 client to a user, use the project reference as the access-key ID, the anon key as the secret, and the user's JWT as the session token; Storage validates the JWT and applies `storage` RLS.

```ts
const client = new S3Client({
  forcePathStyle: true,
  region,
  endpoint: `https://${projectRef}.storage.supabase.co/storage/v1/s3`,
  credentials: {
    accessKeyId: projectRef,
    secretAccessKey: anonKey,
    sessionToken: session.access_token,
  },
})
```

### S3 compatibility boundaries
Objects uploaded through S3, REST, or resumable uploads are interoperable, and S3 presigned query URLs use Signature V4 after S3 access is enabled. S3 versioning, lifecycle configuration, bucket CORS configuration, ACLs, object locking, and server-side-encryption controls are not supported; multipart uploads are automatically aborted after 24 hours.

### Resumable-upload contract
Supabase's TUS endpoint is `/storage/v1/upload/resumable`; large uploads should use the direct `*.storage.supabase.co` hostname and chunks of exactly `6 * 1024 * 1024` bytes. Each generated upload URL accepts `PATCH` requests for up to 24 hours and permits one concurrent writer; different URLs targeting one path are first-completion-wins, or last-completion-wins with `x-upsert: true`.

```ts
new tus.Upload(file, {
  endpoint: `https://${projectRef}.storage.supabase.co/storage/v1/upload/resumable`,
  chunkSize: 6 * 1024 * 1024,
  headers: { authorization: `Bearer ${accessToken}` },
  metadata: { bucketName, objectName, contentType },
})
```

A token from `createSignedUploadUrl(path, { upsert })` can authorize a resumable upload through the `x-signature` header.

### Cross-bucket copy and move
`copy()` and `move()` accept `destinationBucket` and are limited to objects up to 5 GB. A copy needs `SELECT` on the source and `INSERT` on the destination (`UPDATE` as well for upsert); a move needs `SELECT` and `UPDATE`, removes the source, and assigns the initiating user as owner of the destination object.

```ts
await supabase.storage.from('source').move('old/file.bin', 'new/file.bin', {
  destinationBucket: 'destination',
})
```

### Object ownership uses `owner_id`
New bucket and object ownership is derived from the JWT `sub` and stored in `owner_id`; the older `owner` field is deprecated. Resources created with a service key or through the Dashboard have no owner set, and ownership grants no access by itself—it must be enforced in RLS.

### New Storage error envelope
Storage is transitioning from the legacy `{ httpStatusCode, code, message }` body to `{ code, message }` with names such as `NoSuchKey`, `ResourceAlreadyExists`, `ResourceLocked`, `DatabaseTimeout`, and `SlowDown`. A `NoSuchBucket` or `NoSuchKey` response can also mean RLS hid an existing resource; lock failures use `423`, database timeouts `504`, and throttling `503`.

### Smart CDN invalidation does not clear browser caches
On Pro and above, Smart CDN invalidates changed or deleted objects—including transformed images—at edge nodes, but propagation can take up to 60 seconds. `cacheControl` governs the browser cache independently, so frequently replaced assets should use versioned paths and potentially shorter browser TTLs.

### Upload-size ceilings differ by path
The global file-size limit is at most 50 MB on Free and 500 GB on Pro or Team, and a per-bucket limit cannot exceed it. Standard uploads can accept up to 5 GB but are recommended only through 6 MB; paid S3 single-request and multipart uploads support up to 500 GB.

## JavaScript client behavior

### Storage metadata timestamp naming
`storage.from(bucket).info(path)` returns file size, content type, and timestamps. The Storage API field is `last_modified`, not `updated_at`, while the JavaScript client exposes it as `data.lastModified`.

## Platform capabilities

### JavaScript Iceberg catalog client
`iceberg-js` is a minimal vendor-neutral JavaScript client for the Apache Iceberg REST Catalog API.

## Platform capabilities (`1.26.08`)

### Searchable field-level encryption with CipherStash
The CipherStash integration adds field-level encryption with queryable ciphertext and zero-knowledge key management, without requiring schema changes.
