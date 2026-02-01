# S3 Storage (`Bun.s3`)

Native S3 support using the same API as `Bun.file()`. Works with any S3-compatible storage (AWS, R2, GCS).

## Basic Operations

```ts
import { s3, S3Client } from "bun";

// Read/write files (same API as Bun.file)
const file = s3.file("folder/my-file.txt");
const content = await file.text(); // or .json(), .arrayBuffer(), .stream()
await file.write("hello s3!");

// Multi-part upload for large files
const writer = file.writer();
writer.write(chunk);
await writer.end();
```

## Presigned URLs

```ts
const url = s3.presign("folder/file.txt", { expiresIn: 3600 });
```

## S3 Protocol

```ts
await fetch("s3://bucket/file.txt", { method: "PUT", body: "data" });
```

## Custom Client

```ts
const client = new S3Client({
  accessKeyId: "...",
  secretAccessKey: "...",
  endpoint: "https://account.r2.cloudflarestorage.com",
  bucket: "my-bucket",
  virtualHostedStyle: true, // https://bucket.s3.region.amazonaws.com
});
```

## Bucket Listing

```ts
const result = await client.list({
  bucket: "my-bucket",
  prefix: "uploads/",
  maxKeys: 100,
});

for (const item of result.contents || []) {
  console.log(`Key: ${item.key}, Size: ${item.size}`);
}

// Pagination
const nextPage = await client.list({
  bucket: "my-bucket",
  continuationToken: result.nextContinuationToken,
});
```

## Upload Options

```ts
// Storage class
await s3.file("archive.zip").write(data, { storageClass: "GLACIER" });

// Content-Disposition (download behavior)
const file = s3.file("report.pdf", {
  contentDisposition: 'attachment; filename="quarterly-report.pdf"',
});

// Content-Encoding
await s3.file("data.json.gz").write(compressed, { contentEncoding: "gzip" });

// Requester Pays
await s3.file("file.txt").write(data, { requesterPays: true });
```
