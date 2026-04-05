---
name: swift-knowledge-patch
description: "Swift 6.1–6.3 knowledge: default MainActor isolation, @concurrent, InlineArray, Span, @c interop, module selectors, Swift Testing updates. Load before writing Swift 6.1+ code."
license: MIT
metadata:
  author: Nevaberry
  version: "6.3.0"
---

# Swift Knowledge Patch (6.1–6.3)

Covers Swift 6.1 (March 2025) through 6.3 (March 2026). Assumes knowledge of Swift through 6.0 (typed throws, ~Copyable generics, data-race safety, Swift Testing, Embedded Swift preview, 128-bit integers).

## Reference Files

- **`references/concurrency.md`** — default MainActor isolation, @concurrent, nonisolated changes, task group inference, Observations async sequence
- **`references/new-types-and-apis.md`** — InlineArray, Span, Subprocess, Typed NotificationCenter
- **`references/interop.md`** — @c attribute, @objc @implementation, module selectors
- **`references/swift-testing.md`** — TestScoping, exit tests, attachments, warning issues, cancellation

## What's New by Version

| Version | Key Features |
|---------|-------------|
| 6.1 | `nonisolated` on types/extensions, task group type inference, trailing commas everywhere, `@objc @implementation`, package traits, Swift Testing `TestScoping` |
| 6.2 | Default `@MainActor` isolation, `@concurrent`, `InlineArray`, `Span`, `Subprocess`, Typed `NotificationCenter`, `Observations`, exit tests, attachments, precise warning control, strict memory safety |
| 6.3 | `@c` attribute (Swift→C interop), module selectors (`ModuleA::name`), Swift Testing warning issues + cancellation |

## Concurrency Model Changes (6.1–6.2)

The biggest behavioral changes across these releases. See **`references/concurrency.md`** for full details.

### Default MainActor isolation (6.2)
New compiler flag makes all unannotated code `@MainActor` by default — ideal for apps and UI code:
```swift
// Package.swift
.target(name: "MyApp", swiftSettings: [
  .defaultIsolation(MainActor.self),
])
```
Use `nonisolated` to opt out. Use `@concurrent` for concurrent thread pool execution.

### @concurrent (6.2)
Explicitly marks async functions to run on the concurrent thread pool (off-actor):
```swift
@concurrent
static func fetchImage(at url: URL) async throws -> Image {
  let (data, _) = try await URLSession.shared.data(from: url)
  return await decode(data: data)
}
```

### nonisolated async runs on caller's actor (6.2)
Under the `NonisolatedNonsendingByDefault` feature flag (default in 6.2), nonisolated async functions run on the caller's actor instead of switching to the global executor. Use `@concurrent` when you explicitly want off-actor execution.

### nonisolated on types and extensions (6.1)
Prevents `@MainActor` inference on conformances:
```swift
@MainActor struct S { let id: Int }

nonisolated extension S: Equatable {
  static func ==(lhs: S, rhs: S) -> Bool { lhs.id == rhs.id }
}
```

### Task group type inference (6.1)
`withTaskGroup` / `withThrowingTaskGroup` no longer require the `of:` parameter:
```swift
let results = await withTaskGroup { group in
  for id in ids {
    group.addTask { await fetch(id) }
  }
  return await group.reduce(into: []) { $0.append($1) }
}
```

## InlineArray (6.2)

Fixed-size, stack-allocated array. Shorthand syntax `[N of T]`:
```swift
struct Game {
  var bricks: [40 of Sprite]  // shorthand for InlineArray<40, Sprite>
  init(_ sprite: Sprite) {
    bricks = .init(repeating: sprite)
  }
}

var arr: InlineArray<3, Int> = [1, 2, 3]
arr[0] = 10
for item in arr { print(item) }
```

## Span (6.2)

Safe, non-owning view into contiguous memory with compile-time lifetime safety (no runtime overhead). Replaces many `UnsafeBufferPointer` uses:
```swift
func process(_ data: Span<UInt8>) {
  for byte in data { /* ... */ }
}

let array = [1, 2, 3]
let span: Span<Int> = array.span
```

## C Interop: @c Attribute (6.3)

Expose Swift functions to C via generated headers. See **`references/interop.md`** for full details.
```swift
@c func processData(_ ptr: UnsafePointer<UInt8>, count: Int) -> Int32 { ... }
// Generated C header: int32_t processData(const uint8_t *, int);

@c(MyLib_processData)  // custom C name
func processData(_ ptr: UnsafePointer<UInt8>, count: Int) -> Int32 { ... }
```

## Module Selectors (6.3)

Disambiguate APIs from different modules using `::` syntax:
```swift
import ModuleA
import ModuleB

let x = ModuleA::getValue()
let task = Swift::Task { await doWork() }
```

## Language Ergonomics

### Trailing commas everywhere (6.1)
Allowed in tuples, parameter/argument lists, generic params, capture lists, and string interpolations:
```swift
let point = (x: 1, y: 2,)
func foo(a: Int, b: Int,) {}
foo(a: 1, b: 2,)
```

### Precise warning control (6.2)
```swift
.target(name: "MyLib", swiftSettings: [
  .treatAllWarnings(as: .error),
  .treatWarning("DeprecatedDeclaration", as: .warning),
])
```

### Package traits (6.1)
Conditional compilation and optional dependencies:
```swift
dependencies: [
  .package(url: "...", from: "1.0.0", traits: [.default, "Embedded"]),
]
```

### Opt-in strict memory safety (6.2)
Flags uses of unsafe constructs so you can replace them or explicitly acknowledge them. Opt-in per module for security-critical code.

### Raw identifier test names (6.2)
```swift
@Test func `square() returns x * x`() {
  #expect(square(4) == 16)
}
```
