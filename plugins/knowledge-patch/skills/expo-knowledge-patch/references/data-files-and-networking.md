# Data, Files, and Networking

## Transfer and watch files

SDK 55 file-system writes can append data.

SDK 56 expands the object API:

- `File.downloadFileAsync()` reports progress and accepts an `AbortSignal`.
- File and directory copy/move operations accept `overwrite`.
- `file.createUploadTask()` and `File.createDownloadTask()` create cancellable, resumable transfer tasks.
- `File.upload()` handles simple uploads.
- `File.pickFileAsync()` accepts multiple files and MIME types.
- Experimental `File.watch()` and `Directory.watch()` subscribe to changes.

`File` and `Directory` `copy()` and `move()` are asynchronous and return promises. Await them. Use `copySync()` or `moveSync()` only when synchronous I/O is intentional.

## Query and inspect SQLite

SDK 55 adds an on-device database inspector and an automatically parameterized tagged-template API:

```ts
const rows = await db.sql`SELECT * FROM users WHERE age > ${age}`;
```

Use interpolation rather than constructing SQL text manually. In SDK 56, `expo-sqlite` uses native `ArrayBuffer` blobs and adds statement bind parameters and session changesets.

## Adopt stable object APIs

The `/next` variants of `expo-contacts`, `expo-media-library`, and `expo-calendar` preview object-oriented SharedObject APIs in SDK 55. They mutate objects directly rather than passing IDs and provide richer queries.

In SDK 56, the object-oriented Calendar, Contacts, and MediaLibrary APIs are stable. They support granular property loading and Builder-style queries; the original APIs are deprecated.

## Use the global Expo fetch

`expo/fetch` supplies `globalThis.fetch` in SDK 56, so application code does not need a manual import. Restore the React Native implementation only when required:

```sh
EXPO_PUBLIC_USE_RN_FETCH=1
```

On Android, Expo fetch can decompress Brotli, gzip, and zstd responses. It also supports `AbortSignal.timeout()` and `AbortSignal.any()`.

## Host Expo server code

`expo-server` replaces `@expo/server` in SDK 55. It provides server-runtime and hosting adapters; update package imports rather than keeping the old package name.

## Encrypt with Expo Crypto

`expo-crypto` adds AES-GCM support in SDK 55.
