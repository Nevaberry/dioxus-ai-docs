# Data, Files, and Networking

## File and directory operations

File-system writes can append beginning with SDK 55.

In SDK 56, `File` and `Directory` `copy()` and `move()` become asynchronous and return promises. Await them:

```ts
await source.copy(destination);
await source.move(destination);
```

Use `copySync()` or `moveSync()` when synchronous execution is intentional. Copy and move operations also accept `overwrite`.

## Downloads, uploads, and picking

`File.downloadFileAsync()` supports progress reporting and cancellation through `AbortSignal`.

For cancellable, resumable transfers, use `file.createUploadTask()` or `File.createDownloadTask()`. Use `File.upload()` for a simple upload that does not need task lifecycle management.

`File.pickFileAsync()` accepts multiple selections and MIME-type filters.

## File-system watching

Experimental `File.watch()` and `Directory.watch()` subscribe to changes. Treat them as preview APIs.

## SQLite

SDK 55 adds an on-device database inspector and an automatically parameterized tagged-template query API:

```ts
const rows = await db.sql`SELECT * FROM users WHERE age > ${age}`;
```

The interpolation is parameterized rather than inserted into the SQL string.

SDK 56 stores blobs with native `ArrayBuffer` values and adds statement bind parameters and session changesets.

## Object-oriented data modules

The `/next` variants of `expo-contacts`, `expo-media-library`, and `expo-calendar` are previews in SDK 55. Their `SharedObject` APIs mutate objects directly instead of passing IDs and provide richer queries.

In SDK 56, the object-oriented Calendar, Contacts, and MediaLibrary APIs are stable. They support granular property loading and Builder-style queries. The original APIs are deprecated; plan migrations around the stable object models.

## Global fetch behavior

SDK 56 makes `expo/fetch` the provider of `globalThis.fetch`; importing `expo/fetch` manually is unnecessary. Set:

```sh
EXPO_PUBLIC_USE_RN_FETCH=1
```

only when deliberately restoring the React Native fetch implementation.

On Android, responses support Brotli, gzip, and zstd decompression. The implementation also supports `AbortSignal.timeout()` and `AbortSignal.any()` for timeout and combined-cancellation policies.

## Server runtime adapters

`expo-server` replaces `@expo/server` in SDK 55 and provides server-runtime and hosting adapters. Update imports when adopting the replacement package.

## Cryptography

`expo-crypto` adds AES-GCM support in SDK 55.
