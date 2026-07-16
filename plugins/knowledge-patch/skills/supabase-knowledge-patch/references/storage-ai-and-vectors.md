# Storage, AI, and vectors

## S3 and object workflows

### S3 authentication modes

Preferred large-file endpoint: `https://<project-ref>.storage.supabase.co/storage/v1/s3`; it interoperates with REST and resumable objects. Generated S3 keys are server-only and bypass RLS across all buckets. To enforce user Storage RLS, use project ref as access-key ID, anon key as secret, and user JWT as AWS session token. Object versioning is unsupported.

```ts
const s3 = new S3Client({
  forcePathStyle: true, region,
  endpoint: `https://${projectRef}.storage.supabase.co/storage/v1/s3`,
  credentials: {
    accessKeyId: projectRef, secretAccessKey: anonKey,
    sessionToken: session.access_token,
  },
})
```

### Cross-bucket copies and moves

`copy()`/`move()` accept `destinationBucket`; limit is 5 GB and initiator becomes destination owner. Copy needs source `SELECT`, destination `INSERT`, plus `UPDATE` for upsert. Move needs `SELECT` and `UPDATE`.

```ts
await supabase.storage.from('avatars').copy(
  'public/a.png', 'archive/a.png', { destinationBucket: 'avatars-archive' },
)
```

### Signed resumable uploads

TUS should use direct Storage host, fixed 6 MB chunks, `/storage/v1/upload/resumable`. Upload URLs expire in 24h and permit one concurrent writer. `createSignedUploadUrl({ upsert })` supplies a token for `x-signature`; races are first-completion-wins normally, last-completion-wins under upsert.

### Storage file limits

Global upload maximum is 50 MB Free and 500 GB Pro/Team; Enterprise varies. Bucket limits and MIME restrictions can only narrow the global limit.

### New Storage error-code shape

Storage is moving to `{ code, message }` with PascalCase codes such as `NoSuchBucket`, `EntityTooLarge`, `ResourceAlreadyExists`, `DatabaseTimeout`, `ResourceLocked`, `SlowDown`. Legacy `httpStatusCode`/lowercase may coexist. JavaScript should inspect `error.error`, `message`, `status`, `statusCode`.

```json
{ "code": "NoSuchKey", "message": "The specified key does not exist" }
```

### Storage object inspection and V2 listing

Bucket scopes have `exists(path)` and `info(path)`; `info()` exposes size/type/timestamps and camel-case `lastModified`. Provisional `listV2()` separates metadata-rich `objects` from minimal `{ name, key? }` `folders`, returning `hasNext`/`nextCursor` for cursor pagination.

## Analytics buckets and Iceberg

### Analytics buckets and Iceberg

Private-alpha Analytics buckets store Iceberg tables: catalog metadata in REST Catalog and Parquet behind S3. Managed ETL into them was removed; bring ingestion or use managed Database Replication to BigQuery.

```ts
await supabase.storage.analytics.createBucket('analytics-data')
```

### Connecting Iceberg clients

Catalog bearer auth uses service key; data uses separate S3 keys and region. Bucket name is warehouse. PyIceberg, Spark, DuckDB use catalog `/storage/v1/iceberg` and data `/storage/v1/s3`.

```py
catalog = load_catalog(
    "supabase-analytics", type="rest", warehouse="analytics-data",
    uri=f"https://{project_ref}.supabase.co/storage/v1/iceberg",
    token=service_key,
    **{
        "py-io-impl": "pyiceberg.io.pyarrow.PyArrowFileIO",
        "s3.endpoint": f"https://{project_ref}.supabase.co/storage/v1/s3",
        "s3.access-key-id": s3_access_key,
        "s3.secret-access-key": s3_secret_key,
        "s3.region": region,
        "s3.force-virtual-addressing": False,
    },
)
```

### Querying Analytics buckets from Postgres

Dashboard **Query with Postgres** configures Iceberg FDW and foreign tables for ordinary SQL joins. Alpha defaults: 2 buckets/project, 10 namespaces/bucket, 10 tables/namespace. Usage is free during alpha; egress still bills.

### Analytics bucket JavaScript client

`supabase.storage.analytics` creates/deletes Iceberg buckets and lists only `ANALYTICS` buckets with limit/offset/sort options. Delete requires empty bucket.

### iceberg-js

`iceberg-js` is a minimal, platform-neutral JavaScript client for the Apache Iceberg REST Catalog API.

## Vector buckets

### Vector buckets and indexes

Alpha Vector buckets are S3-backed stores for large backend search. Prefer pgvector for low-latency prototypes/smaller user-facing data. Each index fixes immutable `float32` type, dimension, and `cosine`, `euclidean`, or `l2` distance metric.

```ts
await supabase.storage.vectors.createBucket('embeddings')
const bucket = supabase.storage.vectors.from('embeddings')
await bucket.createIndex({
  indexName: 'documents', dataType: 'float32', dimension: 1536,
  distanceMetric: 'cosine',
})
```

### Vector writes and similarity queries

`putVectors()` upserts keyed vectors with filterable metadata. `queryVectors()` takes a `float32` query, `topK`, filters, and return flags; lower distance is closer. Also use `getVectors()`, `deleteVectors()`, and continuation-token `listVectors()`.

```ts
const index = bucket.index('documents')
await index.putVectors({ vectors: [{
  key: 'doc-1', data: { float32: embedding },
  metadata: { category: 'guide', published: true },
}] })
const { data } = await index.queryVectors({
  queryVector: { float32: queryEmbedding }, topK: 5,
  filter: { category: 'guide', published: true },
  returnDistance: true, returnMetadata: true,
})
```

### SQL access to Vector buckets

S3 Vector Wrapper exposes `key`, `data` (`embd`), `metadata`; use only `data <==> query` for similarity and rank with `embd_distance(data)`.

```sql
select key, metadata, embd_distance(data) as distance
from s3_vectors.documents
where data <==> '[0.1, 0.2, 0.3]'::embd
order by embd_distance(data)
limit 5;
```

### Vector alpha limits

Defaults: 10 Vector buckets/project, 10 indexes/bucket, 4,096 dimensions. Limit insert/update operations to 500 vectors per batch; this is the conservative supported value while alpha source limits differ.

### Vector bucket JavaScript client

Use `supabase.storage.vectors` for buckets, `.from(bucket)` for indexes, `.index(index)` for `putVectors`, `getVectors`, `listVectors`, `deleteVectors`, `queryVectors`. Puts upsert keys; queries accept metadata filters and can return metadata/distance.

## Automatic embeddings and scaling

### Queue-backed automatic embedding updates

Use `pgmq`, `pg_cron`, `pg_net`, and a Function so remote inference never occurs in a write transaction. Row triggers enqueue row ID plus embedding contract; scheduled processing reads batches and deletes only after the embedding is stored.

Vault secret `project_url` holds hosted URL; local value is `http://api.supabase.internal:8000`. Invocation helper appends `/functions/v1/<name>` and reuses request Authorization when present.

The generic worker expects numeric PK `id`; content function accepts the row type and returns text. Create separate insert and `update of` triggers and keep update columns aligned with all content-function dependencies.

```sql
create extension if not exists pgmq;
create schema if not exists util;
select pgmq.create('embedding_jobs');

create trigger embed_documents_on_insert
after insert on documents for each row
execute function util.queue_embeddings('embedding_input', 'embedding');

create trigger embed_documents_on_update
after update of title, content on documents for each row
execute function util.queue_embeddings('embedding_input', 'embedding');

select cron.schedule('process-embeddings', '10 seconds',
  $$ select util.process_embeddings(); $$);
```

Stale vectors remain searchable until regeneration. If correctness outweighs coverage, a before-update trigger can null the embedding; the reusable `util.clear_column()` uses `hstore`.

### Embedding retries and failure tracing

Match `pgmq.read` visibility timeout to Function timeout, so failure reappears. The worker isolates batch jobs and returns 200 even with partial failures, with `x-completed-jobs`/`x-failed-jobs`. Inspect `net._http_response` and correlate `x-deno-execution-id` with logs.

```sql
select * from net._http_response
where (headers->>'x-failed-jobs')::int > 0;
```

### Independently scalable vector projects

Put large collections in separate projects for independent scaling. Query directly with Vecs when possible. If the primary DB must expose a remote collection through normal clients, attach with `postgres_fdw` and a foreign table.

```sql
create extension postgres_fdw;
create server docs_server foreign data wrapper postgres_fdw
  options (host 'db.example.supabase.co', port '5432', dbname 'postgres');
create user mapping for authenticated server docs_server
  options (user 'vector_reader', password '<password>');
```

### Python vector client boundary

Vecs fits data-science/ephemeral use and should get the Shared Pooler string. Production Python with versioned migrations should register pgvector through `pgvector-python` in Django, SQLAlchemy, SQLModel, psycopg, asyncpg, or Peewee.
