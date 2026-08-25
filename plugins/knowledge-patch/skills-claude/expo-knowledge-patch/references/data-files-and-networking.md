# Data, Files, and Networking

## File system

### Writes and transfers

Batch `55` adds append support to file-system writes.

Batch `56` expands transfers and picking:

- `File.downloadFileAsync()` supports progress reporting and `AbortSignal` cancellation.
- `copy` and `move` accept `overwrite`.
- `file.createUploadTask()` and `File.createDownloadTask()` create cancellable, resumable tasks.
- `File.upload()` handles a simple upload.
- `File.pickFileAsync()` accepts multiple files and MIME types.
- Experimental `File.watch()` and `Directory.watch()` subscribe to changes.

`File` and `Directory` `copy()` and `move()` are asynchronous and return promises. Await them:

```ts
await file.copy(destination);
await directory.move(destination);
```

When blocking behavior is intentional, use `copySync()` or `moveSync()`.

## Object-oriented data APIs

The `/next` variants of `expo-contacts`, `expo-media-library`, and `expo-calendar` first introduced object-oriented `SharedObject` APIs. These mutate objects directly instead of passing IDs and support richer queries.

The Calendar, Contacts, and MediaLibrary object APIs are stable in SDK 56. They add granular property loading and Builder-style queries; the original APIs are deprecated.

## SQLite and cryptography

### Parameterized SQL and inspection

`expo-sqlite` provides an on-device database inspector and an automatically parameterized tagged-template API:

```ts
const rows = await db.sql`SELECT * FROM users WHERE age > ${age}`;
```

Do not interpolate a hand-built SQL string when the tagged template can bind the value.

### Binary data and sessions

In SDK 56, `expo-sqlite` stores blobs with native `ArrayBuffer`, supports statement bind parameters, and adds session changesets.

`expo-crypto` adds AES-GCM in SDK 55.

## Server runtime

`expo-server` replaces `@expo/server` and provides server-runtime and hosting adapters. Expo Web's server-side rendering and data-loader APIs remain preview surfaces; validate deployment adapters against the selected rendering mode.

## Global fetch

`expo/fetch` supplies `globalThis.fetch` in SDK 56, so application code does not need to import it manually. To deliberately restore React Native fetch, set:

```sh
EXPO_PUBLIC_USE_RN_FETCH=1
```

On Android, Expo fetch decompresses Brotli, gzip, and zstd responses. It also implements `AbortSignal.timeout()` and `AbortSignal.any()` for timeout and composed cancellation.
