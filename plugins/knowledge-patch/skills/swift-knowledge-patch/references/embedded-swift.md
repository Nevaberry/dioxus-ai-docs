# Embedded Swift

Embedded Swift additions from batches `6.2` and `6.3-embedded-and-c`.

## Contents

- [Standard library coverage](#standard-library-coverage)
- [Restriction diagnostics](#restriction-diagnostics)
- [MMIO tooling](#mmio-tooling)
- [LLDB inspection](#lldb-inspection)
- [Object-file control](#object-file-control)
- [Linkage and definition visibility](#linkage-and-definition-visibility)

## Standard library coverage

Swift 6.2 Embedded Swift supports the full `String` API, existential `any` types for class-constrained protocols, and the `InlineArray` and `Span` types.

Since 6.3, the Embedded standard library subset also includes `description` and `debugDescription` for floating-point types such as `Float` and `Double`.

## Restriction diagnostics

The `EmbeddedRestrictions` diagnostic group warns about constructs that Embedded Swift does not support, including untyped throws and calls to generic functions on existential values. It is enabled by default for Embedded Swift. Apply it to an ordinary build to check compatibility before switching build modes.

```sh
swiftc -Wwarning EmbeddedRestrictions Sources/App.swift
```

```swift
swiftSettings: [
    .treatWarning("EmbeddedRestrictions", as: .warning),
]
```

## MMIO tooling

Swift MMIO 0.1.x adds `svd2swift` and a SwiftPM plugin that generate MMIO interfaces from CMSIS SVD files, either manually or during a build.

Its SVD2LLDB plugin addresses registers by device name and can decode fields visually:

```text
svd decode TIMER0.CR 0x0123_4567 --visual
```

## LLDB inspection

LLDB's `memory read` accepts `-t` with a Swift type to render an arbitrary address as that value.

```text
(lldb) memory read -t MyMessage 0x000000016fdfe970
```

Improved DWARF and LLDB support also makes `Array`, `Dictionary`, nested generic aliases, and `InlineArray` inspectable in Embedded Swift core dumps without a live expression evaluator.

## Object-file control

Use `@section` to place a global in a named object-file section and `@used` to force an entity to be emitted even when it appears unused. Choose platform-specific section names with the `objectFormat` condition for `ELF`, `COFF`, `MachO`, or `Wasm`.

```swift
#if objectFormat(ELF)
@section("mysection")
#elseif objectFormat(MachO)
@section("__DATA,mysection")
#endif
@used
let linkerEntry: Int = 42
```

## Linkage and definition visibility

Imported Embedded Swift module symbols are emitted as weak definitions. The linker can therefore deduplicate diamond dependencies without the older `-mergeable-symbols` and `-emit-empty-object-file` workarounds.

Use `@export(implementation)` when clients may emit, specialize, or inline a definition. It supersedes `@_alwaysEmitIntoClient`. Use `@export(interface)` to expose only a callable symbol while hiding its definition from clients, including in Embedded Swift.
