# C, Objective-C, and C++ interoperation

Interop additions from batches `6.1`, `6.2-approachable-concurrency`, `6.2-language`, `6.2-interop-and-testing`, and `6.3-embedded-and-c`.

## Contents

- [Implement imported declarations in Swift](#implement-imported-declarations-in-swift)
- [Strict C++ memory-safety contracts](#strict-c-memory-safety-contracts)
- [Experimental safe wrappers](#experimental-safe-wrappers)
- [Bounds-annotated pointers](#bounds-annotated-pointers)
- [C ABI declarations](#c-abi-declarations)
- [C modules and synthesized interfaces](#c-modules-and-synthesized-interfaces)
- [API notes](#api-notes)

## Implement imported declarations in Swift

### Objective-C types

Since 6.1, combine `@implementation` with `@objc` on a Swift extension to implement a type declared in an Objective-C header. This replaces the need for an Objective-C `@implementation` block and allows an existing class to move to Swift one category at a time without breaking compatibility.

```swift
@objc @implementation
extension LegacyController {
    // Implement declarations from the Objective-C header.
}
```

### Imported async and completion-handler APIs

Objective-C methods transformed by the import-as-async heuristic import as `nonisolated(nonsending)`, preserving caller-actor execution. Imported completion-handler parameters are `@Sendable` by default unless the Objective-C declaration requests otherwise. See [concurrency.md](concurrency.md) for executor and sendability implications.

## Strict C++ memory-safety contracts

### Type escapability

Under strict memory-safety checking, unannotated foreign types other than known-safe numeric, standard-library, and aggregate types are unsafe. Annotate a lifetime-dependent view `SWIFT_NONESCAPABLE`, an independent owner `SWIFT_ESCAPABLE`, and a template `SWIFT_ESCAPABLE_IF(T, ...)` when escapability depends on its arguments. API notes can express the same property with `SwiftEscapable`.

```cpp
struct SWIFT_NONESCAPABLE StringRef { /* borrowed pointer and length */ };
template<class T> struct SWIFT_ESCAPABLE_IF(T) Box { T value; };
```

For compatibility, an unannotated type still imports as `Escapable` even when strict mode warns about it.

### Lifetime dependencies

Every non-escapable parameter and result needs a lifetime annotation for an imported API to be safe:

- Put `__lifetimebound` on a parameter when a result or constructed value depends on it.
- Put `__lifetimebound` after a method signature when the result depends on `this`.
- Use `SWIFT_RETURNS_INDEPENDENT_VALUE` when the result uses static storage or no backing storage.
- Use `__lifetime_capture_by(destination)` when an output, global, or `this` captures an input's dependencies.
- Use `__noescape` when an input is not retained.

```cpp
StringRef fileName(const std::string &path __lifetimebound);
StringRef emptyRef() SWIFT_RETURNS_INDEPENDENT_VALUE;
```

An imported contract remains unsafe in Swift if these annotations cannot express its actual lifetime behavior.

## Experimental safe wrappers

Pass `-enable-experimental-feature SafeInteropWrappers` to generate an additional safe overload for suitably annotated C and C++ APIs.

- A top-level `std::span<const T>` bridges to `Span<T>`.
- A top-level mutable `std::span<T>` bridges to `MutableSpan<T>`.
- Lifetime-bound results carry Swift `@lifetime`.
- Nested spans are not transformed.

```cpp
void inspect(std::span<const int> values __noescape);
// Swift overload: func inspect(_ values: Span<CInt>)
```

## Bounds-annotated pointers

Annotate a pointer with `__counted_by(len)` for an element count or `__sized_by(bytes)` for a byte count. The byte-sized form maps unsized storage to `RawSpan`.

```cpp
int calculate_sum(const int * __counted_by(len) values __noescape, int len);
// Swift overload: func calculate_sum(_ values: Span<CInt>) -> CInt
```

When combined with `__noescape` or `__lifetimebound`, generated overloads use `Span` or `MutableSpan`, omit a recoverable count parameter, and check shared or arithmetic count relationships at the interop boundary.

Without a lifetime annotation, a bounds-annotated pointer instead gains an `UnsafeBufferPointer` overload. Its generated boundary checks still execute in release builds, but it does not provide lifetime safety. Add bounds and lifetime contracts together: adding annotations later can change the one generated safe overload's signature. Bounds can also be specified in API notes.

The bounds transformation has these limits in Swift 6.2:

- It handles only outermost pointers in parameters and results.
- It does not transform globals, fields, or Objective-C method signatures.
- Wrapper generation does not yet account for `__lifetime_capture_by`.
- C code receives bounds enforcement only when compiled with `-fbounds-safety`; otherwise enforcement occurs at the Swift boundary only.

## C ABI declarations

### `@c`

Since 6.3, `@c(name)` is the supported replacement for `@_cdecl`. It defines C-compatible functions and enums and emits declarations into Swift's generated C header.

```swift
@c(MyLib_initialize)
public func initialize() { }
```

When a C header already declares the interface, combine `@c` with `@implementation`. The compiler checks the Swift definition against the C declaration while retaining the C symbol name and compatibility for existing C clients.

```swift
@c @implementation
public func MyLib_initialize() { }
```

### Separate Swift and C views

The imported and Swift-declared views of one C function no longer need to agree on Swift-only metadata such as pointer nullability or sendability. The compiler still diagnoses incompatible underlying C declarations. For example, a Swift implementation can accept a nonnull `UnsafePointer<T>` when the header left pointer nullability unspecified.

## C modules and synthesized interfaces

Place `module.modulemap` beside a C header to make the module importable. In a Swift package, place both under the C target's `include` directory.

```text
module WebGPU {
  header "webgpu.h"
  export *
}
```

Swift 6.2 and later provide `swift-synthesize-interface` to show the exact Swift API imported from the C module.

```sh
swift-synthesize-interface -I . -module-name WebGPU -target <target-triple>
```

On macOS, invoke it through `xcrun` and pass the SDK path as well.

## API notes

Place a YAML file named after the module, such as `WebGPU.apinotes`, beside its module map to adjust the Swift projection without changing the C header.

### Enum projection

`EnumExtensibility: closed` turns a conservatively imported C enum wrapper and its global constants into a Swift enum with cases.

```yaml
---
Name: WebGPU
Tags:
- Name: WGPUAdapterType
  EnumExtensibility: closed
```

### ARC-managed handles

For a C handle with retain and release functions, use `SWIFT_SHARED_REFERENCE(retainFn, releaseFn)` from `<swift/bridging>` to import its pointee as an ARC-managed Swift class. Mark owned results `SWIFT_RETURNS_RETAINED`.

The API-notes equivalents specify reference import, retain and release operations, and ownership of each returning function:

```yaml
Tags:
- Name: WGPUBindGroupImpl
  SwiftImportAs: reference
  SwiftRetainOp: wgpuBindGroupAddRef
  SwiftReleaseOp: wgpuBindGroupRelease
Functions:
- Name: wgpuDeviceCreateBindGroup
  SwiftReturnOwnership: retained
```

### Projecting functions as members

Use `SWIFT_NAME` in a header or `SwiftName` under API-notes `Functions` to add labels and project a free function onto a reference type. Put `self` at the C receiver parameter's position. Prefix the name with `getter:` for a read-only property, or use `.init(...)` for a factory initializer.

```yaml
Functions:
- Name: wgpuQueueWriteBuffer
  SwiftName: WGPUQueueImpl.writeBuffer(self:buffer:bufferOffset:data:size:)
- Name: wgpuQuerySetGetCount
  SwiftName: getter:WGPUQuerySetImpl.count(self:)
- Name: wgpuCreateInstance
  SwiftReturnOwnership: retained
  SwiftName: WGPUInstanceImpl.init(descriptor:)
```

### Strong typedefs and option sets

Set `SwiftWrapper: struct` to import an integer typedef as its own `RawRepresentable` struct rather than a type alias. Add `SwiftConformsTo: Swift.OptionSet` for a flag typedef. Rename associated C constants through `Globals` to obtain normal option-set syntax such as `[.mapRead, .mapWrite]`.

```yaml
Typedefs:
- Name: WGPUBufferUsage
  SwiftWrapper: struct
  SwiftConformsTo: Swift.OptionSet
Globals:
- Name: WGPUBufferUsage_MapRead
  SwiftName: WGPUBufferUsage.mapRead
- Name: WGPUBufferUsage_MapWrite
  SwiftName: WGPUBufferUsage.mapWrite
```

Use the same wrapper technique to give a library-specific integer Boolean its own identity. Add a small Swift extension conforming it to `ExpressibleByBooleanLiteral` when `true` and `false` should construct raw zero-or-one values.

### Nullability overlays

Overlay parameter nullability by zero-based position: `O` imports as optional (`_Nullable`), `N` as non-optional (`_Nonnull`), and `U` as implicitly unwrapped optional (`_Null_unspecified`). Express result nullability in `ResultType`.

```yaml
Functions:
- Name: wgpuCreateInstance
  Parameters:
  - Position: 0
    Nullability: O
  ResultType: "WGPUInstance _Nonnull"
```
