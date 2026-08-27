# Language, Runtime, and Interoperability

## Swift concurrency and memory safety

### Core Data import annotations (26.0)

The iOS 26 SDK imports `NSManagedObject` as nonisolated and non-`Sendable`, and
`NSManagedObjectContext` as nonisolated and `Sendable`. The `perform` and
`performBlock` families take `Sendable` closures. A rebuild can therefore expose
new concurrency warnings.

Keep each managed object inside its context's scope. During testing, pass
`-com.apple.CoreData.ConcurrencyDebug 1` to detect context violations rather
than transferring managed objects across concurrency domains.

### `MutableSpan` inout parameters (26.0)

`MutableSpan` can be passed as an `inout` function parameter without enabling an
experimental feature.

## Objective-C concurrency diagnostics

### Nonatomic-property race sentinel (26.0)

A synthesized setter can briefly store `0x400000000000bad0` during a nonatomic
property mutation; the 32-bit watchOS sentinel is `0xbad0`. If a concurrent
reader crashes on that value, treat it as evidence of unsafe concurrent access
to the property, not as ordinary application data corruption.

## Swift modules and C++ interoperability

### Explicit modules default (26.0)

Xcode 26 enables Swift explicit modules by default for Swift targets. It excludes
targets using a language version earlier than Swift 5 and targets using Swift/C++
interoperability. For severe compatibility problems, temporarily set:

```text
SWIFT_ENABLE_EXPLICIT_MODULES=NO
```

Use the opt-out to isolate the incompatible module or dependency, then remove it
after fixing the underlying issue.

### Inherited shared-reference annotations (26.0)

Swift infers `SWIFT_SHARED_REFERENCE` for a C++ type when its base type already
has that annotation. Avoid duplicating the annotation solely to make the derived
type import with shared-reference semantics.

### Standard-library ABI edge cases (26.0)

Xcode 26 can change the layout of `std::unordered_map`, `std::unordered_set`,
their multi variants, and `std::deque` when an empty allocator shares a base
across rebound allocator types.

An enclosing type can also change layout when it contains a standard container
and the same empty allocator, comparator, or hasher as a `[[no_unique_address]]`
member or empty base. Rebuild and validate both sides of binary interfaces that
contain these shapes.

### Generic `std::char_traits` compatibility (18.5)

Xcode 16.4 restores the generic base `std::char_traits` template that Xcode 16.3
removed, allowing nonstandard types such as `std::basic_string<long long>` to
compile again. This is temporary compatibility: the generic base remains
deprecated and is planned for removal. Migrate nonstandard instantiations rather
than relying on the restoration indefinitely.

## C and POSIX APIs

### hvf availability checks (18.4)

Availability checking for hvf C APIs is disabled unless
`BUILD_FOR_APPLE_SDK` is defined before any hvf header:

```c
#define BUILD_FOR_APPLE_SDK 1
```

Put the definition ahead of every hvf include so declarations receive the
expected availability annotations.

### Public fileport calls (18.4)

`fileport_makeport(2)` and `fileport_makefd(2)` are public APIs and have manual
pages.

### Team-scoped named semaphores (26.0)

For processes signed with a Team ID entitlement, `sem_open` and `sem_unlink`
cannot observe named semaphores created by a different development team. Do not
use a shared semaphore name as cross-team IPC.

## Foundation formatting

### ISO-8601 fractional seconds (26.0)

`ISO8601FormatStyle` permits fractional seconds regardless of the value of its
`includingFractionalSeconds` setting. Parsers that must reject fractional
seconds need separate validation instead of depending on that setting alone.
