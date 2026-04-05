# New Types and APIs (Swift 6.2)

## InlineArray

Fixed-size array with inline storage (stack-allocated). Uses shorthand syntax `[N of T]`:

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

Key characteristics:
- Generic type: `InlineArray<Count, Element>` where `Count` is an integer generic parameter
- Shorthand: `[N of T]` in type position
- Stack-allocated — no heap allocation
- Fixed size known at compile time
- Supports subscript access and iteration
- Initialize with `init(repeating:)` or array literal

## Span

Safe, non-owning view into contiguous memory with compile-time lifetime safety. Zero runtime overhead — replaces many `UnsafeBufferPointer` uses:

```swift
func process(_ data: Span<UInt8>) {
  for byte in data { /* ... */ }
}

let array = [1, 2, 3]
let span: Span<Int> = array.span
```

Key characteristics:
- Non-owning: does not retain the underlying storage
- Lifetime-safe: compiler enforces that the span does not outlive its source
- Zero overhead: no reference counting, no runtime checks beyond bounds
- Access via `.span` property on `Array`, `InlineArray`, and other contiguous collections

## Subprocess

New concurrency-friendly API for launching external processes. Replaces the older `Process`/`NSTask` API with a modern async interface:

```swift
import Subprocess

let result = try await run(.path("/usr/bin/swift"), arguments: ["--version"])
let output = result.standardOutput
```

## Typed NotificationCenter

Notifications use concrete types instead of string names and untyped dictionaries. Provides type safety and concurrency correctness:

```swift
struct UserLoggedIn: NotificationCenter.MainActorMessage {
  var userName: String
}

// Post
NotificationCenter.default.post(UserLoggedIn(userName: "alice"))

// Observe — type-safe, concurrency-correct
let token = NotificationCenter.default.addObserver(of: UserLoggedIn.self) { notification in
  print(notification.userName)
}
```

Key points:
- Define notification types conforming to `NotificationCenter.MainActorMessage` (or appropriate protocol)
- Post with concrete typed instances
- Observe with type parameter — no more stringly-typed notification names
- Concurrency annotations are part of the protocol conformance
