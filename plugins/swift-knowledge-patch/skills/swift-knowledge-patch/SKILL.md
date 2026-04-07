---
name: swift-knowledge-patch
description: "Swift changes since training cutoff (5.10\u20136.3) \u2014 approachable concurrency, InlineArray, @c interop, module selectors, Swift Testing updates. Load before working with Swift."
license: MIT
version: "6.3"
metadata:
  author: Nevaberry
---

# Swift 5.10\u20136.3 Knowledge Patch

Claude's baseline knowledge covers Swift through 5.9. This skill provides features from 5.10 (March 2024) through 6.3 (March 2026).

## Quick Reference

### Concurrency

| Feature | Summary |
|---------|---------|
| `-default-isolation MainActor` | All code MainActor-isolated by default (per module) |
| `@concurrent` | Opt function into concurrent thread pool |
| Nonisolated async | Runs on caller's actor by default (SE-0461) |
| `Task.immediate` | Starts synchronously on caller's executor |
| `isolated deinit` | Runs deinit on actor's executor |
| `weak let` | Immutable weak ref, enables Sendable |
| `@MainActor Equatable` | Actor-isolated protocol conformances |
| `Task(name:)` | Named tasks for debugging |

```swift
// Enable approachable concurrency features per-target:
.enableUpcomingFeature("NonisolatedNonsendingByDefault")
.enableUpcomingFeature("InferIsolatedConformances")
```

See `references/concurrency.md` for full details and examples.

### Language Features

| Feature | Example |
|---------|---------|
| `InlineArray` | `var buf: InlineArray<40, Sprite>` or `[40 of Sprite]` |
| Method key paths | `strings.map(\.uppercased())` |
| Default interpolation | `"\(age, default: "Unknown")"` |
| `enumerated()` | Now conforms to `Collection` |
| Module selectors | `ModuleA::getValue()` |
| `@c` attribute | Expose Swift functions to C |

See `references/language-features.md` for syntax, limitations, and examples.

### Swift Testing

| Feature | API |
|---------|-----|
| Exit tests | `#expect(processExitsWith: .failure) { ... }` |
| Attachments | `Attachment.record("debug info")` |
| Warnings | `Issue.record("msg", severity: .warning)` |
| Cancel test | `try Test.cancel()` |

See `references/swift-testing.md` for details.

### New APIs

| API | Purpose |
|-----|---------|
| `Observations { }` | Async sequence from `@Observable` types |
| `Subprocess` | Process execution (`import Subprocess`) |
| Typed `NotificationCenter` | Type-safe notifications (no string names) |

See `references/new-apis.md` for details.

## Reference Files

| File | Contents |
|------|----------|
| `concurrency.md` | MainActor default, @concurrent, Task.immediate, isolated deinit, weak let |
| `language-features.md` | InlineArray, key paths, interpolation, module selectors, @c interop |
| `swift-testing.md` | Exit tests, attachments, warnings, test cancellation |
| `new-apis.md` | Observations, Subprocess, typed NotificationCenter |

## Critical Examples

### Approachable Concurrency (6.2)

```swift
// With -default-isolation MainActor, no annotations needed:
struct ImageCache {
    static var cache: [URL: Image] = [:]

    static func load(from url: URL) async throws -> Image {
        if let img = cache[url] { return img }
        let img = try await fetchImage(at: url) // stays on MainActor
        cache[url] = img
        return img
    }

    @concurrent // explicitly run off MainActor
    static func fetchImage(at url: URL) async throws -> Image {
        let (data, _) = try await URLSession.shared.data(from: url)
        return decode(data)
    }
}
```

### InlineArray (6.2)

```swift
var bricks: InlineArray<40, Sprite> = .init(repeating: defaultSprite)
// Shorthand:
var bricks2: [40 of Sprite] = .init(repeating: defaultSprite)

bricks[0] = specialSprite
for i in bricks.indices { print(bricks[i]) } // use indices, not for-in
```

### @c Attribute for C Interop (6.3)

```swift
@c func mySwiftFunction() { /* ... */ }
// Generated header: void mySwiftFunction(void);

@c(MyLib_doWork) func doWork() { /* ... */ }
// Generated header: void MyLib_doWork(void);

@c @implementation func existingCFunction() { /* ... */ }
// Validates against pre-existing C header declaration
```

### Module Selectors (6.3)

```swift
import ModuleA
import ModuleB
let x = ModuleA::getValue()
let y = ModuleB::getValue()

// Access Swift concurrency types without ambiguity:
let task = Swift::Task { await doWork() }
```

### Observations Async Sequence (6.2)

```swift
@Observable class Store { var items: [String] = []; var loading = false }
let store = Store()

let stream = Observations {
    (items: store.items, loading: store.loading) // tracks both properties
}
for await snapshot in stream {
    render(snapshot.items, snapshot.loading)
}
```

### Swift Testing: Exit Tests (6.2)

```swift
@Test func preconditionFires() async {
    await #expect(processExitsWith: .failure) {
        precondition(false)
    }
}
```
