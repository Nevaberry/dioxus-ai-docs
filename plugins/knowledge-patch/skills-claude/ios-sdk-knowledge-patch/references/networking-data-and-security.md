# Networking, Data, and Security

## HTTP loading and transport security

### New URLSession loading mode (18.4)

Set `usesClassicLoadingMode` to `false` to opt a configuration into the new HTTP
loading mode. It is planned to become the default in a future release.

```swift
let configuration = URLSessionConfiguration.default
configuration.usesClassicLoadingMode = false
let session = URLSession(configuration: configuration)
```

Test redirects, authentication, proxies, caching, uploads, and cancellation
before changing a shared session configuration.

### iOS 18.3 Simulator request recovery (18.5)

Xcode 16.4 fixes an iOS 18.3 Simulator runtime defect that caused
`NSURLSession` requests to time out and fail consistently. When reproducing that
specific failure, confirm both the Xcode version and selected Simulator runtime.

### TLS 1.2 default minimum (26.0)

For apps linked on or after iOS 26 or macOS 26, `URLSession` and Network
framework connections default to TLS 1.2 instead of TLS 1.0. Upgrade legacy
servers where possible. To make a deliberate transitional exception, configure
one of:

- `URLSessionConfiguration.tlsMinimumSupportedProtocolVersion`
- `sec_protocol_options_set_min_tls_protocol_version`

Keep the exception scoped and test the actual negotiated protocol.

### IKEv2 algorithm removals (26.0)

IKEv2 VPNs no longer support DES, 3DES, SHA1-96, SHA1-160, or Diffie-Hellman
groups below 14. Update both the client profile and VPN server; changing only one
side leaves negotiation incompatible.

## Core Data migration and isolation

### Removed ubiquity options (26.0)

Apps built with the iOS or macOS 26 SDK receive errors for these obsolete Core
Data options:

- `NSPersistentStoreUbiquitousContentNameKey`
- `NSPersistentStoreUbiquitousContentURLKey`
- `NSPersistentStoreUbiquitousPeerTokenOption`
- `NSPersistentStoreRemoveUbiquitousMetadataOption`
- `NSPersistentStoreUbiquitousContainerIdentifierKey`
- `NSPersistentStoreRebuildFromUbiquitousContentOption`

Older builds log warnings instead. Removing the options preserves the local
store but stops synchronization. Migrate synchronization to
`NSPersistentCloudKitContainer` or SwiftData.

### Concurrency-safe access (26.0)

The SDK's newer concurrency annotations make contexts transferable but not the
managed objects they contain. Keep `NSManagedObject` use scoped to its context's
`perform` work, and use `-com.apple.CoreData.ConcurrencyDebug 1` to diagnose
violations. See the language reference for the exact imported annotations.

## XML allocation

### libxml2 custom allocators are deprecated (18.4)

On iOS 18.4, replace the libxml2 allocation functions as follows:

| Deprecated call | Replacement |
| --- | --- |
| `xmlMalloc()`, `xmlMallocAtomic()` | `malloc()` |
| `xmlRealloc()` | `realloc()` |
| `xmlFree()` | `free()` |
| `xmlMemStrdup()` | `strdup()` |

Stop configuring allocators through `xmlMemSetup()`, `xmlMemGet()`,
`xmlGcMemSetup()`, `xmlGcMemGet()`, or their corresponding global variables.
libxml2 and libxslt now use the system allocator internally.

## GPU resource residency

### Metal 4 indirect command buffers (26.0)

When using Metal 4 command encoders, add render and compute pipelines that
support indirect command buffers to the residency set. Do this even though the
Metal driver does not currently enforce the requirement.
