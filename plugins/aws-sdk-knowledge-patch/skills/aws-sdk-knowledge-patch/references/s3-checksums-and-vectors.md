# S3 Checksums and Vectors

## Default Checksums (Dec 2024)

SDKs now compute CRC checksums on every upload by default. S3 also computes server-side checksums on all uploads even without SDK support.

New algorithm: **CRC64NVME**.

Default algorithms vary by SDK:

| SDK | Default algorithm |
|---|---|
| CLI, C++, Rust | CRC64NVME |
| Go, Java, JS, Kotlin, .NET, PHP, Python, Ruby | CRC32 |

### Configuration

| Setting | Env var | Default |
|---|---|---|
| `request_checksum_calculation` | `AWS_REQUEST_CHECKSUM_CALCULATION` | `WHEN_SUPPORTED` |
| `response_checksum_validation` | `AWS_RESPONSE_CHECKSUM_VALIDATION` | `WHEN_SUPPORTED` |

### Multipart Full-Object Checksums

Multipart uploads now support `ChecksumType='FULL_OBJECT'` for a single whole-object checksum instead of per-part composite checksums:

```python
s3.create_multipart_upload(
    Bucket=bucket, Key=key,
    ChecksumAlgorithm='CRC64NVME',
    ChecksumType='FULL_OBJECT'
)
# At completion, pass the precomputed full-object checksum:
s3.complete_multipart_upload(
    Bucket=bucket, Key=key, UploadId=upload_id,
    ChecksumCRC64NVME=full_object_checksum,
    ChecksumType='FULL_OBJECT',
    MultipartUpload={'Parts': parts}
)
```

## S3 Vectors (GA Dec 2025)

New S3 service for storing and querying vector embeddings. Separate from regular S3 buckets.

### Create Vector Bucket and Index

```bash
aws s3vectors create-vector-bucket --vector-bucket-name my-vectors
aws s3vectors create-index \
    --vector-bucket-name my-vectors \
    --index-name my-index \
    --data-type float32 --dimension 1024 \
    --distance-metric cosine \
    --metadata-configuration "nonFilterableMetadataKeys=text_chunk"
```

### Query Vectors

```bash
aws s3vectors query-vectors \
    --index-arn "$INDEX_ARN" \
    --query-vector '{"float32": [...]}' \
    --top-k 10 --return-metadata --return-distance
```

### Limits and Features

- Up to 2B vectors per index
- 50 metadata keys per vector (10 non-filterable)
- Supports cosine and euclidean distance metrics
- Integrates with Bedrock Knowledge Bases and OpenSearch
