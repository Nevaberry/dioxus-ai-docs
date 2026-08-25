# C++, Swift Interop, and Language Runtime Changes

## C and C++ Compatibility

### Enable hvf Availability Checks

For the iOS 18.4 SDK, hvf C API availability checking is disabled unless
`BUILD_FOR_APPLE_SDK` is defined before any hvf header is included:

```c
#define BUILD_FOR_APPLE_SDK 1
```

Define it consistently in translation units that consume the SDK's hvf headers.

### Replace Deprecated libxml2 Allocation APIs

The iOS 18.4 SDK deprecates libxml2's custom allocation API. Replace:

| Deprecated | System replacement |
| --- | --- |
| `xmlMalloc()`, `xmlMallocAtomic()` | `malloc()` |
| `xmlRealloc()` | `realloc()` |
| `xmlFree()` | `free()` |
| `xmlMemStrdup()` | `strdup()` |

Stop configuring allocators through `xmlMemSetup()`, `xmlMemGet()`,
`xmlGcMemSetup()`, `xmlGcMemGet()`, or corresponding globals. libxml2 and
libxslt now allocate internally with the system allocator.

### Treat Generic `std::char_traits` as Temporary Compatibility

Xcode 16.4, paired with the iOS 18.5 SDK, restores the base
`std::char_traits` template that Xcode 16.3 removed. Nonstandard types such as
`std::basic_string<long long>` compile again, but the base template remains
deprecated and is planned for removal. Migrate nonstandard instantiations rather
than relying on the restoration.

### Audit Standard-Library Container ABI

With Xcode 26 and the iOS 26.0 SDK, layouts can change for
`std::unordered_map`, `std::unordered_set`, their multi variants, and
`std::deque` when an empty allocator shares a base across rebound allocator
types. The layout of an enclosing type can also change when it contains a
standard container and the same empty allocator, comparator, or hasher as a
`[[no_unique_address]]` member or empty base.

Treat affected types as ABI-sensitive across separately built modules, rebuild
both sides of a binary boundary together, and do not assume serialized raw
layouts remain compatible.

## Swift and C++ Interop

### Pass `MutableSpan` as `inout`

`MutableSpan` can be used as an `inout` function parameter with the iOS 26.0
SDK without enabling an experimental feature.

### Inherit Shared-Reference Annotations

Swift now infers `SWIFT_SHARED_REFERENCE` for a C++ type when its base type
already carries that annotation. Avoid duplicating the annotation solely to
make a derived type import with shared-reference semantics.

## Objective-C Runtime Diagnostics

### Interpret the Nonatomic Mutation Sentinel

During a synthesized nonatomic-property setter, the runtime may briefly store
`0x400000000000bad0`; on 32-bit watchOS it uses `0xbad0`. If a concurrent
reader crashes on that sentinel after rebuilding with Xcode 26, the crash is
evidence of unsafe concurrent access to the nonatomic property, not an ordinary
application value.
